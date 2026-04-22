import streamlit as st

st.set_page_config(page_title="Methodology", layout="wide")
st.title("📚 Methodology & Data Sources")
st.markdown("---")

st.markdown("""
This page documents exactly how every number in this tool is calculated.
It is designed for academic transparency and for buyers who want to
understand the basis of supplier emissions data.
""")

# ── SECTION 1: SCOPE 1 ────────────────────────────────────────────────
st.subheader("1️⃣ How Scope 1 is Calculated")
st.markdown("""
Scope 1 covers all **direct emissions** from sources owned or controlled
by the company. We use the **fuel-based approach** from the GHG Protocol
Corporate Standard.

**Formula:**
> Scope 1 (tCO₂e) = Fuel Consumed (practical unit) × Emission Factor ÷ 1,000
""")

st.markdown("#### Fuel Emission Factors — Stationary Combustion")
st.table({
    "Fuel": [
        "Diesel / HSD", "LPG", "PNG / Natural Gas",
        "Furnace Oil", "Coal (Bituminous)", "Petrol"
    ],
    "IPCC Name": [
        "Gas/Diesel Oil", "Liquefied Petroleum Gases", "Natural Gas",
        "Residual Fuel Oil", "Other Bituminous Coal", "Motor Gasoline"
    ],
    "Emission Factor": [2.65, 2.99, 1.93, 2.97, 2441.0, 2.24],
    "Unit": [
        "kg CO₂ per litre", "kg CO₂ per kg",
        "kg CO₂ per SCM", "kg CO₂ per litre",
        "kg CO₂ per tonne", "kg CO₂ per litre"
    ],
    "Source": [
        "IPCC 2006 Vol.2 Ch.2 Table 2.2",
        "IPCC 2006 Vol.2 Ch.2 Table 2.2",
        "IPCC 2006 Vol.2 Ch.2 Table 2.2",
        "IPCC 2006 Vol.2 Ch.2 Table 2.2",
        "IPCC 2006 Vol.2 Ch.2 Table 2.2",
        "IPCC 2006 Vol.2 Ch.2 Table 2.2"
    ]
})

st.markdown("#### Fugitive Emissions — Refrigerants")
st.markdown("""
Refrigerant leakage is calculated using Global Warming Potential (GWP)
values from IPCC Fifth Assessment Report (AR5):

> Fugitive CO₂e (tCO₂e) = Refrigerant topped-up (kg) × GWP ÷ 1,000
""")
st.table({
    "Refrigerant": ["R-22", "R-410A", "R-32", "R-134a", "R-407C"],
    "GWP (AR5)":   [1810,    2088,     675,    1430,     1774],
    "Source":      ["IPCC AR5"] * 5
})

st.markdown("#### Process Emissions — Welding CO₂")
st.markdown("""
CO₂ used as shielding gas in MIG/MAG welding is directly released
into the atmosphere. No emission factor is needed:

> Welding CO₂e (tCO₂e) = CO₂ gas consumed (kg) ÷ 1,000

For C25 mixed gas (75% Argon, 25% CO₂): multiply total gas kg by 0.25
to get CO₂ component. Argon has zero GWP and is not included.
""")

st.markdown("---")

# ── SECTION 2: SCOPE 2 ────────────────────────────────────────────────
st.subheader("2️⃣ How Scope 2 is Calculated")
st.markdown("""
Scope 2 covers **indirect emissions** from purchased electricity.
This tool calculates both methods required by the GHG Protocol
Scope 2 Guidance (2015):
""")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    **Location-Based Method**

    Uses the average emission intensity of the state electricity grid:

    > Scope 2 (tCO₂) = Grid kWh × State EF (kg CO₂/kWh) ÷ 1,000

    Captive solar generation is deducted from grid consumption before
    applying the emission factor.
    """)

with col2:
    st.markdown("""
    **Market-Based Method**

    Accounts for Renewable Energy Certificates (RECs) purchased
    from the Indian Energy Exchange (IEX):

    > Adjusted kWh = Grid kWh − Solar kWh − (RECs × 1,000)
    > Scope 2 (tCO₂) = Adjusted kWh × State EF ÷ 1,000

    1 REC = 1 MWh = 1,000 kWh of renewable electricity
    """)

st.markdown("#### State-Wise Grid Emission Factors (FY 2024-25)")
st.markdown("Source: Central Electricity Authority (CEA) CO₂ Baseline Database 2024-25")

st.table({
    "State": [
        "Maharashtra", "Tamil Nadu", "Gujarat", "Karnataka",
        "Haryana", "Jharkhand", "Uttar Pradesh", "Rajasthan",
        "Andhra Pradesh", "Telangana", "Punjab",
        "Madhya Pradesh", "West Bengal", "Odisha",
        "Chhattisgarh", "Delhi", "Uttarakhand", "Kerala"
    ],
    "Grid EF (kg CO₂/kWh)": [
        0.876, 0.844, 0.756, 0.650,
        0.946, 0.968, 0.934, 0.901,
        0.955, 0.850, 0.851,
        0.904, 0.970, 0.881,
        0.954, 0.413, 0.021, 0.009
    ],
    "Grid Character": [
        "Mixed — coal + growing solar",
        "Mixed — wind + coal",
        "Mixed — coal + solar",
        "Renewables dominant",
        "Coal dominant",
        "Coal dominant — highest EF",
        "Coal dominant",
        "Coal + large solar addition",
        "Coal + solar",
        "Coal + solar",
        "Mixed",
        "Coal dominant",
        "Coal dominant",
        "Coal dominant",
        "Coal dominant",
        "Import-heavy — lower EF",
        "Hydro dominant",
        "Hydro dominant — lowest EF"
    ]
})

st.markdown("---")

# ── SECTION 3: CPRI SCORING ───────────────────────────────────────────
st.subheader("3️⃣ Carbon Price Readiness Index (CPRI) — Scoring Methodology")
st.markdown("""
The CPRI is a composite score (0–100) measuring how prepared a supplier
is for India's emerging Carbon Credit Trading Scheme (CCTS) under the
Energy Conservation (Amendment) Act 2022.
""")

st.markdown("#### Pillar Structure and Weights")
st.table({
    "Pillar": [
        "P1 — GHG Measurement & Data Quality",
        "P2 — Governance & Strategy",
        "P3 — Investment Readiness",
        "P4 — Regulatory & Market Awareness",
        "P5 — Human Capital"
    ],
    "Max Points": [25, 25, 20, 20, 10],
    "Weight":     ["25%", "25%", "20%", "20%", "10%"],
    "Key Driver": [
        "Data tracking system, baseline, verification",
        "Board review frequency, emissions targets, ICP",
        "CAPEX pipeline, investments made, barriers",
        "CCTS awareness, OEM pressure, CBAM",
        "Trained staff, system sophistication"
    ]
})

st.markdown("#### Classification Bands")
st.table({
    "Score":  ["0–19", "20–39", "40–59", "60–74", "75–100"],
    "Band":   ["Unaware", "Emerging", "Developing", "Advancing", "Leading"],
    "Colour": ["⬛ Grey", "🟤 Bronze", "🔵 Silver", "🟡 Gold", "🟢 Platinum"],
    "CCTS Risk": ["Critical", "High", "Moderate", "Low-Moderate", "Low"],
    "Meaning": [
        "No measurement, no awareness — maximum financial exposure",
        "Some tracking but no strategy or investment pipeline",
        "Measurement foundation in place, governance beginning",
        "Active strategy, board ownership, investment pipeline",
        "Verified data, SBTi targets, ICP in use, investments made"
    ]
})

st.markdown("---")

# ── SECTION 4: MAC CURVE ──────────────────────────────────────────────
st.subheader("4️⃣ Marginal Abatement Cost (MAC) Curve — Methodology")
st.markdown("""
The MAC curve ranks decarbonisation interventions by cost-effectiveness.
Each bar represents one intervention.

**Bar Width** = Annual CO₂ Abated (tCO₂/year)

**Bar Height** = Net Cost per tCO₂ Abated (INR/tCO₂)

**Formula:**
> Annualised Capital Cost = Total Capital Cost ÷ Useful Life (years)
>
> Net Annual Cost = (Annualised Capital + O&M) − Annual Energy Saving
>
> MAC Cost (INR/tCO₂) = Net Annual Cost ÷ Annual CO₂ Abated

**Negative MAC value** = Intervention saves money while reducing CO₂.
No carbon price needed to justify action.

**Positive MAC value** = Costs money. Financially justified only when
carbon price exceeds this value.
""")

st.markdown("#### MAC Curve Interventions — Base Data")
st.table({
    "Intervention": [
        "Waste Heat Recovery", "PNG/CNG Fuel Switch",
        "LED Lighting Retrofit", "IE3 Motor Upgrade",
        "Solar Rooftop (100 kWp)", "Variable Frequency Drives",
        "Efficient Compressor", "REC Purchase"
    ],
    "Capital Cost (INR)": [
        "₹30 Lakhs", "₹1 Lakh", "₹20 Lakhs", "₹2 Lakhs",
        "₹40 Lakhs", "₹24 Lakhs", "₹8 Lakhs", "Zero"
    ],
    "Useful Life": [
        "10 yrs", "10 yrs", "15 yrs", "15 yrs",
        "25 yrs", "10 yrs", "10 yrs", "Annual"
    ],
    "Primary Source": [
        "TERI CDM case studies",
        "MGL/IGL connection data",
        "EESL LED programme",
        "IndianElectric.com / BEE",
        "MNRE Annual Report 2024-25",
        "PCRA compressed air guide",
        "PCRA energy efficiency guide",
        "IEX REC market data 2024"
    ]
})

st.markdown("""
**Note on Solar Rooftop:** Capital cost and CO₂ abatement are scaled
automatically based on the supplier's reported built-up area
(1 kWp per 100 sq ft, maximum 500 kWp). Annual saving uses
state-specific industrial electricity tariff.

**Note on RECs:** REC purchase is a **reporting instrument** only —
it allows market-based Scope 2 reporting but does not physically
reduce emissions. The MAC cost shown is the cost per tCO₂ of
reported reduction, not physical abatement.
""")

st.markdown("---")

# ── SECTION 5: CARBON COST EXPOSURE ──────────────────────────────────
st.subheader("5️⃣ Carbon Cost Exposure Scenarios")
st.markdown("""
Carbon cost exposure is calculated at three price scenarios reflecting
India's CCTS development trajectory:
""")

st.table({
    "Scenario": [
        "INR 500 / tCO₂",
        "INR 1,000 / tCO₂",
        "INR 2,000 / tCO₂"
    ],
    "Represents": [
        "Conservative — early CCTS phase, limited compliance pressure",
        "Mid-range — comparable to China ETS years 2-3",
        "High — comparable to EU ETS at policy maturity (2021-22)"
    ],
    "Source": [
        "BEE CCTS consultation documents",
        "World Bank State & Trends of Carbon Pricing 2024",
        "ICAP EU ETS historical price data"
    ]
})

st.markdown("""
**Formula:**
> Annual Carbon Cost (INR) = Total Scope 1+2 Emissions (tCO₂) × Carbon Price (INR/tCO₂)
>
> EBITDA Impact (%) = Annual Carbon Cost ÷ Estimated EBITDA × 100

EBITDA is estimated at 10% of annual revenue — consistent with
median EBITDA margins for Indian auto component SMEs
(Source: ACMA Annual Report 2023-24).
""")

st.markdown("---")

# ── SECTION 6: DATA SOURCES ───────────────────────────────────────────
st.subheader("6️⃣ Primary Data Sources")

st.table({
    "Data":  [
        "State grid emission factors",
        "Fuel combustion emission factors",
        "Net Calorific Values for unit conversion",
        "Refrigerant GWP values",
        "Solar benchmark cost",
        "Solar capacity factor",
        "Industrial electricity tariffs",
        "REC market prices",
        "MAC curve technology costs",
        "Sector energy benchmarks",
        "CCTS carbon price scenarios"
    ],
    "Source": [
        "Central Electricity Authority (CEA) — CO₂ Baseline Database 2024-25",
        "IPCC 2006 Guidelines Vol.2 Ch.2 Table 2.2",
        "IPCC 2006 Guidelines Vol.2 Ch.1 Table 1.2",
        "IPCC Fifth Assessment Report (AR5) — GWP values",
        "MNRE Annual Report 2024-25",
        "PVGIS Tool — European Commission JRC (2024)",
        "State Electricity Regulatory Commission tariff orders FY2024-25",
        "Indian Energy Exchange (IEX) REC Market Data 2024",
        "BEE Best Practice Guides, EESL, PCRA, TERI CDM case studies",
        "BRSR Barometer 2023 — StepChange (63 GJ/Cr for auto components)",
        "BEE CCTS consultation, World Bank Carbon Pricing Dashboard 2024"
    ]
})

st.markdown("---")

# ── SECTION 7: LIMITATIONS ────────────────────────────────────────────
st.subheader("7️⃣ Limitations & Assumptions")
st.markdown("""
**Scope covered:** This tool calculates Scope 1 and Scope 2 emissions only.
Scope 3 emissions (upstream supply chain, downstream use of sold products)
are outside the current scope.

**Sector:** Calibrated for Indian auto component manufacturers.
Emission factors and MAC curve costs may not be accurate for other sectors.

**EBITDA assumption:** Estimated at 10% of revenue for all companies.
Actual EBITDA varies significantly by sub-sector and company size.

**MAC curve:** Base costs are derived from published benchmarks
and may vary from actual market prices depending on location,
vendor, system size, and installation complexity.

**Grid emission factors:** State EFs are from CEA FY2024-25 data.
These change annually as India's renewable energy capacity grows.
Companies in high-renewable states (Karnataka, Tamil Nadu) will see
faster reduction in their Scope 2 over time.

**Data reliability:** Emissions calculations are only as accurate
as the input data provided by suppliers. Metered and invoiced data
produces more reliable results than estimates.

**Research context:** This tool was developed as part of an MBA
research project at IIT Roorkee under Prof. Tarun Sharma,
Department of Management Studies. The tool is a research prototype
and should not be used as the sole basis for regulatory compliance
or financial decisions.
""")

st.markdown("---")

# ── FOOTER ────────────────────────────────────────────────────────────
st.markdown("""
**Research Project:** Carbon Price Readiness of Indian Manufacturing SMEs

**Institution:** IIT Roorkee — Department of Management Studies

**Supervisor:** Prof. Tarun Sharma

**Student:** Adil Rahiman — MBA Candidate 2024-26

**Data Sources:** CEA, IPCC 2006, MNRE 2024-25, IEX, BEE, EESL, PCRA, TERI

**Last Updated:** April 2026
""")