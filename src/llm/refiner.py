"""Refinement module for improving selected visualizations."""
import json
from typing import Dict, Any
import pandas as pd
from src.llm.client import LLMClient


class VisualizationRefiner:
    """Refine and enhance selected visualizations with additional details."""
    
    def __init__(self):
        """Initialize the refiner with LLM client."""
        self.llm = LLMClient()
    
    def refine_visualization(
        self,
        viz_config: Dict[str, Any],
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Refine a selected visualization with enhanced parameters.
        
        Args:
            viz_config: The selected visualization configuration
            df: The DataFrame being visualized
            
        Returns:
            Enhanced visualization parameters
        """
        # Get data statistics for the relevant columns
        stats = self._get_column_statistics(viz_config, df)
        
        # Generate refinement prompt
        prompt = self._create_refinement_prompt(viz_config, stats)
        
        # Get LLM suggestions
        try:
            response = self.llm.generate_completion(prompt, temperature=0.5)
            
            # Clean and parse response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            refinements = json.loads(response.strip())
            
            # Merge with original config
            enhanced_config = {**viz_config, **refinements}
            
            return enhanced_config
            
        except Exception as e:
            print(f"⚠️  Refinement failed: {e}")
            # Return original config with basic enhancements
            return self._add_basic_enhancements(viz_config, df)
    
    def _get_column_statistics(
        self,
        viz_config: Dict[str, Any],
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Get statistics for columns used in the visualization.
        
        Args:
            viz_config: Visualization configuration
            df: DataFrame
            
        Returns:
            Dictionary of statistics
        """
        stats = {}
        
        # Get relevant columns
        columns = []
        for key in ['x_axis', 'y_axis', 'color', 'group_by']:
            col = viz_config.get(key)
            if col and col in df.columns:
                columns.append(col)
        
        # Calculate statistics for each column
        for col in columns:
            col_stats = {
                'name': col,
                'dtype': str(df[col].dtype),
                'nunique': int(df[col].nunique()),
                'missing': int(df[col].isnull().sum())
            }
            
            if pd.api.types.is_numeric_dtype(df[col]):
                col_stats.update({
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'mean': float(df[col].mean()),
                    'median': float(df[col].median()),
                    'std': float(df[col].std())
                })
            elif pd.api.types.is_object_dtype(df[col]):
                value_counts = df[col].value_counts()
                col_stats.update({
                    'categories': int(df[col].nunique()),
                    'top_values': value_counts.head(5).to_dict()
                })
            
            stats[col] = col_stats
        
        return stats
    
    def _create_refinement_prompt(
        self,
        viz_config: Dict[str, Any],
        stats: Dict[str, Any]
    ) -> str:
        """Create prompt for visualization refinement.
        
        Args:
            viz_config: Current visualization configuration
            stats: Column statistics
            
        Returns:
            Refinement prompt
        """
        stats_str = json.dumps(stats, indent=2)
        
        return f"""You are a data visualization expert. Refine this visualization to make it more professional and informative.

**Current Visualization:**
- Type: {viz_config.get('viz_type')}
- Title: {viz_config.get('title')}
- X-axis: {viz_config.get('x_axis')}
- Y-axis: {viz_config.get('y_axis')}
- Color: {viz_config.get('color')}

**Data Statistics:**
{stats_str}

**Your Task:**
Provide refinements to enhance this visualization. Consider:
- Better axis labels with units
- Appropriate color scheme (colorblind-friendly)
- Useful annotations (if any)
- Optimal figure size and aspect ratio
- Any other improvements

**Output Format (JSON only):**
{{
  "axis_labels": {{
    "x": "Descriptive label with units",
    "y": "Descriptive label with units"
  }},
  "title": "Enhanced title (if improvement needed)",
  "color_palette": ["#color1", "#color2", "#color3"],
  "annotations": [
    {{"text": "Annotation text", "position": "description"}}
  ],
  "figure_size": {{
    "width": 10,
    "height": 6
  }},
  "additional_params": {{
    "show_grid": true,
    "show_legend": true,
    "font_size": 12
  }}
}}

Respond ONLY with valid JSON, no markdown or additional text."""
    
    def _add_basic_enhancements(
        self,
        viz_config: Dict[str, Any],
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Add basic enhancements without LLM.
        
        Args:
            viz_config: Original configuration
            df: DataFrame
            
        Returns:
            Enhanced configuration
        """
        enhanced = viz_config.copy()
        
        # Add axis labels if not present
        if 'axis_labels' not in enhanced:
            enhanced['axis_labels'] = {
                'x': viz_config.get('x_axis', 'X-axis'),
                'y': viz_config.get('y_axis', 'Y-axis')
            }
        
        # Add default color palette
        if 'color_palette' not in enhanced:
            enhanced['color_palette'] = [
                '#0173b2', '#de8f05', '#029e73', '#cc78bc',
                '#ca9161', '#fbafe4', '#949494', '#ece133'
            ]
        
        # Add default figure size
        if 'figure_size' not in enhanced:
            enhanced['figure_size'] = {'width': 10, 'height': 6}
        
        # Add default additional params
        if 'additional_params' not in enhanced:
            enhanced['additional_params'] = {
                'show_grid': True,
                'show_legend': viz_config.get('color') is not None,
                'font_size': 12
            }
        
        return enhanced


# Quick test
if __name__ == "__main__":
    # Create test data
    test_df = pd.DataFrame({
        'price': [100, 200, 150, 300, 250, 180, 220],
        'size': [50, 75, 60, 100, 85, 55, 70],
        'location': ['Paris', 'Lyon', 'Paris', 'Lyon', 'Paris', 'Lyon', 'Paris']
    })
    
    # Test configuration
    test_config = {
        'viz_type': 'scatter_plot',
        'title': 'Price vs Size',
        'x_axis': 'size',
        'y_axis': 'price',
        'color': 'location',
        'justification': 'Shows relationship between size and price'
    }
    
    # Test refiner
    refiner = VisualizationRefiner()
    
    try:
        refined = refiner.refine_visualization(test_config, test_df)
        
        print("✅ Refinement successful!")
        print("\n📊 Enhanced Configuration:")
        print(json.dumps(refined, indent=2))
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")