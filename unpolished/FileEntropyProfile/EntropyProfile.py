import sys
import math

def arrayNibbleEntropy(A):
    nibbleFreq = [0]*16
    N = len(A)
    for i in range(N):
        nibble = A[i] & 0xF
        nibbleFreq[nibble] = nibbleFreq[nibble] + 1
        nibble = A[i] >> 4
        nibbleFreq[nibble] = nibbleFreq[nibble] + 1
        
    ent = 0.0
    # print repr(nibbleFreq)
    for freq in nibbleFreq:
        if freq > 0:
            # print str(freq) + '=>' + str(math.log(freq, 16))
            ent = ent + freq * math.log(freq, 16)
    return ent


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: EntropyProfile.py [path]filename"
        sys.exit()

    # read the whole file into a byte array
    f = open(sys.argv[1], "rb")
    byteArr = map(ord, f.read())
    f.close()
    fileSize = len(byteArr)
    
    # we process the file in chunks of 512 nibbles (256 bytes)
    numChunks = fileSize/256
    for m in range(numChunks):
        e = arrayNibbleEntropy(byteArr[m*256: (m+1)*256])
        print '\t'.join([ str(m), str(e) ])

# fi


