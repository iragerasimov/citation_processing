# creates data_sets.json that contains data_set_id, title and abstract
# takes as input cmr_datasets.json
# curl "https://cmr.earthdata.nasa.gov/search/collections.json?platform\[\]=Aura&Instrument\[\]=MLS&processing_level_id\[\]=2&version=004&page_size=100" > cmr_datasets.json

import json
import os
import re
import subprocess
import requests
import xml.etree.ElementTree as ET

json_cmr_datasets_path = os.path.abspath("cmr_datasets.json")
with open(json_cmr_datasets_path) as json_cmr_datasets_file:
  json_cmr_datasets = json.load(json_cmr_datasets_file)

json_cmr_dataset_list = json_cmr_datasets["feed"]["entry"]
ns = {'namespace': 'http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/'}

dataset_list = []
for json_cmr_dataset in json_cmr_dataset_list:
  if "_NRT" in json_cmr_dataset["short_name"]:
    continue
  entry_id = json_cmr_dataset["short_name"]+'_'+json_cmr_dataset["version_id"]
  params = (
    ('provider_id', 'GES_DISC'),
    ('entry_id', entry_id),
    ('pretty', 'true'),
  )
  response = requests.get('https://cmr.earthdata.nasa.gov/search/collections.dif10', params=params)
  #response = requests.get('https://cmr.earthdata.nasa.gov/search/collections.dif10?provider_id=GES_DISC&entry_id=ML2CO_004&pretty=true')
  root = ET.fromstring(response.text)
  DOI = None
  for child in root:
    if child.tag == "result":
      items = child.find("{"+ns.get('namespace')+"}DIF")
      for item in items:
        true_tag = item.tag.replace(("{"+ns.get('namespace')+"}"),'')
        if (true_tag == "Dataset_Citation"):
          pids = item.find("{"+ns.get('namespace')+"}Persistent_Identifier")
          for pid in pids:
            true_tag = pid.tag.replace(("{"+ns.get('namespace')+"}"),'')  
            if true_tag == "Identifier":
              DOI = pid.text
              print(DOI)      

  dataset_list.append({
    "data_set_id": json_cmr_dataset["short_name"],
    "version_id": json_cmr_dataset["version_id"],
    "unique_identifier": DOI,
    "title": json_cmr_dataset["dataset_id"],
    "name": json_cmr_dataset["dataset_id"],
    "description": json_cmr_dataset["summary"],
    "date": "",
    "coverages": "",
    "subjects": "",
    "methodology": "",
    "citation": "",
    "additional_keywords": "",
    "family_identifier": "",
    "mention_list": [],
    "identifier_list": [
            {
                "name": "https://doi.org/",
                "identifier": DOI
            }]
  })

new_folder_path = "data"
with open(os.path.join(new_folder_path, "data_sets.json"), "w") as fp:
  json.dump(dataset_list, fp, indent=4)

