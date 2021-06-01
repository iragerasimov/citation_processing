import os
import json
import re
import glob
import time

library_id = '2395775'
library_type = 'group'
api_key = '0pSr6jlYcsrXlmum9RzhwW4P'

from pyzotero import zotero
zot = zotero.Zotero(library_id, library_type, api_key)

zot_doi_list = []
zot_notes = []
zot_pubs = []
zot_atts = []
json_folder_path = "data"
zotero_path = "/home/igerasim/Zotero/storage/"
regex = r"(?:[(<>)]|)"

coll_key = {	'DIFs':'I28ER4KR',
		'SCOPUS':'CIQKAU2P',
		'WOS':'48XLCAWQ',
		'ACOS_OCO':'649MDWWL',
		'SCOPUS + WOS':'QJR2GCH8',
		'Giovanni.2017':'TFS2QQD8',
		'Aura_MLS':'F3P68PWK',
		'Aura_OMI':'VVMITTJ5',
		'GPM':'AHI8WD5Z',
		'TRMM':'FBETQM7W',
		'Giovanni':'KM3DFTCQ',
		'Giovanni.reviewed':'KQJ5V2EC',
		'MERRA-2':'RH6EGMYW',
		'Forward_GESDISC':'8L3ZJKKV'
	}

coll = 'Forward_GESDISC'

try:
  items = zot.collection_items(coll_key[coll], limit=400) # Forward_GESDISC

  while True:
    for pub_item in items:
      if re.search("note", pub_item['data']['itemType']):
        zot_notes.append(pub_item)
      elif re.search("attachment", pub_item['data']['itemType']):
        zot_atts.append(pub_item)
      else:
        zot_pubs.append(pub_item)
    items = zot.follow()
    time.sleep(1)
except StopIteration:
  print('\nAll items processed')
except Exception as ex:
  print(ex)

with open(os.path.join(json_folder_path, "zot_notes_"+coll.lower()+".json"), "w") as fp:
  json.dump(zot_notes, fp, indent=4)
with open(os.path.join(json_folder_path, "zot_pubs_"+coll.lower()+".json"), "w") as fp:
  json.dump(zot_pubs, fp, indent=4)
with open(os.path.join(json_folder_path, "zot_atts_"+coll.lower()+".json"), "w") as fp:
  json.dump(zot_atts, fp, indent=4)
