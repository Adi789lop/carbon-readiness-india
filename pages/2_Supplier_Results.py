import streamlit as st
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from engine.scope1 import calc_stationary, calc_mobile, calc_fugitive, total_scope1
from engine.scope2 import scope2_location, scope2_market, intensity, carbon_exposure
from engine.cpri_score import score
from engine.mac_curve import get_interventions
from engine.storage import load_one, load_all

st.set_page_config(page_title="Supplier Results", layout="wide")
st.title("📊 Supplier Results — Emissions, CPRI & MAC Curve")
st.markdown("---")

# ── CHECK IF FRESH DATA OR LOOKUP NEEDED ─────────────────────────
if 'r' not in st.session_state:
    st.warning("⚠️ No active session found. Please submit data via the Supplier Input page first, OR retrieve a previous submission below.")

    st.markdown("### 🔍 Retrieve Previous Submission")
    col1, col2 = st.columns([3, 1])
    with col1:
        sid_input = st.text_input(
            "Enter your Supplier ID",
            placeholder="e.g. SUP-AABCM1234A-PUNEPRECISION",
            help="Your Supplier ID was shown after submission on Page 1"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        retrieve = st.button("🔎 Retrieve", type="primary", use_container_width=True)

    if retrieve and sid_input:
        try:
            stored = load_one(sid_input)
            if stored:
                st.success(f"✅ Found submission for: **{stored.get('company', 'Unknown')}**")
                st.info("Note: Retrieved view shows summary only. For full charts and MAC curve, please re-submit your data via the Supplier Input page.")

                # Display summary in cards
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("Company", stored.get('company', '—'))
                with col_b:
                    st.metric("Total Scope 1+2", f"{stored.get('total', 0):,.0f} tCO₂e")
                with col_c:
                    st.metric("CPRI Score", f"{stored.get('cpri', 0)} / 100")
                with col_d:
                    st.metric("Band", stored.get('band', '—'))

                st.markdown("---")
                st.markdown("#### Detailed Numbers")
                st.json(stored)
            else:
                st.error(f"❌ No submission found for ID: {sid_input}")
                st.caption("IDs are case-sensitive. Make sure you copy the exact ID shown after submission.")
        except Exception as e:
            st.error(f"Error retrieving data: {e}")

    st.markdown("---")
    st.markdown("### 📝 Or Submit Fresh Data")
    st.info("Click **Supplier Input** in the sidebar to fill in the questionnaire and generate full results with all charts.")
    st.stop()

# ── ACTIVE SESSION — DISPLAY FULL RESULTS ────────────────────────
r = st.session_state['r']

# Defensive check — if session state is corrupted
required_keys = ['s1', 's2_lb', 's2_mb', 'cpri', 'mac', 'company', 'state', 'sid']
missing_keys = [k for k in required_keys if k not in r]
if missing_keys:
    st.error(f"⚠️ Session data is incomplete (missing: {', '.join(missing_keys)}). Please re-submit via the Supplier Input page.")
    st.stop()

s1   = r['s1']
s2_lb = r['s2_lb']
s2_mb = r['s2_mb']
intens = r.get('intensity', {})
exp = r.get('exp', {})
cpri = r['cpri']
mac_df = r['mac']
company = r['company']
state = r['state']
segment = r.get('segment', '')

# ── HEADER CARD ───────────────────────────────────────────────────
st.success(f"📋 Showing results for **{company}** | State: {state} | Segment: {segment}")
st.caption(f"Supplier ID: `{r['sid']}` — save this to retrieve later")

st.markdown("---")

# ── EMISSIONS SUMMARY ────────────────────────────────────────────
st.subheader("1️⃣ Total Emissions — Scope 1 & Scope 2")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Scope 1 Stationary", f"{s1.get('stationary', 0):,.1f} tCO₂e")
with col2:
    st.metric("Scope 1 Mobile", f"{s1.get('mobile', 0):,.1f} tCO₂e")
with col3:
    st.metric("Scope 1 Fugitive", f"{s1.get('fugitive', 0):,.2f} tCO₂e")
with col4:
    st.metric("Scope 1 Total", f"{s1.get('total', 0):,.1f} tCO₂e")

col5, col6, col7 = st.columns(3)
with col5:
    st.metric("Scope 2 — Location Based", f"{s2_lb.get('tco2', 0):,.1f} tCO₂e")
with col6:
    st.metric("Scope 2 — Market Based", f"{s2_mb.get('tco2', 0):,.1f} tCO₂e")
with col7:
    total_lb = s1.get('total', 0) + s2_lb.get('tco2', 0)
    st.metric("**TOTAL (Scope 1+2 Location)**", f"**{total_lb:,.1f} tCO₂e**")

# Pie chart of emissions
labels = ['Scope 1 Stationary', 'Scope 1 Mobile', 'Scope 1 Fugitive', 'Scope 2 Location']
values = [
    s1.get('stationary', 0), s1.get('mobile', 0),
    s1.get('fugitive', 0), s2_lb.get('tco2', 0)
]
fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4)])
fig.update_traces(marker=dict(colors=['#C0392B', '#E67E22', '#9B59B6', '#3498DB']))
fig.update_layout(title="Emissions Breakdown by Source", height=400)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── CARBON EXPOSURE ──────────────────────────────────────────────
st.subheader("2️⃣ Carbon Cost Exposure under CCTS Scenarios")

col_e1, col_e2, col_e3 = st.columns(3)
with col_e1:
    st.metric("@ INR 500/tCO₂", f"₹{exp.get('cost_500', 0):,.1f} Lakhs/yr",
              f"{exp.get('pct_500', 0):.1f}% EBITDA")
with col_e2:
    st.metric("@ INR 1,000/tCO₂", f"₹{exp.get('cost_1000', 0):,.1f} Lakhs/yr",
              f"{exp.get('pct_1000', 0):.1f}% EBITDA")
with col_e3:
    st.metric("@ INR 2,000/tCO₂", f"₹{exp.get('cost_2000', 0):,.1f} Lakhs/yr",
              f"{exp.get('pct_2000', 0):.1f}% EBITDA")

st.markdown("---")

# ── CPRI SCORE ────────────────────────────────────────────────────
st.subheader("3️⃣ Carbon Price Readiness Index (CPRI)")

col_c1, col_c2 = st.columns([1, 2])

with col_c1:
    score_total = cpri.get('total', 0)
    band = cpri.get('band', '—')

    band_colours = {
        'Unaware': '#2C2C2C', 'Emerging': '#7B5800',
        'Developing': '#1B3A6B', 'Advancing': '#1A5C38',
        'Leading': '#0D9E75'
    }
    bg = band_colours.get(band, '#666')

    st.markdown(f"""
    <div style="background:{bg};color:white;padding:20px;border-radius:8px;text-align:center;">
        <div style="font-size:14px;opacity:0.8;">CPRI Score</div>
        <div style="font-size:48px;font-weight:bold;">{score_total} / 100</div>
        <div style="font-size:18px;margin-top:5px;">{band} Band</div>
    </div>
    """, unsafe_allow_html=True)

with col_c2:
    pillars = ['P1 Measurement', 'P2 Governance', 'P3 Investment', 'P4 Awareness', 'P5 Human Capital']
    scores = [
        cpri.get('p1', 0), cpri.get('p2', 0), cpri.get('p3', 0),
        cpri.get('p4', 0), cpri.get('p5', 0)
    ]
    maxes = [25, 25, 20, 20, 10]

    fig_cpri = go.Figure()
    fig_cpri.add_trace(go.Bar(name='Achieved', x=pillars, y=scores, marker_color='#0D9E75'))
    fig_cpri.add_trace(go.Bar(name='Maximum', x=pillars, y=[m - s for m, s in zip(maxes, scores)],
                              marker_color='#E0E4EC'))
    fig_cpri.update_layout(barmode='stack', height=300, title="Pillar-by-Pillar Score",
                           yaxis_title="Points", showlegend=True)
    st.plotly_chart(fig_cpri, use_container_width=True)

st.markdown("---")

# ── MAC CURVE ─────────────────────────────────────────────────────
st.subheader("4️⃣ Personalised Marginal Abatement Cost Curve")

if mac_df is not None and not mac_df.empty:
    # Bar chart
    fig_mac = go.Figure()
    colors = ['#1D9E75' if v < 0 else '#D85A30' for v in mac_df['mac_cost']]
    fig_mac.add_trace(go.Bar(
        x=mac_df['intervention'],
        y=mac_df['mac_cost'],
        marker_color=colors,
        text=[f"₹{v:+,.0f}" for v in mac_df['mac_cost']],
        textposition='outside'
    ))
    fig_mac.add_hline(y=0, line_color='#222', line_width=2)
    fig_mac.update_layout(
        title=f"MAC Curve — {company}",
        xaxis_title="Intervention",
        yaxis_title="Net Cost (INR/tCO₂)",
        height=500
    )
    st.plotly_chart(fig_mac, use_container_width=True)

    # Detailed table
    st.markdown("#### Intervention Details")
    display_df = mac_df.copy()
    display_df['capital'] = display_df['capital'].apply(lambda x: f"₹{x:,.0f}")
    display_df['annual_saving'] = display_df['annual_saving'].apply(lambda x: f"₹{x:,.0f}")
    display_df['mac_cost'] = display_df['mac_cost'].apply(lambda x: f"₹{x:+,.0f}")
    display_df['payback_yrs'] = display_df['payback_yrs'].apply(lambda x: f"{x:.1f} yrs" if x else "N/A")
    display_df.columns = ['Rank', 'Intervention', 'Capital', 'Annual Saving',
                         'CO₂ Abated (tCO₂/yr)', 'MAC Cost (INR/tCO₂)', 'Payback']
    st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.info("No MAC curve interventions available for this profile.")

st.markdown("---")

# ── RECOMMENDATIONS ──────────────────────────────────────────────
st.subheader("5️⃣ Top 3 Recommended Actions")

if mac_df is not None and not mac_df.empty:
    top3 = mac_df.head(3)
    cols = st.columns(3)
    for i, (_, row) in enumerate(top3.iterrows()):
        with cols[i]:
            st.markdown(f"""
            **#{int(row['rank'])} {row['intervention']}**

            • Capital: ₹{row['capital']:,.0f}
            • Saves: ₹{row['annual_saving']:,.0f}/yr
            • CO₂: {row['co2_abated']:.1f} tCO₂/yr
            • MAC: ₹{row['mac_cost']:+,.0f}/tCO₂
            """)

st.markdown("---")
st.caption("Data sources: CEA 2024-25 grid emission factors | IPCC 2006 fuel factors | BEE/EESL/MNRE/PCRA technology costs")