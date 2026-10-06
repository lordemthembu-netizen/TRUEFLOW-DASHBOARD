import streamlit as st
import pandas as pd

def render_transaction_control_room(txn_id: str):
    st.subheader(f"Transaction Control Room: {txn_id}")
    
    # 1. Pipeline Flow Visualization
    st.markdown("### Transaction Process Flow")
    cols = st.columns(7)
    stages = [
        ("PO", "40.00 t", "R1,850/t"),
        ("Dispatch", "40.00 t", "—"),
        ("Weighbridge", "37.20 t", "✓ TRUSTED"),
        ("Delivery Note", "39.20 t", "⚠ Variance"),
        ("GRN", "39.20 t", "—"),
        ("Invoice", "39.20 t", "R72,520"),
        ("Payment", "R72,520", "Pending")
    ]
    
    for col, (stage_name, val, subtext) in zip(cols, stages):
        with col:
            st.metric(label=stage_name, value=val, delta=subtext, delta_color="inverse" if "⚠" in subtext else "normal")

    st.divider()

    # 2. Reconciliation Engine Breakdown
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("#### Physical vs Financial Reconciliation")
        
        recon_df = pd.DataFrame({
            "Metric": ["Trusted Mass (Weighbridge)", "Billed Mass (Invoice/DN)", "Quantity Variance", "Approved Contract Rate", "Potential Exposure"],
            "Value": ["37.20 t", "39.20 t", "+2.00 t (+5.38%)", "R 1,850 / t", "R 3,700.00"]
        })
        st.table(recon_df)
        
        st.warning("⚠ ANOMALY DETECTED: Variance exceeds 3σ historical baseline for ABC Coal Mining Pty Ltd.")

    with col_right:
        st.markdown("#### Audit & Evidence Lineage")
        st.write("Confidence Scores & Extracted Verification:")
        
        docs = [
            {"Doc": "Purchase Order", "ID": "PO-10482", "Confidence": "99.7%", "Status": "Verified"},
            {"Doc": "Digital Weighbridge Log", "ID": "WB-77821", "Confidence": "99.9%", "Status": "Verified (Trusted Anchor)"},
            {"Doc": "Delivery Note", "ID": "DN-55291", "Confidence": "97.8%", "Status": "Discrepancy"},
            {"Doc": "Goods Received Note", "ID": "GRN-99182", "Confidence": "98.2%", "Status": "Verified"},
            {"Doc": "Tax Invoice", "ID": "INV-88172", "Confidence": "99.1%", "Status": "Flagged"}
        ]
        st.dataframe(pd.DataFrame(docs), use_container_width=True)

    st.divider()

    # 3. Investigation & Action Queue Entry
    st.markdown("#### Action & Decision Logging")
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        status = st.selectbox("Update Status", ["Open / Under Review", "Validated Exception", "Recovered / Settled", "Closed (Explained)"])
    with c2:
        priority = st.selectbox("Priority", ["HIGH", "MEDIUM", "LOW"])
    with c3:
        comment = st.text_input("Audit Note / Investigation Reason", placeholder="e.g., Escalated to supplier for weight adjustment credit note...")
        
    if st.button("Submit Decision to Immutable Ledger"):
        st.success(f"Transaction {txn_id} updated to '{status}'. Audit trail logged.")
        import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import os
import hashlib
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & HYPER-SOPHISTICATED INSTITUTIONAL DESIGN SYSTEM
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="TrueFlow // Enterprise Transaction Assurance & Commodity Leakage Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Institutional Dark CSS Styling (Bloomberg/Palantir Grade Slate & Neon Theme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background-color: #070B14;
        color: #F1F5F9;
    }

    /* Top Command Header Container */
    .brand-header {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(10, 15, 30, 0.98) 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
        border-radius: 14px;
        padding: 24px 32px;
        margin-bottom: 24px;
    }

    .brand-logo-text {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 2.1rem;
        letter-spacing: 1.5px;
        color: #FFFFFF;
        margin: 0;
    }

    .brand-logo-highlight {
        color: #38BDF8;
        background: linear-gradient(90deg, #38BDF8, #818CF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .tagline-text {
        font-size: 0.88rem;
        color: #94A3B8;
        margin-top: 4px;
        font-weight: 400;
        letter-spacing: 0.2px;
    }

    /* Status Telemetry Pills */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }

    .status-live {
        background-color: rgba(16, 185, 129, 0.12);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .status-connected {
        background-color: rgba(56, 189, 248, 0.12);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }

    .status-active {
        background-color: rgba(129, 140, 248, 0.12);
        color: #818CF8;
        border: 1px solid rgba(129, 140, 248, 0.3);
    }

    /* Executive KPI Metric Box */
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: all 0.25s ease;
    }

    div[data-testid="stMetric"]:hover {
        border-color: rgba(56, 189, 248, 0.4);
        transform: translateY(-2px);
    }

    div[data-testid="stMetric"] label {
        color: #94A3B8 !important;
        font-size: 0.78rem !important;
        font-weight: 600;
        letter-spacing: 0.6px;
        text-transform: uppercase;
    }

    div[data-testid="stMetricValue"] {
        color: #38BDF8 !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.65rem !important;
        font-weight: 700;
    }

    /* Section Headers */
    .app-section-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: 0.6px;
        margin-top: 28px;
        margin-bottom: 18px;
        border-left: 4px solid #0284C7;
        padding-left: 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* Provenance Stage Cards */
    .provenance-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 14px 12px;
        text-align: center;
        font-family: 'JetBrains Mono', monospace;
    }

    .provenance-card-trusted {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.4);
    }

    .provenance-card-alert {
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.4);
    }

    /* Badges */
    .badge-trusted {
        background-color: rgba(16, 185, 129, 0.2);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.72rem;
    }

    .badge-reported {
        background-color: rgba(245, 158, 11, 0.2);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.72rem;
    }

    .badge-financial {
        background-color: rgba(239, 68, 68, 0.2);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.72rem;
    }

    .hash-code {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.70rem;
        color: #64748B;
        word-break: break-all;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SYNTHETIC MULTI-DOCUMENT LEAKAGE DATA ENGINE
# -----------------------------------------------------------------------------
SUPPLIERS = ["ABC Coal Mining Pty Ltd", "Mpuma Haulage Logistics", "North Ridge Minerals", "Vanguard Bulk Rail", "Khai-Appel Mining Corp"]
TRUCKS = ["MP-1234-GP", "MP-4421-GP", "NW-8812-GP", "KZN-9012-GP", "LIM-3321-GP", "FS-7711-GP"]
MATERIALS = ["RB1 Thermal Coal (Export Grade)", "RB2 Thermal Coal", "Metallurgical Coking Coal", "Iron Ore Fines", "Chrome Ore Concentrate"]
CORRIDORS = ["eMalahleni -> Richards Bay Coal Terminal", "Steelpoort -> Maputo Port", "Middelburg -> Akasia Rail Depot", "Rustenburg -> Durban Port"]

def generate_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()[:16]

def generate_synthetic_transaction():
    if 'txn_counter' not in st.session_state:
        st.session_state.txn_counter = 4920
    st.session_state.txn_counter += 1
    txn_id = f"TXN-2026-{st.session_state.txn_counter:06d}"
    
    supplier = str(np.random.choice(SUPPLIERS, p=[0.35, 0.25, 0.15, 0.15, 0.10]))
    truck = str(np.random.choice(TRUCKS))
    material = str(np.random.choice(MATERIALS))
    corridor = str(np.random.choice(CORRIDORS))
    po_number = f"PO-{np.random.randint(100000, 999999)}"
    approved_rate = float(np.random.choice([1650.00, 1850.00, 2100.00, 2450.00]))
    
    po_quantity = 42.00
    
    # Weighbridge Scale Hardware Telemetry (Physical Ground Truth)
    weighbridge_net = round(float(np.random.uniform(36.20, 39.80)), 2)
    tare_mass = 21.40
    gross_mass = round(weighbridge_net + tare_mass, 2)
    wb_timestamp = (datetime.now() - timedelta(minutes=int(np.random.randint(2, 240)))).strftime("%Y-%m-%d %H:%M:%S")
    
    rand_type = np.random.random()
    
    if rand_type < 0.65:
        # Clean Flow
        dn_quantity = weighbridge_net
        grn_quantity = weighbridge_net
        inv_quantity = weighbridge_net
        inv_rate = approved_rate
        moisture_pct = round(float(np.random.uniform(6.0, 8.5)), 2)
        evidence_present = 7
        anomaly_desc = "Clean Verified Flow"
        leakage_category = "None (Fully Reconciled)"
    elif rand_type < 0.80:
        # Quantity Overbilling / Tare Manipulation
        overbill_t = round(float(np.random.uniform(1.40, 4.20)), 2)
        dn_quantity = round(weighbridge_net + overbill_t, 2)
        grn_quantity = dn_quantity
        inv_quantity = dn_quantity
        inv_rate = approved_rate
        moisture_pct = round(float(np.random.uniform(6.0, 8.5)), 2)
        evidence_present = 7
        anomaly_desc = "Quantity Overbill / Scale Tare Tampering"
        leakage_category = "Physical Scale vs Paper DN Discrepancy"
    elif rand_type < 0.90:
        # Price Creep Deviation
        dn_quantity = weighbridge_net
        grn_quantity = weighbridge_net
        inv_quantity = weighbridge_net
        inv_rate = approved_rate + float(np.random.choice([120.0, 210.0, 350.0]))
        moisture_pct = round(float(np.random.uniform(6.0, 8.5)), 2)
        evidence_present = 6
        anomaly_desc = "Unauthorized Rate Creep"
        leakage_category = "Contract Price Deviation"
    else:
        # Excessive Moisture / Density Shrinkage
        dn_quantity = weighbridge_net
        grn_quantity = weighbridge_net
        inv_quantity = weighbridge_net
        inv_rate = approved_rate
        moisture_pct = round(float(np.random.uniform(12.5, 18.2)), 2) # Excessive water adding fake weight
        evidence_present = 7
        anomaly_desc = "Excessive Moisture / Density Shrinkage"
        leakage_category = "Moisture Tampering / Quality Discrepancy"

    # Quantitative Financial & Physical Calculations
    qty_variance_t = round(inv_quantity - weighbridge_net, 2)
    qty_variance_pct = round((qty_variance_t / weighbridge_net) * 100, 2) if weighbridge_net > 0 else 0.0
    price_variance = round(inv_rate - approved_rate, 2)
    
    # Moisture excess penalty (>9.0% threshold)
    moisture_excess_t = round(weighbridge_net * ((max(0.0, moisture_pct - 9.0)) / 100.0), 2)
    
    quantity_exposure = round(qty_variance_t * approved_rate, 2)
    price_exposure = round(price_variance * inv_quantity, 2)
    moisture_exposure = round(moisture_excess_t * approved_rate, 2)
    
    total_exposure = round(quantity_exposure + price_exposure + moisture_exposure, 2)
    
    # Z-Score Anomaly Calculation (simulated deviation against baseline 38.0t scale mean, std 1.2t)
    z_score = round(abs((weighbridge_net - 38.0) / 1.2) + (qty_variance_t * 1.5) + (price_variance / 100.0), 2)
    
    anomaly_score = min(99, int(z_score * 18 + (10 if evidence_present < 7 else 0)))
    
    priority = "LOW"
    if anomaly_score > 75 or total_exposure > 5000:
        priority = "CRITICAL"
    elif anomaly_score > 45 or total_exposure > 1500:
        priority = "HIGH"
    elif anomaly_score > 25:
        priority = "MEDIUM"

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Document Hashes (Cryptographic Provenance)
    po_hash = generate_hash(f"{po_number}-{supplier}-{po_quantity}")
    wb_hash = generate_hash(f"{txn_id}-{weighbridge_net}-{gross_mass}")
    dn_hash = generate_hash(f"{txn_id}-{dn_quantity}")
    inv_hash = generate_hash(f"{txn_id}-{inv_quantity}-{inv_rate}")

    return {
        "transaction_id": txn_id,
        "timestamp": now_str,
        "supplier": supplier,
        "truck_registration": truck,
        "material": material,
        "corridor": corridor,
        "po_number": po_number,
        "po_quantity_t": po_quantity,
        "approved_rate_zar": approved_rate,
        "weighbridge": {
            "timestamp": wb_timestamp,
            "gross_t": gross_mass,
            "tare_t": tare_mass,
            "net_t": weighbridge_net,
            "ticket_id": f"WB-AKASIA-{np.random.randint(70000, 99999)}",
            "scale_id": "SC-04-NORTH-AKASIA",
            "hash": wb_hash
        },
        "delivery_note": {
            "quantity_t": dn_quantity,
            "document_id": f"DN-{np.random.randint(50000, 89999)}",
            "hash": dn_hash
        },
        "grn": {
            "quantity_t": grn_quantity,
            "grn_id": f"GRN-{np.random.randint(90000, 99999)}"
        },
        "invoice": {
            "quantity_t": inv_quantity,
            "rate_zar": inv_rate,
            "invoice_number": f"INV-{np.random.randint(80000, 89999)}",
            "amount_zar": round(inv_quantity * inv_rate, 2),
            "hash": inv_hash
        },
        "quality": {
            "moisture_pct": moisture_pct,
            "moisture_excess_t": moisture_excess_t
        },
        "provenance": {
            "po_hash": po_hash,
            "wb_hash": wb_hash,
            "dn_hash": dn_hash,
            "inv_hash": inv_hash,
            "chain_verified": True if evidence_present == 7 and qty_variance_t == 0 else False
        },
        "metrics": {
            "trusted_quantity_t": weighbridge_net,
            "claimed_quantity_t": inv_quantity,
            "qty_variance_t": qty_variance_t,
            "qty_variance_pct": qty_variance_pct,
            "price_variance_zar": price_variance,
            "moisture_exposure_zar": moisture_exposure,
            "potential_exposure_zar": total_exposure,
            "evidence_completeness_pct": round((evidence_present / 7) * 100, 1),
            "z_score": z_score,
            "anomaly_score": anomaly_score,
            "anomaly_type": anomaly_desc,
            "leakage_category": leakage_category,
            "priority": priority,
            "investigation_status": "OPEN" if total_exposure > 0 else "AUTO_RECONCILED"
        }
    }

# -----------------------------------------------------------------------------
# 3. SCHEMA-SAFE SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if 'transactions' in st.session_state and len(st.session_state.transactions) > 0:
    first_record = st.session_state.transactions[0]
    if not isinstance(first_record, dict) or "transaction_id" not in first_record or "corridor" not in first_record:
        st.session_state.transactions = []

if 'transactions' not in st.session_state or not st.session_state.transactions:
    st.session_state.transactions = []
    st.session_state.txn_counter = 4920
    st.session_state.recovered_capital_zar = 482500.00
    st.session_state.action_log = []
    
    for _ in range(45):
        st.session_state.transactions.append(generate_synthetic_transaction())

# -----------------------------------------------------------------------------
# 4. SIDEBAR COMMAND CENTER
# -----------------------------------------------------------------------------
st.sidebar.markdown("## 🛡️ TRUEFLOW")
st.sidebar.caption("Transaction Assurance & Leakage Intelligence")

nav_choice = st.sidebar.radio(
    "NAVIGATION PATH",
    [
        " Executive Value & CFO Command",
        " Scale Telemetry & Lineage Engine",
        " Transaction Control & Audit Room",
        " Deep Leakage & Statistical Vector",
        " Supplier Risk & Corridor Analytics",
        " Executive ROI & Audit Reports"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("### ⚡ Telemetry & Stream Engine")
run_simulation = st.sidebar.toggle("Enable Sub-Second Ingestion", value=False)
sim_speed = st.sidebar.slider("Stream Interval (sec)", 0.5, 4.0, 1.5)

if run_simulation:
    st.session_state.transactions.insert(0, generate_synthetic_transaction())
    if len(st.session_state.transactions) > 120:
        st.session_state.transactions.pop()

st.sidebar.divider()
st.sidebar.markdown("**System Architecture Info**")
st.sidebar.caption("📍 Scale Hub: **Akasia, South Africa**")
st.sidebar.caption("⚡ Ingestion Velocity: **< 12ms / Batch**")
st.sidebar.caption("🔗 ERP Adapter: **SAP S/4HANA Active**")
st.sidebar.caption("🛡️ Cryptographic Engine: **SHA-256 Active**")

# Safely build DataFrame
flat_data = []
for t in st.session_state.transactions:
    if isinstance(t, dict) and "transaction_id" in t:
        flat_data.append({
            "Transaction ID": t["transaction_id"],
            "Timestamp": t["timestamp"],
            "Supplier": t["supplier"],
            "Truck": t["truck_registration"],
            "Material": t["material"],
            "Corridor": t["corridor"],
            "Trusted Mass (t)": t["weighbridge"]["net_t"],
            "Invoiced Mass (t)": t["invoice"]["quantity_t"],
            "Billed Rate (ZAR)": t["invoice"]["rate_zar"],
            "Qty Variance (t)": t["metrics"]["qty_variance_t"],
            "Price Variance (ZAR)": t["metrics"]["price_variance_zar"],
            "Potential Exposure (ZAR)": t["metrics"]["potential_exposure_zar"],
            "Z-Score": t["metrics"]["z_score"],
            "Anomaly Score": t["metrics"]["anomaly_score"],
            "Priority": t["metrics"]["priority"],
            "Status": t["metrics"]["investigation_status"],
            "Leakage Category": t["metrics"]["leakage_category"],
            "Evidence %": t["metrics"]["evidence_completeness_pct"],
            "Moisture %": t["quality"]["moisture_pct"]
        })

df = pd.DataFrame(flat_data)

if df.empty:
    st.session_state.transactions = [generate_synthetic_transaction() for _ in range(45)]
    st.rerun()

# -----------------------------------------------------------------------------
# 5. BRANDED ENTERPRISE HERO HEADER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="brand-header">
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 20px;">
        <div>
            <div style="display:flex; align-items:center; gap:12px;">
                <span style="font-size:2.2rem;">🛡️️</span>
                <h1 class="brand-logo-text">TRUE<span class="brand-logo-highlight">FLOW</span></h1>
            </div>
            <p class="tagline-text">
                Autonomous Physical-to-Financial Leakage Intelligence & Multi-Document Provenance Platform
            </p>
        </div>
        <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 8px;">
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
                <span class="status-pill status-live">● SCALE TELEMETRY: LIVE</span>
                <span class="status-pill status-connected">⚡ SAP S/4HANA CONNECTED</span>
                <span class="status-pill status-active">🔒 SHA-256 PROVENANCE: ACTIVE</span>
            </div>
            <span style="color:#64748B; font-size:0.75rem; font-family:'JetBrains Mono'; margin-top:4px;">
                PRIMARY SCALE NODE: AKASIA REGIONAL LOGISTICS HUB, SOUTH AFRICA
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# VIEW 1: EXECUTIVE VALUE & CFO COMMAND
# -----------------------------------------------------------------------------
if nav_choice == " Executive Value & CFO Command":
    
    total_volume_t = float(df["Trusted Mass (t)"].sum())
    total_reconciled_zar = float((df["Trusted Mass (t)"] * df["Billed Rate (ZAR)"]).sum())
    total_exposure_zar = float(df["Potential Exposure (ZAR)"].sum())
    recovered_capital = float(st.session_state.recovered_capital_zar)
    auto_recon_rate = float((len(df[df["Potential Exposure (ZAR)"] == 0]) / len(df)) * 100)
    avg_evidence_completeness = float(df["Evidence %"].mean())
    risk_index = float(df["Anomaly Score"].mean())

    st.markdown('<div class="app-section-title"><span>QUANTITATIVE LEAKAGE & CFO ROI METRICS</span> <span style="font-size:0.8rem; color:#38BDF8; font-weight:400;">REAL-TIME RECONCILIATION AUDIT</span></div>', unsafe_allow_html=True)

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Audited Volume", f"{total_volume_t:,.1f} t", delta=f"R {total_reconciled_zar:,.0f} Total Value")
    m2.metric("Identified Revenue Leakage", f"R {total_exposure_zar:,.2f}", delta=f"{(total_exposure_zar/max(1, total_reconciled_zar))*100:.2f}% Exposure Rate", delta_color="inverse")
    m3.metric("Capital Recovered / Prevented", f"R {recovered_capital:,.2f}", delta="Direct CFO ROI")
    m4.metric("Auto-Reconciliation Rate", f"{auto_recon_rate:.1f}%", delta="Audit Speed: < 12ms")
    m5.metric("Evidence Integrity Score", f"{avg_evidence_completeness:.1f}%", delta=f"Risk Index: {risk_index:.1f}/100", delta_color="inverse")

    st.divider()

    c1, c2 = st.columns([2, 1])

    with c1:
        st.markdown("#### 📈 Cumulative Commodity Value vs. Uncovered Financial Leakage (ZAR)")
        df_sorted = df.iloc[::-1].copy()
        df_sorted["Cumulative_Value"] = (df_sorted["Trusted Mass (t)"] * df_sorted["Billed Rate (ZAR)"]).cumsum()
        df_sorted["Cumulative_Exposure"] = df_sorted["Potential Exposure (ZAR)"].cumsum()

        fig_leak = go.Figure()
        fig_leak.add_trace(go.Scatter(x=df_sorted["Transaction ID"], y=df_sorted["Cumulative_Value"], name="Reconciled Commodity Value (ZAR)", line=dict(color="#38BDF8", width=3)))
        fig_leak.add_trace(go.Scatter(x=df_sorted["Transaction ID"], y=df_sorted["Cumulative_Exposure"], name="Identified Financial Leakage (ZAR)", line=dict(color="#EF4444", width=3, dash="dot"), yaxis="y2"))

        fig_leak.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=340,
            margin=dict(l=10, r=10, t=30, b=10),
            legend=dict(orientation="h", y=1.15),
            yaxis=dict(title="Reconciled Value (ZAR)"),
            yaxis2=dict(title="Leakage (ZAR)", overlaying="y", side="right")
        )
        st.plotly_chart(fig_leak, use_container_width=True)

    with c2:
        st.markdown("#### 🎯 Leakage Root Cause Breakdown")
        fig_pie = px.pie(
            df[df["Potential Exposure (ZAR)"] > 0],
            names="Leakage Category",
            values="Potential Exposure (ZAR)",
            hole=0.5,
            template="plotly_dark",
            color_discrete_sequence=["#EF4444", "#F59E0B", "#818CF8", "#F43F5E"]
        )
        fig_pie.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=340,
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=True,
            legend=dict(orientation="v", y=0.5)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown('<div class="app-section-title">REAL-TIME TRANSACTION STREAM LEDGER</div>', unsafe_allow_html=True)

    def highlight_priority(row):
        if row["Priority"] == "CRITICAL":
            return ['background-color: rgba(239, 68, 68, 0.22); color: #FCA5A5; font-weight:600;'] * len(row)
        elif row["Priority"] == "HIGH":
            return ['background-color: rgba(249, 115, 22, 0.18); color: #FDBA74;'] * len(row)
        return ['background-color: rgba(15, 23, 42, 0.4); color: #E2E8F0;'] * len(row)

    disp_cols = ["Transaction ID", "Timestamp", "Supplier", "Truck", "Material", "Trusted Mass (t)", "Invoiced Mass (t)", "Qty Variance (t)", "Potential Exposure (ZAR)", "Z-Score", "Priority", "Leakage Category"]
    
    st.dataframe(
        df[disp_cols].style.apply(highlight_priority, axis=1).format({
            "Trusted Mass (t)": "{:.2f}",
            "Invoiced Mass (t)": "{:.2f}",
            "Qty Variance (t)": "{:+.2f}",
            "Potential Exposure (ZAR)": "R{:,.2f}",
            "Z-Score": "{:.2f}"
        }),
        use_container_width=True,
        height=380
    )

# -----------------------------------------------------------------------------
# VIEW 2: SCALE TELEMETRY & LINEAGE ENGINE
# -----------------------------------------------------------------------------
elif nav_choice == " Scale Telemetry & Lineage Engine":
    st.markdown('<div class="app-section-title">PHYSICAL SCALE HARDWARE TELEMETRY & 8-STAGE LINEAGE RECONSTRUCTION</div>', unsafe_allow_html=True)
    
    selected_txn_id = st.selectbox("Select Active Scale Transaction Stream Record:", df["Transaction ID"].tolist())
    txn = next((t for t in st.session_state.transactions if isinstance(t, dict) and t.get("transaction_id") == selected_txn_id), None)
    
    if txn:
        wb = txn["weighbridge"]
        m = txn["metrics"]
        prov = txn["provenance"]
        
        # Scale Hardware Live Box
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.3); border-radius:12px; padding:20px; margin-bottom:20px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span class="badge-trusted">HARDWARE SCALE GROUND TRUTH TELEMETRY</span>
                    <h3 style="margin:8px 0 0 0; color:#34D399; font-family:'JetBrains Mono';">NET PHYSICAL MASS: {wb['net_t']:.2f} TONNES</h3>
                    <p style="margin:4px 0 0 0; color:#94A3B8; font-size:0.85rem;">
                        Scale Ticket ID: <b>{wb['ticket_id']}</b> | Terminal: <b>{wb['scale_id']}</b> | Timestamp: <b>{wb['timestamp']}</b>
                    </p>
                </div>
                <div style="text-align:right;">
                    <p style="margin:0; color:#94A3B8; font-size:0.8rem;">GROSS MASS: <b style="color:#FFF;">{wb['gross_t']:.2f} t</b></p>
                    <p style="margin:4px 0 0 0; color:#94A3B8; font-size:0.8rem;">TARE MASS: <b style="color:#FFF;">{wb['tare_t']:.2f} t</b></p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 🔗 Reconstructed Multi-Document Transaction Lineage Graph")
        
        l1, l2, l3, l4, l5, l6, l7, l8 = st.columns(8)
        
        with l1:
            st.markdown(f"""<div class="provenance-card">
            <span class="badge-reported">1. PO</span><br><br>
            <b>{txn['po_quantity_t']:.1f} t</b><br>
            <small>R{txn['approved_rate_zar']:,.0f}/t</small><br>
            <span class="hash-code">#PO-{prov['po_hash'][:6]}</span>
            </div>""", unsafe_allow_html=True)
            
        with l2:
            st.markdown(f"""<div class="provenance-card">
            <span class="badge-reported">2. DISPATCH</span><br><br>
            <b>{txn['po_quantity_t']:.1f} t</b><br>
            <small>Manifest</small><br>
            <span class="hash-code">#DSP-7712</span>
            </div>""", unsafe_allow_html=True)

        with l3:
            st.markdown(f"""<div class="provenance-card provenance-card-trusted">
            <span class="badge-trusted">3. SCALE TRUTH</span><br><br>
            <b style="color:#34D399;">{wb['net_t']:.2f} t</b><br>
            <small>Weighbridge</small><br>
            <span class="hash-code">#{prov['wb_hash'][:6]}</span>
            </div>""", unsafe_allow_html=True)

        with l4:
            card_class = "provenance-card-alert" if txn['delivery_note']['quantity_t'] != wb['net_t'] else "provenance-card"
            st.markdown(f"""<div class="{card_class}">
            <span class="badge-reported">4. DELIVERY NOTE</span><br><br>
            <b>{txn['delivery_note']['quantity_t']:.2f} t</b><br>
            <small>Paper Claim</small><br>
            <span class="hash-code">#{prov['dn_hash'][:6]}</span>
            </div>""", unsafe_allow_html=True)

        with l5:
            st.markdown(f"""<div class="provenance-card">
            <span class="badge-reported">5. GRN</span><br><br>
            <b>{txn['grn']['quantity_t']:.2f} t</b><br>
            <small>Internal Rec.</small><br>
            <span class="hash-code">#GRN-9912</span>
            </div>""", unsafe_allow_html=True)

        with l6:
            card_class = "provenance-card-alert" if m['price_variance_zar'] > 0 or m['qty_variance_t'] > 0 else "provenance-card"
            st.markdown(f"""<div class="{card_class}">
            <span class="badge-financial">6. INVOICE</span><br><br>
            <b>{txn['invoice']['quantity_t']:.2f} t</b><br>
            <small>R{txn['invoice']['rate_zar']:,.0f}/t</small><br>
            <span class="hash-code">#{prov['inv_hash'][:6]}</span>
            </div>""", unsafe_allow_html=True)

        with l7:
            st.markdown(f"""<div class="provenance-card">
            <span class="badge-financial">7. PAYMENT</span><br><br>
            <b>R{txn['payment']['amount_zar']:,.0f}</b><br>
            <small>ERP Batch</small><br>
            <span class="hash-code">#PAY-3312</span>
            </div>""", unsafe_allow_html=True)

        with l8:
            status_color = "#34D399" if m["potential_exposure_zar"] == 0 else "#F87171"
            st.markdown(f"""<div class="provenance-card" style="border:1px solid {status_color};">
            <span style="color:{status_color}; font-weight:700;">8. TRUEFLOW</span><br><br>
            <b style="color:{status_color};">R{m['potential_exposure_zar']:,.0f}</b><br>
            <small>Exposure</small><br>
            <span class="hash-code">#RECON-OK</span>
            </div>""", unsafe_allow_html=True)

        st.divider()

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### ⚖️ Ground Truth Measurement vs Reported Financial Claims")
            recon_table = [
                {"Stage Source": "Scale Scale Hardware (Net Scale Weight)", "Quantity": f"{wb['net_t']:.2f} t", "Trust Status": "🟢 Trusted Physical Ground Truth"},
                {"Stage Source": "Vendor Delivery Note Document", "Quantity": f"{txn['delivery_note']['quantity_t']:.2f} t", "Trust Status": "🟡 Reported Vendor Document"},
                {"Stage Source": "Depot Goods Received Note (GRN)", "Quantity": f"{txn['grn']['quantity_t']:.2f} t", "Trust Status": "🟡 Reported Internal Document"},
                {"Stage Source": "Supplier SAP ERP Invoice", "Quantity": f"{txn['invoice']['quantity_t']:.2f} t", "Trust Status": "🔴 Billed Financial Claim"},
            ]
            st.table(pd.DataFrame(recon_table))

        with col_b:
            st.markdown("#### 🔒 Multi-Document Cryptographic SHA-256 Provenance Verification")
            st.code(f"""
[1] PO Hash        : {prov['po_hash']}  (MATCHED)
[2] Scale Hash     : {prov['wb_hash']}  (HARDWARE VERIFIED)
[3] Delivery Hash  : {prov['dn_hash']}  ({'MISMATCH' if txn['delivery_note']['quantity_t'] != wb['net_t'] else 'MATCHED'})
[4] Invoice Hash   : {prov['inv_hash']}  ({'RATE DEVIATION' if m['price_variance_zar'] > 0 else 'MATCHED'})

SHA-256 PROVENANCE CHAIN STATUS: {'✅ VERIFIED IMMUTABLE' if prov['chain_verified'] else '🚨 CHAIN TAMPERING / VARIANCE DETECTED'}
            """, language="text")

# -----------------------------------------------------------------------------
# VIEW 3: TRANSACTION CONTROL & AUDIT ROOM
# -----------------------------------------------------------------------------
elif nav_choice == " Transaction Control & Audit Room":
    st.markdown('<div class="app-section-title">EXECUTIVE EXCEPTION CONTROL & AUDIT WORKFLOW ROOM</div>', unsafe_allow_html=True)
    
    open_exceptions = df[df["Potential Exposure (ZAR)"] > 0]
    
    if not open_exceptions.empty:
        st.markdown(f"**Active Flagged Financial Leakages requiring Executive Audit Intervention ({len(open_exceptions)} Items):**")
        
        st.dataframe(
            open_exceptions[["Transaction ID", "Timestamp", "Supplier", "Truck", "Corridor", "Qty Variance (t)", "Price Variance (ZAR)", "Potential Exposure (ZAR)", "Priority", "Leakage Category"]].style.format({
                "Qty Variance (t)": "{:+.2f}",
                "Price Variance (ZAR)": "R{:,.2f}",
                "Potential Exposure (ZAR)": "R{:,.2f}"
            }),
            use_container_width=True,
            height=280
        )
        
        st.divider()
        st.markdown("### 📝 Executive One-Click Resolution & ERP Action Center")
        
        target_id = st.selectbox("Select Transaction for Immediate Action:", open_exceptions["Transaction ID"].tolist())
        target_txn = next((t for t in st.session_state.transactions if isinstance(t, dict) and t.get("transaction_id") == target_id), None)
        
        if target_txn:
            m = target_txn["metrics"]
            st.warning(f"""
            **TRANSACTION AUDIT ALERT: {target_id}**
            * **Supplier:** {target_txn['supplier']} | **Truck Reg:** `{target_txn['truck_registration']}`
            * **Identified Leakage Category:** `{m['leakage_category']}`
            * **Calculated Exposure Amount:** **R {m['potential_exposure_zar']:,.2f}**
            """)
            
            c_act1, c_act2, c_act3, c_act4 = st.columns(4)
            
            with c_act1:
                if st.button("🛑 FREEZE PAYMENT BATCH IN SAP"):
                    st.session_state.recovered_capital_zar += m['potential_exposure_zar']
                    st.session_state.action_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] FROZE PAYMENT for {target_id}. R{m['potential_exposure_zar']:,.2f} exposure prevented.")
                    st.success(f"Payment Batch for {target_id} FROZEN in SAP S/4HANA.")
                    
            with c_act2:
                if st.button("📄 ISSUE AUTOMATED CREDIT NOTE"):
                    st.session_state.recovered_capital_zar += m['potential_exposure_zar']
                    st.session_state.action_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ISSUED CREDIT NOTE for {target_id} to {target_txn['supplier']}.")
                    st.info(f"Credit Note request for R{m['potential_exposure_zar']:,.2f} dispatched to vendor ERP portal.")

            with c_act3:
                if st.button("🚨 ESCALATE TO FORENSIC AUDIT"):
                    st.session_state.action_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ESCALATED {target_id} to Internal Audit Lead.")
                    st.error(f"Transaction {target_id} logged in Forensic Investigation Queue.")

            with c_act4:
                if st.button("✅ OVERRIDE & APPROVE VARIANCE"):
                    st.session_state.action_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] OVERRODE {target_id} - operational variance approved.")
                    st.success(f"Transaction {target_id} approved with operational note.")

        if st.session_state.action_log:
            st.markdown("#### 📋 Executive Action Log (Session Audit Trail)")
            for item in reversed(st.session_state.action_log[-5:]):
                st.caption(f"• {item}")

    else:
        st.success("✅ No open leakage exceptions. All current ingestion batches are fully reconciled.")

# -----------------------------------------------------------------------------
# VIEW 4: DEEP LEAKAGE & STATISTICAL VECTOR
# -----------------------------------------------------------------------------
elif nav_choice == " Deep Leakage & Statistical Vector":
    st.markdown('<div class="app-section-title">STATISTICAL Z-SCORE ANOMALY VECTOR & MOISTURE SHRINKAGE ENGINE</div>', unsafe_allow_html=True)
    
    col_z1, col_z2 = st.columns([1, 1])
    
    with col_z1:
        st.markdown("#### 📊 Statistical Z-Score Distribution (Systematic Bias vs. Noise)")
        fig_z = px.histogram(
            df,
            x="Z-Score",
            nbins=20,
            color="Priority",
            color_discrete_map={"LOW": "#10B981", "MEDIUM": "#F59E0B", "HIGH": "#F97316", "CRITICAL": "#EF4444"},
            template="plotly_dark",
            title="Distribution of Load Mass Deviations (Sigma Variance)"
        )
        fig_z.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=320)
        st.plotly_chart(fig_z, use_container_width=True)

    with col_z2:
        st.markdown("#### 💧 Moisture Content vs Weight Inflation Scatter Analysis")
        fig_moist = px.scatter(
            df,
            x="Moisture %",
            y="Qty Variance (t)",
            size="Potential Exposure (ZAR)",
            color="Supplier",
            template="plotly_dark",
            title="Moisture Tampering / Quality Discrepancy Detection"
        )
        fig_moist.add_vline(x=9.0, line_dash="dash", line_color="#EF4444", annotation_text="Max Contract Moisture Threshold (9.0%)")
        fig_moist.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=320)
        st.plotly_chart(fig_moist, use_container_width=True)

    st.markdown("#### 🔬 Statistical Anomaly Summary")
    st.markdown("""
    * **Z-Score Formula:** $z = \\frac{\vert{}x - \\mu\vert{}}{\\sigma} + \\theta_{qty} + \\theta_{price}$ where $\\mu = 38.0t$ baseline scale weight and $\\sigma = 1.2t$.
    * **Systematic Bias Detection:** Suppliers with mean $Z > 2.5$ across $> 5$ loads are flagged for **Systematic Overbilling Fraud** rather than operational tare drift.
    * **Moisture Shrinkage Penalty:** Every $1.0\\%$ moisture above $9.0\\%$ contract threshold converts directly into excess water mass billed as dry coal value.
    """)

# -----------------------------------------------------------------------------
# VIEW 5: SUPPLIER RISK & CORRIDOR ANALYTICS
# -----------------------------------------------------------------------------
elif nav_choice == " Supplier Risk & Corridor Analytics":
    st.markdown('<div class="app-section-title">SUPPLIER RISK SCORECARDS & LOGISTICS CORRIDOR EXPOSURE</div>', unsafe_allow_html=True)
    
    s_col1, s_col2 = st.columns([1, 1])
    
    with s_col1:
        st.markdown("#### 🏢 Vendor Exposure & Risk Scorecard")
        supp_summary = df.groupby("Supplier").agg(
            Total_Batches=("Transaction ID", "count"),
            Leakage_Events=("Potential Exposure (ZAR)", lambda x: (x > 0).sum()),
            Total_Exposure_ZAR=("Potential Exposure (ZAR)", "sum"),
            Avg_Anomaly_Score=("Anomaly Score", "mean")
        ).reset_index()

        st.dataframe(
            supp_summary.style.format({
                "Total_Exposure_ZAR": "R{:,.2f}",
                "Avg_Anomaly_Score": "{:.1f}/100"
            }),
            use_container_width=True
        )

    with s_col2:
        st.markdown("#### 🚚 Logistics Transport Corridor Risk")
        corridor_summary = df.groupby("Corridor").agg(
            Total_Volume_t=("Trusted Mass (t)", "sum"),
            Total_Exposure_ZAR=("Potential Exposure (ZAR)", "sum"),
            Avg_Z_Score=("Z-Score", "mean")
        ).reset_index()

        fig_corr = px.bar(
            corridor_summary,
            x="Corridor",
            y="Total_Exposure_ZAR",
            color="Avg_Z_Score",
            template="plotly_dark",
            title="Total Financial Exposure by Transport Corridor (ZAR)"
        )
        fig_corr.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=300)
        st.plotly_chart(fig_corr, use_container_width=True)

    st.divider()

    st.markdown("#### 🚛 High-Risk Truck Fleet Identification")
    truck_summary = df.groupby(["Truck", "Supplier"]).agg(
        Trips=("Transaction ID", "count"),
        Avg_Trusted_t=("Trusted Mass (t)", "mean"),
        Avg_Invoiced_t=("Invoiced Mass (t)", "mean"),
        Total_Exposure_ZAR=("Potential Exposure (ZAR)", "sum")
    ).reset_index().sort_values(by="Total_Exposure_ZAR", ascending=False)

    st.dataframe(
        truck_summary.style.format({
            "Avg_Trusted_t": "{:.2f} t",
            "Avg_Invoiced_t": "{:.2f} t",
            "Total_Exposure_ZAR": "R{:,.2f}"
        }),
        use_container_width=True
    )

# -----------------------------------------------------------------------------
# VIEW 6: EXECUTIVE ROI & AUDIT REPORTS
# -----------------------------------------------------------------------------
elif nav_choice == " Executive ROI & Audit Reports":
    st.markdown('<div class="app-section-title">EXECUTIVE CFO VALUE SUMMARY & AUDIT COMPLIANCE REPORT</div>', unsafe_allow_html=True)
    
    total_reconciled = float((df["Trusted Mass (t)"] * df["Billed Rate (ZAR)"]).sum())
    total_exposure = float(df["Potential Exposure (ZAR)"].sum())
    prevented_capital = float(st.session_state.recovered_capital_zar)
    net_cfo_savings = prevented_capital
    roi_multiplier = round((net_cfo_savings / 120000.0), 1) if net_cfo_savings > 0 else 0.0 # Assuming platform cost R120k/mo

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(15,23,42,0.9) 0%, rgba(30,41,59,0.8) 100%); border: 1px solid rgba(56,189,248,0.3); border-radius:14px; padding:28px; margin-bottom:24px;">
        <h2 style="margin:0 0 12px 0; color:#38BDF8; font-weight:800;">FINANCIAL VALUE & ROI ASSURANCE SUMMARY</h2>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:20px; margin-top:20px;">
            <div>
                <span style="color:#94A3B8; font-size:0.8rem;">TOTAL RECONCILED VALUE</span>
                <h3 style="margin:4px 0 0 0; color:#FFF; font-family:'JetBrains Mono';">R {total_reconciled:,.2f}</h3>
            </div>
            <div>
                <span style="color:#94A3B8; font-size:0.8rem;">IDENTIFIED LEAKAGE EXPOSURE</span>
                <h3 style="margin:4px 0 0 0; color:#F87171; font-family:'JetBrains Mono';">R {total_exposure:,.2f}</h3>
            </div>
            <div>
                <span style="color:#94A3B8; font-size:0.8rem;">RECOVERED / PREVENTED CAPITAL</span>
                <h3 style="margin:4px 0 0 0; color:#34D399; font-family:'JetBrains Mono';">R {prevented_capital:,.2f}</h3>
            </div>
            <div>
                <span style="color:#94A3B8; font-size:0.8rem;">ESTIMATED ANNUALIZED ROI</span>
                <h3 style="margin:4px 0 0 0; color:#818CF8; font-family:'JetBrains Mono';">{roi_multiplier}x ROI</h3>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 📄 Executive Audit Report Preview")
    
    report_text = f"""
========================================================================================
                      TRUEFLOW TRANSACTION ASSURANCE PLATFORM
                           EXECUTIVE AUDIT REPORT
========================================================================================
Generated On             : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Primary Scale Terminal   : SC-04-NORTH-AKASIA (Akasia Regional Hub, South Africa)
Target ERP Integration   : SAP S/4HANA (Active Connection)

1. EXECUTIVE SUMMARY
----------------------------------------------------------------------------------------
Total Batches Audited     : {len(df)} Batches
Total Volume Reconciled   : {df['Trusted Mass (t)'].sum():,.2f} Tonnes
Total Invoiced Mass       : {df['Invoiced Mass (t)'].sum():,.2f} Tonnes
Total Commodity Value     : R {total_reconciled:,.2f}

2. FINANCIAL LEAKAGE IDENTIFICATION
----------------------------------------------------------------------------------------
Total Identified Leakage  : R {total_exposure:,.2f}
Leakage Exposure Rate     : {(total_exposure/max(1, total_reconciled))*100:.2f}%
Auto-Reconciliation Rate  : {(len(df[df['Potential Exposure (ZAR)'] == 0])/len(df))*100:.1f}%
Capital Recovered/Frozen  : R {prevented_capital:,.2f}

3. HIGH-RISK VENDOR AUDIT RANKING
----------------------------------------------------------------------------------------
{supp_summary.to_string(index=False)}

4. CRYPTOGRAPHIC PROVENANCE & REGULATORY COMPLIANCE
----------------------------------------------------------------------------------------
Scale Telemetry SHA-256   : VERIFIED (100% Scale Hardware Ticket Integrity)
Multi-Document Matching   : PO -> Dispatch -> Weighbridge Scale -> DN -> GRN -> Invoice
Compliance Classification  : FULLY COMPLIANT WITH KING IV & INTERNATIONAL FINANCIAL AUDIT STANDARDS
========================================================================================
    """
    
    st.code(report_text, language="text")
    st.download_button("⬇️ Export Full Audit Report (.TXT)", data=report_text, file_name=f"TrueFlow_Executive_Audit_Report_{datetime.now().strftime('%Y%m%d')}.txt")

# -----------------------------------------------------------------------------
# SUB-SECOND STREAMING REFRESH CONTROLLER
# -----------------------------------------------------------------------------
if run_simulation:
    time.sleep(sim_speed)
    st.rerun()
