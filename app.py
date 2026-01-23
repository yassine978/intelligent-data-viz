"""
Main Streamlit Application - Professional Data Visualization Platform
Person 2 - Visualization & Frontend Lead

This application orchestrates:
1. CSV upload and data preview
2. Problem statement input
3. LLM-based visualization proposals (from Person 1's Analyzer)
4. Interactive dashboard generation
5. Export functionality

Integration Flow:
  Person 1 (LLM Analyzer) → Generates 3 visualization specs
  ↓
  Person 2 (Visualization Generator) → Creates Plotly figures
  ↓
  Person 2 (Dashboard Generator) → Creates professional dashboards
  ↓
  Person 2 (Exporter) → Outputs PNG/HTML
"""

import streamlit as st
import pandas as pd
import os
from typing import List, Dict, Any, Optional, Tuple
import sys
from dotenv import load_dotenv
import json
from functools import lru_cache

# Load environment variables from .env file
load_dotenv()

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from visualization.generator import VisualizationGenerator
from visualization.styler import Styler
from visualization.exporter import VisualizationExporter
from visualization.vlm_enhancer import GroqVLMEnhancer
from llm.analyzer import VisualizationAnalyzer
from ui.components import UIComponents
from utils.logger import get_logger
from utils.exceptions import VisualizationError, VLMError

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Intelligent Data Visualization",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


def convert_llm_to_viz_specs(
    llm_result: Dict[str, Any],
    data: pd.DataFrame
) -> List[Dict[str, Any]]:
    """
    Convert Person 1's LLM output format to Person 2's visualization specs.
    
    Harmonization layer between Person 1 (LLM) and Person 2 (Visualization).
    
    Args:
        llm_result: Output from VisualizationAnalyzer
        data: DataFrame to validate columns against
        
    Returns:
        List of visualization specifications compatible with VisualizationGenerator
    """
    # Mapping from LLM visualization type names to generator type names
    TYPE_MAPPING = {
        'scatter_plot': 'scatter',
        'scatter': 'scatter',
        'bar_chart': 'bar',
        'bar': 'bar',
        'line_chart': 'line',
        'line': 'line',
        'histogram': 'histogram',
        'box_plot': 'box',
        'box': 'box',
        'heatmap': 'heatmap',
    }
    
    viz_specs = []
    
    try:
        llm_visualizations = llm_result.get('visualizations', [])
        
        for viz in llm_visualizations:
            # Map LLM field names to Plotly generator field names
            llm_type = viz.get('viz_type', 'scatter').lower()
            mapped_type = TYPE_MAPPING.get(llm_type, llm_type)
            
            spec = {
                'type': mapped_type,
                'title': viz.get('title', 'Visualization'),
                'description': viz.get('justification', 'LLM-recommended visualization'),
                'justification': viz.get('justification', 'Based on data analysis'),
            }
            
            # Map axis fields
            x_axis = viz.get('x_axis', '')
            y_axis = viz.get('y_axis', '')
            
            # Validate columns exist in data
            valid_cols = set(data.columns)
            
            if x_axis in valid_cols:
                spec['x_col'] = x_axis
            else:
                # Fallback to first column
                spec['x_col'] = data.columns[0] if len(data.columns) > 0 else None
            
            if y_axis in valid_cols:
                spec['y_col'] = y_axis
            else:
                # Fallback to second numeric column
                numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
                spec['y_col'] = numeric_cols[0] if numeric_cols else (data.columns[1] if len(data.columns) > 1 else None)
            
            # Add optional fields
            if 'color_col' in viz and viz['color_col'] in valid_cols:
                spec['color_col'] = viz['color_col']
            
            if 'size_col' in viz and viz['size_col'] in valid_cols:
                spec['size_col'] = viz['size_col']
            
            # Handle barmode for bar charts
            if spec['type'] == 'bar':
                spec['barmode'] = viz.get('barmode', 'group')
            
            # Handle nbins for histograms
            if spec['type'] == 'histogram':
                spec['nbins'] = viz.get('nbins', 30)
            
            viz_specs.append(spec)
        
        logger.info(f"Converted {len(viz_specs)} LLM visualizations to specs")
        return viz_specs
    
    except Exception as e:
        logger.error(f"Error converting LLM output to viz specs: {str(e)}")
        return []


def recommend_kpis(data: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Recommend KPIs based on dataset structure and content.
    
    Args:
        data: DataFrame to analyze
        
    Returns:
        Dictionary with suggested KPIs by category
    """
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
    
    kpis = {
        'Performance Metrics': [],
        'Trend Analysis': [],
        'Distribution Metrics': [],
        'Correlation Analysis': [],
        'Category Performance': []
    }
    
    # Performance Metrics from numeric columns
    if numeric_cols:
        for col in numeric_cols[:3]:
            kpis['Performance Metrics'].extend([
                f"Average {col}",
                f"Median {col}",
                f"Max {col}",
                f"Min {col}"
            ])
        
        # Trend Analysis
        kpis['Trend Analysis'].extend([
            f"Growth rate of {numeric_cols[0]}" if len(numeric_cols) > 0 else None,
            f"Year-over-year change" if len(numeric_cols) > 0 else None,
        ])
        kpis['Trend Analysis'] = [k for k in kpis['Trend Analysis'] if k]
        
        # Distribution Metrics
        kpis['Distribution Metrics'].extend([
            f"Standard deviation of {numeric_cols[0]}" if len(numeric_cols) > 0 else None,
            f"Quartile distribution",
            f"Outlier analysis"
        ])
        kpis['Distribution Metrics'] = [k for k in kpis['Distribution Metrics'] if k]
    
    # Correlation Analysis
    if len(numeric_cols) >= 2:
        kpis['Correlation Analysis'] = [
            f"Correlation between {numeric_cols[0]} and {numeric_cols[1]}",
            f"Correlation matrix of all metrics"
        ]
    
    # Category Performance
    if categorical_cols and numeric_cols:
        kpis['Category Performance'].extend([
            f"Performance by {categorical_cols[0]}" if len(categorical_cols) > 0 else None,
            f"Top performing {categorical_cols[0]}" if len(categorical_cols) > 0 else None,
            f"Category distribution"
        ])
        kpis['Category Performance'] = [k for k in kpis['Category Performance'] if k]
    
    # Remove empty categories
    return {k: v for k, v in kpis.items() if v}


def generate_visualizations_from_llm(
    problem: str,
    data: pd.DataFrame,
    analyzer: VisualizationAnalyzer,
    generator: VisualizationGenerator
) -> Tuple[List[Dict[str, Any]], List[Any]]:
    """
    Complete pipeline: LLM Analysis → Specification Conversion → Visualization Generation.
    
    This is the core integration between Person 1 (LLM) and Person 2 (Visualization).
    
    Args:
        problem: User's problem statement
        data: DataFrame to analyze
        analyzer: Person 1's LLM Analyzer
        generator: Person 2's Visualization Generator
        
    Returns:
        Tuple of (specs, figures) for display
    """
    try:
        # Step 1: Person 1's LLM analyzes problem and data
        logger.info("Step 1/3: LLM Analyzer generating visualization recommendations...")
        llm_result = analyzer.analyze_and_recommend(problem, data)
        
        # Step 2: Convert LLM output to Plotly specs (harmonization)
        logger.info("Step 2/3: Converting LLM output to visualization specifications...")
        viz_specs = convert_llm_to_viz_specs(llm_result, data)
        
        if not viz_specs:
            logger.warning("No visualization specs generated")
            return [], []
        
        # Step 3: Person 2's generator creates actual visualizations
        logger.info("Step 3/3: Generating visualizations from specs...")
        figures = []
        valid_specs = []
        
        for spec in viz_specs:
            try:
                fig = generator.create_from_llm_spec(data, spec)
                figures.append(fig)
                valid_specs.append(spec)
                logger.info(f"Generated {spec['type']} visualization: {spec['title']}")
            except Exception as e:
                logger.error(f"Failed to generate {spec.get('type', 'unknown')} visualization: {str(e)}")
                # Create a fallback figure when generation fails
                try:
                    import plotly.graph_objects as go
                    fallback_fig = go.Figure()
                    fallback_fig.add_annotation(
                        text=f"Failed to generate {spec.get('type', 'visualization')}<br>Error: {str(e)[:100]}",
                        showarrow=False,
                        font=dict(size=16, color="red")
                    )
                    fallback_fig.update_layout(
                        title=f"Error: {spec['title']}",
                        xaxis=dict(visible=False),
                        yaxis=dict(visible=False)
                    )
                    figures.append(fallback_fig)
                    valid_specs.append(spec)
                    logger.info(f"Added fallback figure for {spec.get('type', 'unknown')}")
                except Exception as fallback_err:
                    logger.error(f"Failed to create fallback figure: {str(fallback_err)}")
        
        logger.info(f"Successfully generated {len(figures)} visualizations (including {len(figures) - len(valid_specs)} fallbacks)")
        return valid_specs, figures
    
    except Exception as e:
        logger.error(f"Error in visualization generation pipeline: {str(e)}")
        raise


def generate_dashboard_visuals(dashboard_spec: Dict[str, Any], data: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate professional visual representations of dashboard components.
    
    Args:
        dashboard_spec: Dashboard specification dictionary
        data: Original DataFrame
        
    Returns:
        Dictionary containing Plotly figures for dashboard components
    """
    import plotly.graph_objects as go
    import plotly.express as px
    
    visuals = {}
    
    # Professional color palette
    colors = {
        'primary': '#0066cc',
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'info': '#17a2b8',
        'secondary': '#6c757d',
        'accent': '#ff6b6b'
    }
    
    try:
        # Create KPI Summary Figure with professional styling
        kpi_cards = dashboard_spec.get('kpi_cards', [])
        if kpi_cards:
            kpi_names = [kpi.get('name', 'KPI') for kpi in kpi_cards]
            kpi_values = []
            for kpi in kpi_cards:
                try:
                    val = float(kpi.get('value', 0))
                except:
                    val = 0
                kpi_values.append(val)
            
            fig_kpi = go.Figure(data=[
                go.Bar(
                    y=kpi_names,
                    x=kpi_values,
                    orientation='h',
                    marker=dict(
                        color=kpi_values,
                        colorscale=[colors['primary'], colors['success']],
                        showscale=False,
                        line=dict(color='rgba(0,0,0,0.1)', width=1)
                    ),
                    text=[f"{v:,.2f}" for v in kpi_values],
                    textposition='outside',
                    textfont=dict(size=11, family='Arial, sans-serif', color='#333'),
                    hovertemplate='<b>%{y}</b><br>Value: %{x:,.2f}<extra></extra>'
                )
            ])
            
            fig_kpi.update_layout(
                title=dict(text="<b>Key Performance Indicators (KPI Summary)</b>", font=dict(size=14, color='#1a1a1a')),
                xaxis_title="Value",
                yaxis_title="Metric",
                height=400,
                showlegend=False,
                template='plotly_white',
                font=dict(family='Arial, sans-serif', size=11, color='#333'),
                hovermode='y unified',
                margin=dict(l=150, r=50, t=60, b=50),
                xaxis=dict(
                    gridcolor='rgba(0,0,0,0.05)',
                    showgrid=True,
                    zeroline=False
                ),
                yaxis=dict(
                    gridcolor='rgba(0,0,0,0.05)',
                    showgrid=False,
                    zeroline=False
                ),
                plot_bgcolor='rgba(250,250,250,0.5)',
                paper_bgcolor='white'
            )
            visuals['kpi_summary'] = fig_kpi
        
        # Create Business Metrics Distribution with professional styling
        business_metrics = dashboard_spec.get('business_metrics', [])
        if business_metrics:
            metric_names = [str(m)[:35] for m in business_metrics[:6]]
            metric_values = list(range(len(metric_names), 0, -1))
            
            fig_metrics = go.Figure(data=[
                go.Bar(
                    x=metric_names,
                    y=metric_values,
                    marker=dict(
                        color=metric_values,
                        colorscale=[[0, colors['info']], [1, colors['primary']]],
                        showscale=False,
                        line=dict(color='rgba(0,0,0,0.1)', width=1)
                    ),
                    text=[f"P{v}" for v in metric_values],
                    textposition='outside',
                    textfont=dict(size=10, family='Arial, sans-serif', color='#333'),
                    hovertemplate='<b>%{x}</b><br>Priority: %{y}<extra></extra>'
                )
            ])
            
            fig_metrics.update_layout(
                title=dict(text="<b>Business Metrics Overview</b>", font=dict(size=14, color='#1a1a1a')),
                xaxis_title="Metrics",
                yaxis_title="Priority Level",
                height=400,
                showlegend=False,
                template='plotly_white',
                font=dict(family='Arial, sans-serif', size=10, color='#333'),
                hovermode='x unified',
                margin=dict(l=50, r=50, t=60, b=100),
                xaxis=dict(
                    tickangle=-45,
                    gridcolor='rgba(0,0,0,0.05)',
                    showgrid=False,
                    zeroline=False
                ),
                yaxis=dict(
                    gridcolor='rgba(0,0,0,0.05)',
                    showgrid=True,
                    zeroline=False
                ),
                plot_bgcolor='rgba(250,250,250,0.5)',
                paper_bgcolor='white'
            )
            visuals['business_metrics'] = fig_metrics
        
        # Create Insights Summary as an organized visual
        insights = dashboard_spec.get('insights_summary', [])
        if insights:
            insights_clean = [str(i)[:60] for i in insights[:5]]
            
            fig_insights = go.Figure()
            
            # Create a text annotation for each insight
            annotations = []
            y_pos = len(insights_clean) - 1
            for i, insight in enumerate(insights_clean):
                annotations.append(dict(
                    text=f"<b>→</b> {insight}",
                    xref='paper', yref='paper',
                    x=0.05, y=y_pos - i * 0.18,
                    showarrow=False,
                    font=dict(size=11, family='Arial, sans-serif', color='#333'),
                    align='left',
                    bgcolor='rgba(0,102,204,0.05)',
                    bordercolor=colors['primary'],
                    borderwidth=1,
                    borderpad=10,
                    xanchor='left'
                ))
            
            fig_insights = go.Figure(layout=go.Layout(
                annotations=annotations,
                title=dict(text="<b>Key Insights & Findings</b>", font=dict(size=14, color='#1a1a1a')),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=300 + (len(insights_clean) * 40),
                template='plotly_white',
                margin=dict(l=20, r=20, t=60, b=20),
                hovermode=False,
                paper_bgcolor='white'
            ))
            visuals['insights'] = fig_insights
        
        # Create Filter Recommendations with professional styling
        filters = dashboard_spec.get('filters', [])
        if filters:
            filter_names = []
            for f in filters:
                if isinstance(f, dict):
                    filter_names.append(f.get('name', 'Filter')[:20])
                else:
                    filter_names.append(str(f)[:20])
            
            if filter_names:
                fig_filters = go.Figure(go.Sunburst(
                    labels=['Filters'] + filter_names,
                    parents=[''] + ['Filters'] * len(filter_names),
                    values=[len(filter_names)] + [1] * len(filter_names),
                    marker=dict(
                        colors=[colors['primary']] + [colors['info'], colors['success'], colors['warning'], colors['accent'], colors['secondary']][:len(filter_names)],
                        line=dict(color='white', width=2)
                    ),
                    textfont=dict(size=11, family='Arial, sans-serif', color='white'),
                    hovertemplate='<b>%{label}</b><extra></extra>'
                ))
                
                fig_filters.update_layout(
                    title=dict(text="<b>Recommended Filters</b>", font=dict(size=14, color='#1a1a1a')),
                    height=450,
                    template='plotly_white',
                    margin=dict(l=10, r=10, t=60, b=10),
                    paper_bgcolor='white'
                )
                visuals['filters'] = fig_filters
        
        # Create Dashboard Layout Visualization with radar chart
        layout = dashboard_spec.get('layout', '2x2')
        target_audience = dashboard_spec.get('target_audience', 'General')
        refresh_freq = dashboard_spec.get('refresh_frequency', 'Daily')
        color_scheme = dashboard_spec.get('color_scheme', 'Default')
        
        specs = [
            ('Layout\nComplexity', 3),
            ('Refresh\nFrequency', 4 if 'Real' in refresh_freq else 3),
            ('Audience\nReach', 4 if 'Executive' in target_audience else 3),
            ('Visual\nPolish', 5)
        ]
        
        spec_names = [s[0] for s in specs]
        spec_values = [s[1] for s in specs]
        
        fig_specs = go.Figure(data=[
            go.Scatterpolar(
                r=spec_values + [spec_values[0]],
                theta=spec_names + [spec_names[0]],
                fill='toself',
                name='Dashboard Score',
                marker=dict(color=colors['primary'], size=8),
                line=dict(color=colors['primary'], width=2),
                fillcolor='rgba(0,102,204,0.2)',
                hovertemplate='<b>%{theta}</b><br>Score: %{r}/5<extra></extra>'
            )
        ])
        
        fig_specs.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5],
                    tickfont=dict(size=10, color='#666'),
                    gridcolor='rgba(0,0,0,0.1)'
                ),
                angularaxis=dict(
                    tickfont=dict(size=10, color='#333'),
                    gridcolor='rgba(0,0,0,0.1)'
                ),
                bgcolor='rgba(250,250,250,0.5)'
            ),
            title=dict(text="<b>Dashboard Quality Score</b>", font=dict(size=14, color='#1a1a1a')),
            height=450,
            template='plotly_white',
            showlegend=False,
            margin=dict(l=100, r=100, t=80, b=80),
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif', size=11, color='#333')
        )
        visuals['specifications'] = fig_specs
        
        logger.info(f"Generated {len(visuals)} professional dashboard visual components")
        return visuals
        
    except Exception as e:
        logger.error(f"Error generating dashboard visuals: {str(e)}")
        return {}


def generate_dashboard(
    problem_statement: str,
    data: pd.DataFrame,
    vlm_enhancer: GroqVLMEnhancer,
    figures: list,
    viz_specs: list
) -> Dict[str, Any]:
    """
    Generate a comprehensive dashboard specification using VLM.
    
    Args:
        problem_statement: User's problem statement
        data: DataFrame being analyzed
        vlm_enhancer: VLM enhancer instance
        figures: List of Plotly figures
        viz_specs: List of visualization specifications
        
    Returns:
        Dashboard specification dictionary
    """
    try:
        logger.info("Generating dashboard specification...")
        dashboard_spec = vlm_enhancer.generate_dashboard_spec(
            problem_statement,
            data,
            figures,
            viz_specs
        )
        logger.info("Dashboard specification generated successfully")
        return dashboard_spec
    except Exception as e:
        logger.error(f"Error generating dashboard: {str(e)}")
        # Return basic dashboard spec on error
        return vlm_enhancer._generate_basic_dashboard_spec(problem_statement, data, viz_specs)


# Session state initialization
def init_session_state():
    """Initialize session state variables."""
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'problem_statement' not in st.session_state:
        st.session_state.problem_statement = ""
    if 'visualizations' not in st.session_state:
        st.session_state.visualizations = []
    if 'viz_specs' not in st.session_state:
        st.session_state.viz_specs = []
    if 'selected_viz' not in st.session_state:
        st.session_state.selected_viz = -1
    if 'enhancement_report' not in st.session_state:
        st.session_state.enhancement_report = None
    if 'export_paths' not in st.session_state:
        st.session_state.export_paths = {}
    if 'dashboard_spec' not in st.session_state:
        st.session_state.dashboard_spec = None


@st.cache_resource
def get_components():
    """Get and cache visualization components."""
    styler = Styler(theme='light', palette='primary')
    generator = VisualizationGenerator(styler=styler)
    exporter = VisualizationExporter(output_dir="./exports")
    analyzer = VisualizationAnalyzer(use_cache=True)
    
    # VLM Enhancer is optional - gracefully handle missing API key
    vlm_enhancer = GroqVLMEnhancer()
    
    return {
        'styler': styler,
        'generator': generator,
        'exporter': exporter,
        'vlm_enhancer': vlm_enhancer,
        'analyzer': analyzer
    }


def main():
    """Main application logic."""
    init_session_state()
    
    # Header with professional styling
    st.set_page_config(
        page_title="Data Visualization Platform",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #0066cc 0%, #0099ff 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.5em;
        font-weight: bold;
    }
    .main-header p {
        margin: 10px 0 0 0;
        font-size: 1.1em;
        opacity: 0.95;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <h1>📊 Professional Data Visualization Platform</h1>
        <p>✨ AI-Powered Analysis | 🎨 Smart Dashboards | 📈 Interactive Insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    UIComponents.sidebar_info()
    
    # Main workflow
    with st.container():
        # Step 1: Data Upload
        st.header("Step 1️⃣ Upload Your Data")
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload a CSV file with your data"
        )
        
        if uploaded_file is not None:
            try:
                st.session_state.data = pd.read_csv(uploaded_file)
                st.success("✅ Data loaded successfully!")
                
                # Data preview
                UIComponents.data_preview(st.session_state.data)
                
                # KPI Recommendations
                st.subheader("💡 Recommended KPIs for Your Dataset")
                recommended_kpis = recommend_kpis(st.session_state.data)
                
                col1, col2 = st.columns(2)
                for idx, (category, kpis) in enumerate(recommended_kpis.items()):
                    with col1 if idx % 2 == 0 else col2:
                        st.write(f"**{category}**")
                        for kpi in kpis[:3]:  # Show top 3 per category
                            st.write(f"  • {kpi}")
                
                # Add custom KPI input
                st.write("**Custom KPIs:** Add your own by typing in the problem statement below")
                
            except Exception as e:
                UIComponents.error_message(f"Failed to load data: {str(e)}")
                st.session_state.data = None
                return
        
        # Step 2: Problem Statement
        if st.session_state.data is not None:
            st.header("Step 2️⃣ Define Your Problem")
            st.session_state.problem_statement = UIComponents.problem_statement_input()
            
            # Step 3: Generate Visualizations (Mock - Would come from Person 1's LLM)
            if st.session_state.problem_statement:
                st.header("Step 3️⃣ Visualization Proposals")
                
                if st.button("🚀 Generate Visualizations", key="generate_btn"):
                    with st.spinner("Analyzing data with AI and generating visualizations..."):
                        try:
                            components = get_components()
                            generator = components['generator']
                            analyzer = components['analyzer']
                            
                            # Check if LLM client is available
                            if not analyzer.llm.initialized:
                                UIComponents.error_message(
                                    "⚠️ LLM API not configured - GROQ_API_KEY not found in environment variables. "
                                    "Please add GROQ_API_KEY to your .env file to enable visualization generation."
                                )
                                return
                            
                            # Core integration: Use Person 1's LLM to analyze and Person 2 to visualize
                            viz_specs, figures = generate_visualizations_from_llm(
                                st.session_state.problem_statement,
                                st.session_state.data,
                                analyzer,
                                generator
                            )
                            
                            st.session_state.visualizations = figures
                            st.session_state.viz_specs = viz_specs
                            
                            if figures:
                                st.success(f"✅ Generated {len(figures)} visualization proposals!")
                            else:
                                UIComponents.error_message("Could not generate any visualizations")
                                return
                        
                        except Exception as e:
                            logger.error(f"Error in visualization generation: {str(e)}")
                            UIComponents.error_message(f"Error generating visualizations: {str(e)}")
                            return
                
                # Display visualizations
                if st.session_state.visualizations:
                    st.header("Step 4️⃣ Select & Enhance Visualization")
                    
                    # Extract titles, descriptions, and justifications from specs
                    titles = [spec.get('title', f'Option {i+1}') for i, spec in enumerate(st.session_state.get('viz_specs', []))]
                    descriptions = [spec.get('description', 'LLM-recommended visualization') for spec in st.session_state.get('viz_specs', [])]
                    justifications = [spec.get('justification', 'Based on LLM analysis') for spec in st.session_state.get('viz_specs', [])]
                    
                    selected_idx = UIComponents.visualization_tabs(
                        st.session_state.visualizations,
                        titles,
                        descriptions,
                        justifications
                    )
                    
                    # VLM Enhancement - REMOVED
                    # Dashboard is now the primary feature
                    
                    if selected_idx >= 0:
                        st.header("Step 4️⃣ Dashboard Generation")
                        
                        if st.button("📊 Generate Dashboard with Visualizations", key="generate_dashboard"):
                            with st.spinner("Creating dashboard specification with VLM..."):
                                try:
                                    components = get_components()
                                    vlm_enhancer = components['vlm_enhancer']
                                    
                                    dashboard_spec = generate_dashboard(
                                        st.session_state.problem_statement,
                                        st.session_state.data,
                                        vlm_enhancer,
                                        st.session_state.visualizations,
                                        st.session_state.viz_specs
                                    )
                                    
                                    st.session_state.dashboard_spec = dashboard_spec
                                    st.success("✅ Dashboard specification generated!")
                                    
                                except Exception as e:
                                    UIComponents.error_message(f"Dashboard generation failed: {str(e)}")
                                    logger.error(f"Dashboard generation error: {str(e)}")
                        
                        # Display dashboard specification if available
                        if st.session_state.get('dashboard_spec'):
                            st.header("� Visual Dashboard")
                            
                            dashboard = st.session_state.dashboard_spec
                            
                            # Ensure dashboard is a dict (handle cases where it might be a list)
                            if isinstance(dashboard, list):
                                UIComponents.error_message("Dashboard specification format error")
                            else:
                                # Dashboard Overview
                                st.subheader(dashboard.get('dashboard_title', 'Dashboard'))
                                st.write(dashboard.get('dashboard_description', ''))
                                
                                # Generate visual dashboard components
                                try:
                                    dashboard_visuals = generate_dashboard_visuals(dashboard, st.session_state.data)
                                    
                                    # Display KPI Summary
                                    if 'kpi_summary' in dashboard_visuals:
                                        st.subheader("🎯 KPI Summary")
                                        st.plotly_chart(dashboard_visuals['kpi_summary'], use_container_width=True)
                                    
                                    # Display Business Metrics
                                    if 'business_metrics' in dashboard_visuals:
                                        st.subheader("📈 Business Metrics")
                                        st.plotly_chart(dashboard_visuals['business_metrics'], use_container_width=True)
                                    
                                    # Display Dashboard Specifications
                                    if 'specifications' in dashboard_visuals:
                                        st.subheader("⚙️ Dashboard Configuration")
                                        st.plotly_chart(dashboard_visuals['specifications'], use_container_width=True)
                                    
                                    # Display Filters
                                    if 'filters' in dashboard_visuals:
                                        st.subheader("🔍 Recommended Filters")
                                        st.plotly_chart(dashboard_visuals['filters'], use_container_width=True)
                                    
                                    # Display Insights
                                    if 'insights' in dashboard_visuals:
                                        st.subheader("💡 Key Insights")
                                        st.plotly_chart(dashboard_visuals['insights'], use_container_width=True)
                                    
                                except Exception as e:
                                    logger.error(f"Error generating visual dashboard: {str(e)}")
                                    UIComponents.error_message(f"Could not generate visual dashboard: {str(e)}")
                        
                        # Step 5: Export
                        st.header("Step 5️⃣ Export Results")
                        
                        components = get_components()
                        exporter = components['exporter']
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("📥 Export PNG (High Quality)", key="export_png"):
                                try:
                                    png_path = exporter.export_png(
                                        st.session_state.visualizations[selected_idx],
                                        f"visualization_{selected_idx}",
                                        width=1200,
                                        height=800,
                                        scale=2.0
                                    )
                                    st.session_state.export_paths['png'] = png_path
                                    st.success(f"✅ Saved to {png_path}")
                                except Exception as e:
                                    UIComponents.error_message(f"Export failed: {str(e)}")
                        
                        with col2:
                            if st.button("📥 Export HTML (Interactive)", key="export_html"):
                                try:
                                    html_path = exporter.export_html(
                                        st.session_state.visualizations[selected_idx],
                                        f"visualization_{selected_idx}"
                                    )
                                    st.session_state.export_paths['html'] = html_path
                                    st.success(f"✅ Saved to {html_path}")
                                except Exception as e:
                                    UIComponents.error_message(f"Export failed: {str(e)}")
                        
                        # Display export buttons
                        if st.session_state.export_paths:
                            UIComponents.export_options(
                                st.session_state.export_paths.get('png'),
                                st.session_state.export_paths.get('html')
                            )
    
    # Footer
    UIComponents.footer()


if __name__ == "__main__":
    main()
