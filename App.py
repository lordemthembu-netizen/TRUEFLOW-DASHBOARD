import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 1. STREAMLIT PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="TrueFlow Assurance Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean enterprise aesthetics
st.markdown("""
    <style>
    .main { background-color: #0F172A; }
    .stMetric { background-color: #1E293B; padding: 15px; border-radius: 8px; border: 1px solid #334155; }
    .stMetric label { color: #94A3B8 !important; }
    .stMetric div { color: #F8FAFC !important; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SYNTHETIC DATA GENERATOR (Simulating 90 Days of Coal Transactions)
# -----------------------------------------------------------------------------
@st.cache_data
def generate_transaction_data(num_records=500):
    np.random.seed(42)
    start_date = datetime.now() - timedelta(days=90)
    
    suppliers = ["ABC Coal Mining", "Highveld Haulers", "Vlakfontein Mining Ltd", "Mpumalanga Logistics"]
    trucks = [f"MP {np.random.randint(100, 999)}-{np.random.randint(100, 999)}" for _ in range(25)]
    weighbridges = ["WB-01 (North Gate)", "WB-02 (East Gate)", "WB-03 (Rail Siding)"]
    
    records = []
    
    for i in range(1, num_records + 1):
        txn_id = f"TXN-2026-{1000 + i}"
        timestamp = start_date + timedelta(days=np.random.randint(0, 90), hours=np.random.randint(6, 18))
        supplier = np.random.choice(suppliers)
        truck = np.random.choice(trucks)
        wb = np.random.choice(weighbridges)
        po_number = f"PO-10{np.random.randint(10, 99)}"
        
        # Ground Truth Physical Measurement (Weighbridge)
        physical_mass = round(np.random.uniform(32.0, 38.5), 2)
        po_rate = 1850.0  # R1,850 per tonne contracted
        
        # Introduce deliberate leakage patterns (Anomalies)
        rand_val = np.random.random()
        
        if rand_val < 0.70:
            # 70% Clean Reconciled Transactions
            status = "MATCH"
            billed_mass = physical_mass
            billed_rate = po_rate
            anomaly_type = "None"
            
        elif rand_val < 0.82:
            # Quantity Discrepancy (Overbill Tonnage)
            status = "FINANCIAL_EXPOSURE_DETECTED"
            billed_mass = round(physical_mass + np.random.uniform(1.2, 3.5), 2)
            billed_rate = po_rate
            anomaly_type = "Quantity Overbill"
            
        elif rand_val < 0.92:
            # Contract Price Creep
            status = "FINANCIAL_EXPOSURE_DETECTED"
            billed_mass = physical_mass
            billed_rate = po_rate + np.random.choice([100.0, 150.0, 200.0])
            anomaly_type = "Price Creep"
            
        else:
            # Duplicate / Unverified Bill
            status = "INVESTIGATION_RECOMMENDED"
            billed_mass = physical_mass
            billed_rate = po_rate
            anomaly_type = "Missing WB Evidence"
            
        expected_total = round(physical_mass * po_rate, 2)
        billed_total = round(billed_mass * billed_rate, 2)
        exposure_zar = max(0.0, round(billed_total - expected_total, 2))
        
        records.append({
            "Transaction ID": txn_id,
            "Timestamp": timestamp,
            "Supplier": supplier,
            "Truck Reg": truck,
            "Weighbridge": wb,
            "PO Number": po_number,
            "Physical Mass (t)": physical_mass,
            "Billed Mass (t)": billed_mass,
            "Contract Rate (R/t)": po_rate,
            "Billed Rate (R/t)": billed_rate,
            "Expected Total (ZAR)": expected_total,
            "Billed Total (ZAR)": billed_total,
            "Exposure (ZAR)": exposure_zar,
            "Status": status,
            "Anomaly Family": anomaly_type
        })
        
    df = pd.DataFrame(records)
    return df.sort_values(by="Timestamp", ascending=False)

# Load synthetic dataset
df_raw = generate_transaction_data()

# -----------------------------------------------------------------------------
# 3. SIDEBAR CONTROLS & FILTERS
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/96/000000/lightning-bolt.png", width=50)
st.sidebar.title("TrueFlow Assurance")
st.sidebar.caption("Measure Reality. Reconcile Money. Find Leakage.")
st.sidebar.divider()

# Filters
st.sidebar.subheader("Filter Controls")
supplier_filter = st.sidebar.multiselect(
    "Supplier Name",
    options=df_raw["Supplier"].unique(),
    default=df_raw["Supplier"].unique()
)

status_filter = st.sidebar.multiselect(
    "Reconciliation Status",
    options=df_raw["Status"].unique(),
    default=df_raw["Status"].unique()
)

date_range = st.sidebar.date_input(
    "Date Window",
    value=(df_raw["Timestamp"].min().date(), df_raw["Timestamp"].max().date())
)

# Apply Filters
min_date, max_date = date_range[0], date_range[1]
filtered_df = df_raw[
    (df_raw["Supplier"].isin(supplier_filter)) &
    (df_raw["Status"].isin(status_filter)) &
    (df_raw["Timestamp"].dt.date >= min_date) &
    (df_raw["Timestamp"].dt.date <= max_date)
]

# -----------------------------------------------------------------------------
# 4. EXECUTIVE DASHBOARD HEADER & KPI ROW
# -----------------------------------------------------------------------------
st.title("⚡ Transaction Assurance Dashboard")
st.markdown("### Real-Time Physical-to-Financial Leakage Analysis")

total_processed = len(filtered_df)
total_value_zar = filtered_df["Billed Total (ZAR)"].sum()
total_exposure_zar = filtered_df["Exposure (ZAR)"].sum()
anomalous_txns = len(filtered_df[filtered_df["Status"] != "MATCH"])
leakage_rate = (total_exposure_zar / total_value_zar * 100) if total_value_zar > 0 else 0.0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Transactions", f"{total_processed:,}")
col2.metric("Total Billed Volume", f"R{total_value_zar:,.2f}")
col3.metric("Financial Exposure", f"R{total_exposure_zar:,.2f}", delta=f"{leakage_rate:.2f}% Leakage", delta_color="inverse")
col4.metric("Flagged Exceptions", f"{anomalous_txns:,}")
col5.metric("Assurance Health Score", f"{100 - leakage_rate:.1f}%")

st.divider()

# -----------------------------------------------------------------------------
# 5. CHARTS & LEAKAGE ANALYTICS
# -----------------------------------------------------------------------------
chart_col1, chart_col2 = st.columns([2, 1])

with chart_col1:
    st.subheader("Financial Exposure Over Time by Anomaly Type")
    time_df = filtered_df[filtered_df["Exposure (ZAR)"] > 0].copy()
    time_df["Date"] = time_df["Timestamp"].dt.date
    daily_exposure = time_df.groupby(["Date", "Anomaly Family"])["Exposure (ZAR)"].sum().reset_index()
    
    fig_time = px.bar(
        daily_exposure, 
        x="Date", 
        y="Exposure (ZAR)", 
        color="Anomaly Family",
        color_discrete_map={"Quantity Overbill": "#EF4444", "Price Creep": "#F59E0B", "Missing WB Evidence": "#3B82F6"},
        barmode="stack",
        template="plotly_dark",
        height=350
    )
    fig_time.update_layout(margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="#0F172A", plot_bgcolor="#0F172A")
    st.plotly_chart(fig_time, use_container_width=True)

with chart_col2:
    st.subheader("Exposure Distribution")
    anomaly_dist = filtered_df[filtered_df["Exposure (ZAR)"] > 0].groupby("Anomaly Family")["Exposure (ZAR)"].sum().reset_index()
    
    fig_pie = px.pie(
        anomaly_dist, 
        names="Anomaly Family", 
        values="Exposure (ZAR)",
        hole=0.4,
        color_discrete_sequence=["#EF4444", "#F59E0B", "#3B82F6"],
        template="plotly_dark",
        height=350
    )
    fig_pie.update_layout(margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="#0F172A")
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# -----------------------------------------------------------------------------
# 6. INTERACTIVE TRANSACTION AUDIT TABLE
# -----------------------------------------------------------------------------
st.subheader("Transaction Evidence Ledger")

# Color Status Helper
def highlight_status(val):
    if val == "FINANCIAL_EXPOSURE_DETECTED":
        return 'background-color: #7F1D1D; color: #FCA5A5'
    elif val == "INVESTIGATION_RECOMMENDED":
        return 'background-color: #78350F; color: #FDE68A'
    return 'background-color: #064E3B; color: #A7F3D0'

styled_df = filtered_df.style.applymap(highlight_status, subset=["Status"])\
    .format({
        "Physical Mass (t)": "{:.2f}",
        "Billed Mass (t)": "{:.2f}",
        "Contract Rate (R/t)": "R{:.2f}",
        "Billed Rate (R/t)": "R{:.2f}",
        "Expected Total (ZAR)": "R{:,.2f}",
        "Billed Total (ZAR)": "R{:,.2f}",
        "Exposure (ZAR)": "R{:,.2f}",
        "Timestamp": lambda x: x.strftime('%Y-%m-%d %H:%M')
    })

st.dataframe(styled_df, use_container_width=True, height=400)

# -----------------------------------------------------------------------------
# 7. DEEP-DIVE TRANSACTION DRILL-DOWN
# -----------------------------------------------------------------------------
st.divider()
st.subheader("🔍 Single Transaction Evidence Drill-Down")

selected_txn_id = st.selectbox("Select Transaction ID to inspect canonical evidence chain:", filtered_df["Transaction ID"].unique())

if selected_txn_id:
    txn_data = filtered_df[filtered_df["Transaction ID"] == selected_txn_id].iloc[0]
    
    d_col1, d_col2, d_col3 = st.columns(3)
    
    with d_col1:
        st.markdown("**1. Physical Measurement (Source of Truth)**")
        st.info(f"""
        - **Weighbridge ID:** {txn_data['Weighbridge']}
        - **Truck Reg:** {txn_data['Truck Reg']}
        - **Physical Measured Weight:** {txn_data['Physical Mass (t)']} tonnes
        - **Trust Anchor:** Direct IoT Scale Log
        """)
        
    with d_col2:
        st.markdown("**2. Commercial & Invoice Records**")
        st.warning(f"""
        - **Purchase Order:** {txn_data['PO Number']}
        - **Contracted Unit Rate:** R{txn_data['Contract Rate (R/t)']}/t
        - **Billed Weight:** {txn_data['Billed Mass (t)']} tonnes
        - **Billed Unit Rate:** R{txn_data['Billed Rate (R/t)']}/t
        """)
        
    with d_col3:
        st.markdown("**3. Reconciliation & Audit Determination**")
        if txn_data["Exposure (ZAR)"] > 0:
            st.error(f"""
            - **Audit Status:** {txn_data['Status']}
            - **Identified Anomaly:** {txn_data['Anomaly Family']}
            - **Calculated Exposure:** R{txn_data['Exposure (ZAR)']:,.2f}
            - **Recommendation:** Block Payment & Request Supplier Credit Note
            """)
        else:
            st.success(f"""
            - **Audit Status:** {txn_data['Status']}
            - **Identified Anomaly:** None
            - **Calculated Exposure:** R0.00
            - **Recommendation:** Pre-Cleared for Final AP Disbursement
            """)
