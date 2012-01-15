# settings configuration file

settings = {
	"languages_file":"data/languages/languages.txt",
	"root_folder":".../wikilanguages-pipeline/",

	"languages_properties_file":"data/languages/wikilanguages-scripts.txt",

	"target_language":"en",

	"stats_file":"data/stats/combined-pagecounts-2009",
	"lang_links_file":"data/lang-links/lang-links",

	"splitters_folder":"data/splitters/",
	"vocabularies_folder":"data/vocabularies/",
	"output_folder":"data/output/",

	"top_articles":1000, # use 1000 wikipedia articles per language (1000)
	"top_words":10000,   # add only top 10000 words into vocabulary (10000)
	"top_links":1250,    # use top 1250 words in dictionary (based on inter language links) (1250  or as many)
	
	"min_letters":1, #words with less letters than that will be ignored
	
	"num_context_sentences":3,
	"num_knowns":2,	# control words
	"num_unknowns":8, # unknown words to translate (10 (twelve total words to translate in HIT))
	
	"run_name":"prod_run", # name of this particular config/run (used as prefix for generated output files)
}