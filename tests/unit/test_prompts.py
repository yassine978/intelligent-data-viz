"""Tests for prompt templates module."""
import pytest
from src.llm.prompts import PromptTemplates


def test_analyze_problem_and_data_prompt():
    """Test that problem analysis prompt is generated correctly."""
    templates = PromptTemplates()
    
    column_info = {
        'price': 'float64',
        'size': 'int64',
        'location': 'object'
    }
    
    sample_data = "price,size,location\n100,50,Paris\n200,75,Lyon"
    
    prompt = templates.analyze_problem_and_data(
        problem="What affects housing prices?",
        column_info=column_info,
        sample_data=sample_data
    )
    
    # Check that all key elements are in the prompt
    assert "What affects housing prices?" in prompt
    assert "price" in prompt
    assert "size" in prompt
    assert "location" in prompt
    assert "float64" in prompt
    assert "int64" in prompt
    assert "object" in prompt
    assert sample_data in prompt
    
    # Check for key instructions
    assert "3" in prompt or "three" in prompt.lower()
    assert "JSON" in prompt
    assert "viz_type" in prompt
    assert "justification" in prompt


def test_prompt_includes_all_viz_types():
    """Test that prompt mentions all available visualization types."""
    templates = PromptTemplates()
    
    prompt = templates.analyze_problem_and_data(
        "Test problem",
        {'col1': 'int'},
        "col1\n1\n2"
    )
    
    # Check for all viz types
    viz_types = [
        'scatter_plot',
        'bar_chart',
        'line_chart',
        'histogram',
        'box_plot',
        'heatmap'
    ]
    
    for viz_type in viz_types:
        assert viz_type in prompt


def test_prompt_requests_json_output():
    """Test that prompt explicitly requests JSON output."""
    templates = PromptTemplates()
    
    prompt = templates.analyze_problem_and_data(
        "Test",
        {'col': 'int'},
        "col\n1"
    )
    
    assert "JSON" in prompt
    assert "markdown" in prompt.lower() or "code block" in prompt.lower()


def test_prompt_with_empty_columns():
    """Test prompt generation with minimal data."""
    templates = PromptTemplates()
    
    prompt = templates.analyze_problem_and_data(
        "Simple question",
        {},
        ""
    )
    
    assert "Simple question" in prompt
    assert isinstance(prompt, str)
    assert len(prompt) > 100  # Should still be a substantial prompt


def test_prompt_with_many_columns():
    """Test prompt with many columns."""
    templates = PromptTemplates()
    
    # Create 20 columns
    column_info = {f'col_{i}': 'float64' for i in range(20)}
    
    prompt = templates.analyze_problem_and_data(
        "Complex analysis",
        column_info,
        "sample data"
    )
    
    # Should include all columns
    for col in column_info.keys():
        assert col in prompt