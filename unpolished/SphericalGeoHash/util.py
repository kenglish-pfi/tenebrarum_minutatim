import sys, math

QUARTER_EARTH_CIRCUMFRENCE = 10018750  # in meters

def level_from_meters(meters):
    dist = QUARTER_EARTH_CIRCUMFRENCE
    level = 0
    while dist > meters:
        dist = dist / 2.0
        level = level + 1
    return level
    
def level_to_meters(level):
    return QUARTER_EARTH_CIRCUMFRENCE / math.pow(2.0, level)
    
        
