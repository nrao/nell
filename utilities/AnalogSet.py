# Copyright (C) 2011 Associated Universities, Inc. Washington DC, USA.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# 
# Correspondence concerning GBT software should be addressed as follows:
#       GBT Operations
#       National Radio Astronomy Observatory
#       P. O. Box 2
#       Green Bank, WV 24944-0002 USA

"""
Contains set functions as they pertain to continuous ranges as opposed to
discrete collections of values, e.g, line segments or more relevantly,
time ranges.  When results consist of a list of ranges, the order is not
sorted.
Simply a means for providing one location for such functionality.
This list of functions does not attempt to be exhaustive, only what
was needed by nell.
(Still cannot believe I could not find another implementation.)

Throughout this code define a range is a tuple (x, y) where x <= y.
"""

def overlaps(a, b):
    "Determines whether two ranges intersect."
    return a[0] < b[1] and b[0] < a[1]

def intersect(a, b):
    "Find the intersection of two ranges."
    if a[1] <= b[0] or b[1] <= a[0]:
        return ()
    elif a[0] <= b[0]:
        if a[1] <= b[1]:
            return (b[0], a[1])
        else:
            return (b[0], b[1])
    else:
        if a[1] <= b[1]:
            return (a[0], a[1])
        else:
            return (a[0], b[1])

def intersects(ranges):
    """
    Takes a list of list of ranges, i.e., [[range]], finds the
    intersections among the list of ranges, and returns a list of
    ranges describing the intersections. For example, ranges x, y,
    and z yield r:
    123456 ...
      xxxx   xxxxx  xxxx  xxxxx   
    yyyyyy     yyyyyyyyyy         
       zzzz     zzzzzz     zzzzzzz
       rrr      rr  rr            
    i.e.,
    intersects([[(3,6), (10,14), (17,20), (23,27)],
                [(1,6), (12,21)],
                [(4,7), (13,18), (24,29)])
        yields:
                [(4,6), (13,14), (17,18)]]
    """
    if not ranges:
        return ranges
    retval = ranges[0]
    for range in ranges[1:]:
        temp = []
        for r in retval:
            for e in range:
                t = intersect(r, e)
                if t:
                    temp.append(t)
        retval = temp
    return retval

def union(a, b):
    """
    Find the union(s) between the two ranges.
    Note that since the answer may not be contiguous, this returns
    a list of ranges.
    """
    if a[1] < b[0] or b[1] < a[0]:
        return [a, b]
    elif a[0] <= b[0]:
        if a[1] <= b[1]:
            return [(a[0], b[1])]
        else:
            return [(a[0], a[1])]
    else:
        if a[1] <= b[1]:
            return [(b[0], b[1])]
        else:
            return [(b[0], a[1])]

def unions(ranges, complete = None):
    """
    Given a list of ranges, combine as many of the ranges as possible
    using union to generate a shorter list of longer ranges. For example,
    the ranges u, v, w, x, y, and z yields r.
    123456 ...
      wwww
                          xxxxx
                    yyyy
             uuuuu
                vvvvvv
       zzzz
      rrrrr  rrrrrrrrrrr  rrrrr   
    i.e.,
    unions([(3,6), (23,27), (17,20), (10,14), (23,28), (4,7)])
        yields:
                [(3,7), (10,20), (23,27)]
    """
    if not complete:
        complete = []
    if not ranges:
        return complete
    tst = ranges[0]
    hold = []
    for i in range(1, len(ranges)):
        r = ranges[i]
        u = union(tst, r)
        assert len(u) in [1, 2]
        if len(u) == 1:
            return unions(hold + u + ranges[i + 1:], complete)
        else:
            hold.append(r)
    complete.append(tst)
    return unions(ranges[1:], complete)

def diff(a, b):
    """
    Find the remainder(s) of the a range after the b range is removed.
    Note that since the answer may not be contiguous, this returns
    a list of ranges.
    Note this can be used for complement, i.e., if range a is assumed
    to be the universal set, then it returns all non-b range(s) in
    range a.
    """
    if a[1] <= b[0] or b[1] <= a[0]:
        return [(a[0], a[1])]
    elif a[0] < b[0]:
        if a[1] <= b[1]:
            return [(a[0], b[0])]
        elif a[1] > b[1]:
            return[(a[0],b[0]), (b[1], a[1])]
        else:
            return [(a[0], a[1])]
    elif a[0] > b[0]:
        if a[1] < b[1]:
            return []
        elif a[1] > b[1]:
            return [(b[1], a[1])]
        else:
            return  []
    else:
        if a[1] <= b[1]:
            return []
        else:
            return [(b[1], a[1])]

def diffs(ranges_a, ranges_b):
    """
    Given two lists of ranges, returns a single list of ranges
    consisting of removing all portions from the first list that
    intersect with any range from the second list.  For example,
    ranges x and y yield r.
    123456 ...
      xxxx   xxxxx  xxxx  xxxxx   
    yyyyyy     yyyyyyyyyy         
             rr           rrrrr   
    i.e.,
    diffs([(3,6), (10,14), (17,20), (23,27)],
          [(1,6), (12,21)])
        yields:
                [(10,11), (23,27)]
    """
    if not ranges_b or not ranges_a:
        return ranges_a
    diminished_a = []
    for a in ranges_a:
        diminished_a.extend(diff(a, ranges_b[0]))
    return diffs(diminished_a, ranges_b[1:])
