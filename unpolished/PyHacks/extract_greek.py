import sys
import unicodedata

def safeGetCharName(c):
    name = ""
    try:
        name = unicodedata.name(a)
    except:
        pass
    return name
#

current = ""
for line in sys.stdin:
    if len(current) > 0:
        print(current)
    current = ""
    for a in line:
        name = safeGetCharName(a)
        if "GREEK" in name:
            current += a
        else:
            if len(current) > 0:
                print(current)
            current = ""
#

if len(current) > 0:
    print(current)
