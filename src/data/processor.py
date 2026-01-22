"""Data processing module for handling CSV files and data validation."""
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, List, Any
import io


class DataProcessor:
    """Handle CSV file loading, validation, and preprocessing."""

    def __init__(self, max_file_size_mb: int = 10):
        """Initialize the data processor.
        
        Args:
            max_file_size_mb: Maximum file size in megabytes
        """
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
    
    def _detect_encoding(self, file_content: bytes) -> str:
        """Detect file encoding.
        
        Args:
            file_content: Raw file bytes
            
        Returns:
            Detected encoding (e.g., 'utf-8', 'latin-1')
        """
        result = chardet.detect(file_content)
        encoding = result['encoding']
        
        # Default to utf-8 if detection fails
        if encoding is None:
            encoding = 'utf-8'
        
        # Handle common encoding aliases
        encoding_map = {
            'ascii': 'utf-8',
            'windows-1252': 'cp1252',
        }
        
        return encoding_map.get(encoding.lower(), encoding)
    
    def _detect_separator(self, file_content: str, encoding: str = 'utf-8') -> str:
        """Detect CSV separator/delimiter.
        
        Args:
            file_content: File content as string or bytes
            encoding: File encoding
            
        Returns:
            Detected separator (comma, semicolon, tab, pipe)
        """
        # Convert bytes to string if needed
        if isinstance(file_content, bytes):
            sample = file_content.decode(encoding, errors='replace')[:1000]
        else:
            sample = file_content[:1000]
        
        # Count potential separators in first few lines
        separators = {
            ',': sample.count(','),
            ';': sample.count(';'),
            '\t': sample.count('\t'),
            '|': sample.count('|')
        }
        
        # Return the most common one
        detected = max(separators, key=separators.get)
        
        # Default to comma if no clear winner
        if separators[detected] == 0:
            detected = ','
        
        return detected
    
    def load_csv(
        self, 
        file_path: Optional[str] = None,
        file_content: Optional[bytes] = None,
        encoding: Optional[str] = None,
        separator: Optional[str] = None
    ) -> pd.DataFrame:
        """Load CSV file from path or file content with automatic format detection.
        
        Args:
            file_path: Path to CSV file
            file_content: Raw bytes of CSV file (for uploaded files)
            encoding: File encoding (auto-detected if None)
            separator: CSV separator (auto-detected if None)
            
        Returns:
            Pandas DataFrame
            
        Raises:
            ValueError: If file is invalid or too large
        """
        try:
            # Load file content
            if file_path:
                path = Path(file_path)
                
                # Check file exists
                if not path.exists():
                    raise ValueError(f"File not found: {file_path}")
                
                # Check file size
                if path.stat().st_size > self.max_file_size_bytes:
                    max_mb = self.max_file_size_bytes / (1024 * 1024)
                    raise ValueError(f"File too large. Maximum size: {max_mb}MB")
                
                # Read file content
                with open(file_path, 'rb') as f:
                    file_bytes = f.read()
            
            elif file_content:
                # Check size
                if len(file_content) > self.max_file_size_bytes:
                    max_mb = self.max_file_size_bytes / (1024 * 1024)
                    raise ValueError(f"File too large. Maximum size: {max_mb}MB")
                
                file_bytes = file_content
            
            else:
                raise ValueError("Must provide either file_path or file_content")
            
            # Auto-detect encoding if not provided
            if encoding is None:
                encoding = self._detect_encoding(file_bytes)
                print(f"🔍 Detected encoding: {encoding}")
            
            # Decode file content
            try:
                file_str = file_bytes.decode(encoding)
            except UnicodeDecodeError:
                # Fallback encodings
                for fallback_enc in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        file_str = file_bytes.decode(fallback_enc)
                        encoding = fallback_enc
                        print(f"⚠️  Used fallback encoding: {encoding}")
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError("Could not decode file with any common encoding")
            
            # Auto-detect separator if not provided
            if separator is None:
                separator = self._detect_separator(file_str, encoding)
                sep_names = {',': 'comma', ';': 'semicolon', '\t': 'tab', '|': 'pipe'}
                print(f"🔍 Detected separator: {sep_names.get(separator, separator)}")
            
            # Try to read CSV with detected parameters
            try:
                df = pd.read_csv(
                    io.StringIO(file_str),
                    sep=separator,
                    encoding=encoding,
                    skipinitialspace=True,  # Remove leading whitespace
                    on_bad_lines='warn'      # Warn but don't fail on bad lines
                )
            except Exception as e:
                # Try with engine='python' for more flexibility
                df = pd.read_csv(
                    io.StringIO(file_str),
                    sep=separator,
                    encoding=encoding,
                    engine='python',
                    skipinitialspace=True,
                    on_bad_lines='warn'
                )
            
            # Validate DataFrame
            if df.empty:
                raise ValueError("CSV file is empty")
            
            if len(df.columns) < 2:
                raise ValueError("CSV must have at least 2 columns")
            
            # Clean column names (remove leading/trailing whitespace)
            df.columns = df.columns.str.strip()
            
            print(f"✅ Loaded CSV: {df.shape[0]} rows × {df.shape[1]} columns")
            
            return df
            
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty or corrupted")
        except pd.errors.ParserError as e:
            raise ValueError(f"CSV parsing error: {str(e)}")
        except Exception as e:
            if "CSV" in str(e) or "parse" in str(e).lower():
                raise ValueError(f"Error loading CSV: {str(e)}")
            raise
    

    def get_column_info(self, df: pd.DataFrame) -> Dict[str, str]:
        """Get information about each column's data type.

        Args:
            df: Pandas DataFrame

        Returns:
            Dictionary mapping column names to data types
        """
        column_info = {}

        for col in df.columns:
            dtype = df[col].dtype

            # Categorize data types for LLM understanding
            if pd.api.types.is_numeric_dtype(dtype):
                if pd.api.types.is_integer_dtype(dtype):
                    column_info[col] = "integer"
                else:
                    column_info[col] = "float"
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                column_info[col] = "datetime"
            elif pd.api.types.is_bool_dtype(dtype):
                column_info[col] = "boolean"
            else:
                # Check if it's categorical (few unique values)
                unique_ratio = df[col].nunique() / len(df)
                if unique_ratio < 0.05:  # Less than 5% unique values
                    column_info[col] = "categorical"
                else:
                    column_info[col] = "text"

        return column_info

    def get_sample_data(self, df: pd.DataFrame, n_rows: int = 3) -> str:
        """Get sample rows as formatted string.

        Args:
            df: Pandas DataFrame
            n_rows: Number of rows to sample

        Returns:
            Formatted string representation of sample data
        """
        return df.head(n_rows).to_string(index=False)

    def get_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic statistics about the dataset.

        Args:
            df: Pandas DataFrame

        Returns:
            Dictionary with statistics
        """
        stats = {
            "n_rows": len(df),
            "n_columns": len(df.columns),
            "columns": list(df.columns),
            "numeric_columns": list(df.select_dtypes(include=["number"]).columns),
            "categorical_columns": list(df.select_dtypes(include=["object"]).columns),
            "missing_values": df.isnull().sum().to_dict(),
            "total_missing": int(df.isnull().sum().sum()),
        }

        return stats

    def clean_data(self, df: pd.DataFrame, drop_missing: bool = False) -> pd.DataFrame:
        """Clean the dataset.

        Args:
            df: Pandas DataFrame
            drop_missing: Whether to drop rows with missing values

        Returns:
            Cleaned DataFrame
        """
        df_clean = df.copy()

        # Remove duplicate rows
        df_clean = df_clean.drop_duplicates()

        # Handle missing values
        if drop_missing:
            df_clean = df_clean.dropna()

        # Strip whitespace from string columns
        string_cols = df_clean.select_dtypes(include=["object"]).columns
        for col in string_cols:
            df_clean[col] = df_clean[col].str.strip()

        return df_clean

    def validate_columns_exist(self, df: pd.DataFrame, columns: List[str]) -> bool:
        """Validate that specified columns exist in the DataFrame.

        Args:
            df: Pandas DataFrame
            columns: List of column names to check

        Returns:
            True if all columns exist

        Raises:
            ValueError: If any column doesn't exist
        """
        missing_cols = [col for col in columns if col not in df.columns]

        if missing_cols:
            raise ValueError(f"Columns not found in dataset: {', '.join(missing_cols)}")

        return True


# Quick test
if __name__ == "__main__":
    # Create test CSV
    test_data = """price,size,rooms,location
100,50,2,Paris
200,75,3,Lyon
150,60,2,Paris
300,100,4,Lyon
250,85,3,Paris"""

    # Save test file
    with open("test_data.csv", "w") as f:
        f.write(test_data)

    # Test processor
    processor = DataProcessor()

    try:
        # Load data
        df = processor.load_csv("test_data.csv")
        print("✅ CSV loaded successfully!")
        print(f"   Shape: {df.shape}")

        # Get column info
        col_info = processor.get_column_info(df)
        print("\n📊 Column Information:")
        for col, dtype in col_info.items():
            print(f"   - {col}: {dtype}")

        # Get statistics
        stats = processor.get_statistics(df)
        print(f"\n📈 Statistics:")
        print(f"   - Rows: {stats['n_rows']}")
        print(f"   - Columns: {stats['n_columns']}")
        print(f"   - Numeric columns: {stats['numeric_columns']}")
        print(f"   - Categorical columns: {stats['categorical_columns']}")

        # Get sample data
        sample = processor.get_sample_data(df)
        print(f"\n📋 Sample Data:")
        print(sample)

        # Clean data
        df_clean = processor.clean_data(df)
        print(f"\n🧹 Cleaned data shape: {df_clean.shape}")

        # Validate columns
        processor.validate_columns_exist(df, ["price", "size"])
        print("✅ Column validation passed!")

        # Clean up
        import os

        os.remove("test_data.csv")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
