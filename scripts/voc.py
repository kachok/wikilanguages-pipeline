#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Trains sentence splitter on a random set of wikipedia articles
#
# based on https://github.com/mhq/train_punkt/blob/master/train_tokenizer.py

import codecs
import pickle
import nltk.data
from BeautifulSoup import BeautifulSoup
from nltk.tokenize.punkt import PunktSentenceTokenizer
from nltk.tokenize.punkt import PunktWordTokenizer
from wikipydia import query_random_titles
from wikipydia import query_text_rendered

from urllib import quote_plus, unquote
from pyango_view import str2img
import wikipydia
import re
import wpTextExtractor
import goopytrans
import time
import os
import string
import codecs
import nltk.data

import urllib

import unicodedata

import logging

def build(lang, articles, splitters_folder):
	voc= build_voc(lang,lang, articles, splitters_folder)
	#for word in voc:
	#	print word
	return voc


def build_voc(language, lang, articles, splitters_folder):
	splitter=determine_splitter(lang)
	#add all unicode punctuation categories for exclusion
	all_chars=(unichr(i) for i in xrange(0x10000))
	punct=''.join(c for c in all_chars if unicodedata.category(c)[0]=='P')
	#punct_to_exclude= set(string.punctuation + "1234567890")
	punct_to_exclude= set(punct + "1234567890")	
	vocab_contexts = {}
	num_articles = 0
	num_context_sentences=3
	max_articles=100
	
	#articles["ru"]={"Москва","Красноярск"}
	#articles["en"]={"Oxygen_saturation"}

	for title in articles:
	       title=urllib.unquote(title)
	       logging.debug("processing title: %s" % (title)) 
	       try:
			article_dict = query_text_rendered(title, language=lang)

			wikimarkup = wikipydia.query_text_raw(title, lang)['text']

			# "splitter loaded"
			sentences,tags = wpTextExtractor.wiki2sentences(wikimarkup, splitter, True)

			for sentence in sentences:
				logging.debug("iterating sentence: %s" % (sentence))
				sent = ''.join(ch for ch in sentence if ch not in punct_to_exclude)
				sent = sent.lower()
				words = sent.split(' ')
				for word in words:
					if not word in vocab_contexts:
						vocab_contexts[word] = []
					if len(vocab_contexts[word]) < num_context_sentences:
						vocab_contexts[word].append(sentence)
			num_articles = num_articles + 1
			if num_articles >= max_articles:
				break

	       except :
			logging.warning("error in processing sentence")
	return vocab_contexts

"""
   Extracts all of the non-English vocabulary from each of the pages, and retains
   up to the specified number of context sentences.  The vocab is normaized by 
   lowercasing and stripping punctuation.
   punct_to_exclude= set(string.punctuation + "1234567890")
   vocab_contexts = {}
   num_articles = 0
   for i,article in enumerate(articles[lang]):
      article=urllib.unquote(articles[lang][i])
      try:
         wikimarkup = wikipydia.query_text_raw(article, lang)['text']
         print "wikimarkup loaded"
         sentences,tags = wpTextExtractor.wiki2sentences(wikimarkup, determine_splitter(lang), True)
         print "sentences, tags loaded"
         for sentence in sentences:
            print "iterating: ", sentence
            sent = ''.join(ch for ch in sentence if ch not in punct_to_exclude)
            sent = sent.lower()
            words = sent.split(' ')
            for word in words:
               if not word in en_vocab:
                  if not word in vocab_contexts:
                     vocab_contexts[word] = []
                  if len(vocab_contexts[word]) < num_context_sentences:
                     vocab_contexts[word].append(sentence)
         num_articles = num_articles + 1
         if num_articles >= max_articles:
            break
      except IOError:
         print 'IOError: cannot reach', article, lang, i
      except KeyError:
         print 'KeyError: no page for', article, lang, i 
      except ValueError:
         print 'ValueError: no page for', article, lang, i
   return vocab_contexts
"""

def determine_splitter(lang):
   tokenizer = 'file:/users/dkachaev/repos/hcil/wikilanguages-pipeline/data/splitters/%s.pickle' % (lang)
   #print "Loading tokenizer for: ",lang," from file: ",tokenizer

   tokenizer = nltk.data.load(tokenizer)
   return tokenizer.tokenize


if __name__ == "__main__":
    main()

