from sesshuns.models  import first, TimeZone, Repeat
from sesshuns.utilities import parse_datetime
class BlackoutValidator (object):

    def __init__(self, data, errors, start, end, until, repeat, description):
        self.data        = data
        self.errors      = errors
        self.start_date  = start
        self.end_date    = end
        self.until       = until
        self.repeat      = repeat
        self.description = description

    @staticmethod
    def validate(data):
        # Now see if the data to be saved is valid    
        # Convert blackout to UTC.
        utcOffset = first(TimeZone.objects.filter(timeZone = data['tz'])).utcOffset()
        # watch for malformed dates
        start, stError = parse_datetime(data, 'start', 'starttime', utcOffset)
        end,   edError = parse_datetime(data,   'end',   'endtime', utcOffset)
        until, utError = parse_datetime(data, 'until', 'untiltime', utcOffset)
        repeat      = first(Repeat.objects.filter(repeat = data['repeat']))
        description = data['description']
        errors = [e for e in [stError, edError, utError] if e is not None]

        # more error checking!
        # start, end can't be null
        if start is None or end is None:
            errors.append("ERROR: must specify Start and End")
        # start has to be a start, end has to be an end 
        if end is not None and start is not None and end < start:
            errors.append("ERROR: End must be after Start")
        if end is not None and until is not None and until < end:
            errors.append("ERROR: Until must be after End")
        # if it's repeating, we must have an until date
        if repeat.repeat != "Once" and until is None:
            errors.append("ERROR: if repeating, must specify Until")

        return BlackoutValidator(data, errors, start, end, until, repeat, description)
