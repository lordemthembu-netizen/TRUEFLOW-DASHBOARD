import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import os
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & ENTERPRISE DESIGN SYSTEM
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="TrueFlow // Transaction Assurance Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Institutional Dark CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #0B1120;
        color: #F8FAFC;
    }

    /* Header Container */
    .brand-header {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.7) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        border-radius: 12px;
        padding: 20px 28px;
        margin-bottom: 24px;
    }

    /* KPI Cards */
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    div[data-testid="stMetric"]:hover {
        border-color: rgba(56, 189, 248, 0.35);
    }

    div[data-testid="stMetric"] label {
        color: #94A3B8 !important;
        font-size: 0.78rem !important;
        font-weight: 500;
        letter-spacing: 0.5px;
    }

    div[data-testid="stMetricValue"] {
        color: #38BDF8 !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.55rem !important;
        font-weight: 700;
    }

    /* Section Subheaders */
    .app-section-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: 0.5px;
        margin-top: 24px;
        margin-bottom: 16px;
        border-left: 4px solid #0284C7;
        padding-left: 12px;
    }

    /* Trust Badges */
    .badge-trusted {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.78rem;
    }
    
    .badge-reported {
        background-color: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.78rem;
    }

    .badge-financial {
        background-color: rgba(239, 68, 68, 0.15);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.78rem;
    }

    /* Lineage Flow Cards */
    .lineage-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 12px 16px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SEED DATA & SYNTHETIC MULTI-DOCUMENT TRANSACTION ENGINE
# -----------------------------------------------------------------------------
SUPPLIERS = ["ABC Coal Pty Ltd", "Mpuma Haulage Logistics", "North Ridge Minerals", "Vanguard Mining Ltd"]
TRUCKS = ["MP-1234-GP", "MP-4421-GP", "NW-8812-GP", "KZN-9012-GP", "LIM-3321-GP"]
MATERIALS = ["RB1 Thermal Coal", "RB2 Export Coal", "Coking Coal", "Run of Mine (ROM)"]

if 'transactions' not in st.session_state:
    st.session_state.transactions = []
    st.session_state.txn_counter = 1840
    st.session_state.investigation_queue = {}

def generate_synthetic_transaction():
    st.session_state.txn_counter += 1
    txn_id = f"TXN-2026-{st.session_state.txn_counter:06d}"
    
    supplier = str(np.random.choice(SUPPLIERS, p=[0.40, 0.30, 0.15, 0.15]))
    truck = str(np.random.choice(TRUCKS))
    material = str(np.random.choice(MATERIALS))
    po_number = f"PO-{np.random.randint(10000, 99999)}"
    approved_rate = 1850.00
    
    # 1. PO & Dispatch
    po_quantity = 40.00
    
    # 2. Scale Ground Truth (Trusted Physical Measurement)
    weighbridge_net = round(float(np.random.uniform(36.5, 38.8)), 2)
    gross_mass = round(weighbridge_net + 21.20, 2)
    tare_mass = 21.20
    
    # 3. Reported Quantities (Delivery Note, GRN, Invoice)
    rand_type = np.random.random()
    
    if rand_type < 0.70:
        # Clean Transaction
        dn_quantity = weighbridge_net
        grn_quantity = weighbridge_net
        inv_quantity = weighbridge_net
        inv_rate = approved_rate
        evidence_present = 7
        anomaly_desc = "Clean Flow"
    elif rand_type < 0.88:
        # Quantity Overbill Variance
        overbill_t = round(float(np.random.uniform(1.2, 3.5)), 2)
        dn_quantity = round(weighbridge_net + overbill_t, 2)
        grn_quantity = dn_quantity
        inv_quantity = dn_quantity
        inv_rate = approved_rate
        evidence_present = 7
        anomaly_desc = "Quantity Overbill"
    else:
        # Price Creep + Missing Evidence
        dn_quantity = weighbridge_net
        grn_quantity = weighbridge_net
        inv_quantity = weighbridge_net
        inv_rate = approved_rate + float(np.random.choice([120.0, 185.0, 250.0]))
        evidence_present = 6 # e.g. Missing Delivery Note Scan
        anomaly_desc = "Price Variance / Creep"

    # Quantitative Metrics
    qty_variance_t = round(inv_quantity - weighbridge_net, 2)
    qty_variance_pct = round((qty_variance_t / weighbridge_net) * 100, 2) if weighbridge_net > 0 else 0.0
    price_variance = round(inv_rate - approved_rate, 2)
    
    quantity_exposure = round(qty_variance_t * approved_rate, 2)
    price_exposure = round(price_variance * inv_quantity, 2)
    total_exposure = round(quantity_exposure + price_exposure, 2)
    
    # Statistical Anomaly Score (0 - 100)
    base_score = 10
    if qty_variance_pct > 0:
        base_score += min(60, int(qty_variance_pct * 12))
    if price_variance > 0:
        base_score += 25
    if evidence_present < 7:
        base_score += 15
    anomaly_score = min(99, base_score)
    
    priority = "LOW"
    if anomaly_score > 75:
        priority = "CRITICAL"
    elif anomaly_score > 45:
        priority = "HIGH"
    elif anomaly_score > 25:
        priority = "MEDIUM"

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    txn = {
        "transaction_id": txn_id,
        "timestamp": now_str,
        "supplier": supplier,
        "truck_registration": truck,
        "material": material,
        "po_number": po_number,
        "po_quantity_t": po_quantity,
        "approved_rate_zar": approved_rate,
        "weighbridge": {
            "gross_t": gross_mass,
            "tare_t": tare_mass,
            "net_t": weighbridge_net,
            "ticket_id": f"WB-{np.random.randint(70000, 99999)}"
        },
        "delivery_note": {
            "quantity_t": dn_quantity,
            "document_id": f"DN-{np.random.randint(50000, 89999)}"
        },
        "grn": {
            "quantity_t": grn_quantity,
            "grn_id": f"GRN-{np.random.randint(90000, 99999)}"
        },
        "invoice": {
            "quantity_t": inv_quantity,
            "rate_zar": inv_rate,
            "invoice_number": f"INV-{np.random.randint(80000, 89999)}",
            "amount_zar": round(inv_quantity * inv_rate, 2)
        },
        "payment": {
            "amount_zar": round(inv_quantity * inv_rate, 2),
            "payment_reference": f"PAY-{np.random.randint(30000, 39999)}"
        },
        "metrics": {
            "trusted_quantity_t": weighbridge_net,
            "claimed_quantity_t": inv_quantity,
            "qty_variance_t": qty_variance_t,
            "qty_variance_pct": qty_variance_pct,
            "price_variance_zar": price_variance,
            "potential_exposure_zar": total_exposure,
            "evidence_completeness_pct": round((evidence_present / 7) * 100, 1),
            "anomaly_score": anomaly_score,
            "anomaly_type": anomaly_desc,
            "priority": priority,
            "investigation_status": "OPEN" if total_exposure > 0 else "CLOSED_CLEAN"
        }
    }
    return txn

# Pre-populate session buffer if empty
if not st.session_state.transactions:
    for _ in range(35):
        st.session_state.transactions.append(generate_synthetic_transaction())

# -----------------------------------------------------------------------------
# 3. SIDEBAR NAVIGATION & CONTROLS
# -----------------------------------------------------------------------------
st.sidebar.markdown("## 🛡️ TRUEFLOW")
st.sidebar.caption("Transaction Assurance Platform v2.4")

nav_choice = st.sidebar.radio(
    "Navigation",
    [
        " Executive Overview",
        " Transaction Control Room",
        " Supplier Risk Intelligence",
        " Vehicle Fleet Analytics",
        " Investigation Queue",
        " System Architecture & Provenance"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("### ⚡ Live Stream Controls")
run_simulation = st.sidebar.toggle("Enable Live Ingestion Stream", value=False)
sim_speed = st.sidebar.slider("Stream Interval (sec)", 1.0, 5.0, 2.0)

if run_simulation:
    st.session_state.transactions.insert(0, generate_synthetic_transaction())
    if len(st.session_state.transactions) > 100:
        st.session_state.transactions.pop()

st.sidebar.divider()
st.sidebar.caption("Deterministic Rule Engine: **Active**")
st.sidebar.caption("Statistical Baseline: **4,821 Historical Batches**")

# Prepare Master DataFrame
flat_data = []
for t in st.session_state.transactions:
    flat_data.append({
        "Transaction ID": t["transaction_id"],
        "Timestamp": t["timestamp"],
        "Supplier": t["supplier"],
        "Truck": t["truck_registration"],
        "Material": t["material"],
        "Trusted Mass (t)": t["weighbridge"]["net_t"],
        "Invoiced Mass (t)": t["invoice"]["quantity_t"],
        "Billed Rate (ZAR)": t["invoice"]["rate_zar"],
        "Qty Variance (t)": t["metrics"]["qty_variance_t"],
        "Potential Exposure (ZAR)": t["metrics"]["potential_exposure_zar"],
        "Anomaly Score": t["metrics"]["anomaly_score"],
        "Priority": t["metrics"]["priority"],
        "Status": t["metrics"]["investigation_status"],
        "Anomaly Type": t["metrics"]["anomaly_type"],
        "Evidence %": t["metrics"]["evidence_completeness_pct"]
    })

df = pd.DataFrame(flat_data)

# -----------------------------------------------------------------------------
# 4. BRANDED ENTERPRISE HEADER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="brand-header">
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
        <div>
            <h1 style="margin:0; font-weight:800; font-size:1.8rem; color:#F8FAFC; letter-spacing:1px;">
                TRUE<span style="color:#38BDF8;">FLOW</span> // TRANSACTION ASSURANCE
            </h1>
            <p style="margin:4px 0 0 0; color:#94A3B8; font-size:0.85rem;">
                Autonomous Reconciler of Physical Ground Truth vs. Financial Claims
            </p>
        </div>
        <div style="text-align:right;">
            <span class="badge-trusted">SYSTEM ONLINE</span>
            <p style="margin:4px 0 0 0; color:#64748B; font-size:0.75rem; font-family:'JetBrains Mono';">
                LOCATION: AKASIA, SOUTH AFRICA
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# VIEW 1: EXECUTIVE OVERVIEW
# -----------------------------------------------------------------------------
if nav_choice == " Executive Overview":
    
    total_reconciled_zar = (df["Trusted Mass (t)"] * 1850.0).sum()
    total_exposure_zar = df["Potential Exposure (ZAR)"].sum()
    flagged_txns = len(df[df["Potential Exposure (ZAR)"] > 0])
    avg_anomaly = df["Anomaly Score"].mean()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Reconciled Value", f"R {total_reconciled_zar:,.2f}")
    m2.metric("Total Potential Exposure", f"R {total_exposure_zar:,.2f}", delta=f"{(total_exposure_zar/max(1, total_reconciled_zar))*100:.2f}% Risk Rate", delta_color="inverse")
    m3.metric("Flagged Exceptions", f"{flagged_txns} / {len(df)}", delta=f"{priority_high := len(df[df['Priority'] == 'CRITICAL'])} Critical Priority", delta_color="inverse")
    m4.metric("Avg Fleet Anomaly Index", f"{avg_anomaly:.1f} / 100")

    st.markdown('<div class="app-section-title">EXPOSURE TREND & ANOMALY DISTRIBUTION</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        fig_trend = px.bar(
            df[::-1],
            x="Transaction ID",
            y="Potential Exposure (ZAR)",
            color="Priority",
            color_discrete_map={"LOW": "#10B981", "MEDIUM": "#F59E0B", "HIGH": "#F97316", "CRITICAL": "#EF4444"},
            template="plotly_dark",
            title="Potential Exposure per Ingested Batch (ZAR)"
        )
        fig_trend.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=320)
        st.plotly_chart(fig_trend, use_container_width=True)

    with c2:
        fig_pie = px.pie(
            df,
            names="Anomaly Type",
            values="Potential Exposure (ZAR)",
            hole=0.45,
            template="plotly_dark",
            color_discrete_sequence=["#10B981", "#EF4444", "#F59E0B"],
            title="Exposure by Exception Category"
        )
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=320)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown('<div class="app-section-title">RECENT INGESTED TRANSACTIONS LEDGER</div>', unsafe_allow_html=True)
    
    def highlight_rows(row):
        if row["Priority"] == "CRITICAL":
            return ['background-color: rgba(239, 68, 68, 0.2); color: #FCA5A5'] * len(row)
        elif row["Priority"] == "HIGH":
            return ['background-color: rgba(249, 115, 22, 0.15); color: #FDBA74'] * len(row)
        return ['background-color: rgba(15, 23, 42, 0.4); color: #E2E8F0'] * len(row)

    formatted_df = df.style.apply(highlight_rows, axis=1)\
        .format({
            "Trusted Mass (t)": "{:.2f}",
            "Invoiced Mass (t)": "{:.2f}",
            "Billed Rate (ZAR)": "R{:,.2f}",
            "Qty Variance (t)": "{:+.2f}",
            "Potential Exposure (ZAR)": "R{:,.2f}",
            "Evidence %": "{:.0f}%"
        })
    
    st.dataframe(formatted_df, use_container_width=True, height=350)

# -----------------------------------------------------------------------------
# VIEW 2: TRANSACTION CONTROL ROOM
# -----------------------------------------------------------------------------
elif nav_choice == " Transaction Control Room":
    st.markdown('<div class="app-section-title">TRANSACTION CONTROL ROOM</div>', unsafe_allow_html=True)
    
    selected_txn_id = st.selectbox("Select Transaction ID for Reconstruction:", df["Transaction ID"].tolist())
    
    # Locate transaction record
    txn = next((t for t in st.session_state.transactions if t["transaction_id"] == selected_txn_id), None)
    
    if txn:
        m = txn["metrics"]
        
        # Upper Details Summary
        info_col1, info_col2, info_col3, info_col4 = st.columns(4)
        info_col1.markdown(f"**Supplier:** {txn['supplier']}")
        info_col2.markdown(f"**Truck Reg:** `{txn['truck_registration']}`")
        info_col3.markdown(f"**PO Number:** `{txn['po_number']}`")
        info_col4.markdown(f"**Material:** {txn['material']}")
        
        st.divider()
        
        # 8-Stage Lineage Chain Display
        st.markdown("#### 🔗 Reconstructed Transaction Lineage (8 Representations)")
        
        l1, l2, l3, l4, l5, l6, l7, l8 = st.columns(8)
        
        with l1:
            st.markdown("""<div class="lineage-card">
            <span class="badge-reported">PO</span><br><br>
            <b>40.00 t</b><br>
            <small>R1,850/t</small>
            </div>""", unsafe_allow_html=True)
            
        with l2:
            st.markdown("""<div class="lineage-card">
            <span class="badge-reported">DISPATCH</span><br><br>
            <b>40.00 t</b><br>
            <small>Manifest</small>
            </div>""", unsafe_allow_html=True)

        with l3:
            st.markdown(f"""<div class="lineage-card" style="border:1px solid #10B981;">
            <span class="badge-trusted">WEIGHBRIDGE</span><br><br>
            <b style="color:#34D399;">{txn['weighbridge']['net_t']:.2f} t</b><br>
            <small>Ground Truth</small>
            </div>""", unsafe_allow_html=True)

        with l4:
            st.markdown(f"""<div class="lineage-card">
            <span class="badge-reported">DELIVERY NOTE</span><br><br>
            <b>{txn['delivery_note']['quantity_t']:.2f} t</b><br>
            <small>Paper Claim</small>
            </div>""", unsafe_allow_html=True)

        with l5:
            st.markdown(f"""<div class="lineage-card">
            <span class="badge-reported">GRN</span><br><br>
            <b>{txn['grn']['quantity_t']:.2f} t</b><br>
            <small>Receipt</small>
            </div>""", unsafe_allow_html=True)

        with l6:
            st.markdown(f"""<div class="lineage-card">
            <span class="badge-financial">INVOICE</span><br><br>
            <b>{txn['invoice']['quantity_t']:.2f} t</b><br>
            <small>R{txn['invoice']['rate_zar']:,.0f}/t</small>
            </div>""", unsafe_allow_html=True)

        with l7:
            st.markdown(f"""<div class="lineage-card">
            <span class="badge-financial">PAYMENT</span><br><br>
            <b>R{txn['payment']['amount_zar']:,.0f}</b><br>
            <small>Claimed</small>
            </div>""", unsafe_allow_html=True)

        with l8:
            status_color = "#34D399" if m["potential_exposure_zar"] == 0 else "#F87171"
            st.markdown(f"""<div class="lineage-card" style="border:1px solid {status_color};">
            <span style="color:{status_color}; font-weight:700; font-size:0.75rem;">TRUEFLOW</span><br><br>
            <b style="color:{status_color};">R{m['potential_exposure_zar']:,.0f}</b><br>
            <small>Exposure</small>
            </div>""", unsafe_allow_html=True)

        st.divider()

        # Ground Truth vs Financial Claim Breakdown
        r1, r2 = st.columns([1, 1])
        
        with r1:
            st.markdown("#### 📊 Ground Truth vs. Claim Analysis")
            
            comp_table = [
                {"Source": "Scale Hardware (Weighbridge Net)", "Quantity": f"{txn['weighbridge']['net_t']:.2f} t", "Trust Classification": "🟢 Trusted Physical Ground Truth"},
                {"Source": "Delivery Note Claim", "Quantity": f"{txn['delivery_note']['quantity_t']:.2f} t", "Trust Classification": "🟡 Reported Vendor Document"},
                {"Source": "Goods Received Note (GRN)", "Quantity": f"{txn['grn']['quantity_t']:.2f} t", "Trust Classification": "🟡 Reported Internal Document"},
                {"Source": "Supplier Invoice", "Quantity": f"{txn['invoice']['quantity_t']:.2f} t", "Trust Classification": "🔴 Financial Claim"},
            ]
            st.table(pd.DataFrame(comp_table))

        with r2:
            st.markdown("#### 🚨 Exception Findings")
            if m["potential_exposure_zar"] > 0:
                st.error(f"""
                **QUANTITY EXCEPTION DETECTED**
                * **Trusted Measurement:** {m['trusted_quantity_t']:.2f} t
                * **Invoiced Quantity:** {m['claimed_quantity_t']:.2f} t
                * **Variance:** +{m['qty_variance_t']:.2f} t ({m['qty_variance_pct']}%)
                * **Price Rate Variance:** R{m['price_variance_zar']:,.2f} / t
                
                **Total Calculated Potential Exposure: R {m['potential_exposure_zar']:,.2f}**
                """)
            else:
                st.success("✅ **TRANSACTION FULLY RECONCILED**\nPhysical weighbridge measurement matches invoiced claims within standard zero-variance tolerance.")

            st.markdown(f"**Anomaly Score:** `{m['anomaly_score']} / 100` | **Evidence Completeness:** `{m['evidence_completeness_pct']}%`")

# -----------------------------------------------------------------------------
# VIEW 3: SUPPLIER RISK INTELLIGENCE
# -----------------------------------------------------------------------------
elif nav_choice == " Supplier Risk Intelligence":
    st.markdown('<div class="app-section-title">SUPPLIER RISK & EXPOSURE PROFILES</div>', unsafe_allow_html=True)
    
    supp_summary = df.groupby("Supplier").agg(
        Total_Txns=("Transaction ID", "count"),
        Flagged_Exceptions=("Potential Exposure (ZAR)", lambda x: (x > 0).sum()),
        Total_Exposure_ZAR=("Potential Exposure (ZAR)", "sum"),
        Avg_Anomaly_Score=("Anomaly Score", "mean")
    ).reset_index()

    st.dataframe(supp_summary.style.format({
        "Total_Exposure_ZAR": "R{:,.2f}",
        "Avg_Anomaly_Score": "{:.1f}"
    }), use_container_width=True)

    st.divider()
    
    selected_supp = st.selectbox("Select Supplier to Audit:", SUPPLIERS)
    supp_df = df[df["Supplier"] == selected_supp]
    
    s_col1, s_col2 = st.columns([1, 1])
    with s_col1:
        fig_supp = px.histogram(
            supp_df,
            x="Qty Variance (t)",
            nbins=15,
            template="plotly_dark",
            title=f"Quantity Variance Distribution: {selected_supp}"
        )
        st.plotly_chart(fig_supp, use_container_width=True)
        
    with s_col2:
        st.markdown(f"#### Risk Profile: {selected_supp}")
        st.write(f"* **Total Batches Audited:** {len(supp_df)}")
        st.write(f"* **Total Exposure Identified:** R {supp_df['Potential Exposure (ZAR)'].sum():,.2f}")
        st.write(f"* **Critical Exceptions:** {len(supp_df[supp_df['Priority'] == 'CRITICAL'])}")
        st.write(f"* **Average Evidence Score:** {supp_df['Evidence %'].mean():.1f}%")

# -----------------------------------------------------------------------------
# VIEW 4: VEHICLE FLEET ANALYTICS
# -----------------------------------------------------------------------------
elif nav_choice == " Vehicle Fleet Analytics":
    st.markdown('<div class="app-section-title">TRUCK FLEET ANOMALY INTELLIGENCE</div>', unsafe_allow_html=True)
    
    truck_summary = df.groupby("Truck").agg(
        Total_Trips=("Transaction ID", "count"),
        Avg_Net_Mass_t=("Trusted Mass (t)", "mean"),
        Total_Exposure_ZAR=("Potential Exposure (ZAR)", "sum"),
        Exceptions=("Potential Exposure (ZAR)", lambda x: (x > 0).sum())
    ).reset_index()

    st.dataframe(truck_summary.style.format({
        "Avg_Net_Mass_t": "{:.2f} t",
        "Total_Exposure_ZAR": "R{:,.2f}"
    }), use_container_width=True)

    fig_truck = px.scatter(
        df,
        x="Trusted Mass (t)",
        y="Invoiced Mass (t)",
        color="Truck",
        size="Anomaly Score",
        template="plotly_dark",
        title="Truck Load Telemetry: Invoiced vs. Ground Truth Net Weight"
    )
    st.plotly_chart(fig_truck, use_container_width=True)

# -----------------------------------------------------------------------------
# VIEW 5: INVESTIGATION QUEUE
# -----------------------------------------------------------------------------
elif nav_choice == " Investigation Queue":
    st.markdown('<div class="app-section-title">HUMAN INVESTIGATION & AUDIT WORKFLOW</div>', unsafe_allow_html=True)
    
    open_exceptions = df[df["Potential Exposure (ZAR)"] > 0]
    
    if not open_exceptions.empty:
        st.dataframe(open_exceptions[["Transaction ID", "Supplier", "Truck", "Potential Exposure (ZAR)", "Priority", "Anomaly Type"]], use_container_width=True)
        
        st.divider()
        st.markdown("### 📝 Resolve or Escalate Exception")
        target_id = st.selectbox("Select Exception to Review:", open_exceptions["Transaction ID"].tolist())
        
        c_act1, c_act2, c_act3 = st.columns(3)
        with c_act1:
            if st.button("🔴 Escalate to Forensic Audit"):
                st.warning(f"{target_id} escalated to Internal Audit Lead.")
        with c_act2:
            if st.button("🟠 Issue Supplier Credit Note Request"):
                st.info(f"Credit Note request for {target_id} dispatched to ERP.")
        with c_act3:
            if st.button("🟢 Resolve - Operational Variance Explained"):
                st.success(f"{target_id} status updated to RESOLVED.")
    else:
        st.success("No active open exceptions in the queue.")

# -----------------------------------------------------------------------------
# VIEW 6: SYSTEM ARCHITECTURE & PROVENANCE
# -----------------------------------------------------------------------------
elif nav_choice == " System Architecture & Provenance":
    st.markdown('<div class="app-section-title">TRUEFLOW END-TO-END ENGINE ARCHITECTURE</div>', unsafe_allow_html=True)
    
    st.code("""
  +-----------------------------------------------------------------------------------+
  |                                DOCUMENT & DATA INGESTION                          |
  |  [Digital Weighbridge Scales]   [ERP / SAP Invoices]   [OCR Delivery Notes / GRNs] |
  +-----------------------------------------+-----------------------------------------+
                                            |
                                            v
  +-----------------------------------------------------------------------------------+
  |                              DATA NORMALISATION ENGINE                            |
  |    Standardises units (tonnes), currency (ZAR), timestamps, and vendor metadata   |
  +-----------------------------------------+-----------------------------------------+
                                            |
                                            v
  +-----------------------------------------------------------------------------------+
  |                           8-STAGE TRANSACTION GRAPH RECONSTRUCTION                |
  |    PO --> Dispatch --> Truck --> Weighbridge --> DN --> GRN --> Invoice --> Pay   |
  +-----------------------------------------+-----------------------------------------+
                                            |
                                            v
  +-----------------------------------------+-----------------------------------------+
  |    DETERMINISTIC VARIANCE ENGINE        |       STATISTICAL ANOMALY ENGINE        |
  |    Calculates exact Qty & Price         |       Calculates Z-score deviation      |
  |    Exposure (ZAR)                       |       against 4,000+ historical loads   |
  +-----------------------------------------+-----------------------------------------+
                                            |
                                            v
  +-----------------------------------------------------------------------------------+
  |                              RISK ENGINE & CONTROL ROOM                           |
  |    Prioritises exceptions, assigns anomaly scores, triggers investigation queues |
  +-----------------------------------------------------------------------------------+
    """, language="text")

# -----------------------------------------------------------------------------
# CONTINUOUS RERUN FOR LIVE STREAMING MODE
# -----------------------------------------------------------------------------
if run_simulation:
    time.sleep(sim_speed)
    st.rerun()
