import wikipydia

import urllib

st="%D0%94%D0%B5%D0%BD%D1%8C_%D0%BD%D0%B0%D1%80%D0%BE%D0%B4%D0%BD%D0%BE%D0%B3%D0%BE_%D0%B5%D0%B4%D0%B8%D0%BD%D1%81%D1%82%D0%B2%D0%B0"

st2=urllib.unquote(st)

print st2

#st2="Putin"

#print wikipydia.query_text_raw(st2,"ru")

print wikipydia.query_text_raw("Mathematics","en")
