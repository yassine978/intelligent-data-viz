"""Prompt templates for LLM-based visualization generation - Optimized for token efficiency."""
import json
from typing import Dict


class PromptTemplates:
    """Collection of prompt templates for visualization tasks."""
    
    @staticmethod
    def analyze_problem_and_data(
        problem: str,
        column_info: Dict[str, str],
        sample_data: str,
        compact: bool = True
    ) -> str:
        """Generate prompt for analyzing problem and recommending visualizations.
        
        Args:
            problem: User's problem statement
            column_info: Dictionary of column names to data types
            sample_data: Sample rows from the dataset
            compact: If True, use compact prompt (saves ~30% tokens)
            
        Returns:
            Formatted prompt for the LLM
        """
        if compact:
            return PromptTemplates._create_compact_prompt(problem, column_info, sample_data)
        else:
            return PromptTemplates._create_detailed_prompt(problem, column_info, sample_data)
    
    @staticmethod
    def _create_compact_prompt(
        problem: str,
        column_info: Dict[str, str],
        sample_data: str
    ) -> str:
        """Create compact, token-efficient prompt."""
        # Compact column info - just names and types
        columns_str = ", ".join([f"{col}({dtype})" for col, dtype in column_info.items()])
        
        # Limit sample data to first 200 chars
        sample_preview = sample_data[:200] + "..." if len(sample_data) > 200 else sample_data
        
        return f"""Data viz expert: analyze & recommend 3 visualizations.

PROBLEM: {problem}

COLUMNS: {columns_str}

SAMPLE:
{sample_preview}

TASK: Return 3 different viz recommendations following best practices.

VIZ TYPES: scatter_plot, bar_chart, line_chart, histogram, box_plot, heatmap

OUTPUT (JSON only):
{{
  "analysis": "brief insight",
  "visualizations": [
    {{
      "viz_type": "scatter_plot|bar_chart|line_chart|histogram|box_plot|heatmap",
      "title": "clear title",
      "x_axis": "column_name",
      "y_axis": "column_name",
      "color": "column_name or null",
      "group_by": null,
      "justification": "why this helps",
      "best_practices": ["practice1", "practice2"]
    }}
  ]
}}

Return 3 visualizations. JSON only, no markdown."""
    
    @staticmethod
    def _create_detailed_prompt(
        problem: str,
        column_info: Dict[str, str],
        sample_data: str
    ) -> str:
        """Create detailed prompt (uses more tokens but may give better results)."""
        columns_str = "\n".join([f"- {col}: {dtype}" for col, dtype in column_info.items()])
        
        return f"""You are an expert data visualization consultant. Analyze the problem and recommend visualizations.

**User's Problem:**
{problem}

**Dataset Columns:**
{columns_str}

**Sample Data (first 3 rows):**
{sample_data}

**Your Task:**
1. Analyze what the user wants to discover
2. Recommend EXACTLY 3 different visualization approaches
3. Each visualization must follow data visualization best practices

**Output Format (JSON only, no other text):**
{{
  "analysis": "Brief analysis of the user's question",
  "visualizations": [
    {{
      "viz_type": "scatter_plot",
      "title": "Descriptive title",
      "x_axis": "column_name",
      "y_axis": "column_name",
      "color": "optional_column_name or null",
      "group_by": "optional_column_name or null",
      "justification": "Why this visualization answers the question",
      "best_practices": ["practice1", "practice2", "practice3"]
    }},
    {{
      "viz_type": "bar_chart",
      "title": "Another title",
      "x_axis": "column_name",
      "y_axis": "column_name",
      "color": null,
      "group_by": null,
      "justification": "Why this is useful",
      "best_practices": ["practice1", "practice2"]
    }},
    {{
      "viz_type": "box_plot",
      "title": "Third option",
      "x_axis": "column_name",
      "y_axis": "column_name",
      "color": null,
      "group_by": null,
      "justification": "Why this helps",
      "best_practices": ["practice1", "practice2"]
    }}
  ]
}}

**Available viz_types:** scatter_plot, bar_chart, line_chart, histogram, box_plot, heatmap

Respond ONLY with valid JSON, no markdown code blocks, no additional text."""


# Quick test to compare token usage
if __name__ == "__main__":
    templates = PromptTemplates()
    
    test_columns = {
        'price': 'float64',
        'size': 'int64',
        'rooms': 'int64',
        'location': 'object',
        'year_built': 'int64'
    }
    
    test_sample = """price  size  rooms location  year_built
100    50    2     Paris     2010
200    75    3     Lyon      2015
150    60    2     Paris     2012"""
    
    test_problem = "What factors influence housing prices in French cities?"
    
    # Generate both versions
    compact = templates.analyze_problem_and_data(test_problem, test_columns, test_sample, compact=True)
    detailed = templates.analyze_problem_and_data(test_problem, test_columns, test_sample, compact=False)
    
    # Estimate tokens (rough estimate: 1 token ≈ 4 characters)
    compact_tokens = len(compact) // 4
    detailed_tokens = len(detailed) // 4
    savings = ((detailed_tokens - compact_tokens) / detailed_tokens) * 100
    
    print("=" * 60)
    print("TOKEN OPTIMIZATION COMPARISON")
    print("=" * 60)
    print(f"\n📊 Compact Prompt:")
    print(f"   Characters: {len(compact)}")
    print(f"   Est. Tokens: ~{compact_tokens}")
    print(f"\n📊 Detailed Prompt:")
    print(f"   Characters: {len(detailed)}")
    print(f"   Est. Tokens: ~{detailed_tokens}")
    print(f"\n💰 Savings: ~{savings:.1f}% fewer tokens with compact version")
    print(f"   (≈{detailed_tokens - compact_tokens} tokens saved per request)")
    
    print("\n" + "=" * 60)
    print("COMPACT PROMPT PREVIEW:")
    print("=" * 60)
    print(compact[:300] + "...\n")