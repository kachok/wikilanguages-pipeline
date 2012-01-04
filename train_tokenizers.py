# -*- coding: utf-8 -*-
#
# Trains sentence splitter on a random set of wikipedia articles
#
# based on https://github.com/mhq/train_punkt/blob/master/train_tokenizer.py



from settings import settings
from langlib import get_languages_list, get_languages_properties
from urllib import unquote

import wikipydia
import codecs
import pickle

from nltk.tokenize.punkt import PunktSentenceTokenizer
from nltk.tokenize.punkt import PunktWordTokenizer

from wikipydia import query_random_titles
from wikipydia import query_text_rendered

import nltk.data
from BeautifulSoup import BeautifulSoup


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
        #print ">> ",title
        try:
	        article_dict = query_text_rendered(title, language=lang)
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


def test_tokenization():
    """
    Test Icelandic, Korean and Hungarian sentence splitting.
    """
    is_text = "Hann var þríkvæntur. Fyrsta kona hans var Þorbjörg Þórarinsdóttir frá Múla í Aðaldal, f. 19. júlí 1786 á Myrká, d. 19. júlí 1846 á Völlum. Önnur kona Þorbjörg Bergsdóttir (1807-1851) frá Eyvindarstöðum í Sölvadal. Þriðja kona Guðrún Sigfúsdóttir (1812-1864). Hún var 32 árum yngri en brúðguminn, sem var 72 ára er hann kvæntist henni. Hans klaufi er ævintýri eftir H.C. Andersen. "
    tokenizer = nltk.data.load('tokenizers/punkt/icelandic.pickle')
    print '\n-----\n'.join(tokenizer.tokenize(is_text.strip()))
    
    ko_text = u'1월 20일(현지 시각), 아이티에서 12일 7.0의 강진에 이어 규모 5.9의 강한 지진(사진)이 다시 발생하였다.'
    tokenizer = nltk.data.load('tokenizers/punkt/korean.pickle')
    print '\n-----\n'.join(tokenizer.tokenize(ko_text.strip()))    

    hu_text = """II. József (Bécs, 1741. március 13. – Bécs, 1790. február 20.) osztrák főherceg, Mária Terézia és I. Ferenc császár legidősebb fia. 1765-től német-római császár, 1780-tól magyar és cseh király, az első uralkodó, aki a Habsburg–Lotaringiai-házból származott."""
    tokenizer = nltk.data.load('tokenizers/punkt/hungarian.pickle')
    print '\n-----\n'.join(tokenizer.tokenize(hu_text.strip()))    


def load_freq_pages(page_view_counts_filename, language, limit=settings["top_articles"]):
   """
   Reads a file  with page view counts and retrieves the top-k
   most frequent page for the language
   """
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
            logging.debug("loading page %s" % (title))
            id = wikipydia.query_page_id(title, language=lang)
            freq_pages.append(title)
         except KeyError:
            logging.error( 'no page for %s %s' %(title, lang))
         except IOError:
            logging.error( 'cannot reach  %s %s' %(title, lang))
         except TypeError:
            logging.error( 'unicode object error for %s %s' %(title, lang))
         except UnicodeDecodeError:
            logging.error( 'unicode error for %s %s' %(title, lang))
         except:
            logging.error( 'strange error for %s %s' %(title, lang))
   input_file.close()
   return freq_pages

# basic logging setup for console output
import logging
logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=logging.INFO)

logging.info("tokenizers trainer - START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

# generate list of languages to process
#TODO: for now just load this list from data/languages/languages.txt (list of wikipedia languages with 10,000+ articles)

langs=[] #list of languages represented as wikipedia prefixes e.g. xx - xx.wikipedia.org
logging.info("loading list of languages")
langs=get_languages_list(settings["languages_file"], target_language)

logging.info("# of languages loaded: %s" %(len(langs)))
if len(langs)<=5:
	logging.info("languages are: %s" %(langs))

langs_properties={} #list of languages' properties (e.g. LTR vs RTL script, non latin characters, etc) 
logging.info("loading list of languages' properties")
langs_properties=get_languages_properties(settings["languages_properties_file"], target_language)

# iterate over each language individually
for i, lang in enumerate(langs):
	
	logging.info("processing language: %s (#%s out of %s) " %(lang,i+1,len(langs)))
	
	# get list of top N articles for current language
	# TODO: build method of downloading relevant stats and parsing them
	# for now use data/stats/combined-pagecounts-2009 as a source


	logging.info("loading list of articles")
	articles = load_freq_pages(settings["stats_file"], lang)

	logging.info("# of articles loaded: %s" % (len(articles)))

	train(lang, articles, settings["splitters_folder"])
	logging.info("tokenizer training completed")

logging.info("tokenizers trainer - FINISH")




