# curl "https://cmr.earthdata.nasa.gov/search/collections.json?platform\[\]=Aura&Instrument\[\]=MLS&processing_level_id\[\]=2&version=004&page_size=100" > cmr_datasets.json
# curl -i "https://cmr.earthdata.nasa.gov/search/collections.dif10?provider_id=GES_DISC&entry_id=ML2CO_004&pretty=true"| awk '/<Dataset_Citation>/,/<\/Dataset_Citation>/{if($0~/<Identifier>/) {print $0}}'

import json
import csv
import os
import re
import subprocess
import requests
import xml.etree.ElementTree as ET
import glob

difs = glob.glob("PROD_20200308/*.xml")
ns = {'namespace': 'http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/'}

dataset_list = {}
datasets = {}

def search_by_doi(references, doi):
  for reference in references:
    if reference['doi'] == doi:
      return reference
  return None

def search_by_cit(references, cit):
  for reference in references:
    if reference['cit'] == cit:
      return reference
  return None

def search(references, doi, cit):
  for reference in references:
    if reference['doi'] == doi and reference['cit'] == cit:
      return reference
  return None


for dif in difs:
  #print(dif)
  dataset = ''
  entry_id = ''
  tree = ET.parse(dif)
  root = tree.getroot()
  for child in root:
    true_tag = child.tag.replace(("{"+ns.get('namespace')+"}"),'')
    if true_tag == "Entry_ID":
      dataset = child.find("{"+ns.get('namespace')+"}Short_Name").text
      version = child.find("{"+ns.get('namespace')+"}Version").text
      entry_id = dataset+'_'+child.find("{"+ns.get('namespace')+"}Version").text
      continue
    if true_tag == "Entry_Title":
      title = child.text
  #dataset_list.append({
  #  "dataset": dataset, 
  #  "entry_id": entry_id
  #})
  title = tit=re.sub("\s+V"+version+r'.*', '', title)
  datasets[dataset] = title
  dataset_list[entry_id] = dataset

new_folder_path = "data"
#with open(os.path.join(new_folder_path, "datasets.json"), "w") as fp:
#  json.dump(dataset_list, fp, indent=4)

with open('data/ds_longnames.csv', 'w', newline='') as csvfile:
  spamwriter = csv.writer(csvfile, delimiter=',', dialect='excel')
  for ds in sorted(datasets):
    spamwriter.writerow([ds, datasets[ds]])

