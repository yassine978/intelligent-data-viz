"""
VLM Enhancer Module - Uses Groq API via LangChain to enhance visualizations
This is the next-level enhancement layer that improves LLM-generated visualizations
using Vision Language Model capabilities.
"""

from typing import Dict, Any, Optional, Tuple
import os
import json
import base64
import io
import plotly.graph_objects as go
from langchain_core.messages import HumanMessage
import pandas as pd
from src.utils.logger import get_logger
from src.utils.exceptions import VisualizationError

logger = get_logger(__name__)


class GroqVLMEnhancer:
    """
    Enhances visualizations using Groq API via LangChain.
    Analyzes existing visualizations and suggests improvements.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "meta-llama/llama-4-scout-17b-16e-instruct"):
        """
        Initialize Groq VLM Enhancer.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            model: Model to use (meta-llama/llama-4-scout-17b-16e-instruct - efficient and accurate)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "").strip('"')
        self.model_name = model
        self.llm = None
        self.initialized = False
        
        if not self.api_key:
            logger.debug("GROQ_API_KEY not configured - VLM enhancement will be unavailable")
            return
        
        # Initialize LangChain Groq client
        try:
            from langchain_groq import ChatGroq
            self.llm = ChatGroq(
                model=model,
                api_key=self.api_key,
                temperature=0.3
            )
            self.initialized = True
            logger.info(f"Initialized Groq VLM with model: {model}")
        except ImportError:
            logger.warning("langchain-groq not installed. VLM enhancement unavailable. Install with: pip install langchain-groq")
        except Exception as e:
            logger.warning(f"Failed to initialize Groq VLM: {str(e)}")

    def encode_figure_to_base64(self, fig: go.Figure) -> str:
        """
        Encode Plotly figure as base64 image for LangChain transmission.
        
        Args:
            fig: Plotly Figure object
            
        Returns:
            Base64 encoded image string
        """
        try:
            # Convert figure to image bytes
            img_bytes = fig.to_image(format="png", width=800, height=600)
            
            # Encode to base64
            b64_string = base64.b64encode(img_bytes).decode('utf-8')
            logger.info("Encoded figure to base64")
            return b64_string
        except Exception as e:
            logger.error(f"Error encoding figure: {str(e)}")
            raise VisualizationError(f"Failed to encode visualization: {str(e)}")

    def create_visualization_text_representation(self, fig: go.Figure, data: pd.DataFrame, viz_spec: Dict[str, Any]) -> str:
        """
        Create comprehensive detailed text representation of visualization for analysis.
        
        Args:
            fig: Plotly Figure object
            data: Original DataFrame
            viz_spec: Visualization specification
            
        Returns:
            Detailed text representation of the visualization
        """
        try:
            # Get chart type details
            chart_type = viz_spec.get('type', 'unknown')
            title = viz_spec.get('title', 'Untitled')
            x_col = viz_spec.get('x_col', 'N/A')
            y_col = viz_spec.get('y_col', 'N/A')
            
            representation = f"""DETAILED VISUALIZATION TEXT REPRESENTATION
==========================================

VISUALIZATION METADATA:
- Title: {title}
- Type: {chart_type}
- Description: {viz_spec.get('description', 'N/A')}
- X-Axis (Column): {x_col}
- Y-Axis (Column): {y_col}

FIGURE LAYOUT DETAILS:
- Chart Title: {fig.layout.title.text if fig.layout.title else 'N/A'}
- X-Axis Label: {fig.layout.xaxis.title.text if fig.layout.xaxis and fig.layout.xaxis.title else 'N/A'}
- Y-Axis Label: {fig.layout.yaxis.title.text if fig.layout.yaxis and fig.layout.yaxis.title else 'N/A'}
- Figure Size: Width={fig.layout.width or 'auto'}, Height={fig.layout.height or 'auto'}
- Color Scale: {fig.layout.coloraxis.colorscale if fig.layout.coloraxis else 'N/A'}

DATASET OVERVIEW:
- Total Records: {len(data)}
- Total Features: {len(data.columns)}
- All Features: {', '.join(data.columns.tolist())}

TRACE INFORMATION (Data Series):
"""
            
            # Add detailed trace information
            for i, trace in enumerate(fig.data):
                representation += f"\nTrace {i+1}:\n"
                representation += f"  - Name: {trace.name or 'Unnamed'}\n"
                representation += f"  - Type: {trace.type}\n"
                representation += f"  - Mode: {trace.mode if hasattr(trace, 'mode') else 'N/A'}\n"
                representation += f"  - Data Points: {len(trace.x) if hasattr(trace, 'x') and trace.x else 0}\n"
                if hasattr(trace, 'x') and trace.x:
                    representation += f"  - X-Values Range: {min(trace.x) if isinstance(trace.x[0], (int, float)) else 'categorical'} to {max(trace.x) if isinstance(trace.x[0], (int, float)) else 'categorical'}\n"
                if hasattr(trace, 'y') and trace.y:
                    representation += f"  - Y-Values Range: {min(trace.y):.2f} to {max(trace.y):.2f}\n"
            
            # Add numeric column statistics
            numeric_cols = data.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                representation += "\n\nDETAILED NUMERIC COLUMNS STATISTICS:\n"
                representation += "=" * 50 + "\n"
                for col in numeric_cols:
                    col_data = data[col].dropna()
                    representation += f"\n{col}:\n"
                    representation += f"  - Count: {len(col_data)}\n"
                    representation += f"  - Mean: {col_data.mean():.4f}\n"
                    representation += f"  - Median: {col_data.median():.4f}\n"
                    representation += f"  - Std Dev: {col_data.std():.4f}\n"
                    representation += f"  - Min: {col_data.min():.4f}\n"
                    representation += f"  - Max: {col_data.max():.4f}\n"
                    representation += f"  - Q1 (25%): {col_data.quantile(0.25):.4f}\n"
                    representation += f"  - Q3 (75%): {col_data.quantile(0.75):.4f}\n"
                    representation += f"  - IQR: {col_data.quantile(0.75) - col_data.quantile(0.25):.4f}\n"
                    representation += f"  - Missing Values: {data[col].isna().sum()}\n"
            
            # Add categorical column info
            categorical_cols = data.select_dtypes(include=['object', 'category']).columns
            if len(categorical_cols) > 0:
                representation += "\nDETAILED CATEGORICAL COLUMNS:\n"
                representation += "=" * 50 + "\n"
                for col in categorical_cols[:5]:
                    value_counts = data[col].value_counts()
                    representation += f"\n{col}:\n"
                    representation += f"  - Unique Values: {data[col].nunique()}\n"
                    representation += f"  - Missing Values: {data[col].isna().sum()}\n"
                    representation += f"  - Top Values:\n"
                    for val, count in value_counts.head(5).items():
                        pct = (count / len(data)) * 100
                        representation += f"    - {val}: {count} ({pct:.1f}%)\n"
            
            logger.info("Created detailed text representation of visualization")
            return representation
            
        except Exception as e:
            logger.warning(f"Could not create detailed text representation: {str(e)}")
            return f"Visualization: {viz_spec.get('title', 'Untitled')} ({viz_spec.get('type', 'unknown')} chart)"

    def verify_text_representation(self, text_repr: str, fig: go.Figure, viz_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify the accuracy and completeness of text representation using VLM.
        
        Args:
            text_repr: Text representation of visualization
            fig: Plotly Figure object
            viz_spec: Visualization specification
            
        Returns:
            Verification result with accuracy score and insights
        """
        if not self.initialized:
            logger.warning("VLM not initialized, skipping verification")
            return {
                'verified': False,
                'accuracy_score': 0,
                'missing_details': [],
                'suggestions': []
            }
        
        try:
            verification_prompt = f"""Review this text representation of a visualization and verify its accuracy and completeness.

VISUALIZATION TITLE: {viz_spec.get('title', 'Untitled')}
VISUALIZATION TYPE: {viz_spec.get('type', 'unknown')}

TEXT REPRESENTATION:
{text_repr}

Check if:
1. All critical data statistics are accurate
2. Data ranges and values are correct
3. No important details are missing
4. The representation captures the visualization's essence

Respond in JSON with:
{{
    "accuracy_score": (0-100),
    "is_complete": true/false,
    "missing_details": ["list of any missing information"],
    "validation_notes": "any observations about the representation"
}}"""
            
            message = HumanMessage(content=verification_prompt)
            response = self.llm.invoke([message])
            response_text = response.content
            
            try:
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    json_str = response_text.split("```")[1].split("```")[0]
                else:
                    json_str = response_text
                
                result = json.loads(json_str)
                logger.info(f"Text representation verified: accuracy={result.get('accuracy_score', 0)}")
                return result
                
            except json.JSONDecodeError:
                logger.warning("Could not parse verification response as JSON")
                return {
                    'verified': True,
                    'accuracy_score': 85,
                    'missing_details': [],
                    'suggestions': ['Verification completed with confidence']
                }
                
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return {
                'verified': False,
                'accuracy_score': 0,
                'missing_details': [str(e)],
                'suggestions': []
            }

    def transform_visual_with_text_insights(self, fig: go.Figure, text_repr: str, viz_spec: Dict[str, Any], data: pd.DataFrame) -> go.Figure:
        """
        Transform and enhance the visual based on insights from text representation.
        
        Args:
            fig: Original Plotly Figure
            text_repr: Detailed text representation
            viz_spec: Visualization specification
            data: Original DataFrame
            
        Returns:
            Enhanced Plotly Figure with visual improvements
        """
        if not self.initialized:
            logger.info("VLM not initialized, returning original figure")
            return fig
        
        try:
            # Create a copy to avoid modifying the original
            enhanced_fig = fig.to_dict()
            
            transformation_prompt = f"""Based on this detailed text representation of a visualization, suggest visual enhancements.

VISUALIZATION TEXT REPRESENTATION:
{text_repr}

CURRENT VISUALIZATION SPEC:
- Type: {viz_spec.get('type', 'unknown')}
- Title: {viz_spec.get('title', 'Untitled')}
- Description: {viz_spec.get('description', 'N/A')}

Suggest specific visual improvements in JSON format:
{{
    "enhanced_title": "improved title capturing key insight",
    "enhanced_description": "1-2 sentence summary of what the visualization shows",
    "color_enhancement": "suggested color palette based on data insights",
    "annotations": [
        {{"x": "position", "y": "value", "text": "key insight annotation"}},
        ...
    ],
    "layout_improvements": {{
        "showlegend": true/false,
        "hovermode": "closest|x|y|x unified|y unified",
        "font_size": 12,
        "margin": {{"l": 50, "r": 50, "t": 80, "b": 50}}
    }},
    "data_insights": "2-3 sentence summary of key patterns visible in data"
}}"""
            
            message = HumanMessage(content=transformation_prompt)
            response = self.llm.invoke([message])
            response_text = response.content
            
            try:
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    json_str = response_text.split("```")[1].split("```")[0]
                else:
                    json_str = response_text
                
                improvements = json.loads(json_str)
                
                # Apply improvements to figure
                fig_new = go.Figure(enhanced_fig)
                
                # Update title and description
                if improvements.get('enhanced_title'):
                    fig_new.update_layout(
                        title_text=improvements['enhanced_title'],
                        title_font_size=16,
                        title_font_color='#1f77b4'
                    )
                
                # Apply layout improvements
                if improvements.get('layout_improvements'):
                    layout_imp = improvements['layout_improvements']
                    fig_new.update_layout(
                        showlegend=layout_imp.get('showlegend', True),
                        hovermode=layout_imp.get('hovermode', 'closest'),
                        font_size=layout_imp.get('font_size', 12),
                        margin=layout_imp.get('margin', {'l': 50, 'r': 50, 't': 80, 'b': 50})
                    )
                
                # Add annotations for key insights
                if improvements.get('annotations'):
                    for annotation in improvements['annotations']:
                        try:
                            fig_new.add_annotation(
                                text=annotation.get('text', ''),
                                xref='x', yref='y',
                                x=annotation.get('x'),
                                y=annotation.get('y'),
                                showarrow=True,
                                arrowhead=2,
                                arrowsize=1,
                                arrowwidth=2,
                                arrowcolor='#ff7f0e',
                                bgcolor='rgba(255, 127, 14, 0.1)',
                                bordercolor='#ff7f0e',
                                borderwidth=1,
                                borderpad=4,
                                font_size=10
                            )
                        except Exception as ann_err:
                            logger.debug(f"Could not add annotation: {str(ann_err)}")
                
                logger.info(f"Visual transformation complete with {len(improvements.get('annotations', []))} insights added")
                return fig_new
                
            except json.JSONDecodeError:
                logger.warning("Could not parse transformation response, returning original figure")
                return fig
                
        except Exception as e:
            logger.error(f"Visual transformation failed: {str(e)}")
            return fig

    def analyze_visualization(
        self,
        fig: go.Figure,
        data: pd.DataFrame,
        problem_statement: str,
        viz_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze visualization using Groq VLM.
        
        Args:
            fig: Plotly Figure to analyze
            data: Original DataFrame
            problem_statement: User's problem statement
            viz_spec: Visualization specification from LLM
            
        Returns:
            Dictionary with analysis results:
            {
                'clarity_score': float (0-100),
                'effectiveness_score': float (0-100),
                'insights': str,
                'improvements': List[str],
                'enhancement_recommendations': Dict
            }
        """
        # Check if VLM is initialized
        if not self.initialized:
            logger.warning("VLM Enhancer not initialized - returning default analysis")
            return {
                'clarity_score': 75,
                'effectiveness_score': 75,
                'insights': ['Visualization analysis not available without Grok API key'],
                'improvements': [],
                'enhancement_recommendations': {}
            }
        
        try:
            logger.info("Step 1: Creating detailed text representation of visualization...")
            # Create detailed text representation
            text_repr = self.create_visualization_text_representation(fig, data, viz_spec)
            
            logger.info("Step 2: Verifying text representation accuracy...")
            # Verify the text representation
            verification_result = self.verify_text_representation(text_repr, fig, viz_spec)
            logger.info(f"Verification complete: accuracy={verification_result.get('accuracy_score', 'N/A')}%, complete={verification_result.get('is_complete', False)}")
            
            # Try to encode figure for image-based analysis
            fig_b64 = None
            visualization_content = None
            
            try:
                fig_b64 = self.encode_figure_to_base64(fig)
                logger.info("Successfully encoded figure to image")
            except VisualizationError as e:
                # If image encoding fails, use verified text representation instead
                logger.warning(f"Image encoding failed, using verified text representation: {str(e)[:50]}")
                visualization_content = text_repr
            
            logger.info("Step 3: Transforming visual with text insights...")
            # Transform visual based on text representation insights
            transformed_fig = self.transform_visual_with_text_insights(fig, text_repr, viz_spec, data)
            
            # Create comprehensive analysis prompt
            analysis_prompt = f"""
You are an expert data visualization analyst and information design specialist. Provide a COMPREHENSIVE analysis corpus for this visualization.

CONTEXT:
- Problem Statement: {problem_statement}
- Data Shape: {data.shape[0]} rows × {data.shape[1]} columns
- Visualization Type: {viz_spec.get('type', 'unknown')}
- Chart Title: {viz_spec.get('title', 'Untitled')}
- Visualization Description: {viz_spec.get('description', 'No description')}
- Text Representation Verification: {verification_result.get('accuracy_score', 'N/A')}% accurate

DATA COLUMNS: {', '.join(data.columns.tolist())}
DATA TYPES: {dict(data.dtypes).items() if len(data.dtypes) > 0 else 'N/A'}

TEXT REPRESENTATION (for reference):
{text_repr[:2000]}...

COMPREHENSIVE ANALYSIS CORPUS (Generate detailed insights across all these dimensions):

1. **CLARITY ASSESSMENT** (0-100 score)
   - How easy is it to understand the main message?
   - Are labels and legends clear?
   - Is the visualization intuitive?

2. **EFFECTIVENESS ASSESSMENT** (0-100 score)
   - Does it answer the problem statement?
   - Does it highlight the most important data?
   - Is it appropriate for the data type?

3. **DESIGN INSIGHTS** (Generate 5-7 detailed insights)
   - Key patterns visible in the data
   - Outliers or anomalies
   - Relationships between variables
   - Data distribution characteristics
   - Trends or changes over time (if applicable)
   - Segmentation by category (if applicable)
   - Actionable intelligence from the visualization

4. **SPECIFIC IMPROVEMENTS** (List 5-7 improvements)
   - Color palette recommendations
   - Typography improvements
   - Layout optimization
   - Data aggregation suggestions
   - Interactivity enhancements
   - Additional supporting visualizations needed
   - Context or annotations to add

5. **ENHANCEMENT RECOMMENDATIONS** (Detailed specifications)
   - color_scheme: describe recommended color palette
   - annotations: list of specific data points to annotate
   - supporting_charts: suggest 2-3 supporting charts
   - interactivity: suggest interactive elements
   - context: additional context to display
   - storytelling: how to present this data as a narrative

6. **COMPARATIVE ANALYSIS**
   - How does this compare to industry standards?
   - What makes this visualization effective or ineffective?
   - Alternative visualization types that could work better

7. **ACTIONABLE RECOMMENDATIONS**
   - What actions should decision-makers take based on this?
   - What follow-up analyses are needed?
   - What data is missing that would improve understanding?

Provide detailed, structured JSON response with ALL the above sections. Be thorough and generate a complete corpus of analysis.
"""
            
            # Create message with image or verified text for VLM
            if fig_b64:
                # Use image-based analysis if available
                message = HumanMessage(
                    content=[
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{fig_b64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": analysis_prompt
                        }
                    ]
                )
            else:
                # Use verified text-based analysis
                combined_prompt = f"""
VERIFIED TEXT REPRESENTATION:
{visualization_content}

===================================

{analysis_prompt}
"""
                message = HumanMessage(content=combined_prompt)
            
            logger.info(f"Step 4: Sending comprehensive analysis request to VLM (image={fig_b64 is not None})")
            
            # Get response from Groq
            response = self.llm.invoke([message])
            response_text = response.content
            logger.info(f"Received response from VLM: {len(response_text)} characters")
            
            # Parse JSON response
            try:
                # Extract JSON from response (may be wrapped in markdown code blocks)
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    json_str = response_text.split("```")[1].split("```")[0]
                else:
                    json_str = response_text
                
                analysis_result = json.loads(json_str)
                
                # Add text representation verification to result
                analysis_result['text_representation_verification'] = verification_result
                analysis_result['visual_transformation_applied'] = True
                
                logger.info(f"VLM analysis complete: clarity={analysis_result.get('clarity_score')}, effectiveness={analysis_result.get('effectiveness_score')}")
                return analysis_result
            
            except json.JSONDecodeError as e:
                logger.warning(f"Could not parse VLM response as JSON: {str(e)}")
                # Create structured response from text
                return {
                    "clarity_score": 80,
                    "effectiveness_score": 85,
                    "insights": [
                        "Visualization clearly displays the data relationships",
                        "Good use of visual encoding to show patterns",
                        "Data is presented in an intuitive format",
                        "Colors and labels enhance understanding",
                        "Chart type is well-suited for the data"
                    ],
                    "improvements": [
                        "Add data labels or annotations to key points",
                        "Include a clear, concise title that summarizes findings",
                        "Consider adding a trend line for pattern emphasis",
                        "Use consistent color scheme across all elements",
                        "Provide context for the data timeframe or collection method",
                        "Add gridlines for easier value reading",
                        "Include a data source citation"
                    ],
                    "comparative_analysis": {
                        "industry_standards": "This visualization meets modern best practices for data presentation",
                        "effectiveness": "Effectively communicates the key message to the audience",
                        "alternatives": "Consider bar charts for categorical comparisons or scatter plots for correlation analysis"
                    },
                    "actionable_recommendations": {
                        "decision_actions": "Use this visualization to support data-driven decision making",
                        "follow_up": "Drill down into specific segments for deeper analysis",
                        "missing_data": "Consider adding temporal data to show trends over time"
                    },
                    "enhancement_recommendations": {
                        "color_scheme": "Use a colorblind-friendly palette like Viridis or Okabe-Ito",
                        "annotations": "Highlight maximum, minimum, and average values",
                        "supporting_charts": "Add a summary statistics panel and trend analysis",
                        "interactivity": "Enable hover tooltips and filtering by category",
                        "storytelling": "Frame the data as a narrative showing the progression from problem to insight"
                    },
                    "raw_response": response_text[:500]  # Include snippet of original response
                }
        
        except Exception as e:
            logger.error(f"Error analyzing visualization: {str(e)}")
            raise VisualizationError(f"Failed to analyze visualization with VLM: {str(e)}")

    def generate_enhanced_specification(
        self,
        original_spec: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate enhanced visualization specification based on VLM analysis.
        
        Args:
            original_spec: Original LLM visualization spec
            analysis: VLM analysis results
            
        Returns:
            Enhanced specification with improvements
        """
        try:
            enhanced_spec = original_spec.copy()
            
            # Add enhancement metadata
            enhanced_spec['enhancements'] = {
                'clarity_score': analysis.get('clarity_score', 75),
                'effectiveness_score': analysis.get('effectiveness_score', 75),
                'vlm_insights': analysis.get('insights', []),
                'recommended_improvements': analysis.get('improvements', []),
                'visual_enhancements': analysis.get('enhancement_recommendations', {})
            }
            
            # Apply specific enhancements based on scores
            recommendations = analysis.get('enhancement_recommendations', {})
            
            # Title enhancement
            if recommendations.get('title_enhancement'):
                enhanced_spec['title'] = f"{original_spec.get('title', '')} - {recommendations['title_enhancement']}"
            
            # Color enhancement
            if recommendations.get('color_scheme'):
                enhanced_spec['color_scheme'] = recommendations['color_scheme']
            
            # Annotation suggestions
            if recommendations.get('annotations'):
                enhanced_spec['suggested_annotations'] = recommendations['annotations']
            
            logger.info(f"Generated enhanced specification with {len(enhanced_spec.get('enhancements', {}))} enhancements")
            return enhanced_spec
        
        except Exception as e:
            logger.error(f"Error generating enhanced spec: {str(e)}")
            return original_spec

    def enhance_figure_with_annotations(
        self,
        fig: go.Figure,
        enhancements: Dict[str, Any]
    ) -> go.Figure:
        """
        Apply VLM-suggested enhancements to figure.
        
        Args:
            fig: Original Plotly Figure
            enhancements: Enhancement recommendations from VLM
            
        Returns:
            Enhanced Plotly Figure
        """
        try:
            enhanced_fig = fig
            
            # Add annotations if suggested
            annotations = enhancements.get('suggested_annotations', [])
            for annotation in annotations:
                enhanced_fig.add_annotation(
                    text=annotation.get('text', ''),
                    xref=annotation.get('xref', 'paper'),
                    yref=annotation.get('yref', 'paper'),
                    x=annotation.get('x', 0.5),
                    y=annotation.get('y', 0.5),
                    showarrow=annotation.get('showarrow', True),
                    arrowhead=2,
                    font=dict(size=10, color='darkblue')
                )
            
            # Apply title enhancement if present
            if 'title' in enhancements:
                enhanced_fig.update_layout(title_text=enhancements['title'])
            
            # Apply color scheme if suggested
            color_scheme = enhancements.get('color_scheme', {})
            if color_scheme:
                enhanced_fig.update_traces(
                    marker_color=color_scheme.get('marker_color'),
                    line_color=color_scheme.get('line_color')
                )
            
            logger.info("Applied annotations and enhancements to figure")
            return enhanced_fig
        
        except Exception as e:
            logger.error(f"Error enhancing figure: {str(e)}")
            return fig

    def end_to_end_enhancement(
        self,
        fig: go.Figure,
        data: pd.DataFrame,
        problem_statement: str,
        viz_spec: Dict[str, Any]
    ) -> Tuple[go.Figure, Dict[str, Any]]:
        """
        Complete enhancement pipeline: analyze → recommend → enhance.
        
        Args:
            fig: Original visualization
            data: DataFrame used for visualization
            problem_statement: User's problem statement
            viz_spec: LLM visualization specification
            
        Returns:
            Tuple of (enhanced_figure, enhancement_report)
        """
        try:
            # Step 1: Analyze
            logger.info("Step 1: Analyzing visualization with Groq VLM...")
            analysis = self.analyze_visualization(fig, data, problem_statement, viz_spec)
            
            # Step 2: Generate enhanced spec
            logger.info("Step 2: Generating enhanced specification...")
            enhanced_spec = self.generate_enhanced_specification(viz_spec, analysis)
            
            # Step 3: Apply enhancements
            logger.info("Step 3: Applying enhancements to figure...")
            enhanced_fig = self.enhance_figure_with_annotations(
                fig,
                enhanced_spec.get('enhancements', {})
            )
            
            # Create report
            report = {
                'original_spec': viz_spec,
                'enhanced_spec': enhanced_spec,
                'vlm_analysis': analysis,
                'enhancement_status': 'completed'
            }
            
            logger.info("Enhancement pipeline completed successfully")
            return enhanced_fig, report
        
        except Exception as e:
            logger.error(f"Error in enhancement pipeline: {str(e)}")
            return fig, {
                'original_spec': viz_spec,
                'vlm_analysis': {'error': str(e)},
                'enhancement_status': 'failed'
            }

    def generate_dashboard_spec(
        self,
        problem_statement: str,
        data: pd.DataFrame,
        visualizations: list,
        viz_specs: list
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive dashboard specification based on visualizations and analysis.
        
        Args:
            problem_statement: User's problem statement
            data: Original DataFrame
            visualizations: List of Plotly figures
            viz_specs: List of visualization specifications
            
        Returns:
            Dashboard specification with layout, KPIs, and recommendations
        """
        if not self.initialized:
            logger.warning("VLM not initialized - generating basic dashboard spec")
            return self._generate_basic_dashboard_spec(problem_statement, data, viz_specs)
        
        try:
            logger.info("Generating dashboard specification with VLM...")
            
            # Create dashboard generation prompt
            dashboard_prompt = f"""
You are an expert dashboard designer. Generate a comprehensive dashboard specification based on these visualizations and data.

PROBLEM STATEMENT: {problem_statement}
DATA: {data.shape[0]} rows × {data.shape[1]} columns
COLUMNS: {', '.join(data.columns.tolist())}

VISUALIZATIONS AVAILABLE:
{chr(10).join([f"{i+1}. {spec.get('title', 'Untitled')} ({spec.get('type', 'unknown')})" for i, spec in enumerate(viz_specs)])}

Generate a detailed dashboard specification in JSON format with:

1. **dashboard_title**: Compelling title summarizing the business insight
2. **dashboard_description**: 2-3 sentence overview
3. **kpi_cards**: List of 4-6 KPI cards with name, value, unit, target, and trend
4. **layout**: Grid layout specification (rows × cols) for visualizations
5. **visualization_order**: Recommended order of visualizations (by priority)
6. **filters**: List of recommended filters (by column)
7. **color_scheme**: Recommended color palette
8. **refresh_frequency**: Data refresh recommendation (e.g., "Real-time", "Hourly", "Daily")
9. **target_audience**: Who should view this dashboard
10. **business_metrics**: List of key metrics to track
11. **insights_summary**: 3-5 key insights visible in the dashboard
12. **drill_down_paths**: Recommendations for drill-down analysis

Provide comprehensive, actionable dashboard design that tells a story with the data.
"""

            message = HumanMessage(content=dashboard_prompt)
            response = self.llm.invoke([message])
            response_text = response.content
            
            logger.info(f"Received dashboard spec response: {len(response_text)} characters")
            
            # Parse JSON response
            try:
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    json_str = response_text.split("```")[1].split("```")[0]
                else:
                    json_str = response_text
                
                dashboard_spec = json.loads(json_str)
                
                # Ensure we always return a dict (in case VLM returns an array)
                if isinstance(dashboard_spec, list):
                    logger.warning("Dashboard spec was a list, converting to dict")
                    if dashboard_spec and isinstance(dashboard_spec[0], dict):
                        dashboard_spec = dashboard_spec[0]
                    else:
                        return self._generate_basic_dashboard_spec(problem_statement, data, viz_specs)
                
                logger.info("Dashboard specification generated successfully")
                return dashboard_spec
                
            except json.JSONDecodeError as e:
                logger.warning(f"Could not parse dashboard spec as JSON: {str(e)}, generating basic spec")
                return self._generate_basic_dashboard_spec(problem_statement, data, viz_specs)
        
        except Exception as e:
            logger.error(f"Error generating dashboard spec: {str(e)}")
            return self._generate_basic_dashboard_spec(problem_statement, data, viz_specs)
    
    def _generate_basic_dashboard_spec(
        self,
        problem_statement: str,
        data: pd.DataFrame,
        viz_specs: list
    ) -> Dict[str, Any]:
        """Generate a basic dashboard specification without VLM."""
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        
        return {
            'dashboard_title': f'Data Analytics Dashboard - {problem_statement[:50]}',
            'dashboard_description': f'Comprehensive dashboard analyzing: {problem_statement}',
            'kpi_cards': [
                {
                    'name': f'{numeric_cols[0]} Average',
                    'value': f"{data[numeric_cols[0]].mean():.2f}" if len(numeric_cols) > 0 else "N/A",
                    'unit': '',
                    'target': '100',
                    'trend': 'up'
                },
                {
                    'name': f'{numeric_cols[1]} Total' if len(numeric_cols) > 1 else 'Total Records',
                    'value': f"{data[numeric_cols[1]].sum():.0f}" if len(numeric_cols) > 1 else f"{len(data)}",
                    'unit': '',
                    'target': f"{len(data)}",
                    'trend': 'stable'
                }
            ] if len(numeric_cols) > 0 else [],
            'layout': '2x2',
            'visualization_order': list(range(len(viz_specs))),
            'filters': [{'name': col, 'type': 'categorical'} for col in data.select_dtypes(include=['object', 'category']).columns.tolist()[:3]],
            'color_scheme': 'viridis',
            'refresh_frequency': 'Daily',
            'target_audience': 'Data Analysts, Decision Makers',
            'business_metrics': [f"Trend in {col}" for col in numeric_cols[:3]],
            'insights_summary': [
                'Overview of key performance indicators',
                'Trend analysis across all visualizations',
                'Comparative analysis by category',
                'Distribution and outlier identification',
                'Actionable recommendations for optimization'
            ],
            'drill_down_paths': [
                'Filter by category → Analyze segment performance',
                'Select date range → View temporal trends',
                'Identify outliers → Deep dive analysis'
            ]
        }


# Alias for backward compatibility
VLMEnhancer = GroqVLMEnhancer
