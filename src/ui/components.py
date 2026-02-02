# -*- coding: utf-8 -*-
"""
UI Components Module - Professional Streamlit components
"""

import streamlit as st
from typing import Any, List, Dict, Optional, Callable
import plotly.graph_objects as go
import pandas as pd
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Professional color palette
COLORS = {
    'primary': '#0066cc',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#17a2b8',
    'secondary': '#6c757d',
    'accent': '#ff6b6b',
    'light': '#f8f9fa',
    'dark': '#1a1a1a'
}


class UIComponents:
    """Collection of professional reusable UI components."""

    @staticmethod
    def data_preview(df, title: str = "📊 Data Preview", max_rows: int = 5):
        """Display professional data preview."""
        with st.expander(title, expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📈 Total Rows", f"{len(df):,}")
            with col2:
                st.metric("📋 Columns", len(df.columns))
            with col3:
                st.metric("💾 Memory", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
            
            st.dataframe(df.head(max_rows), use_container_width=True, hide_index=True)
            
            # Column Information (outside nested expander)
            st.markdown("#### 📝 Column Information")
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Type': [str(t) for t in df.dtypes],
                'Missing': [df[col].isna().sum() for col in df.columns],
                'Unique': [df[col].nunique() for col in df.columns]
            })
            st.dataframe(col_info, use_container_width=True, hide_index=True)

    @staticmethod
    def problem_statement_input() -> str:
        """Professional input component for problem statement."""
        st.subheader("📋 Define Your Analysis Problem")
        st.write("Provide a clear description of what you want to analyze or visualize.")
        
        problem = st.text_area(
            "Analysis Objective:",
            placeholder="Example: Analyze the correlation between product features and sales performance...",
            height=100,
            help="Be specific about the insights you're seeking. This helps generate better visualizations."
        )
        
        if problem:
            st.success(f"✅ Objective: {problem[:50]}...")
        
        return problem

    @staticmethod
    def visualization_tabs(
        figures: List[go.Figure],
        titles: List[str],
        descriptions: List[str],
        justifications: List[str]
    ) -> int:
        """
        Display 3 visualization proposals in tabs.
        
        Returns:
            Index of selected visualization (0-2)
        """
        st.subheader("🎨 3 Visualization Proposals")
        
        tabs = st.tabs([f"Option {i+1}" for i in range(len(figures))])
        
        for i, (tab, fig, title, desc, justif) in enumerate(
            zip(tabs, figures, titles, descriptions, justifications)
        ):
            with tab:
                # Title and description
                st.markdown(f"### {title}")
                st.markdown(f"*{desc}*")
                
                # Visualization
                st.plotly_chart(fig, use_container_width=True)
                
                # Justification
                with st.expander("📖 Why This Visualization?"):
                    st.write(justif)
                
                # Select button
                if st.button(f"✅ Select Option {i+1}", key=f"select_{i}"):
                    st.session_state.selected_viz = i
                    st.success(f"Selected Option {i+1}!")
                    return i
        
        return st.session_state.get('selected_viz', -1)

    @staticmethod
    def loading_state(message: str = "Processing..."):
        """Display loading spinner."""
        with st.spinner(message):
            yield

    @staticmethod
    def error_message(message: str, title: str = "❌ Error"):
        """Display professional error message."""
        with st.container():
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                st.write("❌")
            with col2:
                st.error(f"**{title}**\n{message}")

    @staticmethod
    def success_message(message: str, title: str = "✅ Success"):
        """Display professional success message."""
        with st.container():
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                st.write("✅")
            with col2:
                st.success(f"**{title}**\n{message}")

    @staticmethod
    def info_message(message: str, title: str = "ℹ️ Info"):
        """Display professional info message."""
        with st.container():
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                st.write("ℹ️")
            with col2:
                st.info(f"**{title}**\n{message}")

    @staticmethod
    def visualization_stats(fig: go.Figure, data_points: int):
        """Display visualization statistics."""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Data Points", data_points)
        with col2:
            st.metric("Dimensions", len(fig.data))
        with col3:
            trace_types = set(trace.type for trace in fig.data)
            st.metric("Trace Types", len(trace_types))

    @staticmethod
    def export_options(png_path: Optional[str] = None, html_path: Optional[str] = None):
        """Display export buttons."""
        st.subheader("💾 Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if png_path:
                with open(png_path, "rb") as f:
                    st.download_button(
                        label="📥 Download PNG",
                        data=f.read(),
                        file_name="visualization.png",
                        mime="image/png"
                    )
            else:
                st.button("📥 Download PNG", disabled=True)
        
        with col2:
            if html_path:
                with open(html_path, "rb") as f:
                    st.download_button(
                        label="📥 Download HTML",
                        data=f.read(),
                        file_name="visualization.html",
                        mime="text/html"
                    )
            else:
                st.button("📥 Download HTML", disabled=True)

    @staticmethod
    def enhancement_report(analysis: Dict[str, Any]):
        """Display comprehensive VLM enhancement analysis corpus."""
        st.subheader("✨ Comprehensive VLM Enhancement Analysis")
        
        # Scores
        col1, col2 = st.columns(2)
        
        with col1:
            clarity = analysis.get('clarity_score', 75)
            st.metric("Clarity Score", f"{clarity}/100", delta=clarity - 75)
        
        with col2:
            effectiveness = analysis.get('effectiveness_score', 75)
            st.metric("Effectiveness Score", f"{effectiveness}/100", delta=effectiveness - 75)
        
        # Design Insights - Comprehensive Corpus
        with st.expander("🔍 Design Insights & Analysis", expanded=True):
            insights = analysis.get('insights', [])
            if isinstance(insights, list):
                st.write("**Key Findings from Visualization:**")
                for i, insight in enumerate(insights, 1):
                    st.write(f"**{i}.** {insight}")
            else:
                st.write(insights)
        
        # Improvements
        with st.expander("💡 Specific Improvements"):
            improvements = analysis.get('improvements', [])
            if isinstance(improvements, list):
                for i, improvement in enumerate(improvements, 1):
                    st.write(f"**{i}.** {improvement}")
            else:
                st.write(improvements)
        
        # Comparative Analysis
        with st.expander("📊 Comparative Analysis"):
            comparative = analysis.get('comparative_analysis', 'Not available')
            if isinstance(comparative, dict):
                st.write(f"**Industry Standards:** {comparative.get('industry_standards', 'N/A')}")
                st.write(f"**Effectiveness:** {comparative.get('effectiveness', 'N/A')}")
                st.write(f"**Alternatives:** {comparative.get('alternatives', 'N/A')}")
            else:
                st.write(comparative)
        
        # Actionable Recommendations
        with st.expander("🎯 Actionable Recommendations"):
            actions = analysis.get('actionable_recommendations', 'Not available')
            if isinstance(actions, dict):
                st.write(f"**Decision Actions:** {actions.get('decision_actions', 'N/A')}")
                st.write(f"**Follow-up Analysis:** {actions.get('follow_up', 'N/A')}")
                st.write(f"**Missing Data:** {actions.get('missing_data', 'N/A')}")
            else:
                st.write(actions)
        
        # Enhancement Recommendations
        with st.expander("🎨 Visual Enhancement Recommendations"):
            enhancements = analysis.get('enhancement_recommendations', {})
            if isinstance(enhancements, dict):
                st.write(f"**Color Scheme:** {enhancements.get('color_scheme', 'Default')}")
                st.write(f"**Annotations:** {enhancements.get('annotations', 'None')}")
                st.write(f"**Supporting Charts:** {enhancements.get('supporting_charts', 'None')}")
                st.write(f"**Interactivity:** {enhancements.get('interactivity', 'None')}")
                st.write(f"**Storytelling:** {enhancements.get('storytelling', 'N/A')}")
            else:
                st.write(enhancements)
        
        # Enhancement recommendations
        with st.expander("🎯 Enhancement Recommendations"):
            recommendations = analysis.get('enhancement_recommendations', {})
            if recommendations:
                st.json(recommendations)
            else:
                st.write("No specific recommendations at this time")

    @staticmethod
    def sidebar_info():
        """Display professional sidebar information."""
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 🎯 Features")
            features = [
                "📊 AI-Powered Visualization",
                "🔍 Intelligent Data Analysis",
                "📈 Professional Dashboards",
                "💾 Multi-Format Export",
                "⚡ High Performance"
            ]
            for feature in features:
                st.write(f"✓ {feature}")
            
            st.markdown("---")
            st.markdown("### 🔧 Technology Stack")
            st.write("""
- **LLM**: Groq (llama-3.3-70b-versatile)
- **VLM**: Groq (llama-4-scout)
- **Visualization**: Plotly
- **Framework**: Streamlit
""")
            
            st.markdown("---")
            st.markdown("### 💡 Quick Tips")
            tips = [
                "Be specific in problem statements",
                "Review all visualization options",
                "Use dashboard for comprehensive view",
                "Export in multiple formats"
            ]
            for i, tip in enumerate(tips, 1):
                st.write(f"{i}. {tip}")
            
            st.markdown("---")
            st.markdown("### 📞 Support")
            st.write("For issues or feedback, please contact support.")

    @staticmethod
    def footer():
        """Display professional footer."""
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center'>
            <p>Powered by Streamlit, Plotly, and Groq Vision API</p>
        </div>
        """, unsafe_allow_html=True)
