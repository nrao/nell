from datetime                  import datetime, timedelta, date
from math                      import asin, acos, cos, sin
from django.db                 import models
from django.http               import QueryDict
from nell.utilities            import TimeAgent, UserInfo, NRAOBosDB, Score
from nell.utilities.receiver   import ReceiverCompile
from settings                  import ANTIOCH_HOST, PROXY_PORT

import calendar
import pg
from sets                      import Set
import urllib2
import simplejson as json
import sys

def first(results, default = None):
    try:
        return results[0]
    except IndexError:
        return default

def str2dt(str):
    "'YYYY-MM-DD hh:mm:ss' to datetime object"
    if str is None:
        return None

    if ' ' in str:
        dstr, tstr = str.split(' ')
        y, m, d    = map(int, dstr.split('-'))
        time       = tstr.split(':')
        h, mm, ss  = map(int, map(float, time))
        return datetime(y, m, d, h, mm, ss)

    y, m, d   = map(int, str.split('-'))
    return datetime(y, m, d)

def strStr2dt(dstr, tstr):
    return str2dt(dstr + ' ' + tstr) if tstr else str2dt(dstr)
        
def dt2str(dt):
    "datetime object to YYYY-MM-DD hh:mm:ss string"
    if dt is None:
        return None
    else:    
        return dt.strftime("%Y-%m-%d %H:%M:%S")

def d2str(dt):
    "datetime object to YYYY-MM-DD string"
    if dt is None:
        return None
    else:    
        return dt.strftime("%Y-%m-%d")

def t2str(dt):
    "datetime object to hh:mm string"
    if dt is None:
        return None
    else:    
        return dt.strftime("%H:%M")

def range_to_days(ranges):
    dates = []
    for rstart, rend in ranges:
        if rend - rstart > timedelta(days = 1):
            start = rstart
            end   = rstart.replace(hour = 0, minute = 0, second = 0) + timedelta(days = 1)
            while start < rend and end < rend:
                if end - start >= timedelta(days = 1):
                    dates.append(start)
                start = end
                end   = end + timedelta(days = 1)
    return dates

def overlaps(dt1, dt2):
    start1, end1 = dt1
    start2, end2 = dt2

    if start1 < end2 and start2 < end1:
        return True
    else:
        return False

def intersect(a, b):
    """
    Find the intersection between two ranges of values.
    """
    if a[1] <= b[0] or b[1] <= a[0]:
        return ()
    elif a[0] <= b[0]:
        if a[1] <= b[1]:
            return (b[0], a[1])
        else:
            return (b[0], b[1])
    else: # b[0] < a[0]
        if a[1] <= b[1]:
            return (a[0], a[1])
        else:
            return (a[0], b[1])

def find_intersections(events):
    """
    Takes a list of lists of datetime tuples of the form (start, end) 
    representing sets of events, finds the intersections of all the
    sets, and returns a list of datetime tuples of the form (start, end)
    describing the intersections.  All datetime tuples are assumed to be 
    in the same timezone.
    """
    retval = events[0]
    for event in events[1:]:
        temp = []
        for r in retval:
            for e in event:
                t = intersect(r, e)
                if t:
                    temp.append(t)
        retval = temp
    return retval

def consolidate_events(events):
    """
    Takes a list of datetime tuples of the form (start, end) and
    reduces it to the smallest list that fully describes the events.
    All datetime tuples are assumed to be in the same timezone.
    """
    if len(events) == 1:
        return events
    else:
        return combine_events(consolidate_overlaps(events))

def consolidate_overlaps(events):
    reduced = []
    for (begin1, end1) in events:
        begin = begin1
        end   = end1
        for (begin2, end2) in events:
            if (begin1, end1) != (begin2, end2) and \
               begin1 < end2 and begin2 < end1:
                begin = min([begin, begin1, begin2])
                end   = max([end, end1, end2])
        if (begin, end) not in reduced:
            # if it doesn't overlap w/ any of the others, we can add it 
            intersections = find_intersections([reduced, [(begin, end)]])
            if len(intersections) == 0:
                reduced.append((begin, end))
            else:
                # merge with the current reduction
                for i, r in enumerate(reduced):
                    if overlaps(r, (begin, end)):
                        reduced[i] = (min([r[0], begin])
                                    , max([r[1], end  ]))     

    return reduced

def combine_events(events):
    if len(events) in (0, 1):
        return events 

    events = sorted(events)
    combined = [events[0]]
    for (begin2, end2) in events[1:]:
        begin1, end1 = combined[-1]
        if begin2 == end1:
            combined[-1] = (begin1, end2)
        else:
            combined.append((begin2, end2))
    return combined

def compliment_events(events, start, end):
    """
    For a given set of datetime tuples of the form (start, end) which
    falls in the range of the given start, end, what is the complimentary
    set of events.  That is, what are the other events, togethor with
    the given events, which completely cover the given start, end range?
    """
 
    # special case of no events
    if len(events) == 0:
        return [(start, end)]

    events = sorted(events)

    startFirstEvent = events[0][0]
    endLastEvent    = events[-1][1]

    # events have to be in rage
    assert startFirstEvent >= start
    assert endLastEvent <= end

    # special case of no compliment
    if startFirstEvent == start and endLastEvent == end \
        and len(events) == 1:
        return []

    # take care of the beginning first
    firstCmp = (start, startFirstEvent) if start != startFirstEvent else None

    # all the compliments in the middle
    cmp = [] if firstCmp is None else [firstCmp]
    for i in range(len(events)-1):
        # end of current event is start of compliment
        s = events[i][1] 
        # beginning of next event is end of compliment
        e = events[i+1][0]
        if s != e:
            cmp.append((s,e))

    # take care of the ending
    lastCmp = (endLastEvent, end) if end != endLastEvent else None
    if lastCmp is not None:
        cmp.append(lastCmp)

    return cmp    

def trim_events(events, start, end):
    """
    Again, here events is a list of datetime tuples [(start, end)].
    Many of the functions that return these events will return 
    events that overlap with the given start, end boundries.  Here
    we trim any of these overlaps so that no events returned go beyond
    the given start, end.
    """
    
    if len(events) == 0:
        return []

    if events[0][0] < start:
        events[0] = (start, events[0][1])
    if events[-1][1] > end:
        events[-1] = (events[-1][0], end)
    return events    
    

jsonMap = {"authorized"     : "status__authorized"
         , "between"        : "time_between"
         , "backup"         : "status__backup"
         , "pcode"          : "project__pcode"
         , "complete"       : "status__complete"
         , "coord_mode"     : "target__system__name"
         , "enabled"        : "status__enabled"
         , "freq"           : "frequency"
         , "grade"          : "allotment__grade"
         , "id"             : "id"
         , "name"           : "name"
         , "orig_ID"        : "original_id"
         , "receiver"       : "receiver_group__receivers__abbreviation"
         , "PSC_time"       : "allotment__psc_time"
         , "req_max"        : "max_duration"
         , "req_min"        : "min_duration"
         , "science"        : "observing_type__type"
         , "sem_time"       : "allotment__max_semester_time"
         , "source"         : "target__source"
         , "source_h"       : "target__horizontal"
         , "source_v"       : "target__vertical"
         , "total_time"     : "allotment__total_time"
         , "type"           : "session_type__type"
               }

EXPLORER_CONFIG_TYPE_COLUMN = 0
EXPLORER_CONFIG_TYPE_FILTER = 1
