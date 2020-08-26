import os
import json
import re
import glob

# https://pyzotero.readthedocs.io/en/latest/
# https://api.zotero.org/groups/2395775/items
# https://api.zotero.org/groups/2395775/collections
# https://api.zotero.org/groups/2395775/collections/R7GFRKES/tags
# https://api.zotero.org/groups/2395775/collections/R7GFRKES/items?tag=dataset%3AML2CO_003%3A+Level+2+data+of+version+3.3+are+used
# https://api.zotero.org/groups/2395775/collections/R7GFRKES/items?tag=dataset%3AML2CO
# https://api.zotero.org/groups/2395775/items?tag=dataset%3AML2CO
# https://api.zotero.org/groups/2395775/collections/R7GFRKES/items?itemType=note
# https://api.zotero.org/groups/2395775/items?tag=dataset%3AML2CO
# DIFs: https://api.zotero.org/groups/2395775/collections/I28ER4KR/items 
# File "/home/igerasim/anaconda3/lib/python3.7/site-packages/pyzotero/zotero.py", line 1274, in create_items
# #backoff = presp.get("backoff") changed to backoff = presp.headers.get("backoff")


library_id = '2395775'
library_type = 'group'
api_key = '0pSr6jlYcsrXlmum9RzhwW4P'

from pyzotero import zotero
zot = zotero.Zotero(library_id, library_type, api_key)

zot_doi_list = []
refs_list = []
zot_notes = []
zot_pubs = []
eid_list = []
json_folder_path = "data"
regex = r"(?:[(<>)]|)"
regex1 = r"(/|\?|\:|\.)+"

#with open(os.path.join(json_folder_path, "cross_refs_save1.json")) as json_publications_file:
with open(os.path.join(json_folder_path, "cross_docs_cleaned.json")) as json_publications_file:
  refs_list = json.load(json_publications_file)

with open(os.path.join(json_folder_path, "zot_notes.json")) as json_publications_file:
  zot_notes = json.load(json_publications_file)

with open(os.path.join(json_folder_path, "zot_pubs.json")) as json_publications_file:
  zot_pubs = json.load(json_publications_file)

with open(os.path.join(json_folder_path, "datasets.json")) as json_publications_file:
  eid_list = json.load(json_publications_file)

def search_pubs(zot_pubs, doi):
  if re.match("http", doi, re.IGNORECASE) or re.match("ftp", doi, re.IGNORECASE):
    url1 = re.sub(regex1, '', doi)
    for pub_item in zot_pubs:
      url2 = pub_item['data'].get('url', '')
      if not url2:
        continue
      url2 = re.sub(regex1, '', url2)
      if re.search(url1, url2, re.IGNORECASE):
        return pub_item
    return None

  doi1 = re.sub(regex, '', doi)
  for pub_item in zot_pubs:
    doi = pub_item['data'].get('DOI', '')
    if not doi and re.search("DOI: ", pub_item['data']['extra']):
      doi = re.sub("DOI: ", '', pub_item['data']['extra'])
    elif not doi and re.search("Document ID: ", pub_item['data']['extra']):
      doi = pub_item['data']['extra']
    doi2 = re.sub(regex, '', doi)
    if re.search(doi1, doi2, re.IGNORECASE):
      return pub_item
  return None

def get_dataset_list(eid_list, entry_ids):
  datasets = []
  for entry_id in entry_ids:
    datasets.append(eid_list[entry_id])
  return sorted(set(datasets))


note_delim = "<br />"
for ref in refs_list:
  if ref["validated"] != "yes":
    continue
  if not ref["new_doi"]:
    print("Skipping "+ref["cit"])
    continue
  zot_pub = search_pubs(zot_pubs, ref["new_doi"])
  if not zot_pub:
    print('Cannot find '+ref["new_doi"]+' in zotero pubs')
    break
  print("zot item: "+zot_pub["key"])
  to_review = 1
  if len(zot_pub["data"]["tags"]):
    for tag in zot_pub["data"]["tags"]:
      #print("tag: " + tag["tag"])
      if re.search("review", tag["tag"]):
        to_review = 0
        break
  if not to_review:
    continue
  dif_author = ref.get("dif_author", '')
  #if not dif_author:
  print("DIF author: "+ref["dif_author"])
  ref["dif_author"] = re.split(',', ref["dif_author"])[0]
  #break
  (fname, lname) = re.split('\s+', ref["dif_author"])
  dif_author = (fname[0]+lname).lower()
  print('dif_author '+dif_author)
  #zot_pub["data"]["tags"].append('reviewer:'+dif_author)
  note_item = zot.item_template('note')
  #print(note_item)
  datasets = get_dataset_list(eid_list, ref["DIFs"])
  note_item["note"] = note_delim.join(datasets)
  note_item["tags"].append({"tag": "category:unknown"})
  note_item["tags"].append({"tag": "category:dif"})
  print(note_item)
 
  resp = zot.add_tags(zot_pub, 'reviewer:'+dif_author)
  print(resp)
  resp = zot.create_items([note_item], zot_pub["key"])
  print(resp)
  #break



