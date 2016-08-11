import sys, math, numpy, random, os

def A(a):
    return numpy.array(a)

e = 1.0/math.sqrt(2.0)
# Second basis is the first basis rotated 45 degrees on all axes so all endpoints are between all endpoints of first basis
basi = [
    A([ A([0,0,0]), A([1,0,0]), A([0,1,0]), A([0,0,1]), A([-1,0,0]), A([0,-1,0]), A([0,0,-1]) ]), 
    A([ A([0,0,0]), A([(e*e),(e*e),(-e)]),  A([(e*e*e-e*e),(e*e*e+e*e),(e*e)]), A([(e*e*e+e*e),(e*e*e-e*e),(e*e)]), 
                   -A([(e*e),(e*e),(-e)]),  -A([(e*e*e-e*e),(e*e*e+e*e),(e*e)]), -A([(e*e*e+e*e),(e*e*e-e*e),(e*e)]) ])
]
factor = 1.0/math.sqrt(2.0)
skip = A([0,0,0])
        
def soln_value(soln):
    accum = [0,0,0]
    for v in soln:
        accum[0] = accum[0] + v[0]
        accum[1] = accum[1] + v[1]
        accum[2] = accum[2] + v[2]
    denom = math.sqrt( (accum[0]*accum[0]) + (accum[1]*accum[1]) + (accum[2]*accum[2]) )
    accum[0] = accum[0] / denom
    accum[1] = accum[1] / denom
    accum[2] = accum[2] / denom
    return A(accum)

def distance(objective, soln):
    Z = soln_value(soln)
    pre_dist = objective - Z
    dist = math.sqrt((pre_dist[0]*pre_dist[0]) + (pre_dist[1]*pre_dist[1]) + (pre_dist[2]*pre_dist[2]))
    print str(dist) + " := " +repr(Z) + " <=> " + repr(objective)
    return dist

    
def nibble2vect(orientation, index, letter):
    basis_idx = ord(letter) - ord('0')
    if (index & 1) == orientation :
        vect = basi[1][basis_idx]
    else:
        vect = basi[0][basis_idx]
        
    if index > 0:
        pwr = index/2  # assuming integer truncation
        vect = vect * (0.5 * math.pow(factor, pwr))
    
    return vect
    
def refine(objective, epsilon, orientation, soln=[], current_error=2.0, hash=""):
    N = len(soln)
    if N > 29 :
        print "Failed to converge:"
        print "   refine(" + ", ".join([ repr(objective), str(epsilon), str(orientation), repr(soln), str(current_error), hash]) + ")"
        return hash + "7"

    letters = ['0', '1', '2', '3', '4', '5', '6']
    min_hash = hash
    min_dist = current_error * 1.0000001  # need to epsilon this up so that the constraint "dist < min_dist" can find next steps pairs that end in [0,0,0]
    
    if N == 0:
        min_U = A([0,0,0])
        for u in letters[1:]:  # Very important to skip zero-vector the first time
            U = nibble2vect(orientation, 0, u)
            attempt = soln + [U]
            dist = distance(objective, attempt)
            if dist < min_dist:
                min_dist = dist
                min_hash = hash + u
                min_U = U
                
        current_error = min_dist
        hash = min_hash
        return refine(objective, epsilon, orientation, soln + [min_U], current_error, hash)
        
    else:
        # We look ahead 2 steps for minimal error and keep the first 1 on each iteration
#        min_U = A([0,0,0])
#        for u in letters:
#            U = nibble2vect(orientation, N, u)
#            for v in letters:
#                V = nibble2vect(orientation, N+1, v)
#                attempt = soln + [U, V]
#                dist = distance(objective, attempt)
#                if dist < min_dist:
#                    min_dist = dist
#                    min_hash = hash + u + v
#                    min_U = U
#                    
        min_U = A([0,0,0])
        min_V = A([0,0,0])
        for u in letters:
            U = nibble2vect(orientation, N, u)
            for v in letters:
                V = nibble2vect(orientation, N+1, v)
                for w in letters:
                    W = nibble2vect(orientation, N+2, w)
                    for x in letters:
                        X = nibble2vect(orientation, N+3, x)
                        attempt = soln + [U, V, W, X]
                        dist = distance(objective, attempt)
                        if dist < min_dist:
                            min_dist = dist
                            min_hash = hash + u + v + w + x
                            min_U = U
                            min_V = V
                            print min_hash + " : " + str(min_dist) + " " + repr(attempt)
                                    
        # print "dist=" + str(min_dist) + " for " + repr(soln + [min_vect]) 
        if min_dist < epsilon:
            return min_hash
        
        current_error = min_dist
        hash = min_hash[0:-2]
        return refine(objective, epsilon, orientation, soln + [min_U, min_V], current_error, hash)
    

def ecef_geohash(x, y, z, epsilon):
    objective = A([x,y,z])
    return [ refine(objective, epsilon, 0), refine(objective, epsilon, 1) ]

# Austin :      ['412504100002014005[0]', '52504100002014005[000]']
# print ecef_geohash(-0.1165684, -0.8572452, 0.501540, 0.001)

# San Antonio : ['412504100000004[00000]', '52504100000004[000000]']
# print ecef_geohash(-0.128860005, -0.862881594, 0.488789934, 0.001)

# Edge condition
#  Two points within 8 km of each other but:
#  ['1', '2113636363636363636']
#  versus
#  ['1', '1122626262626262626']
# print ecef_geohash(e - .0001, e + .0001, 0, 0.001)
# print ecef_geohash(e + .0001, e - .0001, 0, 0.001)

def randomTest():
    offsets = [-0.001, 0.005, 0.005]
    for i in range(10000):
        t = A([ random.random(), random.random(), random.random() ])
        u0 = t / math.sqrt( (t[0]*t[0]) + (t[1]*t[1]) + (t[2]*t[2]) )
        u1 = [ u0[0] + offsets[0], u0[1] + offsets[1], u0[2] + offsets[2] ]
        random.shuffle(offsets)
        h0 = ecef_geohash(u0[0], u0[1], u0[2], 0.001)
        h1 = ecef_geohash(u1[0], u1[1], u1[2], 0.001)
        pfx = [ os.path.commonprefix([h0[0], h1[0]]), os.path.commonprefix([h0[1], h1[1]]) ]
        N = max( len(pfx[0]), len(pfx[1]) )
        if N < 12 :
            print [u0, u1]
            print h0[0]
            print h1[0]
            print h0[1]
            print h1[1]
            
print ecef_geohash(0.15373484,  0.99290733,  0.01481033, 0.001)

