"""Tests for LLM client module."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.llm.client import LLMClient


def test_client_initialization():
    """Test that client initializes correctly."""
    with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
        client = LLMClient()
        assert client.model == "llama-3.3-70b-versatile"


def test_client_initialization_no_api_key():
    """Test that client raises error without API key."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="GROQ_API_KEY not found"):
            LLMClient()


def test_client_custom_model():
    """Test client with custom model."""
    with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
        client = LLMClient(model="mixtral-8x7b-32768")
        assert client.model == "mixtral-8x7b-32768"


@patch('src.llm.client.Groq')
def test_generate_completion_success(mock_groq_class):
    """Test successful completion generation."""
    # Setup mock
    mock_client = Mock()
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()
    
    mock_message.content = "Test response"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    mock_groq_class.return_value = mock_client
    
    # Test
    with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
        client = LLMClient()
        result = client.generate_completion("Test prompt")
        
        assert result == "Test response"
        mock_client.chat.completions.create.assert_called_once()


@patch('src.llm.client.Groq')
@patch('time.sleep')
def test_generate_completion_retry_on_rate_limit(mock_sleep, mock_groq_class):
    """Test retry logic on rate limit error."""
    mock_client = Mock()
    
    # First call raises rate limit error, second succeeds
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()
    mock_message.content = "Success after retry"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    mock_client.chat.completions.create.side_effect = [
        Exception("Rate limit exceeded"),
        mock_response
    ]
    
    mock_groq_class.return_value = mock_client
    
    # Test
    with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
        client = LLMClient()
        result = client.generate_completion("Test prompt", max_retries=3)
        
        assert result == "Success after retry"
        assert mock_client.chat.completions.create.call_count == 2
        mock_sleep.assert_called_once()  # Should have slept once


@patch('src.llm.client.Groq')
def test_generate_completion_fails_after_max_retries(mock_groq_class):
    """Test that it fails after max retries."""
    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")
    mock_groq_class.return_value = mock_client
    
    with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
        client = LLMClient()
        
        with pytest.raises(Exception, match="Groq API error"):
            client.generate_completion("Test prompt", max_retries=2)


@patch('src.llm.client.Groq')
def test_generate_completion_with_custom_params(mock_groq_class):
    """Test completion with custom parameters."""
    mock_client = Mock()
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()
    
    mock_message.content = "Response"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    mock_groq_class.return_value = mock_client
    
    with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
        client = LLMClient()
        result = client.generate_completion(
            "Test",
            temperature=0.5,
            max_tokens=1000
        )
        
        # Check that custom params were passed
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['temperature'] == 0.5
        assert call_kwargs['max_tokens'] == 1000