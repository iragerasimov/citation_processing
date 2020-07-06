from collections import defaultdict
class Paper(object):
    def __init__(self, zot_dict):
        self.meta = zot_dict['meta']
        self.data = zot_dict['data']
        self.key = zot_dict['key']
        self.notes = []
        self.links = []
        self.tags = []

    def add_note(self, note):
        self.notes.append(note)

    def add_tag(self, tag):
        self.tags.append(tag)

    def add_link(self, link):
        self.links.append(link)



