"""
Visualization Exporter - Export visualizations to PNG and HTML formats
"""

import os
from typing import Optional, Tuple
import plotly.graph_objects as go
from src.utils.logger import get_logger
from src.utils.exceptions import VisualizationError

logger = get_logger(__name__)


class VisualizationExporter:
    """Export visualizations to various formats."""

    def __init__(self, output_dir: str = "./exports"):
        """
        Initialize exporter.
        
        Args:
            output_dir: Directory to save exports
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")

    def export_png(
        self,
        fig: go.Figure,
        filename: str,
        width: int = 1200,
        height: int = 800,
        scale: float = 2.0
    ) -> str:
        """
        Export visualization to PNG with high quality.
        
        Args:
            fig: Plotly Figure
            filename: Output filename (without extension)
            width: Image width in pixels
            height: Image height in pixels
            scale: Quality scale factor
            
        Returns:
            Full path to exported file
        """
        try:
            # Ensure filename is valid
            filename = filename.replace(' ', '_').replace('/', '_')
            filepath = os.path.join(self.output_dir, f"{filename}.png")
            
            # Export with high quality
            fig.write_image(
                filepath,
                width=width,
                height=height,
                scale=scale
            )
            
            logger.info(f"Exported PNG: {filepath} ({width}x{height}, scale={scale})")
            return filepath
        
        except Exception as e:
            logger.error(f"Error exporting PNG: {str(e)}")
            raise VisualizationError(f"Failed to export PNG: {str(e)}")

    def export_html(
        self,
        fig: go.Figure,
        filename: str,
        include_plotlyjs: str = 'cdn',
        config: Optional[dict] = None
    ) -> str:
        """
        Export visualization to interactive HTML.
        
        Args:
            fig: Plotly Figure
            filename: Output filename (without extension)
            include_plotlyjs: 'cdn', 'inline', 'require', or 'false'
            config: Plotly config options
            
        Returns:
            Full path to exported file
        """
        try:
            filename = filename.replace(' ', '_').replace('/', '_')
            filepath = os.path.join(self.output_dir, f"{filename}.html")
            
            default_config = {
                'responsive': True,
                'displayModeBar': True,
                'displaylogo': False,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': filename,
                    'height': 800,
                    'width': 1200,
                    'scale': 2
                }
            }
            
            if config:
                default_config.update(config)
            
            fig.write_html(
                filepath,
                include_plotlyjs=include_plotlyjs,
                config=default_config
            )
            
            logger.info(f"Exported HTML: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Error exporting HTML: {str(e)}")
            raise VisualizationError(f"Failed to export HTML: {str(e)}")

    def export_both(
        self,
        fig: go.Figure,
        filename: str,
        **kwargs
    ) -> Tuple[str, str]:
        """
        Export visualization to both PNG and HTML.
        
        Args:
            fig: Plotly Figure
            filename: Base filename (without extension)
            **kwargs: Additional arguments for export methods
            
        Returns:
            Tuple of (png_path, html_path)
        """
        try:
            png_path = self.export_png(fig, filename, **{k: v for k, v in kwargs.items() 
                                                         if k in ['width', 'height', 'scale']})
            html_path = self.export_html(fig, filename, **{k: v for k, v in kwargs.items() 
                                                           if k in ['include_plotlyjs', 'config']})
            
            logger.info(f"Exported both formats for: {filename}")
            return png_path, html_path
        
        except Exception as e:
            logger.error(f"Error exporting both formats: {str(e)}")
            raise VisualizationError(f"Failed to export both formats: {str(e)}")

    def export_with_metadata(
        self,
        fig: go.Figure,
        filename: str,
        metadata: dict,
        export_format: str = 'both'
    ) -> dict:
        """
        Export visualization with accompanying metadata.
        
        Args:
            fig: Plotly Figure
            filename: Output filename
            metadata: Dictionary with metadata (title, description, etc.)
            export_format: 'png', 'html', or 'both'
            
        Returns:
            Dictionary with export results
        """
        try:
            import json
            
            results = {'format': export_format, 'metadata': metadata}
            
            if export_format in ['png', 'both']:
                results['png_path'] = self.export_png(fig, filename)
            
            if export_format in ['html', 'both']:
                results['html_path'] = self.export_html(fig, filename)
            
            # Save metadata
            metadata_path = os.path.join(self.output_dir, f"{filename}_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            results['metadata_path'] = metadata_path
            
            logger.info(f"Exported with metadata: {filename}")
            return results
        
        except Exception as e:
            logger.error(f"Error exporting with metadata: {str(e)}")
            raise VisualizationError(f"Failed to export with metadata: {str(e)}")

    def list_exports(self) -> list:
        """List all exported files."""
        try:
            files = os.listdir(self.output_dir)
            logger.info(f"Found {len(files)} exported files")
            return sorted(files)
        except Exception as e:
            logger.error(f"Error listing exports: {str(e)}")
            return []

    def clear_exports(self) -> int:
        """Clear all exported files. Returns number of files deleted."""
        try:
            files = os.listdir(self.output_dir)
            for f in files:
                os.remove(os.path.join(self.output_dir, f))
            logger.info(f"Cleared {len(files)} export files")
            return len(files)
        except Exception as e:
            logger.error(f"Error clearing exports: {str(e)}")
            return 0
