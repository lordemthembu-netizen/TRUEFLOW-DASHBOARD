import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG & FUTURISTIC AMBIENT CSS THEME
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="TrueFlow // Cybernetic Assurance Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Cyberpunk / Ambient Neon UI Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=JetBrains+Mono:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'JetBrains Mono', monospace;
    }

    .stApp {
        background: radial-gradient(circle at 50% 10%, #0B1120 0%, #030712 100%);
        color: #E2E8F0;
    }

    /* Ambient Glow Header */
    .ambient-header {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(3, 7, 18, 0.9) 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.12), inset 0 0 20px rgba(16, 185, 129, 0.08);
        backdrop-filter: blur(16px);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 25px;
    }

    .futuristic-title {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(90deg, #38BDF8 0%, #818CF8 50%, #34D399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        letter-spacing: 2.5px;
        margin: 0;
    }

    /* KPI Glow Cards */
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 0 12px rgba(56, 189, 248, 0.05);
        backdrop-filter: blur(12px);
    }

    div[data-testid="stMetric"]:hover {
        border-color: rgba(56, 189, 248, 0.45);
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.2);
    }

    div[data-testid="stMetric"] label {
        color: #94A3B8 !important;
        font-size: 0.78rem !important;
        letter-spacing: 1.2px;
        text-transform: uppercase;
    }

    div[data-testid="stMetricValue"] {
        color: #38BDF8 !important;
        font-family:
