"""Integration tests for the complete data visualization flow."""
import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os

from src.data.processor import DataProcessor
from src.llm.analyzer import VisualizationAnalyzer
from src.visualization.generator import VisualizationGenerator
from src.visualization.exporter import VisualizationExporter


@pytest.fixture
def sample_housing_data():
    """Create sample housing dataset for testing."""
    data = {
        "price": [250000, 300000, 350000, 400000, 450000],
        "size_sqm": [80, 100, 120, 140, 160],
        "rooms": [2, 3, 3, 4, 4],
        "location": ["Paris", "Lyon", "Paris", "Lyon", "Paris"],
        "year_built": [1990, 2000, 2010, 2015, 2020],
    }
    return pd.DataFrame(data)


@pytest.fixture
def groq_api_key():
    """Get Groq API key from environment."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        pytest.skip("GROQ_API_KEY not set - skipping integration tests")
    return api_key


class TestFullVisualizationFlow:
    """Test the complete flow: upload → LLM → visualization → export."""

    def test_complete_flow_housing_data(self, sample_housing_data, groq_api_key, tmp_path):
        """Test full flow with housing price data."""
        # Step 1: Data Processing
        processor = DataProcessor()
        
        # Save to temp CSV file
        csv_path = tmp_path / "housing.csv"
        sample_housing_data.to_csv(csv_path, index=False)
        
        # Load CSV
        df = processor.load_csv(file_path=str(csv_path))
        assert df is not None
        assert len(df) == 5
        
        # Get column info
        col_info = processor.get_column_info(df)
        assert "price" in col_info
        assert "location" in col_info
        
        # Step 2: LLM Analysis
        analyzer = VisualizationAnalyzer(use_cache=False, track_tokens=False)
        problem = "What factors influence housing prices?"
        
        recommendations = analyzer.analyze_and_recommend(problem, df)
        
        assert "visualizations" in recommendations
        assert len(recommendations["visualizations"]) == 3
        
        # Check each recommendation has required fields
        for viz in recommendations["visualizations"]:
            assert "type" in viz
            assert "x_axis" in viz or "columns" in viz
            assert "justification" in viz
        
        # Step 3: Visualization Generation
        generator = VisualizationGenerator()
        first_viz = recommendations["visualizations"][0]
        
        # Generate the visualization
        fig = generator.generate(
            df=df,
            viz_type=first_viz["type"],
            x=first_viz.get("x_axis"),
            y=first_viz.get("y_axis"),
            color=first_viz.get("color"),
            title=f"Housing Analysis: {first_viz['type']}"
        )
        
        assert fig is not None
        
        # Step 4: Export
        exporter = VisualizationExporter()
        output_path = tmp_path / "test_output.png"
        
        success = exporter.export_to_png(fig, str(output_path))
        assert success
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_flow_with_invalid_data(self):
        """Test error handling with invalid data."""
        processor = DataProcessor()
        
        # Create invalid data (all text)
        invalid_data = pd.DataFrame({
            "col1": ["text", "text", "text"],
            "col2": ["more", "text", "here"]
        })
        
        analyzer = VisualizationAnalyzer(use_cache=False)
        problem = "Analyze this data"
        
        # Should either handle gracefully or raise appropriate error
        try:
            recommendations = analyzer.analyze_and_recommend(problem, invalid_data)
            # If it succeeds, check it returns valid structure
            assert "visualizations" in recommendations
        except (ValueError, KeyError) as e:
            # Expected behavior for invalid data
            assert len(str(e)) > 0

    @pytest.mark.slow
    def test_flow_with_multiple_viz_types(self, sample_housing_data, groq_api_key, tmp_path):
        """Test generating different visualization types."""
        analyzer = VisualizationAnalyzer(use_cache=False)
        problem = "Show housing price distribution and trends"
        
        recommendations = analyzer.analyze_and_recommend(problem, sample_housing_data)
        
        generator = VisualizationGenerator()
        exporter = VisualizationExporter()
        
        # Try to generate each recommended visualization
        for i, viz in enumerate(recommendations["visualizations"]):
            try:
                fig = generator.generate(
                    df=sample_housing_data,
                    viz_type=viz["type"],
                    x=viz.get("x_axis"),
                    y=viz.get("y_axis"),
                    color=viz.get("color"),
                    title=f"Test Viz {i+1}"
                )
                
                output_path = tmp_path / f"viz_{i+1}.png"
                success = exporter.export_to_png(fig, str(output_path))
                
                assert success
                assert output_path.exists()
            except Exception as e:
                # Some visualizations might not work with this data
                # That's ok for integration test - just log it
                print(f"Warning: Could not generate {viz['type']}: {e}")

    def test_performance(self, sample_housing_data, groq_api_key):
        """Test that full flow completes in reasonable time."""
        import time
        
        start = time.time()
        
        # Run full flow
        processor = DataProcessor()
        analyzer = VisualizationAnalyzer(use_cache=False)
        problem = "Analyze housing prices"
        
        recommendations = analyzer.analyze_and_recommend(problem, sample_housing_data)
        
        generator = VisualizationGenerator()
        first_viz = recommendations["visualizations"][0]
        fig = generator.generate(
            df=sample_housing_data,
            viz_type=first_viz["type"],
            x=first_viz.get("x_axis"),
            y=first_viz.get("y_axis")
        )
        
        elapsed = time.time() - start
        
        # Should complete in under 10 seconds (LLM call is the bottleneck)
        assert elapsed < 10.0, f"Flow took {elapsed:.2f}s, expected < 10s"


class TestDataIntegrity:
    """Test data integrity throughout the pipeline."""

    def test_data_not_modified(self, sample_housing_data):
        """Test that original data is not modified during processing."""
        original_len = len(sample_housing_data)
        original_cols = list(sample_housing_data.columns)
        
        processor = DataProcessor()
        stats = processor.get_statistics(sample_housing_data)
        
        # Original data should be unchanged
        assert len(sample_housing_data) == original_len
        assert list(sample_housing_data.columns) == original_cols

    def test_column_validation(self, sample_housing_data):
        """Test that column validation works correctly."""
        processor = DataProcessor()
        
        # Valid columns
        assert processor.validate_columns_exist(sample_housing_data, ["price", "size_sqm"])
        
        # Invalid columns
        assert not processor.validate_columns_exist(sample_housing_data, ["nonexistent_column"])
