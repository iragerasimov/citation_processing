import os
import json
import re
import glob

library_id = '2395775'
library_type = 'group'
api_key = '0pSr6jlYcsrXlmum9RzhwW4P'

from pyzotero import zotero
zot = zotero.Zotero(library_id, library_type, api_key)

zot_doi_list = []
refs_list = []
zot_notes = []
zot_pubs = []
json_folder_path = "data"
zotero_path = "/home/igerasim/Zotero/storage/"
cross_ref_file = "cross_refs_save1.json"
regex = r"(?:[(<>)]|)"

with open(os.path.join(json_folder_path, cross_ref_file)) as json_publications_file:
  refs_list = json.load(json_publications_file)

def search_refs(refs_list, doi):
  doi1 = re.sub(regex, '', doi)
  for ref in refs_list:
    doi2 = re.sub(regex, '', ref['new_doi'])
    if re.search(doi1, doi2, re.IGNORECASE):
      ref['zotero'] = 'yes'
      return ref
  return None

try:
  #items = zot.collection_items('I28ER4KR', limit=10) # DIFs
  #items = zot.collection_items('CIQKAU2P', limit=10) # SCOPUS
  #items = zot.collection_items('48XLCAWQ', limit=10) # WOS
  #items = zot.collection_items('649MDWWL', limit=10) # ACOS/OCO
  #items = zot.collection_items('QJR2GCH8', limit=10) # SCOPUS + WOS
  items = zot.collection_items('TFS2QQD8', limit=10) # Giovanni.2017
  #items = zot.collection_items('F3P68PWK', limit=10) # Aura/MLS
  while True:
    for pub_item in items:
      if re.search("note", pub_item['data']['itemType']):
        zot_notes.append(pub_item)
      elif re.search("attachment", pub_item['data']['itemType']):
        #print('This is attachment, skipping')
        a=1
      else:
        zot_pubs.append(pub_item)
    items = zot.follow()
except StopIteration:
  print('\nAll items processed')
except Exception as ex:
  print(ex)

#with open(os.path.join(json_folder_path, "zot_notes_0504_2020.json"), "w") as fp:
with open(os.path.join(json_folder_path, "zot_notes_gio.2017.json"), "w") as fp:
  json.dump(zot_notes, fp, indent=4)
#with open(os.path.join(json_folder_path, "zot_pubs_0504_2020.json"), "w") as fp:
with open(os.path.join(json_folder_path, "zot_pubs_gio.2017.json"), "w") as fp:
  json.dump(zot_pubs, fp, indent=4)

