"""Main analyzer for generating visualization recommendations."""
import json
import hashlib
from pathlib import Path
from typing import Dict, Any
import pandas as pd
from src.llm.client import LLMClient
from src.llm.prompts import PromptTemplates
from src.utils.token_counter import TokenCounter


class VisualizationAnalyzer:
    """Analyzes problems and generates visualization recommendations using LLM."""

    def __init__(self, use_cache: bool = True, track_tokens: bool = False):
        """Initialize the analyzer with LLM client.
        
        Args:
            use_cache: Whether to use caching for LLM responses
            track_tokens: Whether to track token usage
        """
        self.llm = LLMClient()
        self.prompts = PromptTemplates()
        self.use_cache = use_cache
        self.track_tokens = track_tokens
        
        # Setup cache directory
        self.cache_dir = Path("cache")
        if use_cache:
            self.cache_dir.mkdir(exist_ok=True)
        
        # Setup token counter
        if track_tokens:
            self.token_counter = TokenCounter()

# In analyze_and_recommend method, after getting LLM response:
        # Get LLM response
        print("🤖 Calling LLM API...")
        response = self.llm.generate_completion(prompt)
        
        # Track tokens if enabled
        if self.track_tokens:
            token_stats = self.token_counter.track_request(prompt, response)
            print(f"📊 Tokens used: {token_stats['total_tokens']} (${token_stats['estimated_cost']:.4f})")

    def _get_cache_key(self, problem: str, df: pd.DataFrame) -> str:
        """Generate unique cache key from problem and dataset.
        
        Args:
            problem: User's problem statement
            df: Pandas DataFrame
            
        Returns:
            Cache key string
        """
        # Create hash from problem
        problem_hash = hashlib.md5(problem.encode()).hexdigest()[:8]
        
        # Create hash from data structure (columns + shape)
        data_signature = f"{list(df.columns)}_{df.shape}"
        data_hash = hashlib.md5(data_signature.encode()).hexdigest()[:8]
        
        return f"{problem_hash}_{data_hash}"

    def _load_from_cache(self, cache_key: str) -> Dict[str, Any]:
        """Load result from cache if it exists.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached result or None
        """
        if not self.use_cache:
            return None
        
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                # If cache is corrupted, ignore it
                return None
        
        return None

    def _save_to_cache(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Save result to cache.
        
        Args:
            cache_key: Cache key
            result: Result to cache
        """
        if not self.use_cache:
            return
        
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
        except Exception as e:
            # Don't fail if caching fails
            print(f"Warning: Failed to save cache: {e}")

    def analyze_and_recommend(
        self, 
        problem: str, 
        df: pd.DataFrame,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """Analyze problem and dataset, return visualization recommendations.

        Args:
            problem: User's problem statement
            df: Pandas DataFrame with the data
            force_refresh: Skip cache and force new LLM call

        Returns:
            Dictionary with analysis and 3 visualization recommendations
        """
        # Check cache first (unless force_refresh)
        if not force_refresh:
            cache_key = self._get_cache_key(problem, df)
            cached_result = self._load_from_cache(cache_key)
            
            if cached_result is not None:
                print("✓ Using cached result")
                return cached_result
        
        # Prepare data information
        column_info = {col: str(df[col].dtype) for col in df.columns}
        sample_data = df.head(3).to_string()

        # Generate prompt
        prompt = self.prompts.analyze_problem_and_data(
            problem=problem, 
            column_info=column_info, 
            sample_data=sample_data,
            compact=True  # Use compact prompt to save ~30% tokens
        )

        # Get LLM response
        print("🤖 Calling LLM API...")
        response = self.llm.generate_completion(prompt)

        # Parse JSON response
        try:
            # Clean response (remove markdown code blocks if present)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]

            result = json.loads(response.strip())

            # Validate we have 3 visualizations
            if "visualizations" not in result:
                raise ValueError("Response missing 'visualizations' key")

            if len(result["visualizations"]) != 3:
                raise ValueError(
                    f"Expected 3 visualizations, got {len(result['visualizations'])}"
                )
            
            # Validate each visualization has required fields
            required_fields = ['viz_type', 'title', 'x_axis', 'y_axis', 'justification']
            for i, viz in enumerate(result["visualizations"]):
                missing_fields = [f for f in required_fields if f not in viz]
                if missing_fields:
                    raise ValueError(
                        f"Visualization {i+1} missing fields: {missing_fields}"
                    )
            
            # Save to cache
            if not force_refresh:
                self._save_to_cache(cache_key, result)
            
            return result

        except json.JSONDecodeError as e:
            raise Exception(
                f"Failed to parse LLM response as JSON: {str(e)}\n\nResponse was:\n{response}"
            )
        except Exception as e:
            raise Exception(f"Error processing LLM response: {str(e)}")
    
    def clear_cache(self) -> int:
        """Clear all cached results.
        
        Returns:
            Number of cache files deleted
        """
        if not self.cache_dir.exists():
            return 0
        
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        
        return count


# Quick test
if __name__ == "__main__":
    # Create sample data
    test_df = pd.DataFrame(
        {
            "price": [100, 200, 150, 300, 250],
            "size": [50, 75, 60, 100, 85],
            "location": ["Paris", "Lyon", "Paris", "Lyon", "Paris"],
        }
    )

    analyzer = VisualizationAnalyzer(use_cache=True)

    try:
        print("=" * 60)
        print("First call (will hit API):")
        print("=" * 60)
        result = analyzer.analyze_and_recommend(
            "What factors affect the price?", test_df
        )

        print("✅ Analysis successful!")
        print(f"\n📊 Analysis: {result['analysis']}")
        print(f"\n🎨 Generated {len(result['visualizations'])} visualizations:")
        for i, viz in enumerate(result["visualizations"], 1):
            print(f"\n  {i}. {viz['title']}")
            print(f"     Type: {viz['viz_type']}")
            print(f"     Justification: {viz['justification']}")
        
        print("\n" + "=" * 60)
        print("Second call with same data (will use cache):")
        print("=" * 60)
        result2 = analyzer.analyze_and_recommend(
            "What factors affect the price?", test_df
        )
        print("✅ Got result from cache!")
        
        # Test cache clearing
        print("\n" + "=" * 60)
        print("Testing cache clear:")
        print("=" * 60)
        cleared = analyzer.clear_cache()
        print(f"✅ Cleared {cleared} cached items")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")