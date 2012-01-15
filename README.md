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
Run pipeline to generate vocabularies for all languages

Get help on command line options
>python main.py --help

Run full production pipeline
>python main.py --settings settings --debug INFO --tokenizer TRAIN

--tokenizer parameter explained:
TRAIN - will train new tokenizers and save them
NEW - will train tokenizer if it is missing from tokenizer folder
SKIP - will not train tokenizers, will use existing ones (assuming that they are exist for all languages)
ONLY - like TRAIN but will exit after training, without continuing with the rest of the pipeline tasks (tokenizer training only)