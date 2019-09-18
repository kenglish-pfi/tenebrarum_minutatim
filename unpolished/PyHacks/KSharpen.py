# An image sharpening algorithm that functions by making 
# use of un-used intensities at the beginning and/or end of
# the histogram.
#
# For many images this technique provides superior
# results compared to other image sharpening 
# algorithms.

import sys, numpy
import matplotlib.image as img
import matplotlib.pyplot as plt
import cv2

def func2d(f, A):
    return f(map(f, A))

def hist256(array2D):
    shape = array2D.shape
    H = [0]*256
    for i in range(shape[0]):
        for j in range(shape[1]):
            H[array2D[i][j]] = H[array2D[i][j]] + 1
    return H
#

MIN_ZERO_TELOBUCKETS = 16
FUZZY_FACTOR = 6

def BroadenHisto(matrix2D):
    shape = matrix2D.shape
    H = hist256(matrix2D)

    # count leading (Na) and trailing (Nz) zeros
    Na = 0
    for i in range(256):
        if H[i] == 0:
            Na = Na + 1
        else:
            break
    Nz = 0
    for i in range(256):
        if H[255-i] == 0:
            Nz = Nz + 1
        else:
            break
            
    N = Na + Nz
    if N < MIN_ZERO_TELOBUCKETS:
        # Not enough wiggle room in the histogram to make it worth it
        return matrix2D
    
    sfactor = 255.0 / (255.0 - N)
    offset = Na
    # TODO:  Identify Optimal fuz factor equation.
    fuzzy = N / (FUZZY_FACTOR * 255.0)
    
    # Need signed type for numpy.diff to work
    matrix2D = matrix2D.astype(float) 
    matrix2D_t = matrix2D.transpose()
    
    Vcol0 = sfactor * ((matrix2D[0]) - offset)
    Vrow0 = sfactor * ((matrix2D_t[0]) - offset)
    # Purposely make dimensions a little different to get smooth histogram
    Drow = (sfactor + fuzzy) * numpy.diff(matrix2D, n=1, axis=0)
    Dcol = (sfactor - fuzzy) * numpy.diff(matrix2D_t, n=1, axis=0)
    scaleRows = matrix2D.astype(float)
    scaleCols = matrix2D_t.astype(float)
    
    scaleRows[0] = Vcol0
    for i in range(shape[0]-1):
        for j in range(shape[1]):
            scaleRows[i+1][j] = scaleRows[i][j] + Drow[i][j]
    
    
    scaleCols[0] = Vrow0
    for i in range(shape[1]-1):
        for j in range(shape[0]):
            scaleCols[i+1][j] = scaleCols[i][j] + Dcol[i][j]
    
    mxr = func2d(max, scaleRows)
    scaleRows = (255.0 / mxr) * scaleRows
    mxc = func2d(max, scaleCols)
    scaleCols = (255.0 / mxc) * scaleCols
    
    sharpened = (1.0/2.0) * ( scaleRows + scaleCols.transpose((1,0)) )
    # The difference between mxr and mxc gives some idea of difference in spreading.
    # The "crispest" picture actually comes with fuzzy == 0, the best histogram
    # comes with larger fuzzy factors (>6)
    # print(repr([mxr, mxc, func2d(max, sharpened)]))
    return (sharpened + 0.499999999).astype('uint8')