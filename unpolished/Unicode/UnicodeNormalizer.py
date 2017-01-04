import GenerateNormTable

class UnicodeNormalizer:    
    def __init__(self):
        self.norm_table = GenerateNormTable.GenerateCombinedTable()
        
    def normalizeCharacter(self, unicodeCharacter):
        if unicodeCharacter in self.norm_table:
            return self.norm_table[unicodeCharacter]
        return unicodeCharacter    
    #

    def normalizeText(self, unicodeText):
        return u"".join(map(self.normalizeCharacter, unicodeText))
    #

if __name__ == "__main__":

    import sys
    import codecs
    if len(sys.argv) > 1:
        print u" ".join(map(normalizeText, sys.argv[1:]))
    else:
        sys.stdout=codecs.getwriter('UTF-8')(sys.stdout)
        sys.stdin=codecs.getreader('UTF-8')(sys.stdin)
        for line in sys.stdin:
            line.rstrip()
            print(normalizeText(line))

#fi __main__
