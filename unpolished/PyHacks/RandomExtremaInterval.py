import random, sys

current_int = 0
current_interval = 0
for i in range(100000):
    r = random.randint(0, 2000000000)
    current_interval+=1
    if r > current_int:
        current_int = r
        print((current_interval, r))
        current_interval = 0

