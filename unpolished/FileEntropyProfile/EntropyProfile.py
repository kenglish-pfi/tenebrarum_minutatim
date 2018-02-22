import sys
import math
import array

def arrayNibbleEntropy(A):
    nibbleFreq = [0]*16
    N = len(A)
    # The smallest value occurs when the data is evenly spread across all buckets
    # N is in bytes so 2 * N is number of nibbles
    minVal =  2 * N * math.log( (2 * N)/16, 16)
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
    return ent - minVal


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: EntropyProfile.py [path]filename")
        sys.exit()

    # read the whole file into a byte array
    with open(sys.argv[1], "rb") as f:
        byteArr = f.read()
    fileSize = len(byteArr)
    
    # we process the file in chunks of 512 nibbles (256 bytes)
    # TODO:  zero pad and process tail
    numChunks = fileSize >> 8
    for m in range(numChunks):
        e = arrayNibbleEntropy(byteArr[m*256: (m+1)*256])
        print('\t'.join([ str(m), str(e) ]))

# fi


