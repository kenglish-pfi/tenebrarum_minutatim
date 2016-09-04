import sys, codecs
sys.stdin=codecs.getreader('UTF-8')(sys.stdin)
sys.stdout=codecs.getwriter('UTF-8')(sys.stdout)
sys.stderr=codecs.getwriter('UTF-8')(sys.stderr)
import sys
from elasticsearch import Elasticsearch
import json

pairs = []  # The original directed graph:  source -> destination
peers = {}  # Keeps track of all of the nodes a given node talks to
sets = {}   # Keeps track of all of the nodes that talk to a specific small set of nodes
rset = {}   # Reverse lookup of above

# Add a given pair to the pairs and peers lists
def interPair(addr1, addr2):
    if addr1 == addr2:
        return
    pairs.append( (addr1, addr2) )
    if addr1 not in peers:
        peers[addr1] = set([])
    peers[addr1].add(addr2)
    if addr2 not in peers:
        peers[addr2] = set([])
    peers[addr2].add(addr1)
#

# Read directed graph from stdin    
for line in sys.stdin:
    line = line.rstrip()
    A = line.split('\t')
    if len(A) == 2:
        interPair(*A)

# Look through all the peer lists and find places where sets can simplify the graph
for addr1 in peers:
    # If address 1 only talks to one other node, Then put it in the set named after that node
    if len(peers[addr1]) == 1:
        addr2 = list(peers[addr1])[0]
        setname = 'SET(1, "' + addr2 + '")'
        if setname not in sets:
            sets[setname] = set([])
        sets[setname].add(addr1)
        rset[addr1] = setname
    # If address 1 only talks to a few nodes, Then create a set named after the few nodes
    elif len(peers[addr1]) < 9:
        addrs2 = peers[addr1]
        setname = "SET(" + str(len(peers[addr1])) + ', "' + ','.join(sorted(addrs2)) + '")'
        if setname not in sets:
            sets[setname] = set([])
        sets[setname].add(addr1)
        rset[addr1] = setname 

# Now that we have all the info, generate the new graph using the sets where it makes sense
newpairs = {}
for pair in pairs:
    (src, dst) = pair
    if src in rset:
        if len(rset[src]) > 1:
            src = rset[src]
    if dst in rset:
        if len(rset[dst]) > 1:
            dst = rset[dst]
    newpair = (src, dst)
    if newpair not in newpairs:
        newpairs[newpair] = 0
    newpairs[newpair] = newpairs[newpair] + 1
        

print '{'
print '    "sets" : {'
for setname in sets:
    if len(sets[setname]) > 1:
        print '"' + setname + '" : [' + ','.join(sets[setname]) + ']'
print '    }'

print '{'
print '    "edges" : {'
for pair in newpairs:
    print repr(pair) + ' : ' + str(newpairs[pair])
print '    }'
print '}'

        
    
        

    
            
    