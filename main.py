from scripts import languages
#from scripts import stats
from scripts import titles
from scripts import tokenizer
#from scripts import sentences
#from scripts import vocabularies

from settings import settings


# step 1
# generate list of languages to process

#TODO: for now just load this list from data/languages/languages.txt (list of wikipedia languages with 10,000+ articles)

langs={} #list of languages represented as wikipedia prefixes e.g. xx - xx.wikipedia.org
langs=languages.getlist(settings["languages_file"])

print "languages: ",langs
print "# of languages: ", len(langs)

# step 2
# get list of top N articles for each language

# TODO: build method of downloading relevant stats and parsing them
# for now use data/stats/combined-pagecounts-2009 as a source

articles={} 
articles = titles.getarticles(langs, settings["stats_file"])

print "articles: ", articles


# step 3
# train tokenizer for each language (from step #1) based on articles (from step #2)

tokenizer.train(langs, articles, settings["splitters_folder"])

# step 4
# split articles into sentences 

pass

# step 5
# split sentences into words and build cleaned up vocabularies

pass