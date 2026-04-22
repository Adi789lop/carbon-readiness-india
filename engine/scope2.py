import pandas as pd
import os

def get_ef(state: str) -> float:
    STATE_EF = {
        'MAHARASHTRA': 0.876,
        'TAMIL NADU': 0.844,
        'GUJARAT': 0.756,
        'KARNATAKA': 0.650,
        'HARYANA': 0.946,
        'JHARKHAND': 0.968,
        'UTTAR PRADESH': 0.934,
        'RAJASTHAN': 0.901,
        'ANDHRA PRADESH': 0.955,
        'TELANGANA': 0.850,
        'PUNJAB': 0.851,
        'MADHYA PRADESH': 0.904,
        'ODISHA': 0.881,
        'WEST BENGAL': 0.970,
        'CHHATTISGARH': 0.954,
        'DELHI': 0.413,
        'UTTARAKHAND': 0.021,
        'KERALA': 0.009,
    }
    return STATE_EF.get(state.upper(), 0.82)

def scope2_location(state, grid_kwh, solar_kwh=0):
    ef = get_ef(state)
    kwh = max(0, grid_kwh - solar_kwh)
    return {
        'ef': ef,
        'kwh': kwh,
        'tco2': round(kwh * ef / 1000, 2),
        'method': 'Location-Based'
    }

def scope2_market(state, grid_kwh, solar_kwh=0, rec_vol=0):
    ef = get_ef(state)
    kwh = max(0, grid_kwh - solar_kwh - (rec_vol * 1000))
    return {
        'ef': ef,
        'kwh': kwh,
        'tco2': round(kwh * ef / 1000, 2),
        'method': 'Market-Based'
    }

def intensity(s1, s2_lb, revenue, production=0, area=0):
    total = s1 + s2_lb
    return {
        'total': round(total, 2),
        'per_cr':    round(total / revenue, 2) if revenue > 0 else 0,
        'per_tonne': round(total / production, 2) if production > 0 else 0,
        'per_sqft':  round((total * 1000) / area, 4) if area > 0 else 0,
        's1_pct':    round(s1 / total * 100, 1) if total > 0 else 0,
        's2_pct':    round(s2_lb / total * 100, 1) if total > 0 else 0,
    }

def carbon_exposure(total_tco2, ebitda_cr):
    out = {}
    for label, price in [('500', 500), ('1000', 1000), ('2000', 2000)]:
        cost = total_tco2 * price
        out[label] = {
            'lakhs':      round(cost / 1e5, 1),
            'crore':      round(cost / 1e7, 2),
            'ebitda_pct': round(cost / 1e7 / ebitda_cr * 100, 1) if ebitda_cr > 0 else 0
        }
    return out