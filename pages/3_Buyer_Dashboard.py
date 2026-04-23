import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from engine.storage import load_all

st.set_page_config(page_title="Buyer Dashboard", layout="wide")
st.title("🏢 Buyer Dashboard — Supplier Sustainability Portfolio")
st.markdown("---")

# ── PASSWORD PROTECTION ───────────────────────────────────────────────
pwd = st.sidebar.text_input("🔐 Buyer Access Code", type="password")
if pwd != "buyer2024":
    st.warning("Enter the buyer access code in the sidebar to view this dashboard.")
    st.info("Access code is provided by your sustainability team.")
    st.stop()

# ── LOAD ALL SUPPLIER DATA ────────────────────────────────────────────
all_data = load_all()

if not all_data:
    st.info("No supplier data yet. Share the Supplier Input page link with your suppliers.")
    st.stop()

# ── BUILD DATAFRAME ───────────────────────────────────────────────────
rows = []
for sid, d in all_data.items():
    rows.append({
        'Supplier ID':        sid,
        'Supplier':           d.get('company', 'Unknown'),
        'Segment':            d.get('segment', 'Unknown'),
        'State':              d.get('state', 'Unknown'),
        'Revenue (Cr)':       d.get('revenue', 0),
        'Scope 1 (tCO₂)':    d.get('scope1', 0),
        'Scope 2 (tCO₂)':    d.get('scope2_lb', 0),
        'Total (tCO₂)':      d.get('total', 0),
        'tCO₂ / Cr Revenue': d.get('intensity_cr', 0),
        'CPRI Score':         d.get('cpri', 0),
        'Band':               d.get('band', 'Unknown'),
    })

df = pd.DataFrame(rows)
df = df.sort_values('CPRI Score')

# Add band emoji column
band_map = {
    'Unaware':    '⬛ Unaware',
    'Emerging':   '🟤 Emerging',
    'Developing': '🔵 Developing',
    'Advancing':  '🟡 Advancing',
    'Leading':    '🟢 Leading'
}
df['Risk Band'] = df['Band'].map(band_map).fillna('❓ Unknown')

# ── PORTFOLIO KPI STRIP ───────────────────────────────────────────────
st.subheader("📊 Portfolio Summary")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Suppliers",       len(df))
col2.metric("Total Scope 3 (Cat 1)", f"{df['Total (tCO₂)'].sum():,.0f} tCO₂e")
col3.metric("Avg CPRI Score",        f"{df['CPRI Score'].mean():.1f} / 100")
col4.metric("Critical Risk",         len(df[df['CPRI Score'] < 20]),
            "Score below 20")
col5.metric("High Risk",             len(df[df['CPRI Score'] < 40]),
            "Score below 40")

st.markdown("---")

# ── FILTERS ───────────────────────────────────────────────────────────
st.subheader("🔽 Filter Suppliers")
col1, col2, col3 = st.columns(3)
with col1:
    seg_options = ['All'] + sorted(df['Segment'].unique().tolist())
    seg_filter  = st.selectbox("Filter by Segment", seg_options)
with col2:
    state_options = ['All'] + sorted(df['State'].unique().tolist())
    state_filter  = st.selectbox("Filter by State", state_options)
with col3:
    band_options = ['All'] + sorted(df['Band'].unique().tolist())
    band_filter  = st.selectbox("Filter by Risk Band", band_options)

filtered = df.copy()
if seg_filter   != 'All': filtered = filtered[filtered['Segment'] == seg_filter]
if state_filter != 'All': filtered = filtered[filtered['State']   == state_filter]
if band_filter  != 'All': filtered = filtered[filtered['Band']    == band_filter]

st.markdown("---")

# ── SUPPLIER LEAGUE TABLE ─────────────────────────────────────────────
st.subheader("🏆 Supplier League Table")
st.caption("Sorted by CPRI Score — lowest (most at risk) first. Green = higher score = better prepared.")

display_cols = [
    'Supplier', 'Segment', 'State',
    'Total (tCO₂)', 'tCO₂ / Cr Revenue',
    'CPRI Score', 'Risk Band'
]

def colour_cpri(val):
    if val >= 75:
        color = '#1A5C38'
        text = 'white'
    elif val >= 60:
        color = '#7B5800'
        text = 'white'
    elif val >= 40:
        color = '#1B3A6B'
        text = 'white'
    elif val >= 20:
        color = '#8B4513'
        text = 'white'
    else:
        color = '#8B1A1A'
        text = 'white'
    return f'background-color: {color}; color: {text}'

styled_df = filtered[display_cols].style.map(
    colour_cpri,
    subset=['CPRI Score']
)

st.dataframe(
    styled_df,
    use_container_width=True,
    height=350,
    hide_index=True
)

st.markdown("---")

# ── CHARTS ROW ────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🍕 Scope 3 by Segment")
    if not filtered.empty:
        seg_df = filtered.groupby('Segment')['Total (tCO₂)'].sum().reset_index()
        fig_pie = px.pie(
            seg_df,
            values='Total (tCO₂)',
            names='Segment',
            title='Scope 3 Category 1 by Supplier Segment',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_pie.update_layout(height=350)
        st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.subheader("📊 CPRI Score Distribution")
    if not filtered.empty:
        fig_hist = px.histogram(
            filtered,
            x='CPRI Score',
            nbins=10,
            color_discrete_sequence=['#1B3A6B'],
            title='Distribution of Carbon Price Readiness Scores'
        )
        fig_hist.add_vline(
            x=20, line_dash='dash',
            line_color='red',
            annotation_text='Critical threshold'
        )
        fig_hist.add_vline(
            x=40, line_dash='dash',
            line_color='orange',
            annotation_text='Developing threshold'
        )
        fig_hist.update_layout(height=350)
        st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("---")

# ── SCOPE 3 BY STATE ──────────────────────────────────────────────────
st.subheader("🗺️ Scope 3 Concentration by State")
if not filtered.empty:
    state_df = filtered.groupby('State')['Total (tCO₂)'].sum().reset_index()
    state_df  = state_df.sort_values('Total (tCO₂)', ascending=True)
    fig_state = px.bar(
        state_df,
        x='Total (tCO₂)',
        y='State',
        orientation='h',
        title='Total Supplier Emissions by State',
        color='Total (tCO₂)',
        color_continuous_scale='Reds'
    )
    fig_state.update_layout(height=350)
    st.plotly_chart(fig_state, use_container_width=True)

st.markdown("---")

# ── INDIVIDUAL SUPPLIER DEEP DIVE ─────────────────────────────────────
st.subheader("🔍 Individual Supplier Deep Dive")

if not filtered.empty:
    selected = st.selectbox(
        "Select a supplier to view details:",
        filtered['Supplier'].tolist()
    )

    sup_row = filtered[filtered['Supplier'] == selected].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Emissions",   f"{sup_row['Total (tCO₂)']:,.0f} tCO₂e")
    col2.metric("Emission Intensity",f"{sup_row['tCO₂ / Cr Revenue']:,.1f} tCO₂/Cr")
    col3.metric("CPRI Score",        f"{sup_row['CPRI Score']:.0f} / 100")
    col4.metric("Risk Band",          sup_row['Risk Band'])

    # Carbon exposure for selected supplier
    sid = sup_row['Supplier ID']
    raw = load_all().get(sid, {})
    exp = raw.get('exposure', raw.get('exp', {}))

    if exp:
        st.markdown("#### 💰 Carbon Cost Exposure")
        c1, c2, c3 = st.columns(3)
        c1.metric("At INR 500/tCO₂",
                  f"₹{exp.get('500',{}).get('lakhs',0):,.1f} Lakhs",
                  f"{exp.get('500',{}).get('ebitda_pct',0)}% of EBITDA")
        c2.metric("At INR 1,000/tCO₂",
                  f"₹{exp.get('1000',{}).get('lakhs',0):,.1f} Lakhs",
                  f"{exp.get('1000',{}).get('ebitda_pct',0)}% of EBITDA")
        c3.metric("At INR 2,000/tCO₂",
                  f"₹{exp.get('2000',{}).get('lakhs',0):,.1f} Lakhs",
                  f"{exp.get('2000',{}).get('ebitda_pct',0)}% of EBITDA")

st.markdown("---")

# ── EXPORT ────────────────────────────────────────────────────────────
st.subheader("⬇️ Export Data")

export_df = filtered[[
    'Supplier', 'Segment', 'State', 'Revenue (Cr)',
    'Scope 1 (tCO₂)', 'Scope 2 (tCO₂)', 'Total (tCO₂)',
    'tCO₂ / Cr Revenue', 'CPRI Score', 'Risk Band'
]].copy()

csv = export_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Supplier Data as CSV",
    data=csv,
    file_name="supplier_sustainability_report.csv",
    mime="text/csv"
)

st.caption("Data sourced from supplier self-reporting. Emissions calculated using CEA CO₂ Baseline Database 2024-25 and IPCC 2006 Guidelines.")