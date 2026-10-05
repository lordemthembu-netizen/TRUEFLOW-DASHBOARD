```python
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 1. PAGE & THEME CONFIGURATION (Futuristic Quantitative Theme)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="TrueFlow Assurance Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for high-tech quantitative terminal aesthetics
st.markdown("""
    <style>
    /* Dark Theme Core */
    .stApp {
        background-color: #0B0F19;
        color: #E2E8F0;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Neon Glow & Metric Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.8) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5), inset 0 0 10px rgba(56, 189, 248, 0.05);
        border-radius: 12px;
        padding: 18px;
        transition: all 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: rgba(56, 189, 248, 0.5);
        box-shadow: 0 6px 24px rgba(56, 189, 248, 0.15);
    }
    div[data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700 !important;
    }

    /* Section Containers */
    .quant-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }

    /* Headers */
    h1, h2, h3 {
        color: #F8FAFC !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    .neon-text {
        color: #38BDF8;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
    }

    /* Dataframe Styling */
    .stDataFrame {
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 8px;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SYNTHETIC QUANT TRANSACTION GENERATOR
# -----------------------------------------------------------------------------
@st.cache_data
def generate_quant_transactions(num_records=450):
    np.random.seed(101)
    start_date = datetime.now() - timedelta(days=90)
    
    suppliers = ["ABC Coal Mining", "Highveld Haulers Ltd", "Vlakfontein Mining Corp", "Mpumalanga Freight"]
    trucks = [f"MP {np.random.randint(100, 999)}-{np.random.randint(100, 999)}" for _ in range(30)]
    weighbridges = ["WB-01 (North Gate)", "WB-02 (East Siding)", "WB-03 (South Pit)"]
    
    data = []
    
    for i in range(1, num_records + 1):
        txn_id = f"TXN-2026-{10000 + i}"
        timestamp = start_date + timedelta(days=np.random.randint(0, 90), hours=np.random.randint(5, 20))
        supplier = np.random.choice(suppliers)
        truck = np.random.choice(trucks)
        wb = np.random.choice(weighbridges)
        po_num = f"PO-10{np.random.randint(10, 99)}"
        dn_num = f"DN-{np.random.randint(8000, 9999)}"
        inv_num = f"INV-{np.random.randint(5000, 6999)}"
        
        # Ground Truth Physical Mass (Weighbridge)
        physical_mass = round(np.random.uniform(31.5, 39.0), 2)
        po_rate = 1850.0  # Contracted baseline rate per tonne (R1,850/t)
        
        # Stochastic Leakage Injector
        p = np.random.random()
        
        if p < 0.72:
            # Reconciled Match
            status = "MATCH"
            billed_mass = physical_mass
            billed_rate = po_rate
            anomaly = "None"
            risk_score = np.random.uniform(0.01, 0.15)
            
        elif p < 0.84:
            # Quantity Discrepancy (Overbill)
            status = "FINANCIAL_EXPOSURE_DETECTED"
            billed_mass = round(physical_mass + np.random.uniform(1.2, 4.0), 2)
            billed_rate = po_rate
            anomaly = "Quantity Overbill"
            risk_score = np.random.uniform(0.75, 0.98)
            
        elif p < 0.93:
            # Contract Price Creep
            status = "FINANCIAL_EXPOSURE_DETECTED"
            billed_mass = physical_mass
            billed_rate = po_rate + np.random.choice([120.0, 180.0, 250.0])
            anomaly = "Price Creep"
            risk_score = np.random.uniform(0.70, 0.92)
            
        else:
            # Missing Evidence / Identity Discrepancy
            status = "INVESTIGATION_RECOMMENDED"
            billed_mass = physical_mass
            billed_rate = po_rate
            anomaly = "Missing Evidence"
            risk_score = np.random.uniform(0.50, 0.74)
            
        expected_val = round(physical_mass * po_rate, 2)
        billed_val = round(billed_mass * billed_rate, 2)
        financial_exposure = max(0.0, round(billed_val - expected_val, 2))
        
        data.append({
            "Transaction ID": txn_id,
            "Timestamp": timestamp,
            "Supplier": supplier,
            "Truck Reg": truck,
            "Weighbridge": wb,
            "PO Number": po_num,
            "Delivery Note": dn_num,
            "Invoice Number": inv_num,
            "Physical Mass (t)": physical_mass,
            "Billed Mass (t)": billed_mass,
            "Contract Rate (R/t)": po_rate,
            "Billed Rate (R/t)": billed_rate,
            "Expected Total (ZAR)": expected_val,
            "Billed Total (ZAR)": billed_val,
            "Exposure (ZAR)": financial_exposure,
            "Status": status,
            "Anomaly Category": anomaly,
            "Risk Score": risk_score
        })
        
    df = pd.DataFrame(data)
    return df.sort_values(by="Timestamp", ascending=False)

df_raw = generate_quant_transactions()

# -----------------------------------------------------------------------------
# 3. SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
st.sidebar.markdown("## ⚡ TrueFlow Engine")
st.sidebar.caption("Quantitative Transaction Assurance & Real-Time Leakage Analytics")
st.sidebar.divider()

# Interactive Filters
supplier_filter = st.sidebar.multiselect(
    "Select Suppliers",
    options=df_raw["Supplier"].unique(),
    default=df_raw["Supplier"].unique()
)

status_filter = st.sidebar.multiselect(
    "Audit Status",
    options=df_raw["Status"].unique(),
    default=df_raw["Status"].unique()
)

date_window = st.sidebar.date_input(
    "Temporal Window",
    value=(df_raw["Timestamp"].min().date(), df_raw["Timestamp"].max().date())
)

min_d, max_d = date_window[0], date_window[1]
df_filtered = df_raw[
    (df_raw["Supplier"].isin(supplier_filter)) &
    (df_raw["Status"].isin(status_filter)) &
    (df_raw["Timestamp"].dt.date >= min_d) &
    (df_raw["Timestamp"].dt.date <= max_d)
]

# -----------------------------------------------------------------------------
# 4. DASHBOARD HEADER & REAL-TIME QUANT METRICS
# -----------------------------------------------------------------------------
st.markdown("# ⚡ TRUEFLOW ASSURANCE PLATFORM")
st.markdown("<p style='color:#94A3B8; font-size:1.1rem;'>Physical-to-Financial Capital Reconciliation Engine</p>", unsafe_allow_html=True)
st.write("")

tot_txns = len(df_filtered)
tot_billed = df_filtered["Billed Total (ZAR)"].sum()
tot_expected = df_filtered["Expected Total (ZAR)"].sum()
tot_exposure = df_filtered["Exposure (ZAR)"].sum()
leakage_pct = (tot_exposure / tot_billed * 100) if tot_billed > 0 else 0.0
anomalies_cnt = len(df_filtered[df_filtered["Status"] != "MATCH"])

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Analyzed Volume", f"{tot_txns:,} Txns")
k2.metric("Gross Billed Value", f"R{tot_billed:,.0f}")
k3.metric("Verified Value", f"R{tot_expected:,.0f}")
k4.metric("Financial Exposure", f"R{tot_exposure:,.0f}", delta=f"{leakage_pct:.2f}% Leakage", delta_color="inverse")
k5.metric("Identified Anomalies", f"{anomalies_cnt:,}", delta="Flagged", delta_color="off")

st.divider()

# -----------------------------------------------------------------------------
# 5. FUTURISTIC SANKEY FLOW DIAGRAM (QUANT CAPITAL FLOW)
# -----------------------------------------------------------------------------
st.markdown("### 🌐 Physical-to-Financial Capital Flow Network")
st.caption("Visualizing the flow of money from physical weighbridge mass through commercial documentation to final payment disbursement vs flagged financial leakage.")

# Construct Sankey Nodes and Links dynamically from current filtered state
reconciled_val = tot_expected
qty_leakage = df_filtered[df_filtered["Anomaly Category"] == "Quantity Overbill"]["Exposure (ZAR)"].sum()
price_leakage = df_filtered[df_filtered["Anomaly Category"] == "Price Creep"]["Exposure (ZAR)"].sum()
missing_leakage = df_filtered[df_filtered["Anomaly Category"] == "Missing Evidence"]["Exposure (ZAR)"].sum()

sankey_nodes = [
    {"label": f"Gross Billed Claims<br>R{tot_billed:,.0f}"},           # 0
    {"label": f"Physical Ground Truth<br>R{tot_expected:,.0f}"},       # 1
    {"label": f"Claimed Variances<br>R{tot_exposure:,.0f}"},          # 2
    {"label": f"Reconciled Capital<br>R{reconciled_val:,.0f}"},        # 3
    {"label": f"Quantity Overbill<br>R{qty_leakage:,.0f}"},           # 4
    {"label": f"Contract Price Creep<br>R{price_leakage:,.0f}"},      # 5
    {"label": f"Missing Documentation<br>R{missing_leakage:,.0f}"}    # 6
]

node_labels = [n["label"] for n in sankey_nodes]

sankey_sources = [0, 0, 1, 2, 2, 2]
sankey_targets = [1, 2, 3, 4, 5, 6]
sankey_values  = [
    tot_expected, 
    tot_exposure, 
    reconciled_val, 
    max(1.0, qty_leakage), 
    max(1.0, price_leakage), 
    max(1.0, missing_leakage)
]

fig_sankey = go.Figure(data=[go.Sankey(
    node=dict(
        pad=20,
        thickness=20,
        line=dict(color="#38BDF8", width=0.5),
        label=node_labels,
        color=["#0EA5E9", "#10B981", "#EF4444", "#059669", "#F87171", "#FBBF24", "#60A5FA"]
    ),
    link=dict(
        source=sankey_sources,
        target=sankey_targets,
        value=sankey_values,
        color=[
            "rgba(16, 185, 129, 0.3)",
            "rgba(239, 68, 68, 0.4)",
            "rgba(5, 150, 105, 0.4)",
            "rgba(248, 113, 113, 0.6)",
            "rgba(251, 191, 36, 0.6)",
            "rgba(96, 165, 250, 0.6)"
        ]
    )
)])

fig_sankey.update_layout(
    font=dict(size=12, color="#F8FAFC", family="Inter"),
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor="rgba(15, 23, 42, 0.0)",
    plot_bgcolor="rgba(15, 23, 42, 0.0)",
    height=380
)

st.plotly_chart(fig_sankey, use_container_width=True)

st.divider()

# -----------------------------------------------------------------------------
# 6. QUANTITATIVE RISK & LEAKAGE ANALYTICS
# -----------------------------------------------------------------------------
c_left, c_right = st.columns([1, 1])

with c_left:
    st.markdown("### 📊 Anomaly Distribution by Supplier")
    supplier_risk = df_filtered.groupby(["Supplier", "Anomaly Category"])["Exposure (ZAR)"].sum().reset_index()
    
    fig_supp = px.bar(
        supplier_risk,
        x="Supplier",
        y="Exposure (ZAR)",
        color="Anomaly Category",
        color_discrete_map={
            "None": "#10B981",
            "Quantity Overbill": "#EF4444",
            "Price Creep": "#F59E0B",
            "Missing Evidence": "#3B82F6"
        },
        template="plotly_dark",
        barmode="stack",
        height=340
    )
    fig_supp.update_layout(
        paper_bgcolor="rgba(15, 23, 42, 0.0)",
        plot_bgcolor="rgba(15, 23, 42, 0.0)",
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="",
        legend_title_text=""
    )
    st.plotly_chart(fig_supp, use_container_width=True)

with c_right:
    st.markdown("### 📈 Risk Score vs Financial Exposure Scatter")
    fig_scatter = px.scatter(
        df_filtered,
        x="Risk Score",
        y="Exposure (ZAR)",
        color="Anomaly Category",
        size="Billed Total (ZAR)",
        hover_data=["Transaction ID", "Supplier", "Truck Reg"],
        color_discrete_map={
            "None": "#10B981",
            "Quantity Overbill": "#EF4444",
            "Price Creep": "#F59E0B",
            "Missing Evidence": "#3B82F6"
        },
        template="plotly_dark",
        height=340
    )
    fig_scatter.update_layout(
        paper_bgcolor="rgba(15, 23, 42, 0.0)",
        plot_bgcolor="rgba(15, 23, 42, 0.0)",
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="TrueFlow Quant Risk Score (0.0 - 1.0)",
        legend_title_text=""
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# -----------------------------------------------------------------------------
# 7. TRANSACTION EVIDENCE LEDGER & DRILL-DOWN
# -----------------------------------------------------------------------------
st.markdown("### 📋 Canonical Transaction Evidence Ledger")

def highlight_rows(val):
    if val == "FINANCIAL_EXPOSURE_DETECTED":
        return 'background-color: rgba(239, 68, 68, 0.2); color: #FCA5A5;'
    elif val == "INVESTIGATION_RECOMMENDED":
        return 'background-color: rgba(245, 158, 11, 0.2); color: #FDE68A;'
    return 'background-color: rgba(16, 185, 129, 0.1); color: #A7F3D0;'

styled_table = df_filtered.style.applymap(highlight_rows, subset=["Status"])\
    .format({
        "Physical Mass (t)": "{:.2f}",
        "Billed Mass (t)": "{:.2f}",
        "Contract Rate (R/t)": "R{:.2f}",
        "Billed Rate (R/t)": "R{:.2f}",
        "Expected Total (ZAR)": "R{:,.2f}",
        "Billed Total (ZAR)": "R{:,.2f}",
        "Exposure (ZAR)": "R{:,.2f}",
        "Risk Score": "{:.2f}",
        "Timestamp": lambda x: x.strftime('%Y-%m-%d %H:%M')
    })

st.dataframe(styled_table, use_container_width=True, height=360)

# Single Transaction Inspection Panel
st.write("")
st.markdown("#### 🔍 Single Transaction Deep Inspection")
sel_txn = st.selectbox("Select Transaction ID to inspect canonical evidence flow:", df_filtered["Transaction ID"].unique())

if sel_txn:
    t_row = df_filtered[df_filtered["Transaction ID"] == sel_txn].iloc[0]
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.markdown("<div class='quant-card'>", unsafe_allow_html=True)
        st.markdown("**1. Physical Reality Layer**")
        st.markdown(f"""
        - **Weighbridge:** `{t_row['Weighbridge']}`
        - **Truck Reg:** `{t_row['Truck Reg']}`
        - **Net Mass Measured:** `{t_row['Physical Mass (t)']} tonnes`
        - **Timestamp:** `{t_row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')}`
        """)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_b:
        st.markdown("<div class='quant-card'>", unsafe_allow_html=True)
        st.markdown("**2. Commercial Documentation**")
        st.markdown(f"""
        - **PO Number:** `{t_row['PO Number']}` (Rate: `R{t_row['Contract Rate (R/t)']}/t`)
        - **Delivery Note:** `{t_row['Delivery Note']}`
        - **Invoice Billed:** `{t_row['Billed Mass (t)']}t` @ `R{t_row['Billed Rate (R/t)']}/t`
        - **Invoice Total:** `R{t_row['Billed Total (ZAR)']:,.2f}`
        """)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_c:
        st.markdown("<div class='quant-card'>", unsafe_allow_html=True)
        st.markdown("**3. Reconciled Audit Determination**")
        if t_row["Exposure (ZAR)"] > 0:
            st.markdown(f"""
            <span style='color:#EF4444; font-weight:bold;'>🔴 EXPOSURE DETECTED</span><br>
            - **Anomaly:** {t_row['Anomaly Category']}<br>
            - **Calculated Exposure:** <span style='color:#EF4444; font-weight:bold;'>R{t_row['Exposure (ZAR)']:,.2f}</span><br>
            - **Quant Risk Score:** {t_row['Risk Score']:.2f}<br>
            - **Action:** Flag payment for AP freeze.
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <span style='color:#10B981; font-weight:bold;'>🟢 FULLY RECONCILED</span><br>
            - **Anomaly:** None<br>
            - **Calculated Exposure:** R0.00<br>
            - **Quant Risk Score:** {t_row['Risk Score']:.2f}<br>
            - **Action:** Pre-cleared for payment.
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
```
