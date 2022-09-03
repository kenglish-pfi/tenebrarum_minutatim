from multiprocessing.pool import Pool
from multiprocessing import JoinableQueue as Queue
import os, time

POOL_SIZE = 12
RUN_ID = time.time()

def processFile(fullname):
    filename = os.path.basename(fullname)
    dir = fullname[0:-len(filename)]
    (_, ext) = os.path.splitext(filename)
    size = os.path.getsize(fullname)
    mtime = os.path.getmtime(fullname)
    L = [str(RUN_ID), filename, str(mtime), str(size), dir]
    

def explore_path(path):
    directories = []
    nondirectories = []
    for filename in os.listdir(path):
        
        fullname = os.path.join(path, filename)
        if os.path.isdir(fullname):
            directories.append(fullname)
        else:
            nondirectories.append(filename)
    outputfile = path.replace(os.sep, '_') + '.txt'
    with open(outputfile, 'w') as f:
        for filename in nondirectories:
            print >> f, filename
    return directories

def parallel_worker():
    while True:
        path = unsearched.get()
        dirs = explore_path(path)
        for newdir in dirs:
            unsearched.put(newdir)
        unsearched.task_done()

# acquire the list of paths
with open('paths.txt') as f:
    paths = f.split()

unsearched = Queue()
for path in paths:
    unsearched.put(path)

pool = Pool(POOL_SIZE)
for i in range(POOL_SIZE):
    pool.apply_async(parallel_worker)

unsearched.join()
print 'Done'