from CNF    import cnf
from Parse  import parse, scan

class ReceiverCompile:

    def __init__(self, names):
        """
        The argument names contains a list of receiver abbreviations,
        e.g., 1070 or L.
        """
        self.names = names

    def normalize(self, text):
        """
        Accepts a string containing a multi-receiver specification in logical
        form, e.g., "Ka | (L & S)" or "Q" (using receiver abbreviations)
        and returns a list of lists in CNF, e.g.,
        [['Ka', 'L'], ['Ka', 'S']] and [['Q']] respectively. Note that
        'and' may be represented by '&' or '^' and 'or' may be represented
        by '|' or 'v'.
        """
        if text is None:
            return []
        if isinstance(text, unicode):
            text = text.encode("ascii")
        prop = parse(scan('(' + text + ')'))
        rcvr_grps = cnf(prop)
        self.checkAbbreviations(rcvr_grps)
        return rcvr_grps

    def checkAbbreviations(self, rcvr_grps):
        """
        Throws a ValueError if the receiver groups contain a
        non-abbreviations.
        """
        for rg in rcvr_grps:
            for r in rg:
                if r not in self.names:
                    raise ValueError, "%s not a receiver" % r
