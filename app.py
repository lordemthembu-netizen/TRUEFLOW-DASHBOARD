import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG & FUTURISTIC AMBIENT CSS THEME
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="TrueFlow // Cybernetic Assurance Terminal",
    page_icon="âš¡",
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

    /* Streamlit Flow Container Card */
    .flow-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(56, 189, 248, 0.2);
        box-shadow: inset 0 0 20px rgba(15, 23, 42, 0.8), 0 0 25px rgba(0, 0, 0, 0.5);
        border-radius: 12px;
        padding: 20px;
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
st.sidebar.markdown("### âš¡ ENGINE CONTROL")
run_simulation = st.sidebar.toggle("Stream Live Transactions", value=True)
sim_speed = st.sidebar.slider("Update Interval (Seconds)", min_value=2, max_value=30, value=10, step=1)

st.sidebar.divider()
st.sidebar.markdown("**System Telemetry**")
st.sidebar.caption("Refresh Frequency: 10s Cycle")
st.sidebar.caption("Diagram Rendering: High-DPI Plotly Network Sankey")

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

# Generate a new event on every 10-second refresh cycle
if run_simulation:
    generate_live_event()

df = pd.DataFrame(st.session_state.transactions)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Gross Billed Stream", f"R{st.session_state.total_gross:,.2f}")
col2.metric("Reconciled Liquidity", f"R{st.session_state.total_gross - st.session_state.total_exposure:,.2f}")
col3.metric("Flagged Exposure (Leakage)", f"R{st.session_state.total_exposure:,.2f}", delta=f"{(st.session_state.total_exposure/(st.session_state.total_gross+1e-5))*100:.2f}% Risk", delta_color="inverse")
col4.metric("Engine Throughput", f"{len(st.session_state.transactions)} txns/buffer")

st.markdown('<div class="cyber-section">1. AMBIENT CAPITAL & PHYSICAL FLOW DIAGRAM (NEON FLOW NETWORK)</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. HIGH-DPI ELEGANT SANKEY / FLOW NETWORK (NO OVERLAPPING TEXT)
# -----------------------------------------------------------------------------
latest_leak = df.iloc[0]["Leakage (ZAR)"] if not df.empty else 0.0
clean_val = max(100.0, st.session_state.total_gross - st.session_state.total_exposure)
leak_val = max(0.0, st.session_state.total_exposure)

# Node Definitions with Clean Multi-line Formatting to avoid text clipping
node_labels = [
    "<b>[01] WEIGHBRIDGE GATE</b><br>Physical Scale Reading",
    "<b>[02] DIGITAL LOG</b><br>Immutable Evidence Record",
    "<b>[03] RECONCILIATION ENGINE</b><br>Quant Rules & Math Check",
    "<b>[04] VERIFIED SETTLEMENT</b><br>R0 Financial Leakage",
    "<b>[05] FLAGGED LEAKAGE POOL</b><br>Quant Exposure Detected"
]

# Flow values
sankey_fig = go.Figure(data=[go.Sankey(
    arrangement="snap",
    node=dict(
        pad=35,
        thickness=22,
        line=dict(color="rgba(56, 189, 248, 0.6)", width=1.5),
        label=node_labels,
        color=[
            "#38BDF8",  # Cyan (Weighbridge)
            "#818CF8",  # Indigo (Digital Log)
            "#34D399",  # Emerald (TrueFlow Engine)
            "#10B981",  # Green (Verified)
            "#EF4444"   # Red/Crimson (Leakage)
        ],
    ),
    link=dict(
        source=[0, 1, 2, 2],
        target=[1, 2, 3, 4],
        value=[
            clean_val + leak_val,
            clean_val + leak_val,
            clean_val,
            max(0.1, leak_val)
        ],
        color=[
            "rgba(56, 189, 248, 0.28)",
            "rgba(129, 140, 248, 0.28)",
            "rgba(16, 185, 129, 0.45)",
            "rgba(239, 68, 68, 0.60)" if latest_leak > 0 else "rgba(239, 68, 68, 0.15)"
        ]
    )
)])

sankey_fig.update_layout(
    font=dict(family="JetBrains Mono, sans-serif", size=12, color="#F3F4F6"),
    paper_bgcolor="rgba(15, 23, 42, 0.6)",
    plot_bgcolor="rgba(0, 0, 0, 0)",
    height=340,
    margin=dict(l=25, r=25, t=20, b=20)
)

st.plotly_chart(sankey_fig, use_container_width=True)

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
            color_discrete_sequence=["#EF4444"]
        )
        fig_line.update_layout(
            paper_bgcolor="rgba(15, 23, 42, 0.5)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=280
        )
        st.plotly_chart(fig_line, use_container_width=True)

with c_right:
    st.markdown('<div class="cyber-section">3. ANOMALY CATEGORY DISTRIBUTION</div>', unsafe_allow_html=True)
    if not df.empty:
        fig_pie = px.pie(
            df,
            names="Anomaly",
            values="Billed (ZAR)",
            hole=0.55,
            template="plotly_dark",
            color_discrete_sequence=["#10B981", "#EF4444", "#F59E0B"]
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(15, 23, 42, 0.5)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=280
        )
        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown('<div class="cyber-section">4. LIVE TRANSACTION STREAM (AUTO-ADJUSTING LEDGER)</div>', unsafe_allow_html=True)

# Custom row styling function
def style_live_rows(row):
    if row["Status"] == "EXPOSURE DETECTED":
        return ['background-color: rgba(127, 29, 29, 0.45); color: #FCA5A5'] * len(row)
    return ['background-color: rgba(6, 78, 59, 0.35); color: #6EE7B7'] * len(row)

if not df.empty:
    styled_df = df.style.apply(style_live_rows, axis=1)        .format({
            "Scale Mass (t)": "{:.3f}",
            "Billed Mass (t)": "{:.3f}",
            "Expected (ZAR)": "R{:,.2f}",
            "Billed (ZAR)": "R{:,.2f}",
            "Leakage (ZAR)": "R{:,.2f}"
        })
    st.dataframe(styled_df, use_container_width=True, height=280)

# 10-Second Continuous Execution Loop
if run_simulation:
    time.sleep(sim_speed)
    st.rerun()
