import pandas as pd
import os
from engine.scope2 import get_ef

TARIFF = {
    'MAHARASHTRA': 8.50, 'TAMIL NADU': 7.50,
    'GUJARAT': 8.00, 'KARNATAKA': 7.80,
    'HARYANA': 8.00, 'JHARKHAND': 6.50
}

FURNACE = ['Engine & Exhaust', 'Transmission & Steering', 'Suspension & Braking']

INTERVENTIONS = [
    {'id':'WHR',   'name':'Waste Heat Recovery',      'capital':3000000, 'saving_base':1800000, 'co2_base':59.4,  'life':10, 'om':0.03, 'segments':'furnace'},
    {'id':'PNG',   'name':'PNG/CNG Fuel Switch',       'capital':100000,  'saving_base':400000,  'co2_base':26.5,  'life':10, 'om':0.01, 'segments':'diesel'},
    {'id':'LED',   'name':'LED Lighting Retrofit',     'capital':2000000, 'saving_base':4900000, 'co2_base':613.0, 'life':15, 'om':0.01, 'segments':'all'},
    {'id':'MOTOR', 'name':'IE3 Motor Upgrade',         'capital':200000,  'saving_base':282800,  'co2_base':35.4,  'life':15, 'om':0.01, 'segments':'all'},
    {'id':'SOLAR', 'name':'Solar Rooftop',             'capital':4000000, 'saving_base':1165080, 'co2_base':145.8, 'life':25, 'om':0.01, 'segments':'all'},
    {'id':'VFD',   'name':'Variable Frequency Drives', 'capital':2400000, 'saving_base':630000,  'co2_base':78.8,  'life':10, 'om':0.02, 'segments':'all'},
    {'id':'COMP',  'name':'Efficient Compressor',      'capital':800000,  'saving_base':210000,  'co2_base':26.3,  'life':10, 'om':0.02, 'segments':'all'},
    {'id':'REC',   'name':'REC Purchase',              'capital':0,       'saving_base':0,       'co2_base':438.0, 'life':1,  'om':0.00, 'segments':'all'},
]

def get_interventions(responses: dict, state: str, area_sqft: float) -> pd.DataFrame:
    done    = [x.upper() for x in responses.get('E5', [])]
    segment = responses.get('A4', '')
    ef      = get_ef(state)
    tariff  = TARIFF.get(state.upper(), 7.50)
    diesel  = responses.get('B1_diesel', 0)

    rows = []
    for inv in INTERVENTIONS:
        iid = inv['id']
        if iid in done: continue
        if iid == 'WHR' and segment not in FURNACE: continue
        if iid == 'PNG' and diesel == 0: continue

        cap  = float(inv['capital'])
        save = float(inv['saving_base'])
        co2  = float(inv['co2_base'])

        if iid == 'SOLAR':
            kWp   = min((area_sqft / 100) * 0.8, 500)
            scale = kWp / 100
            cap   = cap * scale
            save  = kWp * 1200 * tariff
            co2   = kWp * 1200 * ef / 1000

        life    = float(inv['life'])
        ann_cap = cap / life
        ann_om  = cap * float(inv['om'])
        net     = (ann_cap + ann_om) - save
        mac     = round(net / co2, 0) if co2 > 0 else 0
        payback = round(cap / save, 1) if save > 0 else 99

        rows.append({
            'id': iid, 'name': inv['name'],
            'capital': cap, 'saving': save,
            'co2': round(co2, 1), 'mac': mac,
            'payback': payback,
            'colour': 'green' if mac < 0 else 'red'
        })

    df = pd.DataFrame(rows)
    return df.sort_values('mac') if not df.empty else df