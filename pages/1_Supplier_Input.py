import streamlit as st
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from engine.scope1 import calc_stationary, calc_mobile, calc_fugitive, total_scope1
from engine.scope2 import scope2_location, scope2_market, intensity, carbon_exposure
from engine.cpri_score import score
from engine.mac_curve import get_interventions
from engine.storage import make_id, save

st.set_page_config(page_title="Supplier Input", layout="wide")
st.title("🏭 Supplier Input — Emissions & Readiness Assessment")
st.markdown("Complete all sections. Fields marked * are required.")
st.markdown("---")

# ── CONSENT ──────────────────────────────────────────────────────────
consent = st.checkbox(
    "I agree: my data will be used to calculate emissions and for anonymised academic research at IIT Roorkee. My company-specific data will not be shared without consent."
)
if not consent:
    st.warning("Please accept the data consent statement to proceed.")
    st.stop()

with st.form("supplier_form"):

    # ── SECTION A ─────────────────────────────────────────────────────
    st.subheader("Section A — Company Profile")
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Company Legal Name *")
        pan          = st.text_input("PAN Number *")
    with col2:
        gst     = st.text_input("GST Number")
        segment = st.selectbox("Primary Auto Component Segment *", [
            "Engine & Exhaust", "Transmission & Steering",
            "Suspension & Braking", "Electrical",
            "Body/Chassis", "Rubber", "Other"
        ])

    col3, col4 = st.columns(2)
    with col3:
        state = st.selectbox("Primary Facility State *", [
            "MAHARASHTRA", "TAMIL NADU", "GUJARAT", "KARNATAKA",
            "HARYANA", "JHARKHAND", "UTTAR PRADESH", "RAJASTHAN",
            "ANDHRA PRADESH", "TELANGANA", "PUNJAB",
            "MADHYA PRADESH", "ODISHA", "WEST BENGAL",
            "CHHATTISGARH", "DELHI", "UTTARAKHAND", "KERALA", "OTHER"
        ])
        city = st.text_input("City / District")
    with col4:
        revenue = st.number_input("Annual Turnover (INR Crore) *", min_value=0.0, step=1.0)
        msme    = st.selectbox("MSME Classification", [
            "Micro (< 10 Cr)", "Small (10–100 Cr)", "Medium (100–500 Cr)"
        ])

    col5, col6 = st.columns(2)
    with col5:
        production = st.number_input("Annual Production Output (Units, optional)", min_value=0.0)
    with col6:
        area_sqft = st.number_input("Total Built-up Area (Sq Ft) *", min_value=0.0)

    st.markdown("---")

    # ── SECTION B1 ────────────────────────────────────────────────────
    st.subheader("Section B1 — Stationary Combustion (Fuel Usage)")
    st.caption("Enter fuel consumed by on-site stationary equipment — diesel generators, boilers, furnaces, process heating. Do NOT include vehicle fuel here.")

    fuels_dict = {}
    b1_reliabilities = []

    fuel_list = [
        ("diesel",      "Diesel / HSD",         "Litres"),
        ("lpg",         "LPG",                  "kg"),
        ("png",         "PNG / Natural Gas",     "Standard Cubic Metres (SCM)"),
        ("furnace_oil", "Furnace Oil",           "Litres"),
        ("coal",        "Coal",                  "Tonnes"),
        ("petrol",      "Petrol",               "Litres"),
    ]

    for fid, fname, funit in fuel_list:
        st.markdown(f"**{fname}**")
        c1, c2, c3 = st.columns([2, 2, 2])
        with c1:
            uses = st.selectbox(
                "Do you use this?",
                ["No", "Yes"],
                key=f"use_{fid}"
            )
        with c2:
            qty = st.number_input(
                f"Quantity ({funit})",
                min_value=0.0,
                value=0.0,
                key=f"qty_{fid}"
            )
        with c3:
            rel = st.selectbox(
                "Data Reliability",
                ["Metered/Invoiced", "Estimate", "Best available"],
                key=f"rel_{fid}"
            )
        if uses == "Yes" and qty > 0:
            fuels_dict[fid] = qty
            b1_reliabilities.append(rel)
        st.markdown("---")

    b1_rel = (
        "Metered/Invoiced" if all(r == "Metered/Invoiced" for r in b1_reliabilities)
        else "Mixed" if b1_reliabilities
        else "Estimate"
    )

    st.markdown("---")

    # ── SECTION B2 ────────────────────────────────────────────────────
    st.subheader("Section B2 — Mobile Combustion (Company Vehicles)")
    st.caption("Enter fuel consumed by company vehicles only — forklifts, cars, trucks. Do NOT include DG set or boiler diesel here. EV charging electricity goes in Section C1.")

    vehicles_list = []
    veh_rows = [
        ("Forklifts / Material Handling", ["diesel", "lpg", "ev"]),
        ("Company Cars (Sales/Admin)",    ["petrol", "diesel", "cng", "ev"]),
        ("Logistics Trucks (Owned)",      ["diesel", "cng"]),
        ("Other Utility Vehicles",        ["petrol", "diesel"]),
    ]

    for vtype, fuel_opts in veh_rows:
        c1, c2, c3 = st.columns(3)
        with c1:
            n = st.number_input(f"No. of {vtype}", min_value=0, step=1, key=f"n_{vtype}")
        with c2:
            vfuel = st.selectbox("Fuel Type", fuel_opts, key=f"f_{vtype}")
        with c3:
            vqty = st.number_input("Fuel Consumed (Litres / kg)", min_value=0.0, key=f"q_{vtype}")
        if n > 0 and vqty > 0 and vfuel != "ev":
            vehicles_list.append({"fuel": vfuel, "quantity": vqty})

    st.markdown("---")

   # ── SECTION B3 ────────────────────────────────────────────────────
    st.subheader("Section B3 — Fugitive & Process Emissions")

    st.markdown("**Refrigerants (HVAC / AC Units)**")
    c1, c2, c3 = st.columns(3)
    with c1:
        has_hvac = st.selectbox(
            "HVAC / AC units on site?",
            ["No", "Yes"],
            key="has_hvac"
        )
    with c2:
        ref_type = st.selectbox(
            "Refrigerant Type",
            ["R-22", "R-410A", "R-32", "R-134a", "R-407C"],
            key="ref_type"
        )
    with c3:
        ref_kg = st.number_input(
            "Refrigerant Topped-Up (kg) — enter 0 if HVAC = No",
            min_value=0.0,
            value=0.0,
            key="ref_kg"
        )

    if has_hvac == "No":
        ref_kg = 0.0
        st.caption("✅ No HVAC — refrigerant emissions set to zero.")
    else:
        gwp_map = {
            "R-22": 1810, "R-410A": 2088,
            "R-32": 675, "R-134a": 1430, "R-407C": 1774
        }
        gwp = gwp_map.get(ref_type, 0)
        if ref_kg > 0:
            co2e_preview = round(ref_kg * gwp / 1000, 2)
            st.caption(
                f"ℹ️ {ref_type} has GWP of {gwp}. "
                f"Your fugitive CO₂e = {ref_kg} kg × {gwp} ÷ 1000 "
                f"= **{co2e_preview} tCO₂e**"
            )

    st.markdown("---")

    st.markdown("**MIG/MAG Welding — Process CO₂**")
    c4, c5 = st.columns(2)
    with c4:
        has_weld = st.selectbox(
            "MIG/MAG Welding on site?",
            ["No", "Yes"],
            key="has_weld"
        )
    with c5:
        weld_kg = st.number_input(
            "Welding CO₂ Gas Consumed (kg) — enter 0 if Welding = No",
            min_value=0.0,
            value=0.0,
            key="weld_kg"
        )

    if has_weld == "No":
        weld_kg = 0.0
        st.caption("✅ No welding — process CO₂ set to zero.")
    else:
        if weld_kg > 0:
            weld_co2e = round(weld_kg / 1000, 4)
            st.caption(
                f"ℹ️ For C25 mixed gas (75% Argon, 25% CO₂): "
                f"multiply total gas kg by 0.25 to get CO₂ component. "
                f"Your welding CO₂e = {weld_kg} kg ÷ 1000 = **{weld_co2e} tCO₂e**"
            )
st.markdown("**Data Reliability — Refrigerant & Welding Gas**")
b3_reliability = st.selectbox(
    "How reliable is your refrigerant and welding gas data?",
    [
        "Actuals from bills provided",
        "Approximate Estimate",
        "Best available estimate"
    ],
    key="b3_reliability"
)

reliability_notes = {
    "Actuals from bills provided":
        "✅ High reliability — sourced from supplier invoices or maintenance records.",
    "Approximate Estimate":
        "⚠️ Medium reliability — based on memory or informal records.",
    "Best available estimate":
        "ℹ️ Low reliability — rough guess. Consider improving tracking for better CPRI score."
}
st.caption(reliability_notes.get(b3_reliability, ""))

    # ── SECTION C ─────────────────────────────────────────────────────
    st.subheader("Section C — Scope 2 (Electricity)")

    c1, c2 = st.columns(2)
    with c1:
        grid_kwh  = st.number_input("Grid Electricity Consumed (kWh/year) *", min_value=0.0)
    with c2:
        c2_source = st.selectbox("Data Source", [
            "Actual kWh from bills", "Approximate Estimate", "Best available estimate"
        ])

    c3, c4, c5 = st.columns(3)
    with c3:
        has_rec = st.selectbox("Do you hold RECs from IEX?", ["No", "Yes"])
    with c4:
        rec_vol = st.number_input("REC Volume (1 REC = 1,000 kWh)", min_value=0, step=1) if has_rec == "Yes" else 0
    with c5:
        solar_kwh = st.number_input("Captive / Rooftop Solar Generation (kWh/year)", min_value=0.0)

    dg_use = st.selectbox("DG Set Usage", [
        "No DG Set", "Emergency Only (< 20 hrs/yr)", "Regular Backup / Peak Shaving"
    ])
    st.caption("Note: Diesel consumed by DG sets should be included in B1 Diesel quantity above.")

    st.markdown("---")

    # ── SECTION D ─────────────────────────────────────────────────────
    st.subheader("Section D — Data Infrastructure")

    c1, c2 = st.columns(2)
    with c1:
        D1 = st.selectbox("How is energy/fuel data tracked?", [
            "No tracking", "Manual Excel sheets (annual)",
            "Automated ERP Module", "Real-time IoT Monitoring"
        ])
        D2 = st.selectbox("Baseline year established?", [
            "No", "Yes — Internal", "Yes — 3rd Party Verified"
        ])
    with c2:
        D3 = st.selectbox("Is data independently verified?", [
            "No", "Internal audit only", "Third-party verified"
        ])
        D4 = st.selectbox("Production-normalised tracking (SEC)?", [
            "No", "Yes — tracked for specific machines",
            "Yes — fully integrated daily"
        ])

    st.markdown("---")

    # ── SECTION E ─────────────────────────────────────────────────────
    st.subheader("Section E — Governance & Strategy")

    c1, c2 = st.columns(2)
    with c1:
        E1 = st.selectbox("Board / Senior Management review frequency?", [
            "Never", "Annually (Cost-focused)", "Quarterly (ESG Agenda)"
        ])
        E2 = st.selectbox("Emissions reduction target?", [
            "No target", "General cost-reduction goal",
            "Written Policy (e.g. % by 2030)", "SBTi Committed"
        ])
    with c2:
        E3 = st.selectbox("Internal Carbon Price (Shadow Price) used?", [
            "Not aware of concept", "No — Only standard ROI", "Yes"
        ])
        E3_value = st.number_input("If Yes — Shadow Price (INR / tCO₂)", min_value=0) if E3 == "Yes" else 0

    E4 = st.selectbox("Decarbonisation CAPEX status?", [
        "None identified", "Identified but not budgeted", "Budgeted and Approved"
    ])

    E5 = st.multiselect("Already implemented (select all that apply):", [
        "LED lighting retrofit", "Solar rooftop", "IE3 motors",
        "VFDs", "Waste heat recovery", "Fuel switch to PNG/CNG"
    ])

    st.markdown("---")

    # ── SECTION F ─────────────────────────────────────────────────────
    st.subheader("Section F — Awareness & External Engagement")

    c1, c2, c3 = st.columns(3)
    with c1:
        F1 = st.selectbox("CCTS Awareness?", [
            "Never heard of it", "Aware (Non-applicable)",
            "Aware (Monitoring Thresholds)"
        ])
    with c2:
        F2 = st.selectbox("Customer carbon requests?", [
            "Not yet", "Informal ESG requests", "Mandatory for onboarding"
        ])
    with c3:
        F3 = st.selectbox("Staff GHG / Energy training?", [
            "No training", "1-2 staff trained", "Certified Energy Manager (BEE)"
        ])

    st.markdown("---")

    # ── SECTION G ─────────────────────────────────────────────────────
    st.subheader("Section G — Risk & Barriers")

    c1, c2 = st.columns(2)
    with c1:
        G1 = st.selectbox("EU CBAM awareness?", [
            "Not applicable (No EU exports)",
            "Unaware of potential costs",
            "Aware & concerned about cost impact"
        ])
    with c2:
        G2 = st.selectbox("Biggest barrier to reducing energy?", [
            "No awareness of available solutions",
            "Lack of Capital / High Interest",
            "Lack of Technical Know-how",
            "Short-term Lease Premises",
            "No barriers — actively reducing"
        ])

    st.markdown("---")

    # ── OPTIONAL WATER & WASTE ────────────────────────────────────────
    with st.expander("📌 Optional — Water & Waste Module (for full ESG Score)"):
        st.caption("Completing this section enables a comprehensive ESG Sustainability Score alongside your CPRI.")
        w1, w2 = st.columns(2)
        with w1:
            water_kwh     = st.number_input("Total Water Consumed (KL/year)", min_value=0.0)
            water_tracked = st.selectbox("Water Tracking Maturity", ["Not measured", "Estimated", "Metered"])
            water_stress  = st.selectbox("Water Stressed Zone?", ["No", "Yes", "Not sure"])
        with w2:
            wastewater    = st.selectbox("Wastewater Treatment Plant?", ["Yes", "No", "Not sure"])
            cpcb          = st.selectbox("CPCB Compliance?", ["Fully compliant", "Partially compliant", "Not sure"])
        waste_track  = st.selectbox("Waste Tracking Maturity", ["No tracking", "Estimation only", "Monthly", "Digitally Audited"])
        haz_comply   = st.multiselect("Hazardous Waste Compliance:", ["HW Authorization", "Manifests", "Storage per norms"])
        waste_reduce = st.multiselect("Waste Reduction Initiatives:", ["Scrap Reduction", "Reuse", "Take-back", "Packaging Optimisation"])
        waste_intens = st.selectbox("Waste Intensity Tracked?", ["Not tracked", "Yes — with kg/unit value"])

    st.markdown("---")

    # ── SUBMIT ────────────────────────────────────────────────────────
    submitted = st.form_submit_button("🔍 Calculate My Score", type="primary")

# ── PROCESS ON SUBMIT ─────────────────────────────────────────────────
if submitted:
    if not company_name or not pan or revenue == 0 or grid_kwh == 0:
        st.error("Please fill all required fields marked *")
        st.stop()

    # Scope 1
    stat = calc_stationary(fuels_dict)
    mob  = calc_mobile(vehicles_list)
    fug  = calc_fugitive(ref_type, ref_kg, weld_kg)
    s1   = total_scope1(stat, mob, fug)

    # Scope 2
    s2_lb  = scope2_location(state, grid_kwh, solar_kwh)
    s2_mb  = scope2_market(state, grid_kwh, solar_kwh, rec_vol)
    total  = s1['total'] + s2_lb['tco2']
    intens = intensity(s1['total'], s2_lb['tco2'], revenue, production, area_sqft)
    ebitda = revenue * 0.10
    exp    = carbon_exposure(total, ebitda)

    # Build responses for scoring
    d2_clean = "3rd Party Verified" if "3rd Party" in D2 else ("Internal" if "Internal" in D2 else "No")
    d3_clean = "Third-party" if "Third-party" in D3 else ("Internal audit" if "Internal" in D3 else "No")
    d1_clean = "Real-time IoT" if "IoT" in D1 else ("Automated ERP" if "ERP" in D1 else ("Manual Excel" if "Manual" in D1 else "No tracking"))
    d4_clean = "Fully integrated" if "fully" in D4 else ("Specific machines" if "specific" in D4 else "No")
    e1_clean = "Quarterly ESG" if "Quarterly" in E1 else ("Annually cost" if "Annually" in E1 else "Never")
    e2_clean = "SBTi Committed" if "SBTi" in E2 else ("Written Policy" if "Written" in E2 else ("Cost goal" if "cost" in E2 else "No target"))
    e3_clean = "Yes" if E3 == "Yes" else ("No ROI" if "ROI" in E3 else "Not aware")
    e4_clean = "Budgeted Approved" if "Budgeted" in E4 else ("Identified" if "Identified" in E4 else "None")
    f1_clean = "Monitoring" if "Monitoring" in F1 else ("Aware" if "Aware" in F1 else "Never heard")
    f2_clean = "Mandatory" if "Mandatory" in F2 else ("Informal" if "Informal" in F2 else "Not yet")
    f3_clean = "BEE Certified" if "BEE" in F3 else ("1-2 trained" if "1-2" in F3 else "No training")
    g1_clean = "Not applicable" if "Not applicable" in G1 else ("Aware" if "Aware" in G1 else "Unaware")
    g2_clean = "No barriers" if "No barriers" in G2 else ("Technical" if "Technical" in G2 else ("No awareness" if "No awareness" in G2 else ("Lease" if "Lease" in G2 else "Capital")))

    responses = {
        'D1': d1_clean, 'D2': d2_clean, 'D3': d3_clean, 'D4': d4_clean,
        'E1': e1_clean, 'E2': e2_clean, 'E3': e3_clean,
        'E3_val': E3_value, 'E4': e4_clean, 'E5': E5,
        'F1': f1_clean, 'F2': f2_clean, 'F3': f3_clean,
        'G1': g1_clean, 'G2': g2_clean,
        'B1_rel': b1_rel,
        'B3_rel': b3_reliability,
        'C2': c2_source,
        'A4': segment, 'B1_diesel': fuels_dict.get('diesel', 0)
    }

    # Score
    cpri   = score(responses)
    mac_df = get_interventions(responses, state, area_sqft)

    # Save
    sid = make_id(company_name, pan)
    save(sid, {
        'company':      company_name,
        'segment':      segment,
        'state':        state,
        'revenue':      revenue,
        'scope1':       s1['total'],
        'scope2_lb':    s2_lb['tco2'],
        'scope2_mb':    s2_mb['tco2'],
        'total':        total,
        'intensity_cr': intens['per_cr'],
        'cpri':         cpri['total'],
        'band':         cpri['band'],
        'exposure':     exp
    })

    # Store in session for Page 2
    st.session_state['r'] = {
        'sid': sid, 's1': s1, 's2_lb': s2_lb, 's2_mb': s2_mb,
        'intensity': intens, 'exp': exp, 'cpri': cpri,
        'mac': mac_df, 'company': company_name,
        'state': state, 'segment': segment
    }

    st.success(f"✅ Calculation complete! Your Supplier ID: **{sid}** — Save this to retrieve your results.")
    st.info("👈 Now click **Supplier Results** in the sidebar to see your full report.")