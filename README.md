Wiki Languages Pipeline
============================

Wikipedia Languages Pipeline is multistep pipeline script to:

* Collect list of wikipedia languages
based on stats from - http://meta.wikimedia.org/wiki/List_of_Wikipedias#All_Wikipedias_ordered_by_number_of_articles

* Collect wikipedia articles usage per language

* Create languages vocabularies for every language

* Download top articles for every language

* Split every article in sentences and then in words 

* Automatically train sentence splitter/tokenizer for every language (based on top articles)

* Build foreign language - english dictionaries (based on single word wikipedia titles with language links)

Requirements
------------

Wikipydia library

wpTextExtractor library

NLTK library


Running pipeline
----------------

Train your tokenizers for all languages first
> python train_tokenizers.py

Run pipeline to generate vocabularies for all languages

> python main.py
	
Generate sample input for Str2Img.java (render sample images of words in diff languages (top 50 words))
> python image_test.py