"""Utility for estimating and tracking token usage."""
from typing import Dict, Any
import json
from pathlib import Path


class TokenCounter:
    """Track and estimate token usage for cost monitoring."""
    
    # Rough estimates (1 token ≈ 4 characters for English text)
    CHARS_PER_TOKEN = 4
    
    # Groq pricing (as of Jan 2024 - check current pricing)
    COST_PER_1K_TOKENS = {
        'llama-3.3-70b-versatile': 0.00027,  # $0.27 per 1M tokens
        'llama-3.1-70b-versatile': 0.00027,
        'mixtral-8x7b-32768': 0.00024,
        'llama-3.1-8b-instant': 0.00005,
    }
    
    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        """Initialize token counter.
        
        Args:
            model: Model name for cost calculation
        """
        self.model = model
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_requests = 0
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate number of tokens in text.
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        return len(text) // self.CHARS_PER_TOKEN
    
    def track_request(self, prompt: str, completion: str) -> Dict[str, Any]:
        """Track a request and return stats.
        
        Args:
            prompt: Prompt sent to LLM
            completion: Response from LLM
            
        Returns:
            Dictionary with token stats and cost
        """
        prompt_tokens = self.estimate_tokens(prompt)
        completion_tokens = self.estimate_tokens(completion)
        
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_requests += 1
        
        return {
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': prompt_tokens + completion_tokens,
            'estimated_cost': self._calculate_cost(prompt_tokens + completion_tokens)
        }
    
    def _calculate_cost(self, tokens: int) -> float:
        """Calculate estimated cost for tokens.
        
        Args:
            tokens: Number of tokens
            
        Returns:
            Estimated cost in USD
        """
        cost_per_token = self.COST_PER_1K_TOKENS.get(self.model, 0.0003) / 1000
        return tokens * cost_per_token
    
    def get_total_stats(self) -> Dict[str, Any]:
        """Get cumulative statistics.
        
        Returns:
            Dictionary with total stats
        """
        total_tokens = self.total_prompt_tokens + self.total_completion_tokens
        
        return {
            'total_requests': self.total_requests,
            'total_prompt_tokens': self.total_prompt_tokens,
            'total_completion_tokens': self.total_completion_tokens,
            'total_tokens': total_tokens,
            'total_estimated_cost': self._calculate_cost(total_tokens),
            'avg_tokens_per_request': total_tokens / self.total_requests if self.total_requests > 0 else 0
        }
    
    def save_stats(self, filepath: str = "token_usage.json") -> None:
        """Save statistics to file.
        
        Args:
            filepath: Path to save stats
        """
        stats = self.get_total_stats()
        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=2)
    
    def print_stats(self) -> None:
        """Print current statistics."""
        stats = self.get_total_stats()
        
        print("\n" + "=" * 60)
        print("TOKEN USAGE STATISTICS")
        print("=" * 60)
        print(f"Model: {self.model}")
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Total Tokens: {stats['total_tokens']:,}")
        print(f"  - Prompt: {stats['total_prompt_tokens']:,}")
        print(f"  - Completion: {stats['total_completion_tokens']:,}")
        print(f"Avg Tokens/Request: {stats['avg_tokens_per_request']:.0f}")
        print(f"Estimated Total Cost: ${stats['total_estimated_cost']:.4f}")
        print("=" * 60 + "\n")


# Quick test
if __name__ == "__main__":
    counter = TokenCounter()
    
    # Simulate some requests
    test_prompt = "What factors affect housing prices?" * 100  # ~500 chars
    test_completion = "Analysis: Price is affected by size and location." * 50  # ~250 chars
    
    # Track requests
    for i in range(5):
        stats = counter.track_request(test_prompt, test_completion)
        print(f"Request {i+1}: {stats['total_tokens']} tokens, ${stats['estimated_cost']:.6f}")
    
    # Print total stats
    counter.print_stats()
    
    # Save stats
    counter.save_stats("test_token_usage.json")
    print("✅ Stats saved to test_token_usage.json")