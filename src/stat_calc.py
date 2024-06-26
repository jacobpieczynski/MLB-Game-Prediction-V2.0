# Helper functions to calculate specific stats
def calc_avg(hits, abs):
    if abs == 0:
        return 0
    return round(hits / abs, 3)

def calc_slg(s, d, t, hr, abs):
    if abs == 0:
        return 0
    return round((s + (d * 2) + (t * 3) + (hr * 4)) / abs, 3)

def calc_obp(h, bb, hbp, abs, sf):
    if abs == 0:
        return 0
    return round((h + bb + hbp) / (abs + bb + hbp + sf), 3)

def calc_ops(slg, avg):
    return round(slg + avg, 3)

def calc_iso(slg, ba):
    return slg - ba

def calc_der(h, roe, hr, pa, bb, so, hbp):
    #The formula for Defensive Efficiency Ratio is: 1 - ((H + ROE - HR) / (PA - BB - SO - HBP - HR))
    if (pa - bb - so - hbp - hr) == 0:
        return 0
    return round(1 - ((h + roe - hr) / (pa - bb - so - hbp - hr)), 3)

def calc_pythag(rs, ra):
    #The initial formula for pythagorean winning percentage was as follows: (runs scored ^ 2) / [(runs scored ^ 2) + (runs allowed ^ 2)] 
    return round((pow(rs, 1.83)) / ((pow(rs, 1.83)) + (pow(ra,1.83))), 3)

# Bill James' Log5 Stat
def calc_log5(homepct, vispct):
    if (homepct + vispct - (2 * homepct * vispct)) == 0:
        return 0
    return round((homepct - (homepct * vispct)) / (homepct + vispct - (2 * homepct * vispct)), 3)

def calc_era(er, ip):
    if ip == 0:
        return 0
    return round((9 * er) / ip, 2)

def calc_whip(h, bb, ip):
    if ip == 0:
        return 0
    return round((h + bb) / ip, 2)

def calc_bb9(bb, ip):
    if ip == 0:
        return 0
    return round((bb / ip) * 9, 2)

def calc_k9(k, ip):
    if ip == 0:
        return 0
    return round((k / ip) * 9, 2)

def calc_hr9(hr, ip):
    if ip == 0:
        return 0
    return round((hr / ip) * 9, 2)

# Using an average constant of 3.1, all it does is average it across the league for a whole season, shouldn't make too much of an impact
# Fielding Independent Pitching
def calc_fip(hr, bb, hbp, k, ip, c=3.1):
    #((13*HR)+(3*(BB+HBP))-(2*K))/IP + constant
    if ip == 0:
        return 0
    return round(((13 * hr) + (3 * (bb + hbp)) - (2 * k)) / ip + c, 2)

# Kerry Whisnant formula to predict team win percentages based on runs scored and given up
def calc_whisnant(rpga, rpgb, slga, slgb):
    """
    W1/L1 = (RPG1/RPG2)^a (SLG1/SLG2)^b
    where
    a = 0.723 (RPG1 + RPG2)^.373
    and b = 0.977 (RPG1 + RPG2)^( -.947)
    """
    a = 0.723 * pow((rpga + rpgb), 0.373)
    b = 0.977 * pow((rpga + rpgb), -0.947)
    return round(pow((rpga / rpgb), a) * pow((slga / slgb), b), 3)