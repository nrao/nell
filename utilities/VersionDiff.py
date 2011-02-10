
class VersionDiff():

    def __init__(self, dt = None, field = None, value1 = None, value2 = None):

        self.dt = dt # when the change was made from value1 to value2
        self.field = field
        self.value1 = value1  # original value
        self.value2 = value2  # new value

        self.dtFormat = "%Y-%m-%d %H:%M:%S"

    def __str__(self):
        return  "(%s) field %s: %s -> %s" % (self.dt.strftime(self.dtFormat)
                                           , self.field
                                           , self.value1
                                           , self.value2
                                            )
        
