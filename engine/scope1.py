FUEL_EF = {
    'diesel': 2.65,
    'lpg': 2.99,
    'png': 1.93,
    'furnace_oil': 2.97,
    'coal': 2441.0,
    'petrol': 2.24,
    'cng': 2.02,
}
GWP = {
    'R-22': 1810,
    'R-410A': 2088,
    'R-32': 675,
    'R-134a': 1430,
    'R-407C': 1774
}

def calc_stationary(fuels: dict) -> dict:
    results, total = {}, 0.0
    for fuel, qty in fuels.items():
        if fuel in FUEL_EF and qty > 0:
            t = (qty * FUEL_EF[fuel]) / 1000
            results[fuel] = round(t, 2)
            total += t
    results['total'] = round(total, 2)
    return results

def calc_mobile(vehicles: list) -> float:
    total = 0.0
    for v in vehicles:
        f = v.get('fuel', '').lower()
        q = v.get('quantity', 0)
        if f in FUEL_EF and q > 0:
            total += (q * FUEL_EF[f]) / 1000
    return round(total, 2)

def calc_fugitive(ref_type: str, ref_kg: float, weld_kg: float) -> dict:
    ref  = (ref_kg * GWP.get(ref_type, 0)) / 1000
    weld = weld_kg / 1000
    return {
        'refrigerant': round(ref, 2),
        'welding': round(weld, 2),
        'total': round(ref + weld, 2)
    }

def total_scope1(stat, mobile, fug):
    t = stat.get('total', 0) + mobile + fug.get('total', 0)
    return {
        'stationary': stat.get('total', 0),
        'mobile': mobile,
        'fugitive': fug.get('total', 0),
        'total': round(t, 2)
    }