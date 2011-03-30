from datetime  import datetime, timedelta, date
from utilities import AnalogSet

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
            intersections = AnalogSet.intersects([reduced, [(begin, end)]])
            if len(intersections) == 0:
                reduced.append((begin, end))
            else:
                # merge with the current reduction
                for i, r in enumerate(reduced):
                    if AnalogSet.overlaps(r, (begin, end)):
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
    
