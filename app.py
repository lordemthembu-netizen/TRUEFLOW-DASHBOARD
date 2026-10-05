import streamlit as st
import os

# Set Page Config with Modern Dark Theme
st.set_page_config(
    page_title="TrueFlow // Quant Assurance Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 1. EMBED SVG LOGO & HEADER
# -----------------------------------------------------------------------------
svg_logo = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 200" width="100%" height="120">
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
  <rect width="100%" height="100%" fill="#0B1120" rx="12"/>
  <g transform="translate(30, 10)">
    <polygon points="100,30 150,60 100,90 50,60" fill="url(#tf-cyan)" opacity="0.9"/>
    <polygon points="50,60 100,90 100,150 50,120" fill="url(#tf-purple)" opacity="0.85"/>
    <polygon points="100,90 150,60 150,120 100,150" fill="url(#tf-emerald)" opacity="0.95"/>
    <polyline points="100,30 100,90 150,120" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-dasharray="4,4"/>
  </g>
  <g transform="translate(200, 100)">
    <text font-family="'Helvetica', sans-serif" font-weight="900" font-size="42" fill="#F8FAFC" letter-spacing="3">
      TRUE<tspan fill="#38BDF8">FLOW</tspan>
    </text>
    <text y="32" font-family="monospace" font-weight="600" font-size="14" fill="#64748B" letter-spacing="6">
      QUANT ASSURANCE TERMINAL
    </text>
  </g>
</svg>
"""

# Render SVG Logo at the top of the website
st.markdown(svg_logo, unsafe_allow_html=True)
st.markdown("---")

# -----------------------------------------------------------------------------
# 2. APPLICATION PACKS & DOWNLOAD SECTION ON THE WEBSITE
# -----------------------------------------------------------------------------
st.sidebar.title("📌 Investor & Grant Pack")
st.sidebar.info("Download the complete institutional funding package including financial models, pitch video, and grant application PDFs.")

zip_file_path = "TrueFlow_Funding_Application_Pack.zip"

if os.path.exists(zip_file_path):
    with open(zip_file_path, "rb") as fp:
        btn = st.sidebar.download_button(
            label="⬇️ Download Application Pack (.ZIP)",
            data=fp,
            file_name="TrueFlow_Funding_Application_Pack.zip",
            mime="application/zip"
        )
else:
    st.sidebar.warning("Funding ZIP file not found. Run the generator script to create it.")

# -----------------------------------------------------------------------------
# 3. WEBSITE MAIN DASHBOARD CONTENT
# -----------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Gross Billed", "R 1,524,000", "+12%")
col2.metric("Reconciled Flow", "R 1,380,000", "90.5%")
col3.metric("Flagged Leakage", "R 144,000", "-8.5%", delta_color="inverse")
col4.metric("Engine Status", "ACTIVE", "Z-Score Tier 1")

st.subheader("Interactive Physical-to-Financial Liquidity Flow")
st.write("Real-time physical weighbridge scale telemetry matched deterministically against active contract terms.")

# Embed video pitch demo directly on the website if present
video_file_path = "TrueFlow_Dashboard_Pitch_Demo.mp4"
if os.path.exists(video_file_path):
    st.subheader("📹 Automated Pitch & System Walkthrough")
    st.video(video_file_path)
