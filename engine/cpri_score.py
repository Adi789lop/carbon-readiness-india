def score(r: dict) -> dict:

    # PILLAR 1 — GHG Measurement (25 pts)
    p1 = 0
    d1_map = {
        'Real-time IoT': 4,
        'Automated ERP': 3,
        'Manual Excel': 1,
        'No tracking': 0
    }
    p1 += d1_map.get(r.get('D1', 'No tracking'), 0)

    d2_map = {
        '3rd Party Verified': 6,
        'Internal': 3,
        'No': 0
    }
    p1 += d2_map.get(r.get('D2', 'No'), 0)

    d3_map = {
        'Third-party': 4,
        'Internal audit': 2,
        'No': 0
    }
    p1 += d3_map.get(r.get('D3', 'No'), 0)

    d4_map = {
        'Fully integrated': 5,
        'Specific machines': 3,
        'No': 0
    }
    p1 += d4_map.get(r.get('D4', 'No'), 0)

    b1_map = {
        'Metered/Invoiced': 2,
        'Mixed': 1,
        'Estimate': 0
    }
    p1 += b1_map.get(r.get('B1_rel', ''), 0)

    c2_map = {
        'Actual bills': 4,
        'Approximate': 2,
        'Best available': 0
    }
    p1 += c2_map.get(r.get('C2', ''), 0)

    # PILLAR 2 — Governance (25 pts)
    p2 = 0
    e1_map = {
        'Quarterly ESG': 8,
        'Annually cost': 4,
        'Never': 0
    }
    p2 += e1_map.get(r.get('E1', 'Never'), 0)

    e2_map = {
        'SBTi Committed': 10,
        'Written Policy': 6,
        'Cost goal': 2,
        'No target': 0
    }
    p2 += e2_map.get(r.get('E2', 'No target'), 0)

    icp = r.get('E3_val', 0)
    if r.get('E3') == 'Yes' and icp >= 500:
        p2 += 7
    elif r.get('E3') == 'Yes':
        p2 += 4
    elif r.get('E3') == 'No ROI':
        p2 += 1

    # PILLAR 3 — Investment Readiness (20 pts)
    p3 = 0
    e4_map = {
        'Budgeted Approved': 10,
        'Identified': 5,
        'None': 0
    }
    p3 += e4_map.get(r.get('E4', 'None'), 0)
    p3 += min(6, len(r.get('E5', [])) * 1.5)

    g2_map = {
        'No barriers': 4,
        'Technical': 3,
        'No awareness': 2,
        'Lease': 1,
        'Capital': 0
    }
    p3 += g2_map.get(r.get('G2', 'Capital'), 0)

    # PILLAR 4 — Awareness (20 pts)
    p4 = 0
    f1_map = {
        'Monitoring': 8,
        'Aware': 4,
        'Never heard': 0
    }
    p4 += f1_map.get(r.get('F1', 'Never heard'), 0)

    f2_map = {
        'Mandatory': 7,
        'Informal': 4,
        'Not yet': 0
    }
    p4 += f2_map.get(r.get('F2', 'Not yet'), 0)

    g1_map = {
        'Not applicable': 5,
        'Aware': 4,
        'Unaware': 0
    }
    p4 += g1_map.get(r.get('G1', 'Unaware'), 0)

    # PILLAR 5 — Human Capital (10 pts)
    p5 = 0
    f3_map = {
        'BEE Certified': 6,
        '1-2 trained': 3,
        'No training': 0
    }
    p5 += f3_map.get(r.get('F3', 'No training'), 0)
    p5 += d1_map.get(r.get('D1', 'No tracking'), 0)

    # TOTAL AND BAND
    total = int(p1 + p2 + p3 + p4 + p5)

    if total >= 75:
        band, col, risk = 'Leading',    '🟢 Platinum', 'Low'
    elif total >= 60:
        band, col, risk = 'Advancing',  '🟡 Gold',     'Low-Moderate'
    elif total >= 40:
        band, col, risk = 'Developing', '🔵 Silver',   'Moderate'
    elif total >= 20:
        band, col, risk = 'Emerging',   '🟤 Bronze',   'High'
    else:
        band, col, risk = 'Unaware',    '⬛ Grey',     'Critical'

    # TOP RECOMMENDATIONS
    gaps = []
    if r.get('E2') != 'SBTi Committed':
        gaps.append(('Set formal emissions target (E2)', 10))
    if r.get('D3') != 'Third-party':
        gaps.append(('Get data third-party verified (D3)', 4))
    if r.get('F3') == 'No training':
        gaps.append(('Train staff in GHG accounting (F3)', 6))
    if r.get('D2') == 'No':
        gaps.append(('Establish GHG baseline year (D2)', 6))
    if r.get('E1') != 'Quarterly ESG':
        gaps.append(('Elevate to quarterly ESG review (E1)', 4))

    gaps.sort(key=lambda x: x[1], reverse=True)

    return {
        'total': total,
        'band': band,
        'colour': col,
        'risk': risk,
        'pillars': {
            'P1 Measurement':   int(p1),
            'P2 Governance':    int(p2),
            'P3 Investment':    int(p3),
            'P4 Awareness':     int(p4),
            'P5 Human Capital': int(p5)
        },
        'recommendations': gaps[:3]
    }