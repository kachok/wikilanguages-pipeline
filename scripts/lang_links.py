# -*- coding: utf-8 -*-

import wikipydia
import urllib
import logging


def use_as_gold_standard_translation(en_article, article, lang):
# takes english and foreign language article titles and decides if they can be used as translation pair
	use_it = True
	if en_article == article:
	   use_it = False 
	if use_it and en_article.find(article) != -1:
	   use_it = False
	if use_it and article.find(en_article) != -1:
	   use_it = False
	if use_it:
	   en_words = en_article.split(' ')
	   for word in article.split(' '):
	      if word in en_words:
	         use_it = False
	if use_it:
	   try:
	      categories = wikipydia.query_categories(en_article, 'en')
	      for cat in categories:
	         if year_re.search(cat):
	            use_it = False
	   except IOError:
	      print 'cannot reach', article, lang
	   except KeyError:
	      print 'no page for', article, lang 
	   except ValueError:
	      print 'no page for', article, lang 
	return use_it


def build(articles, lang):
# generates list of language links from foreign wikipedia articles to english articles (returns list of pairs (foreign, english title))
	links=[]
	for title in articles:
		try:
			#proper conversion of wikipedia URLquoted titles into Unicode string
			#it may sometimes fail when title is messed up (e.g. corrupted encoding, etc.)
			#Çàãëàâíàÿ_ñòðàíèöà
			#u'\xc7\xe0\xe3\xeb\xe0\xe2\xed\xe0\xff_\xf1\xf2\xf0\xe0\xed\xe8\xf6\xe0'
			#%C7%E0%E3%EB%E0%E2%ED%E0%FF_%F1%F2%F0%E0%ED%E8%F6%E0
			# it is corrupted title for Заглавная_страница
			title=unicode(urllib.unquote(title).decode('utf8'))
		except:
			logging.warning("failed encoding, article skipped: "+title)

		try:
			all_links=wikipydia.query_language_links(title, lang)
			logging.debug(all_links["en"]+" "+title)

			links.append({"en":all_links["en"],lang:title})
		except:
			logging.debug("NOLINKS: "+title)

		#except KeyError:
		#	print "KeyError"
		
	return links