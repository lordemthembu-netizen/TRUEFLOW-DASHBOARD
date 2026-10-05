import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 1. STREAMLIT PAGE CONFIGURATION & FUTURISTIC QUANT THEME
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="TrueFlow // Quantitative Transaction Assurance",
    page_icon="âš¡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Cyber/Quant CSS Theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'JetBrains Mono', monospace, sans-serif;
    }
    
    .stApp {
        background-color: #030712;
        color: #F3F4F6;
    }
    
    /* Header Card Styling */
    .quant-header {
        background: linear-gradient(135deg, #111827 0%, #030712 100%);
        border: 1px solid #1F2937;
        border-left: 4px solid #10B981;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 25px;
    }
    
    /* KPI Metric Cards */
    div[data-testid="stMetric"] {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid #1F2937;
        padding: 16px;
        border-radius: 8px;
        backdrop-filter: blur(10px);
    }
    
    div[data-testid="stMetric"] label {
        color: #9CA3AF !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #10B981 !important;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
    }
    
    /* Section Headers */
    .section-title {
        color: #38BDF8;
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-top: 15px;
        margin-bottom: 15px;
        border-bottom: 1px solid #1F2937;
        padding-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SYNTHETIC QUANT TRANSACTION DATA ENGINE
# -----------------------------------------------------------------------------
@st.cache_data
def generate_quant_dataset(records=350):
    np.random.seed(42)
    start_time = datetime(2026, 7, 1)
    
    suppliers = ["ABC Mining Corp", "Highveld Haulers Ltd", "Vlakfontein Bulk Supply", "Mpumalanga Logistics"]
    weighbridges = ["WB-NORTH-01", "WB-EAST-02", "WB-RAIL-03"]
    trucks = [f"MP-{np.random.randint(100, 999)}-GP" for _ in range(18)]
    
    data = []
    
    for i in range(1, records + 1):
        txn_id = f"TXN-2026-{i:05d}"
        timestamp = start_time + timedelta(
            days=int(np.random.randint(0, 90)),
            hours=int(np.random.randint(6, 20)),
            minutes=int(np.random.randint(0, 59))
        )
        
        supplier = np.random.choice(suppliers)
        truck = np.random.choice(trucks)
        wb = np.random.choice(weighbridges)
        po_number = f"PO-90{np.random.randint(10, 99)}"
        
        # Ground Truth Physical Scale Data
        physical_mass = round(float(np.random.uniform(31.5, 39.2)), 2)
        contract_rate = 1850.0  # R1,850 per tonne
        
        rand_val = np.random.random()
        
        if rand_val < 0.70:
            # Reconciled Clean Flow
            status = "CLEAN"
            billed_mass = physical_mass
            billed_rate = contract_rate
            anomaly = "None"
        elif rand_val < 0.83:
            # Overbill Tonnage Variance
            status = "LEAKAGE_DETECTED"
            billed_mass = round(physical_mass + float(np.random.uniform(1.2, 3.8)), 2)
            billed_rate = contract_rate
            anomaly = "Tonnage Overbill"
        elif rand_val < 0.93:
            # Rate Creep Discrepancy
            status = "LEAKAGE_DETECTED"
            billed_mass = physical_mass
            billed_rate = contract_rate + float(np.random.choice([120.0, 180.0, 250.0]))
            anomaly = "Price Rate Creep"
        else:
            # Unverified Evidence Flow
            status = "SUSPICIOUS_PATTERN"
            billed_mass = physical_mass
            billed_rate = contract_rate
            anomaly = "Missing Scale Cert"
            
        expected_zar = round(physical_mass * contract_rate, 2)
        billed_zar = round(billed_mass * billed_rate, 2)
        exposure_zar = max(0.0, round(billed_zar - expected_zar, 2))
        
        data.append({
            "Transaction ID": txn_id,
            "Timestamp": timestamp,
            "Date": timestamp.strftime("%Y-%m-%d"),
            "Supplier": supplier,
            "Truck ID": truck,
            "Weighbridge": wb,
            "PO Number": po_number,
            "Physical Mass (t)": physical_mass,
            "Billed Mass (t)": billed_mass,
            "Contract Rate (R/t)": contract_rate,
            "Billed Rate (R/t)": billed_rate,
            "Expected Value (ZAR)": expected_zar,
            "Billed Value (ZAR)": billed_zar,
            "Financial Exposure (ZAR)": exposure_zar,
            "Status": status,
            "Anomaly Category": anomaly
        })
        
    df = pd.DataFrame(data)
    return df.sort_values(by="Timestamp", ascending=False)

df_raw = generate_quant_dataset()

# -----------------------------------------------------------------------------
# 3. SIDEBAR QUANT FILTERS
# -----------------------------------------------------------------------------
st.sidebar.markdown("### âš¡ TRUEFLOW QUANT")
st.sidebar.caption("Transaction Assurance Layer")
st.sidebar.divider()

supplier_sel = st.sidebar.multiselect(
    "Select Suppliers",
    options=df_raw["Supplier"].unique(),
    default=df_raw["Supplier"].unique()
)

status_sel = st.sidebar.multiselect(
    "Audit Status",
    options=df_raw["Status"].unique(),
    default=df_raw["Status"].unique()
)

df_filtered = df_raw[
    (df_raw["Supplier"].isin(supplier_sel)) &
    (df_raw["Status"].isin(status_sel))
]

# -----------------------------------------------------------------------------
# 4. EXECUTIVE HEADER & QUANT METRICS
# -----------------------------------------------------------------------------
st.markdown("""
<div class="quant-header">
    <h2 style="margin:0; color:#F3F4F6; font-size:1.6rem;">TRUEFLOW // TRANSACTION ASSURANCE PLATFORM</h2>
    <p style="margin:5px 0 0 0; color:#9CA3AF; font-size:0.9rem;">
        Reconciling Physical Measurement Reality $\leftrightarrow$ Commercial Contracts $\leftrightarrow$ Financial Settlement
    </p>
</div>
""", unsafe_allow_html=True)

total_gross_zar = df_filtered["Billed Value (ZAR)"].sum()
total_exposure_zar = df_filtered["Financial Exposure (ZAR)"].sum()
clean_value_zar = total_gross_zar - total_exposure_zar
leakage_pct = (total_exposure_zar / total_gross_zar * 100) if total_gross_zar > 0 else 0.0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Gross Billed Volume", f"R{total_gross_zar:,.2f}")
m2.metric("Verified Reconciled Value", f"R{clean_value_zar:,.2f}")
m3.metric("Identified Financial Exposure", f"R{total_exposure_zar:,.2f}", delta=f"{leakage_pct:.2f}% Leakage", delta_color="inverse")
m4.metric("Audited Transactions", f"{len(df_filtered):,}")

st.markdown('<div class="section-title">1. Interactive Capital & Physical Money Flow (Sankey Diagram)</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. FUTURISTIC SANKEY MONEY FLOW DIAGRAM
# -----------------------------------------------------------------------------
# Nodes definition
nodes = [
    {"label": "Physical Reality<br>(Weighbridges)"},         # 0
    {"label": "Commercial Contract<br>(PO Terms)"},          # 1
    {"label": "TrueFlow Assurance Engine"},                 # 2
    {"label": "Verified Settlement<br>(R0 Leakage)"},        # 3
    {"label": "Flagged Exposure<br>(Leakage Pool)"},         # 4
    {"label": "Quantity Overbill"},                         # 5
    {"label": "Price Rate Creep"}                           # 6
]

# Calculate node flow values
overbill_exposure = df_filtered[df_filtered["Anomaly Category"] == "Tonnage Overbill"]["Financial Exposure (ZAR)"].sum()
creep_exposure = df_filtered[df_filtered["Anomaly Category"] == "Price Rate Creep"]["Financial Exposure (ZAR)"].sum()

sankey_fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=20,
        thickness=20,
        line=dict(color="#1F2937", width=1),
        label=[n["label"] for n in nodes],
        color=["#38BDF8", "#818CF8", "#10B981", "#059669", "#EF4444", "#F59E0B", "#DC2626"]
    ),
    link=dict(
        source=[0, 1, 2, 2, 4, 4],
        target=[2, 2, 3, 4, 5, 6],
        value=[
            clean_value_zar + total_exposure_zar,
            clean_value_zar + total_exposure_zar,
            clean_value_zar,
            total_exposure_zar,
            overbill_exposure,
            creep_exposure
        ],
        color=[
            "rgba(56, 189, 248, 0.25)",
            "rgba(129, 140, 248, 0.25)",
            "rgba(16, 185, 129, 0.4)",
            "rgba(239, 68, 68, 0.5)",
            "rgba(245, 158, 11, 0.4)",
            "rgba(220, 38, 38, 0.4)"
        ]
    )
)])

sankey_fig.update_layout(
    font=dict(family="JetBrains Mono", size=12, color="#F3F4F6"),
    paper_bgcolor="#030712",
    plot_bgcolor="#030712",
    height=400,
    margin=dict(l=10, r=10, t=10, b=10)
)

st.plotly_chart(sankey_fig, use_container_width=True)

# -----------------------------------------------------------------------------
# 6. QUANTITATIVE RISK ANALYSIS & MONTE CARLO SIMULATION
# -----------------------------------------------------------------------------
st.markdown('<div class="section-title">2. Quantitative Analytics & Risk Simulations</div>', unsafe_allow_html=True)

q_col1, q_col2 = st.columns([1, 1])

with q_col1:
    st.markdown("**Supplier Financial Leakage Concentration**")
    sup_exposure = df_filtered.groupby("Supplier")["Financial Exposure (ZAR)"].sum().reset_index()
    
    fig_bar = px.bar(
        sup_exposure,
        x="Financial Exposure (ZAR)",
        y="Supplier",
        orientation="h",
        color="Financial Exposure (ZAR)",
        color_continuous_scale="Reds",
        template="plotly_dark"
    )
    fig_bar.update_layout(
        paper_bgcolor="#030712",
        plot_bgcolor="#030712",
        height=320,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with q_col2:
    st.markdown("**Monte Carlo Projected Annual Exposure (1,000 Runs)**")
    
    # Simple Monte Carlo Simulation of 12-Month Leakage
    np.random.seed(42)
    daily_leakage_mean = df_filtered["Financial Exposure (ZAR)"].mean()
    daily_leakage_std = df_filtered["Financial Exposure (ZAR)"].std()
    
    simulations = np.random.normal(daily_leakage_mean * 365, daily_leakage_std * np.sqrt(365), 1000)
    
    fig_hist = px.histogram(
        simulations,
        nbins=40,
        labels={"value": "Annual Projected Exposure (ZAR)"},
        color_discrete_sequence=["#38BDF8"],
        template="plotly_dark"
    )
    fig_hist.update_layout(
        paper_bgcolor="#030712",
        plot_bgcolor="#030712",
        showlegend=False,
        height=320,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# -----------------------------------------------------------------------------
# 7. TRANSACTION EVIDENCE LEDGER (FIXED FOR MODERN PANDAS)
# -----------------------------------------------------------------------------
st.markdown('<div class="section-title">3. Canonical Transaction Audit Ledger</div>', unsafe_allow_html=True)

# Custom row styling function for Pandas Styler
def highlight_status_rows(s):
    if s["Status"] == "LEAKAGE_DETECTED":
        return ["background-color: #450A0A; color: #FCA5A5"] * len(s)
    elif s["Status"] == "SUSPICIOUS_PATTERN":
        return ["background-color: #451A03; color: #FDE68A"] * len(s)
    return ["background-color: #022C22; color: #6EE7B7"] * len(s)

# Apply formatting using map() and style.apply() instead of deprecated applymap
styled_df = df_filtered.style.apply(highlight_status_rows, axis=1)    .format({
        "Physical Mass (t)": "{:.2f}",
        "Billed Mass (t)": "{:.2f}",
        "Contract Rate (R/t)": "R{:.2f}",
        "Billed Rate (R/t)": "R{:.2f}",
        "Expected Value (ZAR)": "R{:,.2f}",
        "Billed Value (ZAR)": "R{:,.2f}",
        "Financial Exposure (ZAR)": "R{:,.2f}"
    })

st.dataframe(styled_df, use_container_width=True, height=380)

# -----------------------------------------------------------------------------
# 8. DRILL-DOWN AUDIT CARD
# -----------------------------------------------------------------------------
st.markdown('<div class="section-title">4. Single Transaction Evidence Chain</div>', unsafe_allow_html=True)

selected_id = st.selectbox("Inspect Transaction ID Record:", df_filtered["Transaction ID"].unique())

if selected_id:
    row = df_filtered[df_filtered["Transaction ID"] == selected_id].iloc[0]
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.info(f"""
        **Physical Reality Layer**
        - Weighbridge: `{row['Weighbridge']}`
        - Scale Mass: `{row['Physical Mass (t)']} tonnes`
        - Truck Reg: `{row['Truck ID']}`
        - Trust Score: `99.8% (Direct Scale IoT)`
        """)
    with col_b:
        st.warning(f"""
        **Commercial Contract Layer**
        - PO Ref: `{row['PO Number']}`
        - Approved Rate: `R{row['Contract Rate (R/t)']}/t`
        - Billed Mass: `{row['Billed Mass (t)']} tonnes`
        - Billed Rate: `R{row['Billed Rate (R/t)']}/t`
        """)
    with col_c:
        if row["Financial Exposure (ZAR)"] > 0:
            st.error(f"""
            **Assurance Reconciliation**
            - Discrepancy: `{row['Anomaly Category']}`
            - Financial Exposure: `R{row['Financial Exposure (ZAR)']:,.2f}`
            - Action: `REJECT INVOICE / CREDIT NOTE REQUIRED`
            """)
        else:
            st.success(f"""
            **Assurance Reconciliation**
            - Discrepancy: `None`
            - Financial Exposure: `R0.00`
            - Action: `APPROVED FOR AUTOMATED PAYMENT`
            """)
