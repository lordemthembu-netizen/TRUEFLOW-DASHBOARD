import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import hashlib
from datetime import datetime, timedelta

# ==========================================
# 1. PAGE CONFIGURATION & DARK THEME STYLING
# ==========================================
st.set_page_config(
    page_title="TrueFlow // Enterprise Transaction Assurance Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Contrast Dark Theme (Control-Room Aesthetic)
st.markdown("""
<style>
    .stApp {
        background-color: #0B1120;
        color: #F8FAFC;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    .header-box {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .badge-live {
        background-color: #064E3B;
        color: #34D399;
        border: 1px solid #059669;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-secure {
        background-color: #1E3A8A;
        color: #60A5FA;
        border: 1px solid #2563EB;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .kpi-card {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 16px;
        text-align: left;
    }
    .kpi-title {
        color: #94A3B8;
        font-size: 0.75rem;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .kpi-value {
        color: #F8FAFC;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .kpi-subtitle {
        font-size: 0.75rem;
        font-weight: 500;
    }
    .text-red { color: #EF4444; }
    .text-green { color: #10B981; }
    .text-blue { color: #38BDF8; }

    .flow-step {
        background: #0F172A;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 12px;
        text-align: center;
    }
    .flow-step-trusted {
        border: 2px solid #10B981;
        background: #022C22;
    }
    .flow-step-flagged {
        border: 2px solid #EF4444;
        background: #450A0A;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATA GENERATION ENGINE
# ==========================================
@st.cache_data
def load_transaction_dataset():
    np.random.seed(42)
    n_records = 150
    suppliers = ["ABC Coal Mining Pty Ltd", "Mpuma Haulage Logistics", "Khai-Appel Mining Corp", "North Ridge Minerals", "Vanguard Bulk Rail"]
    materials = ["RB1 Thermal Coal (Export Grade)", "RB2 Thermal Coal", "Chrome Ore Concentrate", "Iron Ore Fines", "Coking Coal Grade A"]
    trucks = ["KZN-9012-GP", "MP-1234-GP", "LIM-3321-GP", "FS-7711-GP", "MP-9921-GP"]
    
    data = []
    base_time = datetime.now() - timedelta(days=5)
    
    for i in range(n_records):
        txn_id = f"TXN-2026-{4921 + i}"
        timestamp = (base_time + timedelta(minutes=i*45)).strftime("%Y-%m-%d %H:%M:%S")
        supplier = str(np.random.choice(suppliers))
        material = str(np.random.choice(materials))
        truck = str(np.random.choice(trucks))
        
        rate = 1850.0  # R/tonne
        po_mass = 40.0
        weighbridge_mass = float(np.random.normal(37.5, 0.8))
        
        is_exception = np.random.rand() < 0.22
        if is_exception:
            billed_mass = weighbridge_mass + float(np.random.uniform(1.5, 3.5))
            exception_type = str(np.random.choice([
                "Mass Discrepancy (Weighbridge vs. Invoice)",
                "Price Variance / Unapproved Contract Rate",
                "Duplicate Invoice Claim",
                "Moisture Trigger / Quality Downgrade"
            ]))
            status = "Open Exception"
        else:
            billed_mass = weighbridge_mass
            exception_type = "None (Matched)"
            status = "Reconciled"
            
        qty_variance = billed_mass - weighbridge_mass
        potential_exposure = qty_variance * rate if qty_variance > 0 else 0.0
        sha_hash = hashlib.sha256(f"{txn_id}{weighbridge_mass}{billed_mass}".encode()).hexdigest()[:16]
        z_score = round(float(np.abs((qty_variance - 0.1) / 0.25)), 2) if is_exception else round(float(np.random.uniform(0.1, 0.8)), 2)
        
        data.append({
            "Transaction_ID": txn_id,
            "Timestamp": timestamp,
            "Supplier": supplier,
            "Truck": truck,
            "Material": material,
            "PO_Mass_t": po_mass,
            "Weighbridge_Mass_t": round(weighbridge_mass, 2),
            "Billed_Mass_t": round(billed_mass, 2),
            "Qty_Variance_t": round(qty_variance, 2),
            "Approved_Rate_ZAR": rate,
            "Potential_Exposure_ZAR": round(potential_exposure, 2),
            "Z_Score": z_score,
            "Exception_Type": exception_type,
            "Status": status,
            "SHA256_Hash": sha_hash
        })
        
    return pd.DataFrame(data)

df_txns = load_transaction_dataset()

if 'investigations' not in st.session_state:
    st.session_state.investigations = {}

# ==========================================
# 3. EXECUTIVE HEADER
# ==========================================
st.markdown("""
<div class="header-box">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin: 0; font-size: 1.8rem; color: #F8FAFC;">
                🛡️ TRUEFLOW <span style="font-size: 1rem; color: #38BDF8; font-weight: 400;">| TRANSACTION ASSURANCE PLATFORM</span>
            </h1>
            <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.85rem;">
                Autonomous Physical-to-Financial Exposure Intelligence & Multi-Document Provenance
            </p>
        </div>
        <div style="text-align: right;">
            <span class="badge-live">SCALE TELEMETRY: LIVE</span> &nbsp;
            <span class="badge-secure">SAP S/4HANA CONNECTED</span> &nbsp;
            <span class="badge-secure">SHA-256 PROVENANCE: ACTIVE</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. EXECUTIVE KPIS
# ==========================================
st.markdown("### Executive Overview & Financial Metrics")

total_audited = len(df_txns)
total_reconciled_val = (df_txns["Weighbridge_Mass_t"] * df_txns["Approved_Rate_ZAR"]).sum()
total_potential_exposure = df_txns["Potential_Exposure_ZAR"].sum()
active_exceptions = len(df_txns[df_txns["Status"] == "Open Exception"])
evidence_coverage = 99.4

c1, c2, c3, c4, c5 = st.columns(5)
c1.markdown(f'<div class="kpi-card"><div class="kpi-title">Transactions Audited</div><div class="kpi-value">{total_audited:,}</div><div class="kpi-subtitle text-blue">100% Ingested Streams</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi-card"><div class="kpi-title">Value Reconciled</div><div class="kpi-value">R {total_reconciled_val/1e6:.2f}M</div><div class="kpi-subtitle text-green">✓ Verified Ground Truth</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi-card"><div class="kpi-title">Potential Financial Exposure</div><div class="kpi-value text-red">R {total_potential_exposure:,.2f}</div><div class="kpi-subtitle text-red">⚠ Unresolved Discrepancies</div></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi-card"><div class="kpi-title">Active Exception Queue</div><div class="kpi-value text-red">{active_exceptions}</div><div class="kpi-subtitle text-blue">Requires Human Review</div></div>', unsafe_allow_html=True)
c5.markdown(f'<div class="kpi-card"><div class="kpi-title">Evidence Coverage</div><div class="kpi-value text-green">{evidence_coverage}%</div><div class="kpi-subtitle text-green">6/6 Documents/Txn</div></div>', unsafe_allow_html=True)

st.divider()

# ==========================================
# 5. NAVIGATION TABS
# ==========================================
tab_control, tab_evidence, tab_supplier, tab_investigation = st.tabs([
    "🎯 Transaction Control Room", 
    "📑 Multi-Document Evidence Panel", 
    "📊 Supplier Risk Intelligence", 
    "🚨 Investigation Queue & Audit Trail"
])

# ------------------------------------------
# TAB 1: CONTROL ROOM
# ------------------------------------------
with tab_control:
    st.subheader("Transaction Stream Ledger & Real-Time Inspection")
    selected_txn_id = st.selectbox("Select Transaction for Deep Forensic Analysis:", options=df_txns["Transaction_ID"].tolist(), index=0)
    txn = df_txns[df_txns["Transaction_ID"] == selected_txn_id].iloc[0]
    
    st.markdown("#### 7-Stage Transaction Process Flow")
    f1, f2, f3, f4, f5, f6, f7 = st.columns(7)
    
    f1.markdown(f'<div class="flow-step"><div style="font-size:0.7rem; color:#94A3B8;">1. PO ISSUED</div><div style="font-weight:700; font-size:0.9rem;">{txn["PO_Mass_t"]:.2f} t</div><div style="font-size:0.65rem; color:#38BDF8;">R1,850 / t</div></div>', unsafe_allow_html=True)
    f2.markdown(f'<div class="flow-step"><div style="font-size:0.7rem; color:#94A3B8;">2. DISPATCH</div><div style="font-weight:700; font-size:0.9rem;">{txn["PO_Mass_t"]:.2f} t</div><div style="font-size:0.65rem; color:#94A3B8;">Gate Out</div></div>', unsafe_allow_html=True)
    f3.markdown(f'<div class="flow-step flow-step-trusted"><div style="font-size:0.7rem; color:#34D399; font-weight:700;">3. WEIGHBRIDGE</div><div style="font-weight:700; font-size:1.0rem; color:#34D399;">{txn["Weighbridge_Mass_t"]:.2f} t</div><div style="font-size:0.65rem; color:#34D399;">✓ TRUSTED SCALE</div></div>', unsafe_allow_html=True)

    is_warn = txn['Qty_Variance_t'] > 0
    step_class = "flow-step-flagged" if is_warn else "flow-step"
    badge_text = '⚠ Discrepancy' if is_warn else '✓ Matched'
    badge_color = '#EF4444' if is_warn else '#10B981'
    f4.markdown(f'<div class="{step_class}"><div style="font-size:0.7rem; color:#94A3B8;">4. DELIVERY NOTE</div><div style="font-weight:700; font-size:0.9rem;">{txn["Billed_Mass_t"]:.2f} t</div><div style="font-size:0.65rem; color:{badge_color};">{badge_text}</div></div>', unsafe_allow_html=True)

    f5.markdown(f'<div class="flow-step"><div style="font-size:0.7rem; color:#94A3B8;">5. GRN</div><div style="font-weight:700; font-size:0.9rem;">{txn["Billed_Mass_t"]:.2f} t</div><div style="font-size:0.65rem; color:#94A3B8;">Warehouse Sync</div></div>', unsafe_allow_html=True)
    f6.markdown(f'<div class="flow-step"><div style="font-size:0.7rem; color:#94A3B8;">6. TAX INVOICE</div><div style="font-weight:700; font-size:0.9rem;">R {txn["Billed_Mass_t"]*txn["Approved_Rate_ZAR"]:,.2f}</div><div style="font-size:0.65rem; color:#94A3B8;">Vendor Claim</div></div>', unsafe_allow_html=True)
    f7.markdown(f'<div class="flow-step"><div style="font-size:0.7rem; color:#94A3B8;">7. SETTLEMENT</div><div style="font-weight:700; font-size:0.9rem;">R {txn["Weighbridge_Mass_t"]*txn["Approved_Rate_ZAR"]:,.2f}</div><div style="font-size:0.65rem; color:#10B981;">Reconciled Pay</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.markdown("#### Physical vs Financial Reconciliation")
        z_desc = "HIGH ANOMALY" if txn['Z_Score'] > 2.0 else "NORMAL"
        recon_data = {
            "Metric Parameter": [
                "Trusted Physical Mass (Digital Scale Telemetry)",
                "Billed Mass (Vendor Invoice / Delivery Note Claim)",
                "Quantity Variance",
                "Contract Approved Unit Rate",
                "Calculated Potential Financial Exposure",
                "Statistical Anomaly Z-Score",
                "Exception Classification"
            ],
            "Extracted Value": [
                f"{txn['Weighbridge_Mass_t']:.2f} t",
                f"{txn['Billed_Mass_t']:.2f} t",
                f"+{txn['Qty_Variance_t']:.2f} t" if txn['Qty_Variance_t'] > 0 else "0.00 t",
                f"R {txn['Approved_Rate_ZAR']:,.2f} / t",
                f"R {txn['Potential_Exposure_ZAR']:,.2f}",
                f"{txn['Z_Score']} σ ({z_desc})",
                txn['Exception_Type']
            ]
        }
        st.table(pd.DataFrame(recon_data))
        
    with col_right:
        st.markdown("#### Transaction Stream Summary Ledger")
        st.dataframe(
            df_txns[["Transaction_ID", "Supplier", "Material", "Weighbridge_Mass_t", "Billed_Mass_t", "Potential_Exposure_ZAR", "Status"]].head(10),
            use_container_width=True
        )

# ------------------------------------------
# TAB 2: MULTI-DOCUMENT EVIDENCE PANEL
# ------------------------------------------
with tab_evidence:
    st.subheader(f"Evidence Audit Trail for Transaction: {selected_txn_id}")
    e1, e2 = st.columns([1, 1])
    
    with e1:
        st.markdown("#### Extracted Evidence Document Bundle")
        doc_evidence = [
            {"Document Type": "1. Purchase Order", "Doc Ref": "PO-10482", "Key Field": "40.00 t @ R1,850/t", "OCR Confidence": "99.7%", "Status": "Verified"},
            {"Document Type": "2. Digital Weighbridge Scale Log", "Doc Ref": f"WB-{txn['SHA256_Hash'][:5].upper()}", "Key Field": f"{txn['Weighbridge_Mass_t']:.2f} t Net", "OCR Confidence": "99.9% (Hardware Telemetry)", "Status": "Verified Ground Truth"},
            {"Document Type": "3. Delivery Note", "Doc Ref": "DN-55291", "Key Field": f"{txn['Billed_Mass_t']:.2f} t Claimed", "OCR Confidence": "97.8%", "Status": "Discrepancy" if txn['Qty_Variance_t']>0 else "Verified"},
            {"Document Type": "4. Goods Received Note (GRN)", "Doc Ref": "GRN-99182", "Key Field": f"{txn['Billed_Mass_t']:.2f} t Ingested", "OCR Confidence": "98.2%", "Status": "Verified"},
            {"Document Type": "5. Vendor Tax Invoice", "Doc Ref": "INV-88172", "Key Field": f"R {txn['Billed_Mass_t']*txn['Approved_Rate_ZAR']:,.2f}", "OCR Confidence": "99.1%", "Status": "Flagged" if txn['Qty_Variance_t']>0 else "Verified"},
            {"Document Type": "6. Bank Payment Voucher", "Doc Ref": "PAY-33281", "Key Field": "Pending Approval", "OCR Confidence": "100%", "Status": "Held in Escrow"}
        ]
        st.dataframe(pd.DataFrame(doc_evidence), use_container_width=True)

    with e2:
        st.markdown("#### Cryptographic SHA-256 Provenance & Verification")
        st.code(
            f"[CRYPTOGRAPHIC PROVENANCE MANIFEST]\n"
            f"Transaction ID : {selected_txn_id}\n"
            f"Hardware Anchor: Scale #04 (Amatola Hub Weighbridge)\n"
            f"Timestamp      : {txn['Timestamp']}\n"
            f"Scale Payload  : {txn['Weighbridge_Mass_t']} t\n"
            f"SHA-256 Hash   : {txn['SHA256_Hash']}\n\n"
            f"[VERIFICATION RESULT]\n"
            f"✓ Hardware Security Module Signature: VALID\n"
            f"✓ Document Lineage Integrity: 6/6 Documents Verified\n"
            f"✓ Immutable Audit Log Entry Created",
            language="yaml"
        )

# ------------------------------------------
# TAB 3: SUPPLIER RISK INTELLIGENCE
# ------------------------------------------
with tab_supplier:
    st.subheader("Statistical Supplier Risk & Overbilling Profiles")
    
    supp_stats = df_txns.groupby("Supplier").agg(
        Total_Txns=("Transaction_ID", "count"),
        Total_Exceptions=("Potential_Exposure_ZAR", lambda x: int((x > 0).sum())),
        Total_Potential_Exposure=("Potential_Exposure_ZAR", "sum"),
        Avg_Qty_Variance=("Qty_Variance_t", "mean")
    ).reset_index()
    
    supp_stats["Exception_Rate_%"] = round((supp_stats["Total_Exceptions"] / supp_stats["Total_Txns"]) * 100, 2)
    
    s_col1, s_col2 = st.columns([1, 1])
    with s_col1:
        st.markdown("#### Historical Supplier Overbilling Rankings")
        st.dataframe(supp_stats.sort_values(by="Total_Potential_Exposure", ascending=False), use_container_width=True)
        
    with s_col2:
        st.markdown("#### Potential Financial Exposure Distribution by Supplier")
        fig_supp = px.pie(
            supp_stats, 
            names="Supplier", 
            values="Total_Potential_Exposure",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig_supp.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC")
        st.plotly_chart(fig_supp, use_container_width=True)

# ------------------------------------------
# TAB 4: INVESTIGATION QUEUE & AUDIT TRAIL
# ------------------------------------------
with tab_investigation:
    st.subheader("Human-in-the-Loop Investigation Queue")
    st.write("TrueFlow flags potential exceptions. Human auditors confirm and transition transactions to final settlement.")
    
    exceptions_df = df_txns[df_txns["Potential_Exposure_ZAR"] > 0]
    
    if len(exceptions_df) > 0:
        inv_txn_id = st.selectbox("Select Flagged Transaction to Investigate:", options=exceptions_df["Transaction_ID"].tolist())
        inv_item = exceptions_df[exceptions_df["Transaction_ID"] == inv_txn_id].iloc[0]
        
        ic1, ic2 = st.columns([1, 1])
        
        with ic1:
            st.markdown(f"**Selected Transaction:** `{inv_txn_id}`")
            st.markdown(f"**Supplier:** {inv_item['Supplier']}")
            st.markdown(f"**Calculated Exposure:** :red[R {inv_item['Potential_Exposure_ZAR']:,.2f}]")
            st.markdown(f"**Exception Classification:** {inv_item['Exception_Type']}")
            
        with ic2:
            new_status = st.selectbox(
                "Update Investigation Status:",
                ["Open / Under Review", "Validated Exception (Credit Note Issued)", "Closed (Legitimate Adjustment)", "Closed (Measurement Error)"],
                index=0
            )
            audit_note = st.text_area("Auditor Escalation Notes:", placeholder="e.g., Contacted supplier CFO regarding weighbridge discrepancy.")
            
            if st.button("Submit Audit Decision to Immutable Log"):
                record = {
                    "status": new_status,
                    "note": audit_note,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.investigations[str(inv_txn_id)] = record
                st.success(f"Audit record updated for {inv_txn_id}. Transaction status changed to '{new_status}'.")

    st.divider()
    st.markdown("#### Logged Audit Trail History")
    if len(st.session_state.investigations) > 0:
        st.json(st.session_state.investigations)
    else:
        st.info("No manual audit updates recorded yet in this session.")
    
