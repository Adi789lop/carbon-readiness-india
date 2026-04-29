"""
MAC Curve Engine — aligned with Paper Table 4 (Final Version)
Profile 2: Medium SME, Maharashtra reference
Tariff: ₹8.50/kWh (MERC HT industrial FY2024-25)
Grid EF: 0.876 kg CO2/kWh (CEA 2024-25)
"""

import pandas as pd

# ── STATE-SPECIFIC PARAMETERS ──────────────────────────────────────
STATE_EF = {
    'MAHARASHTRA': 0.876, 'TAMIL NADU': 0.844, 'GUJARAT': 0.756,
    'KARNATAKA': 0.650, 'HARYANA': 0.946, 'JHARKHAND': 0.968,
    'UTTAR PRADESH': 0.934, 'RAJASTHAN': 0.901, 'ANDHRA PRADESH': 0.955,
    'TELANGANA': 0.850, 'PUNJAB': 0.851, 'MADHYA PRADESH': 0.904,
    'ODISHA': 0.881, 'WEST BENGAL': 0.970, 'CHHATTISGARH': 0.954,
    'DELHI': 0.413, 'UTTARAKHAND': 0.021, 'KERALA': 0.009, 'OTHER': 0.82
}

# Industrial electricity tariff per state (INR/kWh) - FY2024-25
TARIFF = {
    'MAHARASHTRA': 8.50, 'TAMIL NADU': 7.50, 'GUJARAT': 7.00,
    'KARNATAKA': 7.20, 'HARYANA': 8.00, 'JHARKHAND': 6.50,
    'UTTAR PRADESH': 7.50, 'RAJASTHAN': 7.50, 'ANDHRA PRADESH': 7.20,
    'TELANGANA': 7.50, 'PUNJAB': 7.30, 'MADHYA PRADESH': 7.40,
    'ODISHA': 6.80, 'WEST BENGAL': 7.80, 'CHHATTISGARH': 6.50,
    'DELHI': 9.00, 'UTTARAKHAND': 5.50, 'KERALA': 7.00, 'OTHER': 8.00
}

# Solar capacity factor by state (annual generation per kWp)
SOLAR_CF = {
    'MAHARASHTRA': 1664, 'TAMIL NADU': 1750, 'GUJARAT': 1800,
    'KARNATAKA': 1700, 'HARYANA': 1600, 'JHARKHAND': 1500,
    'UTTAR PRADESH': 1550, 'RAJASTHAN': 1900, 'ANDHRA PRADESH': 1750,
    'TELANGANA': 1700, 'PUNJAB': 1500, 'MADHYA PRADESH': 1700,
    'ODISHA': 1500, 'WEST BENGAL': 1400, 'CHHATTISGARH': 1600,
    'DELHI': 1500, 'UTTARAKHAND': 1300, 'KERALA': 1400, 'OTHER': 1600
}


def get_interventions(responses, state, area_sqft):
    """
    Returns a DataFrame of MAC curve interventions personalised for
    the supplier's state, area, and existing implementations.

    Aligned with research paper Table 4 (Profile 2 reference).
    """

    state = state.upper()
    ef = STATE_EF.get(state, 0.82)
    tariff = TARIFF.get(state, 8.00)

    # Already-implemented interventions are filtered out
    implemented = responses.get('E5', [])
    segment = responses.get('A4', '')
    has_diesel = responses.get('B1_diesel', 0) > 0

    interventions = []

    # ── 1. WASTE HEAT RECOVERY ───────────────────────────────────
    # Only relevant for energy-intensive segments
    if 'Waste heat recovery' not in implemented and segment in [
        'Engine & Exhaust', 'Body/Chassis', 'Transmission & Steering'
    ]:
        cap = 30_00_000
        life = 10
        om_pct = 0.03
        fuel_saved_litres = 20000
        fo_price = 67.21
        fo_ef = 2.97

        ann_cap = cap / life
        ann_om = cap * om_pct
        ann_save = fuel_saved_litres * fo_price
        co2 = fuel_saved_litres * fo_ef / 1000
        net_cost = (ann_cap + ann_om) - ann_save
        mac = net_cost / co2
        payback = cap / ann_save if ann_save > 0 else None

        interventions.append({
            'intervention': 'Waste Heat Recovery',
            'capital': cap, 'annual_saving': ann_save,
            'co2_abated': round(co2, 1),
            'mac_cost': round(mac, 0),
            'payback_yrs': round(payback, 1) if payback else None
        })

    # ── 2. PNG/CNG FUEL SWITCH ───────────────────────────────────
    if 'Fuel switch to PNG/CNG' not in implemented and has_diesel:
        cap = 1_00_000
        life = 10
        om_pct = 0.01
        diesel_replaced_litres = 10000
        price_diff = 35  # INR/litre saving from diesel to PNG
        diesel_ef = 2.65

        ann_cap = cap / life
        ann_om = cap * om_pct
        ann_save = diesel_replaced_litres * price_diff
        co2 = diesel_replaced_litres * diesel_ef / 1000
        net_cost = (ann_cap + ann_om) - ann_save
        mac = net_cost / co2
        payback = cap / ann_save if ann_save > 0 else None

        interventions.append({
            'intervention': 'PNG/CNG Fuel Switch',
            'capital': cap, 'annual_saving': ann_save,
            'co2_abated': round(co2, 1),
            'mac_cost': round(mac, 0),
            'payback_yrs': round(payback, 1) if payback else None
        })

    # ── 3. LED LIGHTING RETROFIT ─────────────────────────────────
    if 'LED lighting retrofit' not in implemented:
        # Scale fittings by facility area: 1 fitting per 250 sq ft
        fittings = max(int(area_sqft / 250), 50) if area_sqft > 0 else 200
        cap = fittings * 10000  # INR 10,000 per fitting
        life = 15
        om_pct = 0.01
        watts_saved = 250  # 400W MH replaced with 150W LED
        operating_hours = 4800  # 16 hrs/day × 300 days
        kwh_saved = fittings * watts_saved * operating_hours / 1000

        ann_cap = cap / life
        ann_om = cap * om_pct
        ann_save = kwh_saved * tariff
        co2 = kwh_saved * ef / 1000
        net_cost = (ann_cap + ann_om) - ann_save
        mac = net_cost / co2
        payback = cap / ann_save if ann_save > 0 else None

        interventions.append({
            'intervention': 'LED Lighting Retrofit',
            'capital': cap, 'annual_saving': round(ann_save),
            'co2_abated': round(co2, 1),
            'mac_cost': round(mac, 0),
            'payback_yrs': round(payback, 1) if payback else None
        })

    # ── 4. SOLAR ROOFTOP ─────────────────────────────────────────
    if 'Solar rooftop' not in implemented:
        # 1 kWp per 100 sq ft, max 500 kWp
        kwp = min(area_sqft / 100, 500) if area_sqft > 0 else 100
        cap = kwp * 40000  # INR 40,000 per kWp installed
        life = 25
        om_pct = 0.01
        solar_cf = SOLAR_CF.get(state, 1600)
        kwh_generated = kwp * solar_cf

        ann_cap = cap / life
        ann_om = cap * om_pct
        ann_save = kwh_generated * tariff
        co2 = kwh_generated * ef / 1000
        net_cost = (ann_cap + ann_om) - ann_save
        mac = net_cost / co2 if co2 > 0 else 0
        payback = cap / ann_save if ann_save > 0 else None

        interventions.append({
            'intervention': f'Solar Rooftop ({int(kwp)} kWp)',
            'capital': round(cap), 'annual_saving': round(ann_save),
            'co2_abated': round(co2, 1),
            'mac_cost': round(mac, 0),
            'payback_yrs': round(payback, 1) if payback else None
        })

    # ── 5. VARIABLE FREQUENCY DRIVES (per kW) ─────────────────────
    if 'VFDs' not in implemented:
        # Quoted per kW of motor capacity for clarity
        cap = 8000
        life = 10
        om_pct = 0.02
        kwh_saved_per_kw = 300  # 30% saving on 1000 hrs/yr at full load
        ann_cap = cap / life
        ann_om = cap * om_pct
        ann_save = kwh_saved_per_kw * tariff
        co2 = kwh_saved_per_kw * ef / 1000
        net_cost = (ann_cap + ann_om) - ann_save
        mac = net_cost / co2
        payback = cap / ann_save if ann_save > 0 else None

        interventions.append({
            'intervention': 'Variable Frequency Drives (per kW)',
            'capital': cap, 'annual_saving': round(ann_save),
            'co2_abated': round(co2, 2),
            'mac_cost': round(mac, 0),
            'payback_yrs': round(payback, 1) if payback else None
        })

    # ── 6. EFFICIENT COMPRESSOR ──────────────────────────────────
    cap = 8_00_000
    life = 10
    om_pct = 0.02
    kwh_saved = 30000  # 15% saving on 200,000 kWh baseline
    ann_cap = cap / life
    ann_om = cap * om_pct
    ann_save = kwh_saved * tariff
    co2 = kwh_saved * ef / 1000
    net_cost = (ann_cap + ann_om) - ann_save
    mac = net_cost / co2
    payback = cap / ann_save if ann_save > 0 else None

    interventions.append({
        'intervention': 'Efficient Compressor',
        'capital': cap, 'annual_saving': round(ann_save),
        'co2_abated': round(co2, 1),
        'mac_cost': round(mac, 0),
        'payback_yrs': round(payback, 1) if payback else None
    })

    # ── 7. IE3 MOTOR UPGRADE (per 10 kW) ─────────────────────────
    if 'IE3 motors' not in implemented:
        cap = 1_00_000  # premium for 10 kW IE3 over IE1
        life = 15
        om_pct = 0.01
        kwh_saved = 2020  # 5-8% efficiency gain
        ann_cap = cap / life
        ann_om = cap * om_pct
        ann_save = kwh_saved * tariff
        co2 = kwh_saved * ef / 1000
        net_cost = (ann_cap + ann_om) - ann_save
        mac = net_cost / co2
        payback = cap / ann_save if ann_save > 0 else None

        interventions.append({
            'intervention': 'IE3 Motor Upgrade (per 10 kW)',
            'capital': cap, 'annual_saving': round(ann_save),
            'co2_abated': round(co2, 2),
            'mac_cost': round(mac, 0),
            'payback_yrs': round(payback, 1) if payback else None
        })

    # ── 8. REC PURCHASE (per MWh) ────────────────────────────────
    rec_price = 2500  # INR per REC = INR per MWh (IEX 2024-25)
    co2_per_mwh = ef  # 1 MWh × EF = tCO2 reported
    mac_rec = rec_price / co2_per_mwh

    interventions.append({
        'intervention': 'REC Purchase (per MWh)',
        'capital': 0, 'annual_saving': 0,
        'co2_abated': round(co2_per_mwh, 3),
        'mac_cost': round(mac_rec, 0),
        'payback_yrs': None
    })

    df = pd.DataFrame(interventions)
    df = df.sort_values('mac_cost').reset_index(drop=True)
    df.insert(0, 'rank', df.index + 1)

    return df