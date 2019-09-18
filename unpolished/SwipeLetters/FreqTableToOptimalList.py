import sys, math, numpy

letters = range(26)
frequencies = numpy.zeros((26,26))
positions = numpy.zeros((26,2))
distances = numpy.zeros((26,26))

def position(idx):
    theta = idx * 2.0 * math.pi / 26.0 ;
    x = math.cos(theta)
    y = math.sin(theta)
    return numpy.array( [x, y] )

def computeDistances():
    for i in range(26):
        positions[i] = position(i)
    for i in range(26):
        for j in range(26):
            distances[i][j] = numpy.linalg.norm(positions[i] - positions[j])
            
def energy(layout):
    e = 0.0
    for i in range(26):
        for j in range(26):
            if i != j:
                dist = distances[layout[i]][layout[j]]
                ee = frequencies[i][j]
                e = e + (ee / dist)
    return e



def init():   
    computeDistances()
    N=0
    for line in sys.stdin:
        line = line.rstrip()
        L = line.split('\t')
        N = N + 1
        if N == 1:
            continue
        if N > 26:
            break
        for i in range(26):
            # print('\t'.join([ str(letters[N-2]), str(letters[i]), L[i+1]]))
            frequencies[N-2][i] = float(L[i+1])
            frequencies[i][N-2] = float(L[i+1])

def my_swap(layout, i, j):
    new_layout = list(layout)
    a = new_layout[i]
    new_layout[i] = new_layout[j]
    new_layout[j] = a
    return new_layout
            
def sort():
    current_layout = list(letters)
    current_e = energy(current_layout)
    for k in range(26*26):
        break_e = current_e
        for i in range(26):
            for j in range(26):
                if i != j:
                    test_layout = my_swap(current_layout, i, j)
                    test_e = energy(test_layout)
                    if test_e < current_e:
                        print(repr(test_e) + '\t' + repr(current_e))
                        current_layout = test_layout
                        current_e = test_e
                        break
        if current_e == break_e:
            # We went all the way through without an improvement
            break
    return current_e, current_layout
    
init()
print(repr(letters))
e, layout = sort()
alph_layout = [ chr( ord('a') + layout[i] ) for i in range(26) ]
print(repr(alph_layout))

