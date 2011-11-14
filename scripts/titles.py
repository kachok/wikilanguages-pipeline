#returns list of articles per language

def getarticles(langs, filename):
	fd = open(filename)
	
	articles={}
	
	for line in fd:
		# process content
		(lang, pos, title, count) = line.split(" ")
	
		#skip wikipedia subprojects (e.g. wikiquotes, etc)
		if lang.find(".")>0:
			continue
	
		if lang in langs:
			if lang in articles:
				articles[lang].append(title)
			else:
				articles[lang]=[]
				articles[lang].append(title)
		else:
			#language is not on our list, skip it
			pass

	return articles