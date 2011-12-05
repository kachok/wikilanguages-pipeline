#returns list of articles per language

import logging
import settings

def getarticles(language, filename):
	fd = open(filename)
	
	articles=[]
	
	total=0
	titles=0
	top=settings.settings["top_articles"]
	
	for line in fd:
		
		total=total+1
		
		# process content
		(lang, pos, title, count) = line.split(" ")
	
		#skip wikipedia subprojects (e.g. wikiquotes, etc)
		if lang.find(".")>0:
			continue
	
		if lang==language:
				#NOTE: currently top X functionality relies on titles being sorted by frequency in source file
				if titles<top:
					articles.append(title)
				titles=titles+1
		else:
			#language is not on current language, skip it
			pass

	logging.info("titles processed: %s, titles from language %s found %s, added: %s"%(total, language, titles, top))
	return articles