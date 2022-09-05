'''
    Generator for the numerator and denominator lattices of the first value of the rational solutions for cycles satisfying the Collatz criteria.

    We work from integer matrices of rank N that provide rational solutions of cycle-length N-1.

'''

import numpy as np

'''
    State vector for lattice is:
    [n, a, b, t]
    n : current numerator
    a + b : current denominator
    t : addend for next numerator -- this is the non-commutative term and only comes into play with the "up" operand 
         ( and is the reason we do not have a linear inverse-up operator)
'''
nd_label_root = "_"
nd_vec_root = np.array([0, -1, 1, -1])

nd_op_up = np.array([
    [-2,   0,  0,  1 ],
    [ 0,  -3,  0,  0 ],
    [ 0,   0, -2,  0 ],
    [ 0,   0,  0, -3 ]
])

nd_op_dn = np.array([
    [-1,  0,  0,  0 ],
    [ 0, -1,  0,  0 ],
    [ 0,  0, -2,  0 ],
    [ 0,  0,  1, -1 ]
])

nd_op_invdn = np.array([
    [-1,      0,      0,  0 ],
    [ 0,     -1,      0,  0 ],
    [ 0,      0, -1.0/2,  0 ],
    [ 0,      0, -1.0/2, -1 ]
])

def closest_int(f):
    if 0.0 <= f:
        return int(f + 0.49999999999999999999999999999999999)
    else:
        return int(f - 0.50000000000000000000000000000000000)

vf_closest_int = np.vectorize(closest_int)


def rotateLabelBits(label_bits):
    ''' Rotate  a string e.g. "001" -> "010"
    '''
    car = label_bits[0]
    cdr = label_bits[1:]
    return cdr + car
#

def getRotatedLabelSet(label_bits):
    ''' 
        Given one rotatable string, collect the whole set.  
        (We use set() to filter out the symmetric cases if any)
    '''
    n = len(label_bits)
    rotations = set([label_bits])
    for i in range(n):
        label_bits = rotateLabelBits(label_bits)
        rotations.add(label_bits)
        
    return rotations
#

def solutionFromLabel(label):
    rank = len(label)
    mat = np.zeros((rank,rank))
    y = np.zeros((rank))
    mat[rank-1][0] = 1
    mat[rank-1][rank-1] = -1
    for i in range(rank-1):
        mat[i][i+1] = 2
        if label[i+1:i+2] == "1":
            mat[i][i] = -3
            y[i] = 1
        else:
            mat[i][i] = -1
    x = np.linalg.solve(mat, y)
    det = np.linalg.det(mat)
    numer = closest_int(x[-1]*det)
    denom = closest_int(det)
    return (numer, denom), x
#

class Node:
    def __init__(self, label, vec):
        self.label = label
        self.vec = vec 
        self.rank = len(label)
    
    def down_vec(self):
        ''' Here we see that:
                the Up numerator of rank+1 is a function of the "2-factor" of the parent of parent denominator of rank-1
                t: the t computed here becomes a factor in the _next_ Up numerator
                b: the b that gets added to t is the "2-factor" of the _previous_ denominator
        '''
        forward_down = np.inner(nd_op_dn, self.vec)
        #n,a,b,t = self.vec
        #a_, b_ = (-1)*a, (-2)*b
        #n_ = (-1)*n
        ## p = self.rank - 1 ... 2**(p) :=: b (on entry)
        #t_ = (-1)*t + b                                 # <-- Note this relationship between numerator and denominator
        #forward_down = np.array([n_, a_, b_, t_])
        return forward_down

    def up_vec(self):
        forward_up = np.inner(nd_op_up, self.vec)
        #n,a,b,t = self.vec
        #a_, b_ = (-3)*a, (-2)*b
        #n_ = (-2)*n + t
        #t_ = (-3)*t
        #forward_up = np.array([n_, a_, b_, t_])
        return forward_up

    def invdn_vec(self):
        rev_dn = np.inner(nd_op_invdn, self.vec)
        #n_,a_,b_,t_ = self.vec
        #a, b = (-1)*a_, b_//(-2)  # b is always a multiple of 2
        #c = b
        #t = (-1)*(t_ - c)
        #n = (-1)*n_
        #rev_dn = np.array([n, a, b, t])
        return rev_dn

    def invup_vec(self):
        # we can't use a simple single step transform ... have to computer prior numnerator to extract "t"
        n_, a_, b_, t_ = self.vec
        a, b = a_//(-3), b_//(-2)
        t = t_//(-3)
        n = (n_ - t)//(-2)  # a subtraction followed by division can't be done in one matrix step
        return np.array([n, a, b, t])

    def forward(self, zero_for_down_one_for_up):
        if zero_for_down_one_for_up == 0:
            return Node(self.label + "0", self.down_vec())
        else:
            return Node(self.label + "1", self.up_vec())

    def reverse(self, zero_for_down_one_for_up):
        if zero_for_down_one_for_up == 0:
            return Node(self.label[0:-1], self.invdn_vec())
        else:
            return Node( self.label[0:-1],self.invup_vec())
        
    def numerator(self):
        return self.vec[0]

    def denominator(self):
        return self.vec[1] + self.vec[2]

    def tup(self):
        return (self.numerator(), self.denominator())

    def solution_set_size(self):
        return len(getRotatedLabelSet(self.label[1:]))

    def solveMatrix(self):
        ''' Solve the rational equation for the current node's cycle values.  
            x[0] of the solution should always be numerator/denominator since the lattice is a generator for the x[0]
        '''
        return solutionFromLabel(self.label)
    #
#
class NodeRoot(Node):
    ''' The starting point for the lattices
    '''
    def __init__(self):
        super().__init__(nd_label_root, nd_vec_root)
#

