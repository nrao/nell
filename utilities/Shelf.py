import shelve
from Borg import Borg

class Shelf(Borg):
    """
    Borg (singleton-type class that only worries about a single state)
    for retaining data between server invocations using shelve.  Persistance
    is convenient, not guaranteed since it depends on a file in /tmp.
    """
    _shared_state = {}

    def __init__(self):
        self.shelf = shelve.open("/tmp/nell_shelve")

    def __getitem__(self, name):
        return self.shelf[name]

    def __setitem__(self, name, value):
        self.shelf[name] = value

    def sync(self):
        self.shelf.sync()

    def close(self):
        self.shelf.close()
