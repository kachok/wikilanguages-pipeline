# -*- coding: utf-8 -*-

from scripts2 import languages, titles, tokenizer, voc, lang_links

#from scripts import stats
#from scripts import sentences

from settings import settings

import wikipydia
import urllib
import json
import pickle

from nltk.corpus import wordnet

# basic logging setup for console output
import logging
logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=logging.INFO)

logging.info("synonyms pipeline - START")

# generate list of languages to process
#TODO: for now just load this list from data/languages/languages.txt (list of wikipedia languages with 10,000+ articles)

langs={} #list of languages represented as wikipedia prefixes e.g. xx - xx.wikipedia.org
langs=languages.getlist(settings["languages_file"])

logging.info("list of languages is loaded")
logging.info("# of languages: %s" %(len(langs)))
if len(langs)<=5:
	logging.info("languages are: %s" %(langs))


# iterate over each language individually
for i, lang in enumerate(langs):
	
	logging.info("processing language: %s (#%s out of %s) " %(lang,i+1,len(langs)))
	
	# get list of top N articles for current language

	# TODO: build method of downloading relevant stats and parsing them
	# for now use data/stats/combined-pagecounts-2009 as a source

	articles={} 
	articles = titles.getarticles(lang, settings["stats_file"])

	logging.info("loaded list of %s articles" % (len(articles)))

	
	for title in articles:
		ss=wordnet.synsets(title)
		for s in ss:
			print s, " ", s.lemma_names

		
logging.info("synonyms pipeline - FINISH")
