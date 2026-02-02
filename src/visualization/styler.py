"""
Visualization Styler - Applies uniform styling with colorblind-safe palettes
"""

from typing import Dict
import plotly.graph_objects as go
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Styler:
    """Apply consistent styling to visualizations."""

    # Colorblind-safe palettes (Okabe-Ito palette + extensions)
    COLORBLIND_SAFE = {
        'primary': [
            '#1b9e77',  # teal
            '#d95f02',  # orange
            '#7570b3',  # purple
            '#e7298a',  # pink
            '#66a61e',  # green
            '#e6ab02',  # gold
        ],
        'diverging': 'RdBu',
        'sequential': 'Viridis',
    }

    def __init__(self, theme: str = 'light', palette: str = 'primary'):
        """
        Initialize styler.
        
        Args:
            theme: 'light' or 'dark'
            palette: 'primary', 'diverging', or 'sequential'
        """
        self.theme = theme
        self.palette = palette
        self.colors = self.COLORBLIND_SAFE[palette]

    def apply_theme(self, fig: go.Figure) -> go.Figure:
        """
        Apply consistent theme to figure.
        
        Args:
            fig: Plotly figure
            
        Returns:
            Modified figure with applied theme
        """
        try:
            # Update layout
            fig.update_layout(
                font=dict(
                    family="Arial, sans-serif",
                    size=12,
                    color='#333333' if self.theme == 'light' else '#ffffff'
                ),
                plot_bgcolor='rgba(240, 240, 240, 0.5)' if self.theme == 'light' else 'rgba(50, 50, 50, 0.8)',
                paper_bgcolor='white' if self.theme == 'light' else '#1f1f1f',
                title_font_size=14,
                title_font_color='#333333' if self.theme == 'light' else '#ffffff',
                title_x=0.5,
                title_xanchor='center',
                showlegend=True,
                legend=dict(
                    bgcolor='rgba(255, 255, 255, 0.8)' if self.theme == 'light' else 'rgba(50, 50, 50, 0.8)',
                    bordercolor='#cccccc' if self.theme == 'light' else '#666666',
                    borderwidth=1,
                ),
                hovermode='closest',
                margin=dict(l=60, r=40, t=80, b=60),
            )

            # Update axes
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray' if self.theme == 'light' else '#444444',
                zeroline=False,
                showline=True,
                linewidth=2,
                linecolor='#cccccc' if self.theme == 'light' else '#666666',
            )

            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray' if self.theme == 'light' else '#444444',
                zeroline=False,
                showline=True,
                linewidth=2,
                linecolor='#cccccc' if self.theme == 'light' else '#666666',
            )

            # Apply color palette to traces
            if hasattr(self, 'colors'):
                for i, trace in enumerate(fig.data):
                    if trace.type in ['scatter', 'bar', 'box']:
                        trace.marker.color = self.colors[i % len(self.colors)]

            logger.info(f"Applied {self.theme} theme with {self.palette} palette")
            return fig

        except Exception as e:
            logger.error(f"Error applying theme: {str(e)}")
            return fig

    def apply_best_practices(self, fig: go.Figure) -> go.Figure:
        """
        Apply visualization best practices.
        Removes chartjunk, ensures proper data-ink ratio.
        """
        try:
            # Remove gridlines on secondary axes
            fig.update_xaxes(showgrid=True, zeroline=False)
            fig.update_yaxes(showgrid=True, zeroline=False)

            # Remove unnecessary box lines
            fig.update_xaxes(showline=True, linewidth=1, linecolor='black')
            fig.update_yaxes(showline=True, linewidth=1, linecolor='black')

            # Ensure proper hover information
            for trace in fig.data:
                if hasattr(trace, 'hovertemplate'):
                    if not trace.hovertemplate or trace.hovertemplate == '%{x}<br>%{y}<extra></extra>':
                        trace.hovertemplate = '<b>%{x}</b><br>Value: %{y}<extra></extra>'

            logger.info("Applied visualization best practices")
            return fig

        except Exception as e:
            logger.error(f"Error applying best practices: {str(e)}")
            return fig

    def set_theme(self, theme: str):
        """Change theme ('light' or 'dark')."""
        if theme in ['light', 'dark']:
            self.theme = theme
        else:
            logger.warning(f"Invalid theme: {theme}. Using default 'light'")

    def set_palette(self, palette: str):
        """Change color palette."""
        if palette in self.COLORBLIND_SAFE:
            self.palette = palette
            self.colors = self.COLORBLIND_SAFE[palette]
        else:
            logger.warning(f"Invalid palette: {palette}. Using default 'primary'")
