import math

class SearchResult(object):
    def __init__(self, path=[], path_len=0, ele_gain=0):
        self.path = path
        self.path_len = path_len
        self.ele_gain = ele_gain
