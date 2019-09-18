import sys, codecs
sys.stdin=codecs.getreader('UTF-8')(sys.stdin)
sys.stdout=codecs.getwriter('UTF-8')(sys.stdout)
import json
import collections

# Recursively index into nested objects using an array of indeces
def arrayIndex(B, array_idx):
    if len(array_idx) == 0:
        return None
    elif len(array_idx) == 1:
        print >>sys.stderr, "B=" + repr(B) + ", array_idx=" + repr(array_idx)
        return B[array_idx[0]]
    else:
        if array_idx[0] in B:
            return arrayIndex(B[array_idx[0]], array_idx[1:])
        else:
            return None

# Index into nested objects using "dot" notation.
def dotIndex(B, dot_idx_str):
    P = dot_idx_str.split('.')
    return arrayIndex(B, P)

# Turns a single-valued array into a scalar
def unwrap(A):
    if isinstance(A, list):
        if len(A) > 1:
            print >> sys.stderr, "Unexpected multi-valued array: " + repr(A)
        return A[0]
    return A

    
def main(column_list):
    columns = column_list.split(',')

    R = json.load(sys.stdin)

    for obj in R["hits"]["hits"]:
        C = []
        for c in columns:
            C.append(unwrap(dotIndex(obj, c)))
        print u'\t'.join( map(unicode, C) )

main(sys.argv[1])