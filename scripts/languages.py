import codecs

def getlist(filename):
	langs=[]

	fd = codecs.open( filename ,"r","utf-16")
	line=fd.readline() #skip headers
	for line in fd:
		# process content
		content = line.split("	")
			
		#print content[0]," - ",content[1]
		langs.append(content[3])

	#print langs
	return langs
	
