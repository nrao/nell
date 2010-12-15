class Document(object):
    def __init__(self):
        self.observers = []

    def notify(self, keyword, value):
        for o in self.observers:
            o.onNotify(keyword, value)

    def addObserver(self, observer):
        self.observers.append(observer)
