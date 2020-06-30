# takes as input data_sets.json and extracts all notes from Zotero that have that dataset tag
# using notes it creates a list of all dataset mentions and dumps it into data_set_citations.json
# then it creates a list of all publications that have those mentions and publications paper titles 
# and places that list into publications.json

import os
import json
import re
import glob

from pyzotero import zotero

library_id = '2395775'
library_type = 'group'
api_key = '0pSr6jlYcsrXlmum9RzhwW4P'


zot = zotero.Zotero(library_id, library_type, api_key)

publication_list = []
publication_ids = []
citation_list = []
json_folder_path = "data"
zotero_path = "~/Zotero/storage/"
datasets_file = "data_sets.json"
publications_file = "publications.json"
data_set_citations_file = "data_set_citations.json"

with open(os.path.join(json_folder_path, datasets_file)) as json_datasets_file:
    dataset_list = json.load(json_datasets_file)

#  with open(os.path.join(json_folder_path, publications_file)) as json_publications_file:
#  publications_list = json.load(json_publications_file)


def search(cit_list, publication_id, dataset_id):
  for citation in cit_list:
    if citation['publication_id'] == publication_id and citation['data_set_id'] == dataset_id:
      return citation
  return False


def search_pubs(pub_list, publication_id):
  for publication in pub_list:
    if publication['publication_id'] == publication_id:
      return publication
  return False


for dataset in dataset_list:
  dataset_tag = "dataset:"+dataset["data_set_id"] 
  try:
    #items = zot.collection_items('R7GFRKES', tag=dataset_tag, limit=10)
    items = zot.items(tag=dataset_tag, limit=10)
    print(str(len(items))+" for "+ dataset_tag) 
    while True:
      for item in items:
        if item['data']['itemType'] != 'note':
          continue
       # print ('Note: %s Tags: %s' % (item['data']['note'], item['data']['tags']))
        publication_id = item['data']['parentItem']
        note = re.sub('(</p>)|(<p>)|(<br />)|(<br/>)', '', item['data']['note'])      
        print('Note: %s Publication: %s' % (item['data']['note'], publication_id))
        citation = search(citation_list, publication_id, dataset["data_set_id"])
        if citation:
          print("appending note to "+publication_id+", "+dataset["data_set_id"])
          citation["mention_list"].append(note)
        else:
          print("creating new citation for "+publication_id+", "+dataset["data_set_id"])
          citation_list.append({
            "citation_id": len(citation_list)+1,
            "publication_id": publication_id,
            "data_set_id": dataset["data_set_id"],
            "mention_list": [ note ],
            "score": 1.0   
          })
        if publication_id not in publication_ids:
          publication_ids.append(publication_id)
      items = zot.follow()
  except StopIteration:
    print('\nAll items processed')
  except Exception as ex:
    print(ex)

with open(os.path.join(json_folder_path, data_set_citations_file), "w") as fp:
  json.dump(citation_list, fp, indent=4)

for publication_id in publication_ids:
   if search_pubs(publication_list, publication_id):
     continue
   pub_item = zot.item(publication_id)
   #print ('Id: %s; Title: %s; date: %s;' % (publication_id, pub_item['data']['title'], pub_item['data']['date']))
   author = pub_item['data']['creators'][0]["lastName"]
   title = pub_item['data']['title']
   nums = re.findall(r'\d{4}', pub_item['data']['date'])
   year = None
   pdf_name = None
   if nums:
     year = nums[0]
     pdf_name = year+'_'
   if author:
     pdf_name = pdf_name+author+'_'
   pdf_name = pdf_name+title[0:50]
   if ':' in pdf_name:
     pdf_name = pdf_name.split(':')[0]
   #print ('PDF name: %s' % (pdf_name))
   pdf_name = re.sub('(<)|(>)', '', pdf_name)
   pdf_name = re.sub('/', '-', pdf_name)
   pdf_files = glob.glob(zotero_path+'*/'+pdf_name+'*.pdf');
   pdf_file = None
   txt_name = None
   if pdf_files:
     pdf_file = pdf_files[0] #os.path.basename(pdf_files[0])
     txt_name = publication_id+'.txt'
   else:
     print("No pdf file for "+pdf_name)
   #print ('PDF name: %s' % (pdf_file))
   publication_list.append({
     "publication_id": publication_id,
     "unique_identifier": pub_item['data']['DOI'],
     "title": pub_item['data']['title'],
     "pub_date": year,
     "pdf_file_name": pdf_file,
     "text_file_name": txt_name
   })

with open(os.path.join(json_folder_path, publications_file), "w") as fp:
  json.dump(publication_list, fp, indent=4)

