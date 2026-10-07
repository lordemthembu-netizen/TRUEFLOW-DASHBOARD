import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# ==========================================
# 1. PAGE CONFIG & DARK THEME CONTROL ROOM
# ==========================================
st.set_page_config(page_title='TRUEFLOW | Transaction Assurance', page_icon='🛡️', layout='wide')

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
html,body,[class*="css"]{font-family:Inter,sans-serif}
.stApp{background:radial-gradient(circle at 10% 0%,rgba(35,92,160,.13),transparent 28%),radial-gradient(circle at 90% 5%,rgba(0,190,150,.08),transparent 24%),#070c16;color:#e7edf7}
.block-container{padding-top:1.2rem;max-width:1500px}
.tf-header{border:1px solid #1d304c;border-radius:14px;padding:22px 24px;background:linear-gradient(135deg,#0c1525,#101b2c);box-shadow:0 12px 35px rgba(0,0,0,.25)}
.tf-brand{font-size:27px;font-weight:800}
.tf-brand span{color:#35b8ff}
.tf-sub{color:#8190a6;font-size:13px;margin-top:5px}
.pill{display:inline-block;padding:5px 9px;border-radius:999px;font-family:'JetBrains Mono';font-size:10px;margin:3px 5px 0 0;border:1px solid #29415f;background:#0b1727;color:#8fa4be}
.pill.green{color:#56e3b2;border-color:#1c6853}
.pill.blue{color:#63c8ff;border-color:#225a83}
.pill.amber{color:#ffd36b;border-color:#735b1e}
.section{font-size:17px;font-weight:800;margin:24px 0 12px;border-left:3px solid #28b9ff;padding-left:10px}
.card{border:1px solid #1b2b43;border-radius:12px;padding:14px;background:#0b1321;min-height:100px}
.card-label{color:#7e8ca1;font-size:10px;text-transform:uppercase;letter-spacing:.7px}
.card-value{font-family:'JetBrains Mono';font-size:24px;font-weight:700;margin-top:7px}
.card-note{font-size:10px;color:#687990;margin-top:4px}
.red{color:#ff6577!important}
.green{color:#54e0b0!important}
.blue{color:#5cc7ff!important}
.amber{color:#ffd36b!important}
.stage{border:1px solid #1e2e46;border-radius:10px;padding:11px 8px;background:#0b1422;min-height:88px;text-align:center}
.stage-title{font-size:9px;color:#77879d;text-transform:uppercase}
.stage-value{font-family:'JetBrains Mono';font-size:16px;margin-top:8px}
.stage-note{font-size:9px;color:#4dbf9c;margin-top:4px}
.alert-high{border-left:4px solid #ff5269;background:#1a0f17;padding:12px;border-radius:8px}
.alert-clean{border-left:4px solid #43d5a5;background:#0c1715;padding:12px;border-radius:8px}
.smallmono{font-family:'JetBrains Mono';font-size:11px}
</style>''', unsafe_allow_html=True)

# ==========================================
# 2. SYNTHETIC TRANSACTION GENERATOR
# ==========================================
SUPPLIERS=['ABC Coal Mining Pty Ltd','Mpuma Haulage Logistics','Khai-Appel Mining Corp','North Ridge Minerals','Vanguard Bulk Rail']
MATERIALS=['RB1 Thermal Coal','RB2 Thermal Coal','Coking Coal','Iron Ore Fines','Chrome Ore Concentrate']
TRUCKS=['MP-1234-GP','LIM-3321-GP','FS-7711-GP','MP-4421-GP','KZN-9012-GP','MP-6789-GP']

def make_transaction(i, mode=None):
    rng=np.random.default_rng(1000+i)
    supplier=SUPPLIERS[i%5]
    material=MATERIALS[i%5]
    truck=TRUCKS[i%6]
    base=round(float(rng.uniform(34.5,39.8)),2)
    rate=float(rng.choice([1650,1750,1850,1950,2100]))
    approved=40.0
    
    if mode is None: 
        # Corrected probabilities so p sums exactly to 1.0
        mode=rng.choice(['clean','clean','clean','clean','qty','qty','price','duplicate','missing','identity'],p=[.40,.08,.08,.08,.12,.08,.05,.05,.03,.03])
        
    wb=dn=grn=inv_qty=base
    inv_rate=rate
    duplicate=missing=identity=False
    
    if mode=='qty': 
        dn=round(base+rng.uniform(1,3),2)
        grn=inv_qty=dn
    elif mode=='price': 
        inv_rate=round(rate*rng.uniform(1.03,1.09),2)
    elif mode=='duplicate': 
        duplicate=True
    elif mode=='missing': 
        missing=True
    elif mode=='identity': 
        identity=True
        
    invoice=round(inv_qty*inv_rate,2)
    payment=round(invoice*(2 if duplicate else 1),2)
    qty_exp=max(0,inv_qty-wb)*rate
    price_exp=max(0,inv_rate-rate)*inv_qty
    dup_exp=invoice if duplicate else 0
    exposure=round(qty_exp+price_exp+dup_exp,2)
    var_pct=((inv_qty-wb)/wb*100) if wb else 0
    baseline=max(.12,.16+(i%5)*.05)
    z=abs(var_pct-baseline)/.35 if var_pct else abs(baseline)/.35
    score=round(min(99,max(1,35+abs(var_pct)*8+(35 if duplicate else 0)+(25 if price_exp else 0)+(15 if missing else 0)+(10 if identity else 0))))
    
    status='CLEAN'
    priority='LOW'
    classification='None'
    
    if duplicate: status,priority,classification='EXCEPTION','HIGH','Duplicate billing risk'
    elif qty_exp>0: status,priority,classification='EXCEPTION','HIGH','Quantity discrepancy'
    elif price_exp>0: status,priority,classification='EXCEPTION','HIGH','Price variance'
    elif identity: status,priority,classification='EXCEPTION','MEDIUM','Identity / truck mismatch'
    elif missing: status,priority,classification='EXCEPTION','MEDIUM','Missing evidence'
    
    return {
        'transaction_id':f'TXN-2026-{4921+i:04d}',
        'timestamp':datetime.now()-timedelta(minutes=(150-i)*4),
        'supplier':supplier,
        'truck':truck,
        'material':material,
        'po_number':f'PO-{10480+i}',
        'approved_qty_t':approved,
        'approved_rate':rate,
        'dispatch_t':approved,
        'weighbridge_t':wb,
        'delivery_note_t':dn,
        'grn_t':grn,
        'invoice_qty_t':inv_qty,
        'invoice_rate':inv_rate,
        'invoice_amount':invoice,
        'payment_amount':payment,
        'qty_exposure':round(qty_exp,2),
        'price_exposure':round(price_exp,2),
        'duplicate_exposure':round(dup_exp,2),
        'potential_exposure':exposure,
        'variance_t':round(inv_qty-wb,2),
        'variance_pct':round(var_pct,2),
        'baseline_pct':round(baseline,2),
        'z_score':round(z,2),
        'anomaly_score':score,
        'evidence_present':7-(1 if missing else 0),
        'evidence_total':7,
        'status':status,
        'priority':priority,
        'classification':classification,
        'duplicate':duplicate,
        'missing_evidence':missing,
        'identity_mismatch':identity
    }

@st.cache_data
def build_data():
    forced={4:'qty',8:'price',13:'duplicate',19:'missing',27:'identity',34:'qty',42:'price',56:'duplicate',73:'qty',91:'missing',112:'price',127:'qty'}
    return pd.DataFrame([make_transaction(i,forced.get(i)) for i in range(150)])

df=build_data()

# Session State Initializations
if 'investigation' not in st.session_state: 
    st.session_state.investigation={}
if 'selected_txn' not in st.session_state: 
    st.session_state.selected_txn=df.iloc[4].transaction_id

# Header Banner
st.markdown('''<div class="tf-header"><div class="tf-brand">🛡️ TRUE<span>FLOW</span> <span style="font-size:12px;color:#6f86a1">| TRANSACTION ASSURANCE</span></div><div class="tf-sub">AI-powered physical-to-financial transaction assurance</div><div><span class="pill green">DEMO DATA</span><span class="pill blue">QUANTITATIVE ENGINE: ACTIVE</span><span class="pill blue">EVIDENCE PROVENANCE: ACTIVE</span><span class="pill amber">HUMAN REVIEW REQUIRED</span></div></div>''',unsafe_allow_html=True)

# Sidebar Controls
with st.sidebar:
    st.markdown('## TRUEFLOW')
    page=st.radio('Control Room',['Executive Overview','Transaction Control Room','Evidence','Risk & Analytics','Investigation Queue'])
    st.divider()
    only=st.checkbox('Exceptions only',False)
    selected_suppliers=st.multiselect('Supplier',sorted(df.supplier.unique()))
    
    view=df[df.supplier.isin(selected_suppliers)].copy() if selected_suppliers else df.copy()
    if only: 
        view=view[view.status=='EXCEPTION']
        
    st.caption('Prototype / synthetic data')
    st.caption('No live SAP, weighbridge or payment connection is claimed.')

# Executive KPIs
audited=len(view)
value=view.invoice_amount.sum()
exposure=view.potential_exposure.sum()
exceptions=(view.status=='EXCEPTION').sum()
coverage=(view.evidence_present/view.evidence_total*100).mean() if audited > 0 else 0

def metric(label,value,note,cls=''):
    st.markdown(f'<div class="card"><div class="card-label">{label}</div><div class="card-value {cls}">{value}</div><div class="card-note">{note}</div></div>',unsafe_allow_html=True)

st.markdown('<div class="section">Executive Overview & Financial Metrics</div>',unsafe_allow_html=True)
cols=st.columns(5)
with cols[0]: metric('Transactions Audited',f'{audited:,}','Synthetic transactions processed','blue')
with cols[1]: metric('Value Reconciled',f'R {value:,.0f}','Commercial value checked','green')
with cols[2]: metric('Potential Exposure',f'R {exposure:,.2f}','Unresolved exceptions','red')
with cols[3]: metric('Active Exception Queue',f'{exceptions}','Requires human review','amber')
with cols[4]: metric('Evidence Coverage',f'{coverage:.1f}%','Required evidence present','green')

# Safe transaction dropdown selector helper
def get_valid_txn_selection(available_options):
    if st.session_state.selected_txn not in available_options:
        return available_options[0] if len(available_options) > 0 else None
    return st.session_state.selected_txn

# ==========================================
# PAGE 1: EXECUTIVE OVERVIEW
# ==========================================
if page=='Executive Overview':
    st.markdown('<div class="section">Exposure & Exception Intelligence</div>',unsafe_allow_html=True)
    c1,c2=st.columns([1.65,1])
    
    with c1:
        if len(view) > 0:
            t=view.sort_values('timestamp').copy()
            t['cumulative_value']=t.invoice_amount.cumsum()
            t['cumulative_exposure']=t.potential_exposure.cumsum()
            fig=px.line(t,x='timestamp',y=['cumulative_value','cumulative_exposure'],labels={'value':'ZAR','timestamp':'Time','variable':''},title='Cumulative reconciled value vs potential exposure')
            fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',legend_title_text='')
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.info('No transaction data for current filter selection.')
            
    with c2:
        root=view[view.status=='EXCEPTION']['classification'].value_counts().reset_index()
        root.columns=['classification','count']
        if len(root) > 0:
            fig2=px.pie(root,values='count',names='classification',hole=.52,title='Exception classification')
            fig2.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2,use_container_width=True)
        else: 
            st.info('No exceptions in current filter.')
            
    st.markdown('<div class="section">Exception Snapshot</div>',unsafe_allow_html=True)
    snap=view[view.status=='EXCEPTION'].sort_values('potential_exposure',ascending=False).head(8)
    if len(snap) > 0:
        st.dataframe(snap[['transaction_id','supplier','truck','classification','potential_exposure','anomaly_score','priority']].rename(columns={'potential_exposure':'Potential Exposure','anomaly_score':'Anomaly Score'}),use_container_width=True,hide_index=True)
    else:
        st.write("No active exceptions detected under current filter criteria.")

# ==========================================
# PAGE 2: TRANSACTION CONTROL ROOM
# ==========================================
elif page=='Transaction Control Room':
    st.markdown('<div class="section">Transaction Control Room</div>',unsafe_allow_html=True)
    opts=view.transaction_id.tolist() if len(view)>0 else df.transaction_id.tolist()
    
    selected_target = get_valid_txn_selection(opts)
    selected=st.selectbox('Select transaction for deep forensic analysis',opts,index=opts.index(selected_target))
    st.session_state.selected_txn=selected
    
    tx=df[df.transaction_id==selected].iloc[0]
    
    if tx.status=='EXCEPTION': 
        st.markdown(f'<div class="alert-high">🔴 <b>{tx.classification}</b> — {tx.priority} priority. Potential exposure: <b>R {tx.potential_exposure:,.2f}</b>. Human investigation required.</div>',unsafe_allow_html=True)
    else: 
        st.markdown('<div class="alert-clean">🟢 Transaction currently reconciles. No material exception detected.</div>',unsafe_allow_html=True)
        
    st.markdown('### 7-Stage Transaction Process Flow')
    stages=[('1. PURCHASE ORDER',f'{tx.approved_qty_t:.2f} t',f'R{tx.approved_rate:,.0f}/t'),('2. DISPATCH',f'{tx.dispatch_t:.2f} t','Truck dispatched'),('3. WEIGHBRIDGE',f'{tx.weighbridge_t:.2f} t','✓ TRUSTED SCALE'),('4. DELIVERY NOTE',f'{tx.delivery_note_t:.2f} t','Reported quantity'),('5. GRN',f'{tx.grn_t:.2f} t','Warehouse record'),('6. INVOICE',f'R{tx.invoice_amount:,.0f}',f'{tx.invoice_qty_t:.2f} t billed'),('7. SETTLEMENT',f'R{tx.payment_amount:,.0f}','Payment record')]
    sc=st.columns(7)
    for col,(title,val,note) in zip(sc,stages):
        with col: 
            st.markdown(f'<div class="stage"><div class="stage-title">{title}</div><div class="stage-value">{val}</div><div class="stage-note">{note}</div></div>',unsafe_allow_html=True)
            
    st.markdown('### Physical vs Financial Reconciliation')
    a,b=st.columns([1.15,.85])
    with a:
        rec=pd.DataFrame({
            'Metric':['Trusted Physical Mass (Digital Scale)','Delivery Note Quantity','GRN Quantity','Billed Quantity','Quantity Variance','Quantity Variance %','Contract Approved Unit Rate','Invoice Unit Rate','Price Exposure','Quantity Exposure','Duplicate Exposure','Potential Financial Exposure','Statistical Anomaly Z-Score','Exception Classification'],
            'Value':[f'{tx.weighbridge_t:.2f} t',f'{tx.delivery_note_t:.2f} t',f'{tx.grn_t:.2f} t',f'{tx.invoice_qty_t:.2f} t',f'{tx.variance_t:+.2f} t',f'{tx.variance_pct:+.2f}%',f'R {tx.approved_rate:,.2f}/t',f'R {tx.invoice_rate:,.2f}/t',f'R {tx.price_exposure:,.2f}',f'R {tx.qty_exposure:,.2f}',f'R {tx.duplicate_exposure:,.2f}',f'R {tx.potential_exposure:,.2f}',f'{tx.z_score:.2f}',tx.classification]
        })
        st.dataframe(rec,use_container_width=True,hide_index=True)
        
    with b:
        st.markdown('#### Transaction metadata')
        st.write(f'**Supplier:** {tx.supplier}')
        st.write(f'**Truck:** {tx.truck}')
        st.write(f'**Material:** {tx.material}')
        st.write(f'**PO:** {tx.po_number}')
        st.write(f'**Transaction:** `{tx.transaction_id}`')
        st.write(f'**Timestamp:** {tx.timestamp:%Y-%m-%d %H:%M}')
        st.write(f'**Anomaly score:** `{tx.anomaly_score}/100`')
        st.write(f'**Priority:** `{tx.priority}`')

# ==========================================
# PAGE 3: EVIDENCE & PROVENANCE
# ==========================================
elif page=='Evidence':
    st.markdown('<div class="section">Multi-Document Evidence & Provenance</div>',unsafe_allow_html=True)
    opts=view.transaction_id.tolist() if len(view)>0 else df.transaction_id.tolist()
    
    selected_target = get_valid_txn_selection(opts)
    selected=st.selectbox('Transaction',opts,index=opts.index(selected_target))
    tx=df[df.transaction_id==selected].iloc[0]
    st.session_state.selected_txn=selected
    
    docs=[('Purchase Order',tx.po_number,f'{tx.approved_qty_t:.2f} t @ R{tx.approved_rate:,.0f}/t',True,99.7),('Dispatch Record',f'DIS-{tx.transaction_id[-4:]}',f'{tx.dispatch_t:.2f} t • {tx.truck}',True,98.9),('Digital Weighbridge',f'WB-{tx.transaction_id[-4:]}',f'Net {tx.weighbridge_t:.2f} t',True,99.9),('Delivery Note',f'DN-{tx.transaction_id[-4:]}',f'Claimed {tx.delivery_note_t:.2f} t',True,97.8),('Goods Receipt',f'GRN-{tx.transaction_id[-4:]}',f'Recorded {tx.grn_t:.2f} t',not tx.missing_evidence,98.4),('Invoice',f'INV-{tx.transaction_id[-4:]}',f'{tx.invoice_qty_t:.2f} t • R{tx.invoice_amount:,.2f}',True,99.1),('Payment',f'PAY-{tx.transaction_id[-4:]}',f'R{tx.payment_amount:,.2f}',True,99.4)]
    
    for name,ref,detail,present,conf in docs:
        icon='✓' if present else '⚠'
        cls='green' if present else 'amber'
        st.markdown(f'<div class="card" style="margin-bottom:8px;min-height:0;"><b class="{cls}">{icon} {name}</b> &nbsp; <span class="smallmono">{ref}</span><br><span style="color:#9aa8ba;font-size:12px">{detail}</span><span style="float:right;color:#7f92aa;font-size:11px">Confidence {conf:.1f}% • Source: demo ledger</span></div>',unsafe_allow_html=True)
        
    st.info('Production version: every extracted value should retain source document, page/field, extraction engine version and timestamp.')

# ==========================================
# PAGE 4: RISK & ANALYTICS
# ==========================================
elif page=='Risk & Analytics':
    st.markdown('<div class="section">Risk, Supplier & Truck Intelligence</div>',unsafe_allow_html=True)
    supplier=df.groupby('supplier').agg(Transactions=('transaction_id','count'),Exceptions=('status',lambda x:(x=='EXCEPTION').sum()),Exposure=('potential_exposure','sum'),AvgVariance=('variance_pct','mean')).reset_index()
    supplier['Exception Rate %']=supplier.Exceptions/supplier.Transactions*100
    
    c1,c2=st.columns(2)
    with c1:
        fig=px.bar(supplier.sort_values('Exposure',ascending=False),x='supplier',y='Exposure',title='Potential exposure by supplier',labels={'Exposure':'ZAR','supplier':''})
        fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig,use_container_width=True)
        
    with c2:
        fig=px.bar(supplier.sort_values('Exception Rate %',ascending=False),x='supplier',y='Exception Rate %',title='Exception rate by supplier',labels={'Exception Rate %':'%','supplier':''})
        fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig,use_container_width=True)
        
    st.dataframe(supplier.rename(columns={'AvgVariance':'Avg Quantity Variance %'}),use_container_width=True,hide_index=True)
    
    st.markdown('### Truck intelligence')
    truck=df.groupby('truck').agg(Trips=('transaction_id','count'),Exceptions=('status',lambda x:(x=='EXCEPTION').sum()),Exposure=('potential_exposure','sum'),AvgMass=('weighbridge_t','mean'),AvgVariance=('variance_pct','mean')).reset_index()
    st.dataframe(truck,use_container_width=True,hide_index=True)

# ==========================================
# PAGE 5: INVESTIGATION QUEUE
# ==========================================
else:
    st.markdown('<div class="section">Investigation Queue & Audit Trail</div>',unsafe_allow_html=True)
    q=df[df.status=='EXCEPTION'].copy()
    q['Decision']=q.transaction_id.map(lambda x:st.session_state.investigation.get(x,'Open'))
    q=q.sort_values(['priority','potential_exposure'],ascending=[True,False])
    
    st.dataframe(q[['transaction_id','supplier','classification','potential_exposure','anomaly_score','priority','Decision']].rename(columns={'transaction_id':'Transaction','classification':'Issue','potential_exposure':'Potential Exposure','anomaly_score':'Score'}),use_container_width=True,hide_index=True)
    
    st.markdown('### Review transaction')
    if len(q) > 0:
        selected=st.selectbox('Transaction',q.transaction_id.tolist())
        tx=df[df.transaction_id==selected].iloc[0]
        current=st.session_state.investigation.get(selected,'Open')
        
        statuses=['Open','Under Review','Validated Exception','Recovered','Explained / Closed']
        decision=st.selectbox('Investigation status',statuses,index=statuses.index(current))
        note=st.text_area('Investigator note',placeholder='Record the reason, evidence reviewed and outcome.')
        
        if st.button('Save investigation outcome',type='primary'): 
            st.session_state.investigation[selected]=decision
            st.success(f'{selected} updated to: {decision}')
            st.rerun()
    else:
        st.info("No 
