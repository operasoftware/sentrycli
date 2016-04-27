from dateutil.parser import parse


class Event(object):
    def __init__(self, raw):
        self.raw = raw

    @property
    def ctime(self):
        return parse(self.raw['dateCreated'])
