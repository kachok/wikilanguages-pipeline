# downloads wikipedia raw stats

import urllib
import re

import time 

 
data = urllib.urlopen('http://dumps.wikimedia.org/other/pagecounts-raw/2011/2011-11/').read()    
#print data

p = re.compile('pagecounts-\d{8}-\d{6}.gz')

m=p.findall(data)

print m

for i in range(len(m)):
	if (i%2==0):
		print m[i]

#time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(epoch))

print len(m)

for i in range(len(m)):
	if (i%2==0):
		print "downloading ",  m[i]
		clicks = urllib.urlopen('http://dumps.wikimedia.org/other/pagecounts-raw/2011/2011-11/'+m[i]).read()
		file = open(m[i], "w")
		file.write(clicks)
		file.close()
		print "done"
