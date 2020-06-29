import os
import json
import re
import glob

from Paper import *


from pyzotero import zotero

library_id = '6657757'
library_type = 'user'
api_key = 'ZUtqoDZaIFDZTZoTt83hoId7'

zot = zotero.Zotero(library_id, library_type, api_key)

collection_id = '4HLCJQ8L'
collection = zot.collection(collection_id)

print(collection['data'])
print(collection['meta'])
items = zot.collection_items(collection_id)
print(items[0])
print(len(items))