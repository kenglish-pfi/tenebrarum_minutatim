import sys

for line in sys.stdin:
    line = line.rstrip()
    A = line.split('.')
    if len(A) == 4:
        for i in range(4):
            if len(A[i]) == 1:
                A[i] = "00" + A[i] 
            elif len(A[i]) == 2:
                A[i] = "0" + A[i]
        line = '.'.join(A)
    print(line)