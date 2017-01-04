import UnicodeNormalizer
u = UnicodeNormalizer.UnicodeNormalizer()
print repr(  u.normalizeCharacter(u'A') == u'a'  )
print repr(  u.normalizeText(u"AZ") == u"az"  )
