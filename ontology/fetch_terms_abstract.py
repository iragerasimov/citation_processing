import os
import json
import re
import glob
import csv
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from collections import OrderedDict

class bcolors:
    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'          # '\033[42 green background
    YELLOW = '\033[93m'		# '\033[43 brownish background
    RED = '\033[91m'
    GREY = '\033[90m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

json_folder_path = 'data'
terms_file = 'terms.json'
zot_pubs_file = 'zot_pubs_joshua.json' #zot_pubs_scopus+wos.json'
ps = PorterStemmer()
stop_words = set(stopwords.words('english'))
new_stopwords = ['lead', 'leading']
stop_words.update(new_stopwords)
new_stop_words = set(stop_words)
#print(new_stop_words)

variables = []
cvs_wos_path = "data/sciencekeywords.csv"
wos_dois = {}
with open(cvs_wos_path, newline='') as csvfile:
  reader = csv.reader(csvfile, delimiter=',') #, quotechar='|')
  for row in reader:
    for i in range (3, 6, 1):
      if row[i] and not re.search(r"(/|\()", row[i]):
        variables.append(row[i].lower())
variables = sorted(set(variables), key=len, reverse = True)

with open(os.path.join(json_folder_path, terms_file)) as json_publications_file:
  terms = json.load(json_publications_file)

with open(os.path.join(json_folder_path, zot_pubs_file)) as json_publications_file:
  zot_list = json.load(json_publications_file)

sweet_cats = {'Phenomena': 1, 'Realm': 2, 'Material': 3, 'Materials': 3, 'Property': 4, 'State': 5, 'Human': 6, 'Process': 7, 'Representation': 8, 'Relationships': 9}
cnt = 0
all_titles = []
for pub_item in zot_list:
  abstract = pub_item['data'].get('abstractNote', '')
  title = pub_item['data'].get('title', '')
  Abstract = title + '. '+abstract
  abstract = title.lower() + '. ' + abstract.lower()
  abstract = re.sub(r'\n|\t', '', abstract) 
  #print(abstract)
  abstract_tokens = []
  abstract_tokens1 = word_tokenize(abstract)
  abstract_array = [0] * len(abstract_tokens1)
  var_array = [0] * len(abstract_tokens1)
  #abstract_tokens2 = [w for w in abstract_tokens1 if not w in new_stop_words]
  for a in abstract_tokens1:
    abstract_tokens.append(ps.stem(a))
  #print(abstract_tokens)
  #print(' '.join(abstract_tokens1))
  #break
  categories = {}
  sweet_terms = {}
  found_terms = []
  for term in sorted(terms.keys(), key=len, reverse = True):
    term_present = False
    term_tokens = []
    term_tokens1 = word_tokenize(term)
    #term_tokens2 = [w for w in term_tokens1 if not w in new_stop_words]
    for a in term_tokens1:
      term_tokens.append(ps.stem(a))
    if len(term_tokens) < len(term_tokens1):
      continue
    tocken_cnt = len(term_tokens)
    for i in range(0, len(abstract_tokens) - tocken_cnt):
      for j in range(0, tocken_cnt):
        if abstract_array[i+j]:
          term_present = False
          break
        if abstract_tokens[i+j] != term_tokens[j]:
          term_present = False
          break
        #print(abstract_tokens[i+j]+' '+term_tokens[j])
        term_present = True
      if term_present:
        for j in range(0, tocken_cnt):
          abstract_array[i+j] = sweet_cats[(terms[term][0].split())[0]]
        found_terms.append(term)

  found_vars = []
  for var in variables:
    var_tokens = []
    for a in word_tokenize(var):
      var_tokens.append(ps.stem(a))
    tocken_cnt = len(var_tokens)
    for i in range(0, len(abstract_tokens) - tocken_cnt):
      for j in range(0, tocken_cnt):
        if var_array[i+j]:
          var_present = False
          break
        if abstract_tokens[i+j] != var_tokens[j]:
          var_present = False
          break
        #print(abstract_tokens[i+j]+' '+var_tokens[j])
        var_present = True
      if var_present:
        for j in range(0, tocken_cnt):
          var_array[i+j] = 10
        found_vars.append(var)

  for term in set(found_terms):
    for category in terms[term]:
      sw = (category.split())[0]
      if sweet_terms.get(sw, ''):
        sweet_terms[sw].append(term)
      else:
        sweet_terms[sw] = [term]
      if categories.get(category, ''):
        categories[category].append(term)
      else:
        categories[category] = [term]

  for cat in sweet_terms.keys():
    if sweet_cats[cat] == 1:
      print(cat+': ', bcolors.GREEN, ', '.join(sweet_terms[cat]),bcolors.ENDC)
    elif sweet_cats[cat] == 2:
      print(cat+': ', bcolors.BLUE, ', '.join(sweet_terms[cat]),bcolors.ENDC)
    else:
      print(cat+': ', bcolors.BOLD,', '.join(sweet_terms[cat]),bcolors.ENDC)
  print('Science Keywords: ',bcolors.RED, set(found_vars),bcolors.ENDC)

  for i in range(0, len(abstract_tokens)):
    if var_array[i] == 10:  # science keyword
      abstract_tokens1[i] = bcolors.RED+abstract_tokens1[i]+bcolors.ENDC
    elif abstract_array[i] == 1:  # phenomena
     abstract_tokens1[i] = bcolors.GREEN+abstract_tokens1[i]+bcolors.ENDC
    elif abstract_array[i] == 2:  # realm
      abstract_tokens1[i] = bcolors.BLUE+abstract_tokens1[i]+bcolors.ENDC
    elif abstract_array[i] > 2:  # other
      abstract_tokens1[i] = bcolors.BOLD+abstract_tokens1[i]+bcolors.ENDC

#    if abstract_array[i] + var_array[i] == 1:  # phenomena
#      abstract_tokens1[i] = bcolors.GREEN+abstract_tokens1[i]+bcolors.ENDC
#    elif abstract_array[i] + var_array[i] == 2:  # realm
#      abstract_tokens1[i] = bcolors.GREY+abstract_tokens1[i]+bcolors.ENDC
#    elif abstract_array[i] + var_array[i] == 3:  # science keyword
#      abstract_tokens1[i] = bcolors.RED+abstract_tokens1[i]+bcolors.ENDC
#    elif abstract_array[i] + var_array[i] == 4:  # phenomena and science keyword
#      abstract_tokens1[i] = bcolors.PINK+abstract_tokens1[i]+bcolors.ENDC
#    elif abstract_array[i] + var_array[i] == 5:  # phenomena and science keyword
#      abstract_tokens1[i] = bcolors.BLUE+abstract_tokens1[i]+bcolors.ENDC
  abstract = ' '.join(abstract_tokens1)
  categories1 = OrderedDict(sorted(categories.items()))
  categories1['abstract'] = Abstract
  all_titles.append(categories1)
  print('\n'+abstract)
  #break

with open(os.path.join(json_folder_path, "title_terms_joshua.json"), "w") as fp:
  json.dump(all_titles, fp, indent=4)



