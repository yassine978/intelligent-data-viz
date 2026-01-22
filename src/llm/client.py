"""LLM Client for API calls using Groq."""
import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Client for interacting with Groq API."""

    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        """Initialize the LLM client.

        Args:
            model: The Groq model to use
                   Options: 
                   - llama-3.3-70b-versatile (recommended)
                   - llama-3.1-70b-versatile
                   - mixtral-8x7b-32768
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        self.client = Groq(api_key=api_key)
        self.model = model

    def generate_completion(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 2000,
        max_retries: int = 3
    ) -> str:
        """Generate a completion from the LLM with retry logic.

        Args:
            prompt: The prompt to send to the LLM
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            max_retries: Maximum number of retry attempts

        Returns:
            The generated text response

        Raises:
            Exception: If the API call fails after all retries
        """
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check if it's a rate limit error
                is_rate_limit = "rate" in error_msg or "limit" in error_msg or "429" in error_msg
                
                # Check if it's the last attempt
                is_last_attempt = attempt == max_retries - 1
                
                if is_rate_limit and not is_last_attempt:
                    # Exponential backoff: 2s, 4s, 8s
                    wait_time = 2 ** (attempt + 1)
                    print(f"⚠️  Rate limit hit. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                
                # If it's the last attempt or non-rate-limit error, raise
                raise Exception(f"Groq API error: {str(e)}")


# Quick test
if __name__ == "__main__":
    client = LLMClient()
    
    # Test basic call
    print("Testing Groq LLM client...")
    result = client.generate_completion("Say 'Hello from Groq!'")
    print(f"✅ Groq Response: {result}")
    
    # Test retry logic
    print("\nTesting with retry logic enabled...")
    result2 = client.generate_completion(
        "Say 'Hello again!'",
        max_retries=3
    )
    print(f"✅ Groq Response: {result2}")