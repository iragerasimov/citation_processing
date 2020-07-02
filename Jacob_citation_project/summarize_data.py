import os
import json
import time
from collections import defaultdict
import matplotlib.pyplot as plt
import re
import glob

from pyzotero import zotero

# library_id = '6657757' # Personal Library ID
library_id = '2395775' # Group Library ID
library_type = 'group'
api_key = 'tB3q3dduZDZR1xXOXGw9ngvV'

zot = zotero.Zotero(library_id, library_type, api_key)

# collection_id = '4HLCJQ8L' # Individual collection id
collection_id = 'F3P68PWK'
collection = zot.collection(collection_id)

load_json = True

if 'itemDict.txt' in list(os.listdir()) and load_json:
    print("Loading values...")
    with open("itemDict.txt", "r") as json_file:
        items = json.load(json_file)
else:
    print("Getting Zotero data...")
    start_time = time.time()
    items = zot.everything(zot.collection_items(collection_id))
    with open('itemDict.txt', "w") as outfile:
        json.dump(items, outfile)
    print("Data loaded. It took %s seconds to load the data." %(time.time() - start_time))

count_note = 0
count_journal = 0
count_other = 0
d = defaultdict(int)

for item in items:
    if item['data']['itemType'] == 'note':
        for tag in item['data']['tags']:
            if 'dataset' not in tag['tag']:
                continue
            d[tag['tag'].split(":")[1]] += 1
        count_note += 1
        continue
    elif item['data']['itemType'] == 'journalArticle':
        count_journal += 1
    else:
        count_other += 1
print(count_note, count_journal, count_other)
print(len(d.keys()))
print(sum(d.values()))
x = []
y = []
for key in d.keys():
    if d[key] > 10:
        x.append(key)
        y.append(d[key])
print(len(x))
print(y)

# plt.bar(x, y)
# plt.legend()
# plt.show()
# plt.hist(d.values(), [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50], histtype='bar')
# plt.xlabel("Dataset Frequency in MLS/Aura")
# plt.show()