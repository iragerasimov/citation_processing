import os
import json
import time
from collections import defaultdict
from Paper import *


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

articles = {}
notes = {}
attachments = {}
other = {}
lookup_child_notes = defaultdict(list)
lookup_child_links = defaultdict(list)
for item in items:
    if item['data']['itemType'] == 'note':
        notes[item['key']] = item
        lookup_child_notes[item['data']['parentItem']] = item['key']
    elif item['data']['itemType'] == 'journalArticle':
        articles[item['key']] = item
    elif item['data']['itemType'] == 'attachment':
        attachments[item['key']] = item
        lookup_child_links[item['data']['parentItem']] = item['key']
    else:
        other[item['key']] = item

papers = []
for article in articles.keys(): ### ONLY ADDS 1 NOTE PER TIME
    paper = Paper(articles[article])
    if lookup_child_notes[article]:
        paper.add_note(notes[lookup_child_notes[article]]['data']['note'])
        for tag in notes[lookup_child_notes[article]]['data']['tags']:
            paper.add_tag(tag['tag'])

    if lookup_child_links[article]:
        data = attachments[lookup_child_links[article]]['data']
        paper.add_link(data['url'])
    papers.append(paper)

for i in range(10):
    print(papers[i].links, papers[i].notes, papers[i].tags)

