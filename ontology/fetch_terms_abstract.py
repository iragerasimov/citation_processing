import os
import json
import re
import glob
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from collections import OrderedDict

json_folder_path = 'data'
terms_file = 'terms1.json'
zot_pubs_file = 'zot_pubs_gio.2017.json' #zot_pubs_scopus+wos.json'
ps = PorterStemmer()
stop_words = set(stopwords.words('english'))
new_stopwords = ['lead', 'leading']
stop_words.update(new_stopwords)
new_stop_words = set(stop_words)
#print(new_stop_words)

with open(os.path.join(json_folder_path, terms_file)) as json_publications_file:
  terms = json.load(json_publications_file)

with open(os.path.join(json_folder_path, zot_pubs_file)) as json_publications_file:
  zot_list = json.load(json_publications_file)

cnt = 0
all_titles = []
for pub_item in zot_list:
  abstract = pub_item['data'].get('abstractNote', '')
  title = pub_item['data'].get('title', '').lower()
  #print(abstract)
  abstract_tokens = []
  abstract_tokens1 = word_tokenize(abstract)
  abstract_tokens2 = [w for w in abstract_tokens1 if not w in new_stop_words]
  for a in abstract_tokens2:
    abstract_tokens.append(ps.stem(a))
  #print(abstract_tokens)
  categories = {}
  found_terms = []
  for term in terms.keys():
    term_present = False
    term_tokens = []
    term_tokens1 = word_tokenize(term)
    term_tokens2 = [w for w in term_tokens1 if not w in new_stop_words]
    for a in term_tokens2:
      term_tokens.append(ps.stem(a))
    if len(term_tokens) < len(term_tokens1):
      continue
    tocken_cnt = len(term_tokens)
    for i in range(0, len(abstract_tokens) - tocken_cnt):
      for j in range(0, tocken_cnt):
        if abstract_tokens[i+j] != term_tokens[j]:
          term_present = False
          break
        #print(abstract_tokens[i+j]+' '+term_tokens[j])
        term_present = True
      if term_present:
        break
    if term_present:
      append = True
      for found_term in found_terms:
        if len(term) > len(found_term):
          if ps.stem(found_term) in ps.stem(term) or found_term in term:
            #print('removing: '+found_term+' '+term)
            #print('removing: '+ps.stem(found_term)+' '+ps.stem(term))
            found_terms.remove(found_term)
            break
        elif ps.stem(term) in ps.stem(found_term) or term in found_term:
          append = False
      if append:
        found_terms.append(term)
      #print(term_tokens)

  for term in found_terms:
    for category in terms[term]:
      if categories.get(category, ''):
        categories[category].append(term)
      else:
        categories[category] = [term]
  
  categories1 = OrderedDict(sorted(categories.items()))
  categories1['abstract'] = title+ ' Abstract '+abstract
  all_titles.append(categories1)
  #break 

with open(os.path.join(json_folder_path, "title_terms_gio.2017.json"), "w") as fp:
  json.dump(all_titles, fp, indent=4)



