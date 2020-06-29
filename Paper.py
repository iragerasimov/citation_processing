class Paper(object):
    def __init__(self, zot_dict):
        self.meta = zot_dict['meta']
        self.data = zot_dict['data']
        self.library = zot_dict['library']
        self.key = zot_dict['key']
