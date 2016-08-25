import sys, math
import algorithm

def degrees_to_radians(angle):
    rad = math.pi * angle / 180.0
    return rad
    
def radians_to_degrees(rad):
    deg = 180.0 * rad / math.pi
    return deg

def xyz2latlon(xyz):
    latlon_radians = algorithm.xyz2angles(xyz)
    lat_deg = radians_to_degrees(latlon_radians[0])
    lon_deg = radians_to_degrees(latlon_radians[1])
    return [lat_deg, lon_deg]
    
def latlon2xyz(latlon_deg):
    xyz = algorithm.angles2xyz([degrees_to_radians(latlon_deg[0]), degrees_to_radians(latlon_deg[1])])
    return xyz

def geo(hash):
    vector = algorithm.vector(hash)
    ll = xyz2latlon(vector)
    return ll

def hash(lat_deg, lon_deg, level, search_level=0):
    xyz = latlon2xyz([lat_deg, lon_deg])
    return algorithm.hash(xyz, level, search_level)