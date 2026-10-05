import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import time
import os
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG & FUTURISTIC AMBIENT CSS THEME
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="TrueFlow Quant // Cybernetic Assurance Terminal",
    page_icon="⚡",
    layout="wide",  # Ensures full-screen responsiveness across monitors
    initial_sidebar_state="expanded"
)

# Custom Cyberpunk / Ambient Neon UI Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=JetBrains+Mono:wght@300;500;700&display=swap');

    /* Main Container & Dark Space BG */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #0d1527 0%, #030712 100%);
        color: #e2e8f0;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Full-Width Ambient Glow Header Container */
    .ambient-header {
        background: rgba(11, 17, 32, 0.7);
        border: 1px solid rgba(56, 189, 248, 0.25);
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.12), inset 0 0 15px rgba(16, 185, 129, 0.08);
        backdrop-filter: blur(12px);
        border-radius: 12px;
        padding: 20px 25px;
        margin-bottom: 25px;
        width: 100%;
    }

    /* KPI Glow Cards */
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5), inset 0 0 10px rgba(56, 189, 248, 0.05);
        backdrop-filter: blur(8px);
        transition: all 0.3s ease;
    }

    div[data-testid="stMetric"]:hover {
        border-color: rgba(56, 189, 248, 0.4);
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.25);
    }

    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-size: 0.75rem !important;
        letter-spacing: 1px;
    }

    div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-family: 'Orbitron', sans-serif;
        font-size: 1.6rem !important;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
    }

    /* Live Data Pulse Indicator */
    .pulse-node {
        height: 10px;
        width: 10px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 12px #10b981;
        animation: pulse 1.5s infinite alternate;
    }

    @keyframes pulse {
        0% { opacity: 0.3; transform: scale(0.8); }
        100% { opacity: 1; transform: scale(1.3); }
    }

    /* Section Headers */
    .cyber-section {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.95rem;
        color: #818cf8;
        letter-spacing: 2px;
        margin-top: 20px;
        margin-bottom: 15px;
        border-left: 3px solid #38bdf8;
        padding-left: 10px;
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
        "Timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
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
# 3. SIDEBAR CONTROLS, BRANDING & DOWNLOAD BUTTON
# -----------------------------------------------------------------------------
st.sidebar.markdown("### ⚡ TRUEFLOW QUANT")
run_simulation = st.sidebar.toggle("Stream Live Transactions", value=True)
sim_speed = st.sidebar.slider("Flow Interval (sec)", 0.5, 3.0, 1.0)

st.sidebar.divider()
st.sidebar.markdown("### 📌 INVESTOR & GRANT PACK")
st.sidebar.caption("Download the complete institutional funding package including financial models, pitch video, and grant application PDFs.")

zip_file_path = "TrueFlow_Funding_Application_Pack.zip"
if os.path.exists(zip_file_path):
    with open(zip_file_path, "rb") as fp:
        st.sidebar.download_button(
            label="⬇️ Download Application Pack (.ZIP)",
            data=fp,
            file_name="TrueFlow_Funding_Application_Pack.zip",
            mime="application/zip",
            use_container_width=True
        )
else:
    st.sidebar.info("Run generator script to generate downloadable .ZIP package.")

st.sidebar.divider()
st.sidebar.caption("Protocol: WebGL Animated Node Flow")
st.sidebar.caption("Quantum Seed: Active")

# -----------------------------------------------------------------------------
# 4. BRANDED HEADER (VECTOR LOGO & SYSTEM TITLE)
# -----------------------------------------------------------------------------
header_html = """
<div class="ambient-header">
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 20px;">
        <div style="display: flex; align-items: center; gap: 20px;">
            <!-- Isometric Cube Vector Logo -->
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 180" style="width: 70px; height: 70px; flex-shrink: 0;">
                <defs>
                    <linearGradient id="tf-cyan" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#38BDF8" />
                        <stop offset="100%" stop-color="#0284C7" />
                    </linearGradient>
                    <linearGradient id="tf-emerald" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#34D399" />
                        <stop offset="100%" stop-color="#059669" />
                    </linearGradient>
                    <linearGradient id="tf-purple" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#818CF8" />
                        <stop offset="100%" stop-color="#4F46E5" />
                    </linearGradient>
                </defs>
                <g>
                    <polygon points="100,20 160,55 100,90 40,55" fill="url(#tf-cyan)" opacity="0.95"/>
                    <polygon points="40,55 100,90 100,160 40,125" fill="url(#tf-purple)" opacity="0.88"/>
                    <polygon points="100,90 160,55 160,125 100,160" fill="url(#tf-emerald)" opacity="0.95"/>
                    <polyline points="100,20 100,90 160,125" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="5,5"/>
                </g>
            </svg>
            <div>
                <h1 style="font-family: 'Orbitron', sans-serif; font-size: 2.2rem; font-weight: 900; letter-spacing: 3px; margin: 0; color: #F8FAFC;">
                    TRUE<span style="color: #38BDF8;">FLOW</span> QUANT
                </h1>
                <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.85rem; font-family: 'JetBrains Mono', monospace; letter-spacing: 1px;">
                    CYBERNETIC PHYSICAL-TO-FINANCIAL LIQUIDITY ASSURANCE TERMINAL
                </p>
            </div>
        </div>
        <div style="text-align: right;">
            <span class="pulse-node"></span>
            <span style="font-family:'Orbitron'; color:#10b981; font-weight:700; font-size:0.85rem; margin-left:8px; letter-spacing:1px;">
                LIVE STREAMING ACTIVE
            </span>
        </div>
    </div>
</div>
"""

st.markdown(header_html, unsafe_allow_html=True)

# Generate a new record on cycle
if run_simulation:
    generate_live_event()

df = pd.DataFrame(st.session_state.transactions)

# Metric Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Gross Billed Stream", f"R{st.session_state.total_gross:,.2f}")
col2.metric("Reconciled Liquidity", f"R{st.session_state.total_gross - st.session_state.total_exposure:,.2f}")
col3.metric("Flagged Exposure (Leakage)", f"R{st.session_state.total_exposure:,.2f}", delta=f"{(st.session_state.total_exposure/(st.session_state.total_gross+1e-5))*100:.2f}% Risk", delta_color="inverse")
col4.metric("Engine Throughput", f"{len(st.session_state.transactions)} txns/buffer")

st.markdown('<div class="cyber-section">1. AMBIENT CAPITAL & PHYSICAL FLOW DIAGRAM (ANIMATED NETWORK)</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. DYNAMIC WEBGL ANIMATED FLOW GRAPH (PyDeck)
# -----------------------------------------------------------------------------
nodes_data = [
    {"name": "1. WEIGHBRIDGE GATE (Physical)", "coordinates": [29.23, -25.87], "color": [56, 189, 248]},
    {"name": "2. DIGITIZED SCALE MEASUREMENT", "coordinates": [29.25, -25.86], "color": [52, 211, 153]},
    {"name": "3. TRUEFLOW RECONCILIATION ENGINE", "coordinates": [29.27, -25.85], "color": [129, 140, 248]},
    {"name": "4. SETTLED LIQUIDITY (Clean Pool)", "coordinates": [29.29, -25.84], "color": [16, 185, 129]},
    {"name": "5. LEAKAGE EXPOSURE POOL (Flagged)", "coordinates": [29.29, -25.87], "color": [239, 68, 68]}
]

latest_leak = df.iloc[0]["Leakage (ZAR)"] if not df.empty else 0.0

flow_arcs = [
    {"source": [29.23, -25.87], "target": [29.25, -25.86], "color": [56, 189, 248, 180]},
    {"source": [29.25, -25.86], "target": [29.27, -25.85], "color": [52, 211, 153, 200]},
    {"source": [29.27, -25.85], "target": [29.29, -25.84], "color": [16, 185, 129, 220]},
]

if latest_leak > 0:
    flow_arcs.append({"source": [29.27, -25.85], "target": [29.29, -25.87], "color": [239, 68, 68, 255]})

nodes_df = pd.DataFrame(nodes_data)
arcs_df = pd.DataFrame(flow_arcs)

node_layer = pdk.Layer(
    "ScatterplotLayer",
    nodes_df,
    get_position="coordinates",
    get_fill_color="color",
    get_radius=180,
    pickable=True
)

text_layer = pdk.Layer(
    "TextLayer",
    nodes_df,
    get_position="coordinates",
    get_text="name",
    get_size=14,
    get_color=[243, 244, 246],
    get_angle=0,
    get_text_anchor="'middle'",
    get_alignment_baseline="'bottom'"
)

arc_layer = pdk.Layer(
    "ArcLayer",
    arcs_df,
    get_source_position="source",
    get_target_position="target",
    get_source_color="color",
    get_target_color="color",
    get_width=6,
    auto_highlight=True
)

view_state = pdk.ViewState(
    latitude=-25.855,
    longitude=29.26,
    zoom=12.2,
    pitch=50,
    bearing=-20
)

r = pdk.Deck(
    layers=[arc_layer, node_layer, text_layer],
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/dark-v10",
    tooltip={"text": "{name}"}
)

st.pydeck_chart(r, use_container_width=True)

# -----------------------------------------------------------------------------
# 6. DYNAMICALLY ADJUSTING CHARTS & RECENT LEDGER
# -----------------------------------------------------------------------------
c_left, c_right = st.columns([1, 1])

with c_left:
    st.markdown('<div class="cyber-section">2. REAL-TIME EXPOSURE VOLATILITY</div>', unsafe_allow_html=True)
    if not df.empty:
        fig_line = px.line(
            df[::-1],
            x="Timestamp",
            y="Leakage (ZAR)",
            markers=True,
            template="plotly_dark",
            color_discrete_sequence=["#ef4444"]
        )
        fig_line.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=280
        )
        st.plotly_chart(fig_line, use_container_width=True)

with c_right:
    st.markdown('<div class="cyber-section">3. ANOMALY FAMILY BREAKDOWN</div>', unsafe_allow_html=True)
    if not df.empty:
        fig_pie = px.pie(
            df,
            names="Anomaly",
            values="Billed (ZAR)",
            hole=0.5,
            template="plotly_dark",
            color_discrete_sequence=["#10b981", "#ef4444", "#f59e0b"]
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=280
        )
        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown('<div class="cyber-section">4. LIVE TRANSACTION STREAM (AUTO-ADJUSTING)</div>', unsafe_allow_html=True)

def style_live_rows(row):
    if row["Status"] == "EXPOSURE DETECTED":
        return ['background-color: rgba(127, 29, 29, 0.4); color: #fca5a5'] * len(row)
    return ['background-color: rgba(6, 78, 59, 0.3); color: #6ee7b7'] * len(row)

if not df.empty:
    styled_df = df.style.apply(style_live_rows, axis=1)\
        .format({
            "Scale Mass (t)": "{:.3f}",
            "Billed Mass (t)": "{:.3f}",
            "Expected (ZAR)": "R{:,.2f}",
            "Billed (ZAR)": "R{:,.2f}",
            "Leakage (ZAR)": "R{:,.2f}"
        })
    st.dataframe(styled_df, use_container_width=True, height=280)

# Rerun trigger for continuous ambient animation
if run_simulation:
    time.sleep(sim_speed)
    st.rerun()
