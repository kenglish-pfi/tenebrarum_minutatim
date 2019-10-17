import os, sys
import urllib.request  # Python 3

OUI_ENV_VAL='WIRESHARK_OUI_DB_PATH'

__D = {}
__OUI_DB_PATH="./wireshark_oui.txt"

def __init__():
    if OUI_ENV_VAL in os.environ:
        __OUI_DB_PATH = os.environ[OUI_ENV_VAL]
#

def fetchDB():
    urllib.request.urlretrieve('https://code.wireshark.org/review/gitweb?p=wireshark.git;a=blob_plain;f=manuf', __OUI_DB_PATH)
#

def cleanOui(oui):
    if "/36" in oui:
        oui = oui[0:13]
    elif "/28" in oui:
        oui = oui[0:10]
    return oui
#
def loadDB():
    if not os.path.isfile(__OUI_DB_PATH):
        fetchDB()
    with open(__OUI_DB_PATH) as f:
        for line in f:
            if line[0] == '#':
                continue
            line = line.rstrip()
            A = line.split('\t')
            if len(A) == 3:
                (oui, short_name, long_name) = A
                if '/' in oui:
                    oui = cleanOui(oui)
                __D[oui] = [short_name, long_name]
#

# When approx == True, we will take the next least OUI as the assumed answer
def lookupOUI(mac, approx=False):
    if len(__D) == 0:
        loadDB()
    short_name, long_name = ["",""]
    for oui in [mac[0:13], mac[0:10], mac[0:8]]: # try /36 then /28 then /24
        if oui in __D:
            short_name, long_name = __D[oui]
            approx = False
            break
    if short_name == "" and approx:
        keys = sorted(__D.keys())
        # TODO: maybe speed up with binary search?
        for i in range(len(keys)):
            if keys[i] > mac[0:8] and i > 0:  # ignoring /36, /28 possibilties they shouldn't ever fall into this case
                oui = keys[i-1]
                short_name, long_name = __D[oui]
                break
    #
    return short_name, long_name, approx
#

if __name__ == "__main__":
    mac = sys.argv[1]
    short_name, long_name, approx = lookupOUI(mac, approx=True)
    print('\t'.join([mac, short_name, long_name, str(approx)]))
#

#  Tests
#
# # A /36
# $ ~/anaconda3/bin/python wiresharkoui.py 70:B3:D5:FE:D0:01
# ('NironPro', 'Niron systems & Projects')
#
# # A /28
# $ ~/anaconda3/bin/python wiresharkoui.py FC:D2:B6:90:00:01
# ('Winglet', 'Winglet Systems Inc.')
#
# # A /24
# $ ~/anaconda3/bin/python wiresharkoui.py D4:81:CA:00:00:01
# ('Idevices', 'iDevices, LLC')
#
# # A /24 gap -- Shenzhen Fast owns D4:83:04, but no one is assigned to D4:83:05
# $ ~/anaconda3/bin/python wiresharkoui.py D4:83:05:00:00:01
# ('Shenzhen', 'Shenzhen Fast Technologies Co.,Ltd')
