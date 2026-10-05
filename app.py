import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import time
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
        transition: all 0.4s ease;
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
        font-family: 'Orbitron', sans-serif;
        font-size: 1.65rem !important;
        text-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
    }

    /* Live Pulse Indicator */
    .pulse-node {
        height: 10px;
        width: 10px;
        background-color: #10B981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 14px #10B981;
        animation: pulse 2s infinite alternate;
    }

    @keyframes pulse {
        0% { opacity: 0.3; transform: scale(0.85); }
        100% { opacity: 1; transform: scale(1.35); }
    }

    /* Section Titles */
    .cyber-section {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.92rem;
        color: #818CF8;
        letter-spacing: 2px;
        margin-top: 25px;
        margin-bottom: 15px;
        border-left: 3px solid #38BDF8;
        padding-left: 12px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. STATE INITIALIZATION & LIVE DATA GENERATOR
# -----------------------------------------------------------------------------
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
    st.session_state.txn_counter = 1847
    st.session_state.total_gross = 0.0
    st.session_state.total_exposure = 0.0

def generate_live_event():
    st.session_state.txn_counter += 1
    txn_id = f"TXN-2026-{st.session_state.txn_counter:06d}"
    
    physical_mass = round(float(np.random.uniform(32.0, 39.5)), 3)
    contract_rate = 1850.0
    
    rand_type = np.random.random()
    if rand_type < 0.75:
        status = "RECONCILED"
        billed_mass = physical_mass
        anomaly = "Clean Flow"
        leakage = 0.0
    elif rand_type < 0.90:
        status = "EXPOSURE DETECTED"
        billed_mass = round(physical_mass + float(np.random.uniform(1.1, 3.2)), 3)
        anomaly = "Quantity Overbill"
        leakage = round((billed_mass - physical_mass) * contract_rate, 2)
    else:
        status = "EXPOSURE DETECTED"
        billed_mass = physical_mass
        anomaly = "Price Creep"
        leakage = round(physical_mass * float(np.random.choice([150.0, 220.0])), 2)

    expected_val = round(physical_mass * contract_rate, 2)
    billed_val = expected_val + leakage

    event = {
        "ID": txn_id,
        "Timestamp": datetime.now().strftime("%H:%M:%S"),
        "Scale Mass (t)": physical_mass,
        "Billed Mass (t)": billed_mass,
        "Expected (ZAR)": expected_val,
        "Billed (ZAR)": billed_val,
        "Leakage (ZAR)": leakage,
        "Status": status,
        "Anomaly": anomaly
    }
    
    st.session_state.transactions.insert(0, event)
    if len(st.session_state.transactions) > 50:
        st.session_state.transactions.pop()
        
    st.session_state.total_gross += billed_val
    st.session_state.total_exposure += leakage

# -----------------------------------------------------------------------------
# 3. SIDEBAR CONTROLS (DEFAULT UPDATE INTERVAL = 10 SECONDS)
# -----------------------------------------------------------------------------
st.sidebar.markdown("### ⚡ ENGINE CONTROL")
run_simulation = st.sidebar.toggle("Stream Live Transactions", value=True)
sim_speed = st.sidebar.slider("Update Interval (Seconds)", min_value=2, max_value=30, value=10, step=1)

st.sidebar.divider()
st.sidebar.markdown("**System Telemetry**")
st.sidebar.caption("Refresh Frequency: 10s Cycle")
st.sidebar.caption("Diagram Rendering: WebGL Ambient Animated Network")

# -----------------------------------------------------------------------------
# 4. DASHBOARD HEADER & AMBIENT METRICS
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="ambient-header">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h1 class="futuristic-title">TRUEFLOW // QUANT ASSURANCE TERMINAL</h1>
            <p style="margin:6px 0 0 0; color:#94A3B8; font-size:0.88rem;">
                Autonomous Physical-to-Financial Liquidity Flow Reconciler
            </p>
        </div>
        <div style="text-align:right;">
            <span class="pulse-node"></span>
            <span style="font-family:'Orbitron'; color:#10B981; font-weight:700; font-size:0.88rem; margin-left:8px;">
                10s LIVE CYCLE ACTIVE
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Generate a new event on every refresh cycle
if run_simulation:
    generate_live_event()

df = pd.DataFrame(st.session_state.transactions)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Gross Billed Stream", f"R{st.session_state.total_gross:,.2f}")
col2.metric("Reconciled Liquidity", f"R{st.session_state.total_gross - st.session_state.total_exposure:,.2f}")
col3.metric("Flagged Exposure (Leakage)", f"R{st.session_state.total_exposure:,.2f}", delta=f"{(st.session_state.total_exposure/(st.session_state.total_gross+1e-5))*100:.2f}% Risk", delta_color="inverse")
col4.metric("Engine Throughput", f"{len(st.session_state.transactions)} txns/buffer")

st.markdown('<div class="cyber-section">1. AMBIENT CAPITAL & PHYSICAL FLOW DIAGRAM (ANIMATED NETWORK)</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. RESTORED & CLEANED WEBGL ANIMATED NETWORK (NO OVERLAPPING TEXT)
# -----------------------------------------------------------------------------
nodes_data = [
    {"name": "1. WEIGHBRIDGE GATE", "subtext": "Physical Scale Reality", "coords": [29.210, -25.850], "color": [56, 189, 248]},
    {"name": "2. DIGITAL LOG", "subtext": "Canonical Record", "coords": [29.245, -25.850], "color": [129, 140, 248]},
    {"name": "3. TRUEFLOW QUANT ENGINE", "subtext": "Deterministic & Z-Score Math", "coords": [29.280, -25.850], "color": [52, 211, 153]},
    {"name": "4. SETTLED LIQUIDITY", "subtext": "Clean Payment Approved", "coords": [29.315, -25.825], "color": [16, 185, 129]},
    {"name": "5. LEAKAGE FLAGGED", "subtext": "Quant Anomaly Blocked", "coords": [29.315, -25.875], "color": [239, 68, 68]}
]

latest_leak = df.iloc[0]["Leakage (ZAR)"] if not df.empty else 0.0

flow_arcs = [
    {"source": [29.210, -25.850], "target": [29.245, -25.850], "color": [56, 189, 248, 220]},
    {"source": [29.245, -25.850], "target": [29.280, -25.850], "color": [129, 140, 248, 220]},
    {"source": [29.280, -25.850], "target": [29.315, -25.825], "color": [16, 185, 129, 240]},
]

if latest_leak > 0:
    flow_arcs.append({"source": [29.280, -25.850], "target": [29.315, -25.875], "color": [239, 68, 68, 255]})

nodes_df = pd.DataFrame(nodes_data)
arcs_df = pd.DataFrame(flow_arcs)

outer_ring_layer = pdk.Layer(
    "ScatterplotLayer",
    nodes_df,
    get_position="coords",
    get_fill_color="color",
    get_radius=220,
    opacity=0.25,
    pickable=False
)

node_center_layer = pdk.Layer(
    "ScatterplotLayer",
    nodes_df,
    get_position="coords",
    get_fill_color="color",
    get_radius=90,
    opacity=0.95,
    pickable=True
)

title_text_layer = pdk.Layer(
    "TextLayer",
    nodes_df,
    get_position="coords",
    get_text="name",
    get_size=13,
    get_color=[243, 244, 246],
    get_pixel_offset=[0, -24],
    get_text_anchor="'middle'",
    get_alignment_baseline="'bottom'"
)

sub_text_layer = pdk
        
