import os
import json
import re
import glob
import csv
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
#from nltk.stem import PorterStemmer
#from nltk.stem import LancasterStemmer
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from collections import OrderedDict
from colored import fg, style
import inflect
import numpy as np
from collections import Counter

json_folder_path = 'data'
terms_file = 'terms.json'
#zot_pubs_file = 'zot_pubs_gior.json' #zot_pubs_scopus+wos.json'
zot_pubs_file = 'publications_abstr_gior.json'
csv_sks_path = "data/sciencekeywords.csv"
csv_instr_path = "data/instruments.csv"
csv_missions_path = "data/missions.csv"
csv_locs_path = "data/locations.csv"

#ps = PorterStemmer()
#ps = LancasterStemmer()
ps = SnowballStemmer("english")
#stop_words = set(stopwords.words('english'))
p = inflect.engine()

variables = []
with open(csv_sks_path, newline='') as csvfile:
  reader = csv.reader(csvfile, delimiter=',') 
  for row in reader:
    for i in range (3, 7, 1):
      if row[i] and not re.search(r"(/|\()", row[i]):
        sing = p.singular_noun(row[i])
        if sing and sing != 'biomas':
          variables.append(sing.lower())
        else:
          variables.append(row[i].lower())
variables = sorted(set(variables), key=len, reverse = True)

instruments = []
with open(csv_instr_path, newline='') as csvfile:
  reader = csv.reader(csvfile, delimiter=',') 
  for row in reader:
    for i in range (4, 6, 1):
      if row[i]: # and not re.search(r"(/|\()", row[i]):
        instruments.append(row[i]) #.lower())
instruments = sorted(set(instruments), key=len, reverse = True)
#print(instruments)
#exit()

missions = []
with open(csv_missions_path, newline='') as csvfile:
  reader = csv.reader(csvfile, delimiter=',')
  for row in reader:
    for i in range (2, 4, 1):
      if row[i]: # and not re.search(r"(/|\()", row[i]):
        missions.append(row[i]) #.lower())
missions = sorted(set(missions), key=len, reverse = True)

locations = []
with open(csv_locs_path, newline='') as csvfile:
  reader = csv.reader(csvfile, delimiter=',')
  for row in reader:
    #print("ROW: ")
    #print(row)
    for i in range (1, 5, 1):
      if row[i]: # and not re.search(r"(/|\()", row[i]):
        #print(row[i])
        locations.append(row[i].lower())
locations = sorted(set(locations), key=len, reverse = True)
#print(locations)
#exit()

with open(os.path.join(json_folder_path, terms_file)) as json_publications_file:
  terms = json.load(json_publications_file)

with open(os.path.join(json_folder_path, zot_pubs_file)) as json_publications_file:
  zot_list = json.load(json_publications_file)

def extract_gcmd_terms (all_terms, abstract_tokens, term_array, mask_array, stem=True):
  #if not stem:
  #  print (' '.join(abstract_tokens))
  #  exit()
  gcmd_terms = []
  lc_abstract_tokens = []
  for token in abstract_tokens:
    lc_abstract_tokens.append(token.lower())
  for var in all_terms:
    tokens = word_tokenize(var)
    token_cnt = len(tokens)
    if stem: # or token_cnt > 1:
      tokens = []
      for a in word_tokenize(var):
        tokens.append(ps.stem(a))
      abstract_tokens = lc_abstract_tokens
    #if var == 'MLS':
    #  print (' '.join(abstract_tokens))
    #  print(token_cnt)
    #  exit()
    for i in range(0, len(abstract_tokens) - token_cnt + 1): #-1):
      present = False
      for j in range(0, token_cnt):
        if mask_array[i+j]:
          present = False
          break
        if term_array[i+j]:
          present = False
          break
        if abstract_tokens[i+j] != tokens[j]:
          present = False
          break
        present = True
      if present:
        for j in range(0, token_cnt):
          term_array[i+j] = 1
        gcmd_terms.append(var)
  return gcmd_terms


sweet_cats = {'Phenomena': 1, 'Realm': 2, 'Material': 3, 'Materials': 3, 'Property': 4, 'State': 5, 'Human': 6, 'Process': 7, 'Representation': 8, 'Relationships': 9}
pos_set = ('NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'JJR', 'JJS', 'VBG', 'VBP')
phen_set = ('variability', 'variation', 'transport', 'emission', 'perturbation', 'change', 'evolution')
sing_set = ('biomass', 'data', 'gas', 'as', 'mass')
cnt = 0
all_titles = []
for pub_item in zot_list:
  #Abstract =  pub_item['data'].get('title', '') + '. '+ pub_item['data'].get('abstract', '')
  Abstract =  pub_item['title']+ '. '+ pub_item['abstract']
  #Abstract = "Case Study. A severe dust storm and the evolution of the PM10"
#"Upwelling areas as climate change refugia for the distribution and genetic diversity of a marine macroalga"
#Aerosol optical depth variability over the Arabian Peninsula as inferred from satellite measurements"
#Diagnostic evaluation of the Community Earth System Model in simulating mineral dust emissions with insight into large-scale dust storm mobilization in the Middle East and North Africa"
  Abstract = re.sub(r'\s*\<\s*\/*su(b|p)\s*\>\s*', '', Abstract)
  Abstract = re.sub(r'\n|\t', '', Abstract)
  Abstract = re.sub(r'-', ' ', Abstract)
  Abstract1 = Abstract
  abstract = Abstract.lower()
  #print(abstract)
  Abstract_tokens = word_tokenize(Abstract)	# tokens with original letters
  #abstract_tokens1 = word_tokenize(abstract)	# tokens with lowercase letters
  abstract_pos = nltk.pos_tag(Abstract_tokens)  # list of (token, POS) tuples
  #print(abstract_pos)
  abstract_tokens_sing = []
  for i in range(len(abstract_pos)):
    #if abstract_pos[i][1] == 'NNS' or abstract_pos[i][1] == 'NNP' :
    temp = list(abstract_pos[i])
    sing = p.singular_noun(abstract_pos[i][0])
    if sing and abstract_pos[i][0] not in sing_set:
      temp[0] = sing
    if temp[0].lower() == 'a': 
      temp[1] = 'DT';
    abstract_pos[i] = tuple(temp)
    abstract_tokens_sing.append(abstract_pos[i][0].lower())
    #print(abstract_pos[i])
  #print(abstract_pos)
  #exit()
  abstract_array = [0] * len(Abstract_tokens)
  term_array = ["" for i in range(len(Abstract_tokens))]
  var_array = [0] * len(Abstract_tokens)
  instr_array = [0] * len(Abstract_tokens)
  miss_array = [0] * len(Abstract_tokens)
  locs_array = [0] * len(Abstract_tokens)
  #abstract_tokens2 = [w for w in abstract_tokens1 if not w in new_stop_words]
  abstract_tokens = []				# stemmed lowercase tokens
  for a in Abstract_tokens:
    abstract_tokens.append(ps.stem(a))
  #print(abstract_tokens)
  #print(' '.join(Abstract_tokens))

  mask_array = abstract_array
  # find all instruments, missions, locations and science keywords
  found_instr = extract_gcmd_terms (instruments, Abstract_tokens, instr_array, mask_array, False)  # unstemmed tokens
  found_miss = extract_gcmd_terms (missions, Abstract_tokens, miss_array, mask_array, False)       # unstemmed tokens
  found_locs = extract_gcmd_terms (locations, abstract_tokens_sing, locs_array, mask_array, False)      # stemmed tokens 
  mask_array = list(np.array(instr_array)+np.array(miss_array)+np.array(locs_array))
  found_vars = extract_gcmd_terms (variables, abstract_tokens_sing, var_array, mask_array, False)        # stemmed tokens

  # search for SWEET terms excluding instruments, missions, locations
  categories = {}
  sweet_terms = {}
  found_terms = []
  for term in sorted(terms.keys(), key=len, reverse = True):
    term_present = False
    term_tokens = []
    term_tokens1 = word_tokenize(term)
    ###term_tokens2 = [w for w in term_tokens1 if not w in new_stop_words]
    #for a in term_tokens1:
    #  term_tokens.append(ps.stem(a))
    term_tokens = term_tokens1
    #if len(term_tokens) < len(term_tokens1):
    #  continue
    tocken_cnt = len(term_tokens)
    for i in range(0, len(abstract_tokens) - tocken_cnt + 1):
      for j in range(0, tocken_cnt):
        if mask_array[i+j]:
          term_present = False
          break
        if abstract_array[i+j]:
          term_present = False
          break
        #if abstract_tokens[i+j] != term_tokens[j]:
        if abstract_pos[i+j][1] not in pos_set:
          term_present = False
          break
        if abstract_pos[i+j][0].lower() != term_tokens[j]:
          term_present = False
          break
        #print(abstract_tokens[i+j]+' '+term_tokens[j])
        term_present = True
      if term_present:
        for j in range(0, tocken_cnt):
          abstract_array[i+j] = sweet_cats[(terms[term][0].split())[0]]
          term_array[i+j] = term_tokens[j]
        found_terms.append(term)
  #print(found_terms)

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
    print(cat+': ', fg(sweet_cats[cat]+5), ', '.join(set(sweet_terms[cat])),style.RESET)
  print('Science Keywords: ', fg(1), set(found_vars), style.RESET)
  print('Instruments: ', fg(2), set(found_instr), style.RESET)
  print('Missions: ', fg(4), set(found_miss), style.RESET)
  print('Locations: ', fg(5), set(found_locs), style.RESET)

  for i in range(0, len(abstract_tokens)):
    if instr_array[i]:   # instruments
      Abstract_tokens[i] = fg(2)+Abstract_tokens[i]+style.RESET
    elif miss_array[i]:   # missions
      Abstract_tokens[i] = fg(4)+Abstract_tokens[i]+style.RESET
    elif locs_array[i]:   # locations
      Abstract_tokens[i] = fg(5)+Abstract_tokens[i]+style.RESET
    elif abstract_array[i]:  # sweet terms
      Abstract_tokens[i] = fg(abstract_array[i]+5)+Abstract_tokens[i]+style.RESET
      term_array[i] = fg(abstract_array[i]+5)+term_array[i]+style.RESET
    elif var_array[i]:  # science keyword
      Abstract_tokens[i] = fg(1)+Abstract_tokens[i]+style.RESET
  Abstract = ' '.join(Abstract_tokens)
  abstract_terms = " ".join(term_array)
  #categories1 = OrderedDict(sorted(categories.items()))
  #categories1 = {}
  #categories1['abstract'] = Abstract1
  #all_titles.append(categories1)
  print(Abstract+'\n')
  #print(abstract_terms+'\n')

  #print(abstract_array)
  last_ind=-1
  phenomena = []
  out_phenomena = []
  for i in range(0, len(abstract_tokens)):
    if i <= last_ind:
      continue
    if abstract_array[i] == 1 or abstract_array[i] == 4: # Phenomena or Property
      phen_array = []
      phen_ind = [i, i]
      #print(phen_ind)
      #print(term_array[i])
      for j in range(i-1, -1, -1):
        if abstract_array[j]:
          phen_ind[0] = j
        else:
          break
      for j in range(i+1, len(abstract_tokens), 1):
        if abstract_array[j]:
          phen_ind[1] = j
        elif abstract_pos[j-1][0].lower() and abstract_pos[j][1] == 'IN' and abstract_array[j+1]:
          phen_ind[1] = j
        elif abstract_pos[j-1][0].lower() and abstract_pos[j][1] == 'IN' and abstract_pos[j+1][1] == 'DT' and abstract_array[j+2]:
          phen_ind[1] = j
        elif abstract_pos[j][1] == 'DT' and abstract_pos[j-1][1] == 'IN' and abstract_pos[j-2][0].lower() and abstract_array[j+1]:
          phen_ind[1] = j
        else:
          break
      #print(phen_ind)
      last_ind = phen_ind[1]
      #print("last ind: "+str(last_ind))
      out_array = []
      skip = 0
      ind = 0
      for j in range(phen_ind[0], phen_ind[1]+1):
        if term_array[j]:
          if not skip:
            phen_array.append(term_array[j])
            out_array.append(abstract_pos[j][0].lower())
          else:
            phen_array.insert(ind, term_array[j])
            out_array.insert(ind, abstract_pos[j][0].lower())
            ind += 1
        else:
          skip = 1
          ind = 0
          #phen_array.append(Abstract_tokens[j].lower())
        #out_array.append(abstract_pos[j][0])
      phenomena.append(" ".join(phen_array))
      out_phenomena.append(" ".join(out_array))
  #print(Counter(phenomena))
  phenomena_set = sorted(set(phenomena))
  c = Counter(phenomena)
  for phen in phenomena_set:
    print("Phenomena ("+ str(c[phen]) +"): "+phen)
  all_titles.append({'abstract': Abstract1, 
                     'instruments': sorted(set(found_instr)), 
                     'missions': sorted(set(found_miss)),
                     'locations': sorted(set(found_locs)),
                     'phenomena': sorted(out_phenomena)})
  cnt += 1
  #if cnt == 1: #80:
  #  break

with open(os.path.join(json_folder_path, "title_terms_gior.json"), "w") as fp:
  json.dump(all_titles, fp, indent=4)


# added SWEET terms
# phytoplankton bloom
# solar irradiance
# vertical distribution
# marine environment
# pm2.5
# urban
