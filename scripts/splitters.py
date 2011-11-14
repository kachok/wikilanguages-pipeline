import languages
import train_tokenizer
from time import gmtime, strftime


langs=languages.get_langs()

for l in langs:
	print l
	train_tokenizer.train(l)
	print "trained: ",l," at ",strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())