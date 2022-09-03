'''
Graph reduction algorithm that removes Dandelions and more

Input: 
   Edge table tab-delimited file, first two columns must be "Source", "Target"

Output:
   New edge table
'''

from os import X_OK
import sys

max_set_count = 0

def main():
    D = {}

    def collect_edge(x, y):
        global max_set_count
        if x not in D:
            D[x] = set([y])
        else:
            D[x].add(y)
        #
        if len(D[x]) > max_set_count:
            max_set_count = len(D[x])
    #    
    def collect_pair(x,y):
        collect_edge(x,y)
        collect_edge(y,x)
    #

    # Collect all edges from the input into the dictionary
    counter = 0
    for line in sys.stdin:
        line = line.rstrip()
        cols = line.split('\t')
        if counter == 0:
            if cols[0] != "Source" or cols[1] != "Target":
                usage()
                exit(1)
        else:
            collect_pair(cols[0], cols[1])
        counter += 1
    #

    E = {}
    replace = {}
    for n in range(min(max_set_count, 5)):
        for pivot in D:
            reduce = {}
            for x in D[pivot]:
                # dandelion: n==1 
                if len(D[x]) == n:
                    key = tuple(sorted(D[x]))
                    val = x
                    if key not in reduce:
                        reduce[key] = []
                    reduce[key].append(val)
            for key in reduce:
                if len(reduce[key]) > 0:
                    # replace the nodes in the list with the tuple of the nodes
                    for x in reduce[key]:
                        replace[x] = tuple(sorted(reduce[key]))

    for pivot in D:
        if pivot in replace:
            key = replace[pivot]
        else:
            key = pivot
        if key not in E:
            E[key] = set([])
        for x in D[pivot]:
            if x in replace:
                val = replace[x]
            else:
                val = x
            E[key].add(val)
        #D = E
    #
    #print(E)
    def my_str(str_or_tup):
        if isinstance(str_or_tup, str):
            return str_or_tup
        elif len(str_or_tup) == 1:
            return str_or_tup[0]
        else:
            return str(str_or_tup)
    #

    edges = set([])
    for key in E:
        k = my_str(key)
        for val in E[key]:
            v = my_str(val)
            if k < v:
                edges.add((k, v))
            else:
                edges.add((v, k))
    
    # Write out reduced graph
    line = '\t'.join(["Source", "Target"])
    sys.stdout.write(line + '\n')
    for edge in edges:
        line = '\t'.join(edge)
        sys.stdout.write(line + '\n')
                        

if __name__ == "__main__":
    main()
#

