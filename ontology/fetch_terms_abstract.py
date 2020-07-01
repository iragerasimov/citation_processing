import os
import json
import re
import glob
import csv
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from collections import OrderedDict
from colored import fg, style

json_folder_path = 'data'
terms_file = 'terms.json'
zot_pubs_file = 'zot_pubs_joshua.json' #zot_pubs_scopus+wos.json'
csv_sks_path = "data/sciencekeywords.csv"
csv_instr_path = "data/instruments.csv"
csv_missions_path = "data/missions.csv"
csv_locs_path = "data/locations.csv"

ps = PorterStemmer()
stop_words = set(stopwords.words('english'))
new_stopwords = ['lead', 'leading']
stop_words.update(new_stopwords)
new_stop_words = set(stop_words)

variables = []
with open(csv_sks_path, newline='') as csvfile:
  reader = csv.reader(csvfile, delimiter=',') 
  for row in reader:
    for i in range (3, 7, 1):
      if row[i] and not re.search(r"(/|\()", row[i]):
        variables.append(row[i].lower())
variables = sorted(set(variables), key=len, reverse = True)

instruments = []
with open(csv_instr_path, newline='') as csvfile:
  reader = csv.reader(csvfile, delimiter=',') 
  for row in reader:
    for i in range (4, 6, 1):
      if row[i]: # and not re.search(r"(/|\()", row[i]):
        instruments.append(row[i].lower())
instruments = sorted(set(instruments), key=len, reverse = True)

missions = []
with open(csv_missions_path, newline='') as csvfile:
  reader = csv.reader(csvfile, delimiter=',')
  for row in reader:
    for i in range (1, 4, 1):
      if row[i]: # and not re.search(r"(/|\()", row[i]):
        missions.append(row[i].lower())
missions = sorted(set(missions), key=len, reverse = True)

locations = []
with open(csv_locs_path, newline='') as csvfile:
  reader = csv.reader(csvfile, delimiter=',')
  for row in reader:
    for i in range (1, 4, 1):
      if row[i]: # and not re.search(r"(/|\()", row[i]):
        locations.append(row[i].lower())
locations = sorted(set(locations), key=len, reverse = True)

with open(os.path.join(json_folder_path, terms_file)) as json_publications_file:
  terms = json.load(json_publications_file)

with open(os.path.join(json_folder_path, zot_pubs_file)) as json_publications_file:
  zot_list = json.load(json_publications_file)

def extract_gcmd_terms (all_terms, abstract_tokens, term_array):
  gcmd_terms = []
  for var in all_terms:
    tokens = []
    for a in word_tokenize(var):
      tokens.append(ps.stem(a))
    tocken_cnt = len(tokens)
    for i in range(0, len(abstract_tokens) - tocken_cnt):
      present = False
      for j in range(0, tocken_cnt):
        if var_array[i+j]:
          present = False
          break
        if abstract_tokens[i+j] != tokens[j]:
          present = False
          break
        present = True
      if present:
        for j in range(0, tocken_cnt):
          term_array[i+j] = 1
        gcmd_terms.append(var)
  return gcmd_terms


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
  instr_array = [0] * len(abstract_tokens1)
  miss_array = [0] * len(abstract_tokens1)
  locs_array = [0] * len(abstract_tokens1)
  #abstract_tokens2 = [w for w in abstract_tokens1 if not w in new_stop_words]
  for a in abstract_tokens1:
    abstract_tokens.append(ps.stem(a))
  #print(abstract_tokens)
  #print(' '.join(abstract_tokens1))
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

  found_vars = extract_gcmd_terms (variables, abstract_tokens, var_array)
  found_instr = extract_gcmd_terms (instruments, abstract_tokens, instr_array)
  found_miss = extract_gcmd_terms (missions, abstract_tokens, miss_array)
  found_locs = extract_gcmd_terms (locations, abstract_tokens, locs_array)

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

  # list of colors is in https://pypi.org/project/colored/
  for cat in sweet_terms.keys():
    print(cat+': ', fg(sweet_cats[cat]+5), ', '.join(set(sweet_terms[cat])),bcolors.ENDC)
  print('Science Keywords: ', fg(1), set(found_vars), style.RESET)
  print('Instruments: ', fg(2), set(found_instr), style.RESET)
  print('Missions: ', fg(4), set(found_miss), style.RESET)
  print('Locations: ', fg(5), set(found_locs), style.RESET)

  for i in range(0, len(abstract_tokens)):
    if var_array[i]:  # science keyword
      abstract_tokens1[i] = fg(1)+abstract_tokens1[i]+style.RESET
    elif instr_array[i]:   # instruments
      abstract_tokens1[i] = fg(2)+abstract_tokens1[i]+style.RESET
    elif miss_array[i]:   # instruments
      abstract_tokens1[i] = fg(4)+abstract_tokens1[i]+style.RESET
    elif locs_array[i]:   # instruments
      abstract_tokens1[i] = fg(5)+abstract_tokens1[i]+style.RESET
    elif abstract_array[i]:  # sweet terms
     abstract_tokens1[i] = fg(abstract_array[i]+5)+abstract_tokens1[i]+style.RESET
  abstract = ' '.join(abstract_tokens1)
  categories1 = OrderedDict(sorted(categories.items()))
  categories1['abstract'] = Abstract
  all_titles.append(categories1)
  print('\n'+abstract+'\n')
  #break

with open(os.path.join(json_folder_path, "title_terms_joshua.json"), "w") as fp:
  json.dump(all_titles, fp, indent=4)



