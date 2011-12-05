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

import urllib


def train(langs, articles, splitters_folder):
	for lang in langs:
	    collect_wiki_corpus(lang,lang, articles, splitters_folder)
	    train_sentence_splitter(lang, splitters_folder)

def collect_wiki_corpus(language, lang, articles, splitters_folder):
    """
    Download <n> random wikipedia articles in language <lang>
    """
    filename = "%s%s.plain" % (splitters_folder,language)
    out = codecs.open(filename, "w", "utf-8")

    for title in articles[lang]:
        title=urllib.unquote(title)
        print ">> ",title
        try:
	        article_dict = query_text_rendered(title, language=lang)
	        print "Training on ", urllib.unquote(title)
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
        except:
			print "error"
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


if __name__ == "__main__":
    main()

