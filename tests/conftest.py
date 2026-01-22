import pytest
import pandas as pd
import tempfile
import os

@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing."""
    data = {
        "x": [1, 2, 3, 4, 5],
        "y": [10, 20, 30, 40, 50],
        "category": ["A", "B", "A", "B", "A"]
    }
    return pd.DataFrame(data)

@pytest.fixture
def temp_csv_file(sample_csv_data):
    """Temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        sample_csv_data.to_csv(f, index=False)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)

@pytest.fixture
def mock_openai_response():
    """Mock response from OpenAI API."""
    return {
        "choices": [
            {
                "message": {
                    "content": '{"visualizations": ["scatter", "bar", "line"], "justifications": ["Good for correlation", "Shows categories", "Trends over time"]}'
                }
            }
        ]
    }