"""
Visualization Generator Module - Generates 6 types of visualizations using Plotly
Coordinated with Person 1's LLM output to ensure data integrity.
"""

from typing import Dict, Any, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from src.utils.exceptions import VisualizationError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VisualizationGenerator:
    """Generate 6 types of visualizations based on LLM recommendations."""

    def __init__(self, styler: Optional["Styler"] = None):
        """
        Initialize visualization generator.
        
        Args:
            styler: Style configuration object (optional, uses defaults if None)
        """
        self.styler = styler

    def generate_scatter_plot(
        self,
        data: pd.DataFrame,
        x_col: str,
        y_col: str,
        color_col: Optional[str] = None,
        size_col: Optional[str] = None,
        title: str = "Scatter Plot",
        **kwargs
    ) -> go.Figure:
        """
        Generate scatter plot visualization.
        
        Args:
            data: DataFrame containing the data
            x_col: Column name for X-axis
            y_col: Column name for Y-axis
            color_col: Optional column for color encoding
            size_col: Optional column for size encoding
            title: Plot title
            
        Returns:
            Plotly Figure object
        """
        try:
            if x_col not in data.columns or y_col not in data.columns:
                raise VisualizationError(
                    f"Columns '{x_col}' or '{y_col}' not found in data"
                )

            fig = px.scatter(
                data,
                x=x_col,
                y=y_col,
                color=color_col,
                size=size_col,
                hover_data={col: ":.2f" if data[col].dtype in ['float64', 'float32'] else True 
                           for col in [x_col, y_col, color_col, size_col] 
                           if col and col in data.columns},
                title=title,
                **kwargs
            )

            if self.styler:
                fig = self.styler.apply_theme(fig)
            
            fig.update_layout(
                height=500,
                showlegend=True,
                hovermode='closest',
                plot_bgcolor='rgba(240, 240, 240, 0.5)',
                paper_bgcolor='white',
                font=dict(size=12, family="Arial, sans-serif"),
            )

            logger.info(f"Generated scatter plot: {x_col} vs {y_col}")
            return fig

        except Exception as e:
            logger.error(f"Error generating scatter plot: {str(e)}")
            raise VisualizationError(f"Failed to generate scatter plot: {str(e)}")

    def generate_bar_chart(
        self,
        data: pd.DataFrame,
        x_col: str,
        y_col: str,
        color_col: Optional[str] = None,
        title: str = "Bar Chart",
        barmode: str = "group",
        **kwargs
    ) -> go.Figure:
        """Generate bar chart visualization."""
        try:
            if x_col not in data.columns or y_col not in data.columns:
                raise VisualizationError(
                    f"Columns '{x_col}' or '{y_col}' not found in data"
                )

            fig = px.bar(
                data,
                x=x_col,
                y=y_col,
                color=color_col,
                barmode=barmode,
                title=title,
                **kwargs
            )

            if self.styler:
                fig = self.styler.apply_theme(fig)

            fig.update_layout(
                height=500,
                showlegend=True,
                xaxis_tickangle=-45,
                plot_bgcolor='rgba(240, 240, 240, 0.5)',
                paper_bgcolor='white',
                font=dict(size=12, family="Arial, sans-serif"),
            )

            logger.info(f"Generated bar chart: {x_col} vs {y_col}")
            return fig

        except Exception as e:
            logger.error(f"Error generating bar chart: {str(e)}")
            raise VisualizationError(f"Failed to generate bar chart: {str(e)}")

    def generate_line_chart(
        self,
        data: pd.DataFrame,
        x_col: str,
        y_col: str,
        color_col: Optional[str] = None,
        title: str = "Line Chart",
        **kwargs
    ) -> go.Figure:
        """Generate line chart visualization."""
        try:
            if x_col not in data.columns or y_col not in data.columns:
                raise VisualizationError(
                    f"Columns '{x_col}' or '{y_col}' not found in data"
                )

            data_sorted = data.sort_values(by=x_col)

            fig = px.line(
                data_sorted,
                x=x_col,
                y=y_col,
                color=color_col,
                markers=True,
                title=title,
                **kwargs
            )

            if self.styler:
                fig = self.styler.apply_theme(fig)

            fig.update_layout(
                height=500,
                showlegend=True,
                hovermode='x unified',
                plot_bgcolor='rgba(240, 240, 240, 0.5)',
                paper_bgcolor='white',
                font=dict(size=12, family="Arial, sans-serif"),
            )

            logger.info(f"Generated line chart: {x_col} vs {y_col}")
            return fig

        except Exception as e:
            logger.error(f"Error generating line chart: {str(e)}")
            raise VisualizationError(f"Failed to generate line chart: {str(e)}")

    def generate_histogram(
        self,
        data: pd.DataFrame,
        col: str,
        color_col: Optional[str] = None,
        nbins: int = 30,
        title: str = "Histogram",
        **kwargs
    ) -> go.Figure:
        """Generate histogram visualization."""
        try:
            if col not in data.columns:
                raise VisualizationError(f"Column '{col}' not found in data")

            fig = px.histogram(
                data,
                x=col,
                color=color_col,
                nbins=nbins,
                title=title,
                **kwargs
            )

            if self.styler:
                fig = self.styler.apply_theme(fig)

            fig.update_layout(
                height=500,
                showlegend=True,
                plot_bgcolor='rgba(240, 240, 240, 0.5)',
                paper_bgcolor='white',
                font=dict(size=12, family="Arial, sans-serif"),
            )

            logger.info(f"Generated histogram for column: {col}")
            return fig

        except Exception as e:
            logger.error(f"Error generating histogram: {str(e)}")
            raise VisualizationError(f"Failed to generate histogram: {str(e)}")

    def generate_box_plot(
        self,
        data: pd.DataFrame,
        y_col: str,
        x_col: Optional[str] = None,
        color_col: Optional[str] = None,
        title: str = "Box Plot",
        **kwargs
    ) -> go.Figure:
        """Generate box plot visualization with outlier detection."""
        try:
            if y_col not in data.columns:
                raise VisualizationError(f"Column '{y_col}' not found in data")

            if x_col and x_col not in data.columns:
                raise VisualizationError(f"Column '{x_col}' not found in data")

            fig = px.box(
                data,
                y=y_col,
                x=x_col,
                color=color_col,
                points="outliers",
                title=title,
                **kwargs
            )

            if self.styler:
                fig = self.styler.apply_theme(fig)

            fig.update_layout(
                height=500,
                showlegend=True,
                plot_bgcolor='rgba(240, 240, 240, 0.5)',
                paper_bgcolor='white',
                font=dict(size=12, family="Arial, sans-serif"),
            )

            logger.info(f"Generated box plot for: {y_col}")
            return fig

        except Exception as e:
            logger.error(f"Error generating box plot: {str(e)}")
            raise VisualizationError(f"Failed to generate box plot: {str(e)}")

    def generate_heatmap(
        self,
        data: pd.DataFrame,
        title: str = "Correlation Heatmap",
        **kwargs
    ) -> go.Figure:
        """Generate correlation heatmap visualization."""
        try:
            numeric_data = data.select_dtypes(include=[np.number])
            
            if numeric_data.empty:
                raise VisualizationError("No numeric columns found for heatmap")

            corr_matrix = numeric_data.corr()

            fig = go.Figure(
                data=go.Heatmap(
                    z=corr_matrix.values,
                    x=corr_matrix.columns,
                    y=corr_matrix.columns,
                    colorscale="RdBu",
                    zmid=0,
                    zmin=-1,
                    zmax=1,
                    text=np.round(corr_matrix.values, 2),
                    texttemplate="%{text}",
                    textfont={"size": 10},
                    hovertemplate="<b>%{y}</b> vs <b>%{x}</b><br>Correlation: %{z:.3f}<extra></extra>"
                )
            )

            fig.update_layout(
                title=title,
                height=500,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=12, family="Arial, sans-serif"),
                xaxis_tickangle=-45,
            )

            logger.info("Generated correlation heatmap")
            return fig

        except Exception as e:
            logger.error(f"Error generating heatmap: {str(e)}")
            raise VisualizationError(f"Failed to generate heatmap: {str(e)}")

    def create_from_llm_spec(
        self,
        data: pd.DataFrame,
        viz_spec: Dict[str, Any]
    ) -> go.Figure:
        """
        Create visualization from LLM specification.
        Harmonized with Person 1's LLM output format.
        """
        try:
            viz_type = viz_spec.get('type', '').lower()
            title = viz_spec.get('title', 'Visualization')
            
            if viz_type == 'scatter':
                return self.generate_scatter_plot(
                    data,
                    x_col=viz_spec['x_col'],
                    y_col=viz_spec['y_col'],
                    color_col=viz_spec.get('color_col'),
                    size_col=viz_spec.get('size_col'),
                    title=title
                )
            elif viz_type == 'bar':
                return self.generate_bar_chart(
                    data,
                    x_col=viz_spec['x_col'],
                    y_col=viz_spec['y_col'],
                    color_col=viz_spec.get('color_col'),
                    title=title,
                    barmode=viz_spec.get('barmode', 'group')
                )
            elif viz_type == 'line':
                return self.generate_line_chart(
                    data,
                    x_col=viz_spec['x_col'],
                    y_col=viz_spec['y_col'],
                    color_col=viz_spec.get('color_col'),
                    title=title
                )
            elif viz_type == 'histogram':
                return self.generate_histogram(
                    data,
                    col=viz_spec['x_col'],
                    color_col=viz_spec.get('color_col'),
                    nbins=viz_spec.get('nbins', 30),
                    title=title
                )
            elif viz_type == 'box':
                return self.generate_box_plot(
                    data,
                    y_col=viz_spec['y_col'],
                    x_col=viz_spec.get('x_col'),
                    color_col=viz_spec.get('color_col'),
                    title=title
                )
            elif viz_type == 'heatmap':
                return self.generate_heatmap(data, title=title)
            else:
                raise VisualizationError(f"Unknown visualization type: {viz_type}")

        except KeyError as e:
            logger.error(f"Missing required field in visualization spec: {str(e)}")
            raise VisualizationError(f"Invalid visualization specification: missing {str(e)}")
        except Exception as e:
            logger.error(f"Error creating visualization from spec: {str(e)}")
            raise VisualizationError(f"Failed to create visualization: {str(e)}")
