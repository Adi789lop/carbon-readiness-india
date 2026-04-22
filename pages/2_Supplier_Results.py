import streamlit as st
import plotly.graph_objects as go
import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from engine.storage import load_one

st.set_page_config(page_title="Supplier Results", layout="wide")
st.title("📊 Your Emissions & Readiness Report")
st.markdown("---")

# ── LOAD RESULTS ──────────────────────────────────────────────────────
if 'r' in st.session_state:
    r = st.session_state['r']
else:
    st.info("Enter your Supplier ID to retrieve your results.")
    sid_input = st.text_input("Supplier ID")
    if sid_input:
        raw = load_one(sid_input.upper())
        if raw:
            st.session_state['r'] = raw
            r = raw
            st.rerun()
        else:
            st.error("ID not found. Please check and try again.")
    st.stop()

# ── COMPANY HEADER ────────────────────────────────────────────────────
st.subheader(f"🏭 {r.get('company', 'Your Company')} — {r.get('segment', '')} | {r.get('state', '')}")
st.markdown("---")

# ── SCREEN 1: EMISSIONS SUMMARY ───────────────────────────────────────
st.subheader("1️⃣ Carbon Footprint — Scope 1 & Scope 2")

s1   = r['s1']
s2   = r['s2_lb']
s2mb = r['s2_mb']
intn = r['intensity']
total = s1['total'] + s2['tco2']

col1, col2, col3, col4 = st.columns(4)
col1.metric("🔴 Total Scope 1",
            f"{s1['total']:,.1f} tCO₂e",
            "Direct emissions")
col2.metric("🔵 Total Scope 2 (Location)",
            f"{s2['tco2']:,.1f} tCO₂e",
            f"Grid EF: {s2['ef']} kg CO₂/kWh")
col3.metric("⚫ Total Scope 1+2",
            f"{total:,.1f} tCO₂e",
            "Your carbon footprint")
col4.metric("📈 Emission Intensity",
            f"{intn['per_cr']:,.1f} tCO₂/Cr",
            "Per Crore Revenue")

st.markdown(" ")

# Breakdown pie chart
col_a, col_b = st.columns(2)

with col_a:
    labels = ['Stationary Combustion', 'Mobile Combustion',
              'Fugitive Emissions', 'Scope 2 — Grid Electricity']
    values = [s1['stationary'], s1['mobile'],
              s1['fugitive'], s2['tco2']]
    colours = ['#D62728', '#FF7F0E', '#E377C2', '#1F77B4']

    fig_pie = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colours
    ))
    fig_pie.update_layout(
        title='Emissions by Source',
        height=350,
        showlegend=True
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_b:
    st.markdown("#### Scope 2 — Two Methods")
    st.markdown(f"""
    | Method | tCO₂e | Explanation |
    |--------|--------|-------------|
    | **Location-Based** | {s2['tco2']:,.1f} | Uses state grid emission factor |
    | **Market-Based** | {s2mb['tco2']:,.1f} | After deducting RECs and captive solar |
    """)

    st.markdown("#### Emission Intensity Metrics")
    st.markdown(f"""
    | Metric | Value |
    |--------|-------|
    | Per Crore Revenue | {intn['per_cr']:,.1f} tCO₂/Cr |
    | Per Tonne Output | {intn['per_tonne']:,.1f} tCO₂/tonne |
    | Scope 1 Share | {intn['s1_pct']}% |
    | Scope 2 Share | {intn['s2_pct']}% |
    """)

    st.info("💡 This figure represents your **Scope 3 Category 1** emissions from your buyer's perspective.")

st.markdown("---")

# ── SCREEN 2: CARBON COST EXPOSURE ────────────────────────────────────
st.subheader("2️⃣ Carbon Cost Exposure — India CCTS Scenarios")
st.caption("How much would carbon pricing cost your business at different price levels?")

exp = r['exp']

col1, col2, col3 = st.columns(3)
col1.metric(
    "🟡 At INR 500 / tCO₂",
    f"₹{exp['500']['lakhs']:,.1f} Lakhs / year",
    f"{exp['500']['ebitda_pct']}% of estimated EBITDA"
)
col2.metric(
    "🟠 At INR 1,000 / tCO₂",
    f"₹{exp['1000']['lakhs']:,.1f} Lakhs / year",
    f"{exp['1000']['ebitda_pct']}% of estimated EBITDA"
)
col3.metric(
    "🔴 At INR 2,000 / tCO₂",
    f"₹{exp['2000']['lakhs']:,.1f} Lakhs / year",
    f"{exp['2000']['ebitda_pct']}% of estimated EBITDA"
)

st.caption("EBITDA estimated at 10% of annual revenue. Carbon price scenarios based on India CCTS policy consultations and comparable emerging market ETS experience.")

st.markdown("---")

# ── SCREEN 3: CPRI SCORE ───────────────────────────────────────────────
st.subheader("3️⃣ Carbon Price Readiness Index (CPRI)")

cpri = r['cpri']

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown(f"### {cpri['total']} / 100")
    st.markdown(f"**Band:** {cpri['colour']} {cpri['band']}")
    st.markdown(f"**CCTS Risk Level:** {cpri['risk']}")
    st.markdown(" ")

    risk_colour = {
        'Low': '🟢', 'Low-Moderate': '🟡',
        'Moderate': '🟠', 'High': '🔴', 'Critical': '⬛'
    }
    icon = risk_colour.get(cpri['risk'], '⚪')
    st.markdown(f"#### {icon} {cpri['risk']} Risk")

with col2:
    pillars = cpri['pillars']
    max_pts = {
        'P1 Measurement': 25,
        'P2 Governance': 25,
        'P3 Investment': 20,
        'P4 Awareness': 20,
        'P5 Human Capital': 10
    }
    labels = list(pillars.keys())
    values = list(pillars.values())
    maxvals = [max_pts.get(k, 25) for k in labels]
    pct = [round(v/m*100) for v, m in zip(values, maxvals)]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=values,
        y=labels,
        orientation='h',
        marker_color=['#1B3A6B', '#1B7A6B', '#7B5800', '#4B0082', '#1A5C38'],
        text=[f"{v} / {m}" for v, m in zip(values, maxvals)],
        textposition='outside'
    ))
    fig_bar.update_layout(
        title='Score by Pillar',
        height=280,
        xaxis=dict(range=[0, 25], title='Score'),
        margin=dict(l=160, r=40, t=40, b=20)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("#### 🚀 Top Actions to Improve Your Score")
for action, pts in cpri['recommendations']:
    st.success(f"**+{int(pts)} pts** — {action}")

st.markdown("---")

# ── SCREEN 4: MAC CURVE ────────────────────────────────────────────────
st.subheader("4️⃣ Your Personalised Marginal Abatement Cost Curve")
st.caption("Ranked by cost-effectiveness. Green bars save money while reducing CO₂. No carbon price needed to justify them.")

mac = r.get('mac')

if mac is not None and len(mac) > 0:
    colours = ['#1A5C38' if c == 'green' else '#8B1A1A' for c in mac['colour']]

    fig_mac = go.Figure()
    fig_mac.add_trace(go.Bar(
        x=mac['name'],
        y=mac['mac'],
        marker_color=colours,
        text=[f"₹{int(v):,}" for v in mac['mac']],
        textposition='outside',
        customdata=list(zip(
            mac['capital'],
            mac['saving'],
            mac['co2'],
            mac['payback']
        )),
        hovertemplate=(
            '<b>%{x}</b><br>'
            'MAC Cost: ₹%{y:,.0f}/tCO₂<br>'
            'Capital Cost: ₹%{customdata[0]:,.0f}<br>'
            'Annual Saving: ₹%{customdata[1]:,.0f}<br>'
            'CO₂ Abated: %{customdata[2]} tCO₂/yr<br>'
            'Payback: %{customdata[3]} years'
            '<extra></extra>'
        )
    ))
    fig_mac.add_hline(y=0, line_color='black', line_width=2)
    fig_mac.update_layout(
        title='Marginal Abatement Cost Curve — Your Facility',
        yaxis_title='Net Cost per tCO₂ Abated (INR)',
        xaxis_title='Intervention',
        height=420,
        showlegend=False
    )
    st.plotly_chart(fig_mac, use_container_width=True)

    st.markdown("#### Intervention Details")
    display_mac = mac[['name', 'capital', 'saving', 'co2', 'mac', 'payback']].copy()
    display_mac.columns = [
        'Intervention', 'Capital Cost (INR)',
        'Annual Saving (INR)', 'CO₂ Abated (tCO₂/yr)',
        'MAC Cost (INR/tCO₂)', 'Payback (years)'
    ]
    display_mac['Capital Cost (INR)']   = display_mac['Capital Cost (INR)'].apply(lambda x: f"₹{int(x):,}")
    display_mac['Annual Saving (INR)']  = display_mac['Annual Saving (INR)'].apply(lambda x: f"₹{int(x):,}")
    display_mac['MAC Cost (INR/tCO₂)'] = display_mac['MAC Cost (INR/tCO₂)'].apply(lambda x: f"₹{int(x):,}")
    st.dataframe(display_mac, use_container_width=True, hide_index=True)

    total_abatement = mac['co2'].sum()
    total_saving    = mac[mac['mac'] < 0]['saving'].sum()
    st.success(f"**Total abatement potential:** {total_abatement:,.0f} tCO₂/year | **Total annual saving from no-regret interventions:** ₹{total_saving/100000:,.1f} Lakhs")

else:
    st.info("No applicable interventions found based on your profile. This may mean all interventions are already implemented.")

st.markdown("---")
st.caption(f"Supplier ID: {r.get('sid', 'N/A')} | Share this ID with your buyer to appear on their dashboard.")