"""Tests for visualization analyzer module."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import json
from pathlib import Path
import tempfile
from src.llm.analyzer import VisualizationAnalyzer


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        'price': [100, 200, 150, 300],
        'size': [50, 75, 60, 100],
        'location': ['Paris', 'Lyon', 'Paris', 'Lyon']
    })


@pytest.fixture
def mock_llm_response():
    """Mock LLM response with valid visualization recommendations."""
    return json.dumps({
        "analysis": "The data shows relationship between price and size",
        "visualizations": [
            {
                "viz_type": "scatter_plot",
                "title": "Price vs Size",
                "x_axis": "size",
                "y_axis": "price",
                "color": "location",
                "group_by": None,
                "justification": "Shows correlation",
                "best_practices": ["Clear axes", "Color coding"]
            },
            {
                "viz_type": "bar_chart",
                "title": "Average Price by Location",
                "x_axis": "location",
                "y_axis": "price",
                "color": None,
                "group_by": None,
                "justification": "Compares locations",
                "best_practices": ["Clear labels"]
            },
            {
                "viz_type": "box_plot",
                "title": "Price Distribution",
                "x_axis": "location",
                "y_axis": "price",
                "color": None,
                "group_by": None,
                "justification": "Shows distribution",
                "best_practices": ["Shows outliers"]
            }
        ]
    })


def test_analyzer_initialization():
    """Test analyzer initializes correctly."""
    with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
        analyzer = VisualizationAnalyzer(use_cache=False)
        assert analyzer.use_cache == False


@patch('src.llm.analyzer.LLMClient')
def test_analyze_and_recommend_success(mock_llm_class, sample_dataframe, mock_llm_response):
    """Test successful analysis and recommendation."""
    # Setup mock
    mock_llm = Mock()
    mock_llm.generate_completion.return_value = mock_llm_response
    mock_llm_class.return_value = mock_llm
    
    # Test
    analyzer = VisualizationAnalyzer(use_cache=False)
    result = analyzer.analyze_and_recommend(
        "What affects price?",
        sample_dataframe
    )
    
    # Verify result structure
    assert 'analysis' in result
    assert 'visualizations' in result
    assert len(result['visualizations']) == 3
    
    # Verify each visualization has required fields
    for viz in result['visualizations']:
        assert 'viz_type' in viz
        assert 'title' in viz
        assert 'x_axis' in viz
        assert 'y_axis' in viz
        assert 'justification' in viz


@patch('src.llm.analyzer.LLMClient')
def test_analyze_handles_markdown_json(mock_llm_class, sample_dataframe, mock_llm_response):
    """Test that analyzer handles JSON wrapped in markdown code blocks."""
    mock_llm = Mock()
    # Wrap response in markdown code block
    mock_llm.generate_completion.return_value = f"```json\n{mock_llm_response}\n```"
    mock_llm_class.return_value = mock_llm
    
    analyzer = VisualizationAnalyzer(use_cache=False)
    result = analyzer.analyze_and_recommend("Test", sample_dataframe)
    
    assert 'visualizations' in result
    assert len(result['visualizations']) == 3


@patch('src.llm.analyzer.LLMClient')
def test_analyze_fails_on_invalid_json(mock_llm_class, sample_dataframe):
    """Test that analyzer raises error on invalid JSON."""
    mock_llm = Mock()
    mock_llm.generate_completion.return_value = "Not valid JSON at all"
    mock_llm_class.return_value = mock_llm
    
    analyzer = VisualizationAnalyzer(use_cache=False)
    
    with pytest.raises(Exception, match="Failed to parse"):
        analyzer.analyze_and_recommend("Test", sample_dataframe)


@patch('src.llm.analyzer.LLMClient')
def test_analyze_fails_on_wrong_number_of_visualizations(mock_llm_class, sample_dataframe):
    """Test that analyzer validates number of visualizations."""
    mock_llm = Mock()
    # Return only 2 visualizations instead of 3
    bad_response = json.dumps({
        "analysis": "Test",
        "visualizations": [
            {"viz_type": "scatter_plot", "title": "Test", "x_axis": "a", "y_axis": "b", "justification": "test"},
            {"viz_type": "bar_chart", "title": "Test2", "x_axis": "c", "y_axis": "d", "justification": "test"}
        ]
    })
    mock_llm.generate_completion.return_value = bad_response
    mock_llm_class.return_value = mock_llm
    
    analyzer = VisualizationAnalyzer(use_cache=False)
    
    with pytest.raises(Exception, match="Expected 3 visualizations"):
        analyzer.analyze_and_recommend("Test", sample_dataframe)


@patch('src.llm.analyzer.LLMClient')
def test_analyze_fails_on_missing_visualizations_key(mock_llm_class, sample_dataframe):
    """Test error when 'visualizations' key is missing."""
    mock_llm = Mock()
    bad_response = json.dumps({"analysis": "Test only"})
    mock_llm.generate_completion.return_value = bad_response
    mock_llm_class.return_value = mock_llm
    
    analyzer = VisualizationAnalyzer(use_cache=False)
    
    with pytest.raises(Exception, match="missing 'visualizations' key"):
        analyzer.analyze_and_recommend("Test", sample_dataframe)


@patch('src.llm.analyzer.LLMClient')
def test_caching_works(mock_llm_class, sample_dataframe, mock_llm_response):
    """Test that caching system works."""
    mock_llm = Mock()
    mock_llm.generate_completion.return_value = mock_llm_response
    mock_llm_class.return_value = mock_llm
    
    # Use temporary directory for cache
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = VisualizationAnalyzer(use_cache=True)
        analyzer.cache_dir = Path(tmpdir)
        
        # First call - should hit LLM
        result1 = analyzer.analyze_and_recommend("Test", sample_dataframe)
        assert mock_llm.generate_completion.call_count == 1
        
        # Second call with same data - should use cache
        result2 = analyzer.analyze_and_recommend("Test", sample_dataframe)
        assert mock_llm.generate_completion.call_count == 1  # Still 1, not 2
        
        # Results should be identical
        assert result1 == result2


@patch('src.llm.analyzer.LLMClient')
def test_force_refresh_bypasses_cache(mock_llm_class, sample_dataframe, mock_llm_response):
    """Test that force_refresh bypasses cache."""
    mock_llm = Mock()
    mock_llm.generate_completion.return_value = mock_llm_response
    mock_llm_class.return_value = mock_llm
    
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = VisualizationAnalyzer(use_cache=True)
        analyzer.cache_dir = Path(tmpdir)
        
        # First call
        analyzer.analyze_and_recommend("Test", sample_dataframe)
        
        # Second call with force_refresh
        analyzer.analyze_and_recommend("Test", sample_dataframe, force_refresh=True)
        
        # Should have called LLM twice
        assert mock_llm.generate_completion.call_count == 2


def test_clear_cache():
    """Test cache clearing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            analyzer = VisualizationAnalyzer(use_cache=True)
            analyzer.cache_dir = Path(tmpdir)
            
            # Create some dummy cache files
            (analyzer.cache_dir / "test1.json").write_text("{}")
            (analyzer.cache_dir / "test2.json").write_text("{}")
            
            # Clear cache
            count = analyzer.clear_cache()
            
            assert count == 2
            assert len(list(analyzer.cache_dir.glob("*.json"))) == 0


@patch('src.llm.analyzer.LLMClient')
def test_analyze_with_missing_required_fields(mock_llm_class, sample_dataframe):
    """Test that analyzer validates required fields in visualizations."""
    mock_llm = Mock()
    # Return visualization missing 'justification' field
    bad_response = json.dumps({
        "analysis": "Test",
        "visualizations": [
            {"viz_type": "scatter_plot", "title": "Test", "x_axis": "a", "y_axis": "b"},  # Missing justification
            {"viz_type": "bar_chart", "title": "Test", "x_axis": "a", "y_axis": "b", "justification": "ok"},
            {"viz_type": "line_chart", "title": "Test", "x_axis": "a", "y_axis": "b", "justification": "ok"}
        ]
    })
    mock_llm.generate_completion.return_value = bad_response
    mock_llm_class.return_value = mock_llm
    
    analyzer = VisualizationAnalyzer(use_cache=False)
    
    with pytest.raises(Exception, match="missing fields"):
        analyzer.analyze_and_recommend("Test", sample_dataframe)