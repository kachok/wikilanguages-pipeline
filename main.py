# -*- coding: utf-8 -*-

from scripts import languages, titles, tokenizer, voc, lang_links

#from scripts import stats
#from scripts import sentences

from settings import settings

import wikipydia
import urllib
import json
import pickle

# basic logging setup for console output
import logging
logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=logging.INFO)

logging.info("wikilanguages pipeline - START")

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

	# train tokenizer for each language (from step #1) based on articles (from step #2)

	#tokenizer.train(langs, articles, settings["splitters_folder"])
	#logging.info("tokenizer training completed")

	# split articles into sentences 
	# split sentences into words and build cleaned up vocabularies

	#articles={"en":["Oxygen_saturation"]}
	#langs={"en"}

	#articles={"ru":["Красноярск"]}
	#langs={"ru"}

	ctx=voc.build(lang, articles, settings["vocabularies_folder"])
	logging.info("build vocabulary based on articles, total words #: %s " % (len(ctx)))

	links=lang_links.build(articles, lang)
	
	logging.info("generated list of linked articles, total pairs #: %s " % (len(links)))
	
	#for link in links:
	#	print link["en"]+" - "+link[lang]
	
	
	#dump vocabulary and links to file
	
	#print json.dumps(ctx, sort_keys=True, indent=4)
	#print json.dumps(links, sort_keys=True, indent=4)
	
	f=open(settings["output_folder"]+lang+"_vocabulary.pickle","w")
	pickle.dump(ctx,f)
	f.close()
	logging.info("saved vocabulary into: %s " % (settings["output_folder"]+lang+"_vocabulary.pickle"))
	
	f=open(settings["output_folder"]+lang+"_links.pickle","w")
	pickle.dump(links,f)
	f.close()
	logging.info("saved language links into: %s " % (settings["output_folder"]+lang+"_links.pickle"))
	
		
logging.info("wikilanguages pipeline - FINISH")
