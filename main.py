# -*- coding: utf-8 -*-

from urllib import unquote
import wikipydia
import re
import wpTextExtractor
import time
import os
import codecs
import nltk.data


from BeautifulSoup import BeautifulSoup
from nltk.tokenize.punkt import PunktSentenceTokenizer
from nltk.tokenize.punkt import PunktWordTokenizer

from nltk.corpus import wordnet

import unicodedata

import pickle

import wikilanguages

import argparse
import logging

parser = argparse.ArgumentParser(description='Build vocabularies and dictionaries for multiple languages based on Wikipedia',epilog="And that's how you'd do it")

parser.add_argument('--settings', default='settings', help='filename of settings file to use: settings (.py) will be used by default')
parser.add_argument('--level',default='INFO', choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL"],help='logging level: e.g. DEBUG, INFO, etc.')
parser.add_argument('--tokenizer',default='SKIP', choices=["TRAIN","SKIP"], help='tokenizer trainer behaviour: TRAIN (train all tokenizer), SKIP (skip training completely)')
parser.add_argument('--pipeline',default='PROCESS', choices=["PROCESS","SKIP"], help='pipeline behaviour: PROCESS (process and collect vocabularies/dictionaries),  SKIP (skip pipeline completely)')
parser.add_argument('--override',default='YES', choices=["YES","NO"], help='override already trained tokenizers and/or output files')

args = parser.parse_args()

print "debug level: ", args.level


# basic logging setup for console output
numeric_level = getattr(logging, args.level.upper(), None)
if not isinstance(numeric_level, int):
	raise ValueError('Invalid log level: %s' % args.level)

logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=numeric_level)


try:
	settings_module = __import__(args.settings) #, globals={}, locals={}, fromlist=[], level=-1
	settings=settings_module.settings
except ImportError: 
	import sys
	sys.stderr.write("Error: Can't find the file '%r.py' in the directory containing %r.\n" % (args.settings, args.settings))
	sys.exit(1)




def train(lang, articles, splitters_folder):
	collect_wiki_corpus(lang,lang, articles, splitters_folder)
	train_sentence_splitter(lang, splitters_folder)

def collect_wiki_corpus(language, lang, articles, splitters_folder):
	"""
	Download <n> random wikipedia articles in language <lang>
	"""
	filename = "%s%s.plain" % (splitters_folder,language)
	out = codecs.open(filename, "w", "utf-8")

	for title in articles:
		title=unquote(title)
		print ">> ",title
		print unquote(title)
		try:
			article_dict = wikipydia.query_text_rendered(title, language=lang)
			logging.debug("Training on: %s" % (unquote(title)))
			# Soup it
			soup = BeautifulSoup(article_dict['html'])
			p_text = ''
			for p in soup.findAll('p'):
				only_p = p.findAll(text=True)
				p_text = ''.join(only_p)

				# Tokenize but keep . at the end of words
				p_tokenized = ' '.join(PunktWordTokenizer().tokenize(p_text))

				out.write(p_tokenized)
				out.write("\n")
		except KeyError:
			logging.error("tokenizer training error")
		#except:
			#logging.error("some weird (JSON) error")
	out.close()


def train_sentence_splitter(lang, splitters_folder):
	"""
	Train an NLTK punkt tokenizer for sentence splitting.
	http://www.nltk.org
	"""
	# Read in trainings corpus
	plain_file = "%s%s.plain" % (splitters_folder,lang)
	text = codecs.open(plain_file, "Ur", "utf-8").read()

	# Train tokenizer
	tokenizer = PunktSentenceTokenizer()
	tokenizer.train(text)

	# Dump pickled tokenizer
	pickle_file = "%s%s.pickle" % (splitters_folder,lang)
	out = open(pickle_file, "wb")
	pickle.dump(tokenizer, out)
	out.close()


def determine_splitter(lang):
	#TODO: build better tokenizer selector (e.g. rely on existing NLTK tokenizers as well as custom tokenizers for Japanese/Chineese)
	#OPT: tokenizer is loaded on every call (cache?)
	try:
		tokenizer = 'file:'+settings["root_folder"]+settings["splitters_folder"]+'%s.pickle' % (lang)
	
		logging.debug("tokenizer from file %s" %(tokenizer))
		#print "Loading tokenizer for: ",lang," from file: ",tokenizer
		tokenizer = nltk.data.load(tokenizer)
		return tokenizer.tokenize
	except:
		logging.error("tokenizer for language %s not found" % (lang))
		return None

def use_as_gold_standard_translation(en_article, article, lang):
	# takes english and foreign language article titles and decides if they can be used as translation pair
	year_re = re.compile(r'\b\d\d\d\d')
	
	use_it = True
	
	#filter out all non-english vocabulary words based on WordNet
	if not wordnet.synsets(en_article):
		use_it=False
	
	#use only it is a single word (both foreign and english)
	if (len(en_article.split(" "))>1):
		use_it = False 
	if (len(article.split(" "))>1):
		use_it = False 
	
	
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



def load_freq_pages(page_view_counts_filename, language, limit=settings["top_articles"]):
	"""
	Reads a file  with page view counts and retrieves the top-k
	most frequent page for the language
	"""
	#OPT: counts file is parsed separately for each language
	logging.info("loading list of articles for language %s" % (language))
	
	logging.debug("load freq pages for %s, limit=%s" % (language,limit))
	freq_pages = []
	#input_file = codecs.open(page_view_counts_filename, 'r', 'utf-8')
	input_file = open(page_view_counts_filename, 'r')
	for line in input_file:
		#line = line.encode('UTF-8')
		line = line.rstrip('\n')
		(lang, rank, title, count) = line.split(' ')
		if lang==language and len(freq_pages) < limit:
			title = unquote(title)
			try:
				id = wikipydia.query_page_id(title, language=lang)
				freq_pages.append(title)
			except KeyError:
				#logging.debug( 'no page for %s %s' % (title, language))
				print 'no page for ', title, language
			except IOError:
				#logging.debug( 'cannot reach %s %s' % (title, language))
				print 'cannot reach ', title, language
			except TypeError:
				#logging.debug( 'unicode object error for %s %s' % (title, language))
				print 'unicode object error for ', title, language
			except UnicodeDecodeError:
				#logging.debug( 'unicode error for %s %s' % (title, language))
				print 'unicode error for ', title, language
	input_file.close()
	
	logging.info("# of articles loaded: %s" % (len(freq_pages)))
	
	return freq_pages

def get_vocab(articles, lang, lang_properties, num_context_sentences=settings["num_context_sentences"], max_articles=settings["top_articles"]):
	#build vocabulary based on list of articles and compile context sentences for each word

	logging.info("generating vocabulary")
	#add all unicode punctuation categories for exclusion
	all_chars=(unichr(i) for i in xrange(0x10000))
	punct=''.join(c for c in all_chars if unicodedata.category(c)[0]=='P')
	#punct_to_exclude= set(string.punctuation + "1234567890")
	punct_to_exclude= set(punct + "1234567890")	

	vocab={}
	num_articles=0

	splitter=determine_splitter(lang)
	
	for i,article in enumerate(articles):
		try:
			wikimarkup = wikipydia.query_text_raw(articles[i], lang)['text']
			sentences,tags = wpTextExtractor.wiki2sentences(wikimarkup, splitter, True)

			for sentence in sentences:
				sent = ''.join(ch for ch in sentence if ch not in punct_to_exclude)
				sent = sent.lower()
				words = sent.split(' ')

				for word in words:
				# filter words that are obviously non foreighn language (plain english or gibberish/non-alpha)
				#if not word in en_vocab:

					if len(word)<settings["min_letters"]:
						break

					if not word in vocab:
						vocab[word] = {"frequency":1,"context":[]}
					else:
						vocab[word]["frequency"]=vocab[word]["frequency"]+1
					if len(vocab[word]["context"]) < num_context_sentences:
						vocab[word]["context"].append(sentence)

			num_articles = num_articles + 1
			if num_articles >= max_articles:
				break

		except KeyError:
			#logging.debug( u'no page for %s %s' % (article, lang))
			print u'no page for ', article, lang
		except IOError:
			#logging.debug( u'cannot reach %s %s' % (article, lang))
			print u'cannot reach ', article, lang
		except TypeError:
			#logging.debug( u'unicode object error for %s %s' % (article, lang))
			print u'unicode object error for ', article, lang
		except UnicodeDecodeError:
			#logging.debug( u'unicode error for %s %s' % (article, lang))
			print u'unicode error for ', article, lang
		except:
			#logging.debug( u'somethign weird happened for %s %s' % (article, lang))
			print u'somethign weird happened for ', article, lang

	logging.info("vocabulary size: %s" % (len(vocab)))
	return vocab

def vocab_filter_latin(vocab):
	# filter out latin words
	logging.info("filtering latin words")
	vocab_filtered={}
	
	ref=re.compile("\w+")
	for word in vocab:
		if ref.search(word)==None:
			vocab_filtered[word]=vocab[word]

	logging.info("vocabulary size filtered to: %s" % (len(vocab_filtered)))
	return vocab_filtered

def vocab_freq_top(vocab, top=settings["top_words"]):
	# sorts vocabulary by frequence and returns TOP X words
		
	vocab_sorted=sorted(vocab, key=lambda key: vocab[key]["frequency"], reverse=True)
	#print "sorted"
	#print vocab_sorted
	logging.debug("top %s words: "%(top))
	vocab_filtered={}
	
	if len(vocab_sorted)<top:
		top=len(vocab_sorted)
	for i in range(0,top):
		vocab_filtered[vocab_sorted[i]]=vocab[vocab_sorted[i]]
		logging.debug(vocab_sorted[i]+" "+str(vocab[vocab_sorted[i]]))

	logging.info("vocabulary size cut to: %s" % (len(vocab_filtered)))
	return vocab_filtered


def get_lang_links(lang_links_filename, lang, per_lang_limit=10000):
	'''
	Reads a file with inter language links and returns a hash
	of the links between English and the speified languages
	also provides order in file
	'''
	logging.info("loading interlanguage links")
	# initalize the lang links hash
	lang_links = {}

	input_file = codecs.open(lang_links_filename, 'r', 'utf-8')
	# the first line of the file has the lang codes
	line = input_file.readline()
	line = line.rstrip('\n')
	langs = line.split('\t')
	en_index = langs.index('en')
	lang_index = []

	for i,language in enumerate(langs):
		if language==lang:
			lang_index=i

	for i, line in enumerate(input_file):
		line = line.encode('UTF-8')
		line = line.rstrip('\n')
		links = line.split('\t')

		link = links[lang_index]
		lang = langs[lang_index]
		if not links[lang_index] == "":
			english=links[en_index].lower()
			foreign=links[lang_index].lower()
			lang_links[english] = {"translation":foreign,"order":i}

		if len(lang_links) >= per_lang_limit:
			break

	input_file.close()
	logging.info("# of language links: %s" % (len(lang_links)))
	return lang_links

def get_lang_links_context(lang_links, lang, max_items=settings["top_links"], num_context_sentences=settings["num_context_sentences"]):
#(articles, lang, lang_properties, num_context_sentences=settings["num_context_sentences"], max_articles=settings["top_articles"]):
	#build vocabulary based on list of articles and compile context sentences for each word
	"""
	Extracts all of the non-English vocabulary from each of the pages, and retains
	up to the specified number of context sentences.  The vocab is normaized by 
	lowercasing and stripping punctuation.
	"""
	logging.info("getting context for interlanguage links")
	
	#add all unicode punctuation categories for exclusion
	all_chars=(unichr(i) for i in xrange(0x10000))
	punct=''.join(c for c in all_chars if unicodedata.category(c)[0]=='P')
	#punct_to_exclude= set(string.punctuation + "1234567890")
	punct_to_exclude= set(punct + "1234567890")	

	links_with_context={}

	splitter=determine_splitter(lang)

	for i,en_article in enumerate(lang_links):
		logging.debug ("item # %s from %s, # of good links %s, # of links needed %s" % (i, en_article,len(links_with_context), max_items))

		if len(links_with_context) >= max_items:
			break

		
		article = lang_links[en_article]["translation"]
		
		if use_as_gold_standard_translation(en_article, article, lang):
			logging.debug("link accepted %s - %s" % (en_article,article))

			word = unicode(article, "UTF-8")
			try:
				wikimarkup = wikipydia.query_text_raw(article, lang)['text']
				sentences,tags = wpTextExtractor.wiki2sentences(wikimarkup, splitter, True)
				
				for j,sentence in enumerate(sentences):
					if re.search(word, sentence):
						if not word in links_with_context:
							links_with_context[word] = {"context":[],"translation":en_article}
						
						if len(links_with_context[word]["context"]) < num_context_sentences:
							links_with_context[word]["context"].append(sentence)
							links_with_context[word]["translation"] = en_article
						else:
							break
			except KeyError:
				#logging.debug( u'no page for %s %s' % (article, lang))
				print u'no page for ', article, lang
			except IOError:
				logging.debug( u'cannot reach %s %s' % (article, lang))
			except TypeError:
				#logging.debug( u'unicode object error for %s %s' % (article, lang))
				print 'unicode object error for', article, lang
			except UnicodeDecodeError:
				#logging.debug( u'unicode error for %s %s' % (article, lang))
				print u'unicode error ', article, lang
			except:
				#logging.debug( u'somethign weird happened for %s %s' % (article, lang))
				print u'somethign weird happened for  ', article, lang
		else:
			logging.debug("link rejected %s - %s" % (en_article,article))
			

	return links_with_context


def save_results(lang, vocab, lang_links):
	path = settings["output_folder"]
	if not os.path.exists(path):
		os.makedirs(path)
	logging.info("output folder prepared: %s" % (path))

	date_time_str = time.strftime("%Y-%m-%dT%H%M")
	#output_filename = path + settings["run_name"] + '_' + language + '_' + date_time_str + ".csv"


	#write_dict_hit(lang, output_filename, en_vocab, lang_links, articles, num_context_sentences)
	
	f=open(settings["output_folder"]+settings["run_name"] + '_' +lang+"_vocabulary.pickle","w")
	pickle.dump(vocab,f)
	f.close()
	logging.info("saved vocabulary into: %s " % (settings["output_folder"]+lang+"_vocabulary.pickle"))

	f=open(settings["output_folder"]+settings["run_name"] + '_' +lang+"_links.pickle","w")
	pickle.dump(lang_links,f)
	f.close()
	logging.info("saved language links into: %s " % (settings["output_folder"]+lang+"_links.pickle"))
	

################################################################################

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

# generate list of languages to process
#TODO: for now just load this list from data/languages/languages.txt (list of wikipedia languages with 10,000+ articles)

langs=[] #list of languages represented as wikipedia prefixes e.g. xx - xx.wikipedia.org
langs=wikilanguages.load(settings["languages_file"])

logging.info("# of languages loaded: %s" %(len(langs)))
if len(langs)<=5:
	logging.info("languages are: %s" %(langs))

langs_properties={} #list of languages' properties (e.g. LTR vs RTL script, non latin characters, etc) 
langs_properties=wikilanguages.langs


if args.tokenizer=="TRAIN":
	logging.info("tokenizers trainer - START")

	# iterate over each language individually
	for i, lang in enumerate(langs):

		logging.info("processing language: %s (#%s out of %s) " %(lang,i+1,len(langs)))

		train_tokenizer=True
		if args.override=="NO":
			try:
				tokenizer = 'file:'+settings["root_folder"]+settings["splitters_folder"]+'%s.pickle' % (lang)
				tokenizer = nltk.data.load(tokenizer)
				train_tokenizer=False
				logging.info("tokenizer already exists")
				
			except:
				pass

		if train_tokenizer:
			logging.info("starting tokenizer trainer")

			logging.info("loading list of articles")
			articles = load_freq_pages(settings["stats_file"], lang)

			logging.info("# of articles loaded: %s" % (len(articles)))

			train(lang, articles, settings["splitters_folder"])
			logging.info("tokenizer training completed")

	logging.info("tokenizers trainer - FINISH")
elif args.tokenizer=="SKIP":
	logging.info("skipping tokenizer training")
	
if args.pipeline=="PROCESS":

	logging.info("wikilanguages pipeline - START")
	# iterate over each language individually
	for i, lang in enumerate(langs):
		
		logging.info("--------------------------------------------------------------------------------")
		logging.info("processing language: %s (#%s out of %s) " %(lang,i+1,len(langs)))
	
	
	
		process_pipeline=True
		if args.override=="NO":
			try:
				output = 'file:'+settings["root_folder"]+settings["splitters_folder"]+'%s.pickle' % (lang)

				# TODO: verify that output exist
				path = settings["output_folder"]
				f=open(settings["output_folder"]+settings["run_name"] + '_' +lang+"_vocabulary.pickle")
				f.close()
				f=open(settings["output_folder"]+settings["run_name"] + '_' +lang+"_links.pickle")
				f.close()
				process_pipeline=False
				logging.info("output already exists")
				
			except:
				pass

		if process_pipeline:
			# get list of top N articles for current language
			# TODO: build method of downloading relevant stats and parsing them
			# for now use data/stats/combined-pagecounts-2009 as a source
		
			articles = load_freq_pages(settings["stats_file"], lang)
		
			vocab = get_vocab(articles, lang, langs_properties[lang])
			
			#if non-latin, filter all "english" words
			if (langs_properties[lang]["script"]["non_latin"]=='yes'):
				vocab=vocab_filter_latin(vocab)
		
			#cut off words below top X
			vocab=vocab_freq_top(vocab)
			
			lang_links = get_lang_links(settings["lang_links_file"], lang)
			
			lang_links = get_lang_links_context(lang_links, lang, settings["top_links"], settings["num_context_sentences"])
		
			save_results(lang, vocab, lang_links)
		
			#debug printout of vocabulary
			#print "DEBUG - vocab"
			#for word in vocab:
			#	print word, vocab[word]["frequency"], len(vocab[word]["context"])
		
			#debug printout of lang links
			#print "DEBUG - lang_links"
			#for word in lang_links:
			#	print word, lang_links[word]["translation"], len(lang_links[word]["context"])
		
	
	logging.info("wikilanguages pipeline - FINISH")
elif args.pipeline=="SKIP":
	logging.info("skipping pipeline processing")
