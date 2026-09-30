import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

DARK_THEME_LAYOUT = {
    'paper_bgcolor': 'rgba(15, 23, 42, 0.0)',
    'plot_bgcolor': 'rgba(15, 23, 42, 0.0)',
    'font': {'color': '#F8FAFC', 'family': 'Inter, sans-serif'},
    'xaxis': {
        'gridcolor': 'rgba(255, 255, 255, 0.08)',
        'zerolinecolor': 'rgba(255, 255, 255, 0.15)',
        'tickfont': {'color': '#94A3B8'}
    },
    'yaxis': {
        'gridcolor': 'rgba(255, 255, 255, 0.08)',
        'zerolinecolor': 'rgba(255, 255, 255, 0.15)',
        'tickfont': {'color': '#94A3B8'}
    },
    'margin': dict(l=40, r=40, t=50, b=40)
}

COLOR_PALETTE = [
    '#38BDF8', '#F43F5E', '#10B981', '#F59E0B', '#8B5CF6', 
    '#EC4899', '#06B6D4', '#84CC16', '#EAB308', '#6366F1'
]

def apply_plotly_theme(fig, title=""):
    """Applies modern sleek dark theme to Plotly figures."""
    fig.update_layout(**DARK_THEME_LAYOUT)
    if title:
        fig.update_layout(title={'text': title, 'x': 0.02, 'y': 0.95, 'font': {'size': 18, 'color': '#F8FAFC'}})
    return fig

def render_kpi_card(title: str, value: str, subtitle: str = "", icon: str = "📊", color_gradient: str = "linear-gradient(135deg, #1E293B, #0F172A)"):
    """Renders a modern glassmorphic KPI card HTML component in Streamlit."""
    card_html = f"""
    <div style="
        background: {color_gradient};
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(12px);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #94A3B8;">{title}</span>
            <span style="font-size: 1.5rem;">{icon}</span>
        </div>
        <div style="font-size: 2.2rem; font-weight: 800; color: #F8FAFC; margin: 8px 0 4px 0; letter-spacing: -0.02em;">{value}</div>
        <div style="font-size: 0.8rem; color: #38BDF8; font-weight: 500;">{subtitle}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
