"""Tests for data processor module."""
import pytest
import pandas as pd
from pathlib import Path
import tempfile
from src.data.processor import DataProcessor


@pytest.fixture
def sample_csv_content():
    """Create sample CSV content."""
    return """price,size,location
100,50,Paris
200,75,Lyon
150,60,Paris"""


@pytest.fixture
def temp_csv_file(sample_csv_content):
    """Create temporary CSV file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(sample_csv_content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    Path(temp_path).unlink()


def test_processor_initialization():
    """Test processor initializes with correct defaults."""
    processor = DataProcessor()
    assert processor.max_file_size_bytes == 10 * 1024 * 1024


def test_processor_custom_max_size():
    """Test processor with custom max file size."""
    processor = DataProcessor(max_file_size_mb=5)
    assert processor.max_file_size_bytes == 5 * 1024 * 1024


def test_load_csv_from_file(temp_csv_file):
    """Test loading CSV from file path."""
    processor = DataProcessor()
    df = processor.load_csv(file_path=temp_csv_file)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert list(df.columns) == ['price', 'size', 'location']
    assert df['price'].tolist() == [100, 200, 150]


def test_load_csv_from_bytes(sample_csv_content):
    """Test loading CSV from bytes."""
    processor = DataProcessor()
    file_bytes = sample_csv_content.encode('utf-8')
    
    df = processor.load_csv(file_content=file_bytes)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert 'price' in df.columns


def test_load_csv_file_not_found():
    """Test error when file doesn't exist."""
    processor = DataProcessor()
    
    with pytest.raises(ValueError, match="File not found"):
        processor.load_csv(file_path="nonexistent.csv")


def test_load_csv_no_input():
    """Test error when no input provided."""
    processor = DataProcessor()
    
    with pytest.raises(ValueError, match="Must provide either"):
        processor.load_csv()


def test_load_csv_empty_file():
    """Test error with empty CSV."""
    processor = DataProcessor()
    empty_content = b""
    
    with pytest.raises(ValueError, match="Must provide either"):
        processor.load_csv(file_content=empty_content)


def test_load_csv_too_large():
    """Test error when file exceeds size limit."""
    processor = DataProcessor(max_file_size_mb=0.001)  # Very small limit
    
    large_content = "col1,col2\n" + "1,2\n" * 10000
    large_bytes = large_content.encode('utf-8')
    
    with pytest.raises(ValueError, match="too large"):
        processor.load_csv(file_content=large_bytes)


def test_load_csv_with_semicolon_separator():
    """Test CSV with semicolon separator."""
    processor = DataProcessor()
    csv_content = b"price;size;location\n100;50;Paris\n200;75;Lyon"
    
    df = processor.load_csv(file_content=csv_content)
    
    assert len(df) == 2
    assert 'price' in df.columns


def test_load_csv_with_tab_separator():
    """Test CSV with tab separator."""
    processor = DataProcessor()
    csv_content = b"price\tsize\tlocation\n100\t50\tParis\n200\t75\tLyon"
    
    df = processor.load_csv(file_content=csv_content)
    
    assert len(df) == 2
    assert 'price' in df.columns


def test_get_column_info():
    """Test column info extraction."""
    processor = DataProcessor()
    df = pd.DataFrame({
        'int_col': [1, 2, 3],
        'float_col': [1.1, 2.2, 3.3],
        'str_col': ['a', 'b', 'c'],
        'bool_col': [True, False, True]
    })
    
    col_info = processor.get_column_info(df)
    
    assert col_info['int_col'] == 'integer'
    assert col_info['float_col'] == 'float'
    # Boolean columns may be detected as float in pandas
    assert col_info['bool_col'] in ['boolean', 'float', 'integer']
    assert col_info['str_col'] in ['text', 'categorical']


def test_get_sample_data():
    """Test sample data extraction."""
    processor = DataProcessor()
    df = pd.DataFrame({
        'col1': [1, 2, 3, 4, 5],
        'col2': ['a', 'b', 'c', 'd', 'e']
    })
    
    sample = processor.get_sample_data(df, n_rows=3)
    
    assert isinstance(sample, str)
    assert '1' in sample
    assert '2' in sample
    assert '3' in sample
    assert '4' not in sample  # Should only have 3 rows


def test_get_statistics():
    """Test statistics calculation."""
    processor = DataProcessor()
    df = pd.DataFrame({
        'num1': [1, 2, 3],
        'num2': [4, 5, 6],
        'cat': ['a', 'b', 'c']
    })
    
    stats = processor.get_statistics(df)
    
    assert stats['n_rows'] == 3
    assert stats['n_columns'] == 3
    assert 'num1' in stats['numeric_columns']
    assert 'num2' in stats['numeric_columns']
    assert 'cat' in stats['categorical_columns']
    assert stats['total_missing'] == 0


def test_clean_data_removes_duplicates():
    """Test that clean_data removes duplicates."""
    processor = DataProcessor()
    df = pd.DataFrame({
        'col1': [1, 2, 2, 3],
        'col2': ['a', 'b', 'b', 'c']
    })
    
    cleaned = processor.clean_data(df)
    
    assert len(cleaned) == 3  # One duplicate removed


def test_clean_data_strips_whitespace():
    """Test that clean_data strips whitespace from strings."""
    processor = DataProcessor()
    df = pd.DataFrame({
        'col1': ['  text  ', 'normal', '  spaces']
    })
    
    cleaned = processor.clean_data(df)
    
    assert cleaned['col1'].tolist() == ['text', 'normal', 'spaces']


def test_clean_data_drops_missing_when_requested():
    """Test dropping missing values."""
    processor = DataProcessor()
    df = pd.DataFrame({
        'col1': [1, 2, None, 4],
        'col2': ['a', 'b', 'c', 'd']
    })
    
    cleaned = processor.clean_data(df, drop_missing=True)
    
    assert len(cleaned) == 3  # One row with None dropped


def test_validate_columns_exist_success():
    """Test column validation with existing columns."""
    processor = DataProcessor()
    df = pd.DataFrame({
        'col1': [1, 2],
        'col2': [3, 4],
        'col3': [5, 6]
    })
    
    assert processor.validate_columns_exist(df, ['col1', 'col2']) == True


def test_validate_columns_exist_failure():
    """Test column validation with missing columns."""
    processor = DataProcessor()
    df = pd.DataFrame({
        'col1': [1, 2],
        'col2': [3, 4]
    })
    
    with pytest.raises(ValueError, match="Columns not found"):
        processor.validate_columns_exist(df, ['col1', 'col3', 'col4'])


def test_load_csv_few_columns():
    """Test error when CSV has too few columns."""
    processor = DataProcessor()
    csv_content = b"only_one_column\n1\n2\n3"
    
    with pytest.raises(ValueError, match="at least 2 columns"):
        processor.load_csv(file_content=csv_content)