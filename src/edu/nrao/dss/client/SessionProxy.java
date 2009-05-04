package edu.nrao.dss.client;

import java.util.ArrayList;
import java.util.List;

class SessionProxy {
    public SessionProxy(Session session) {
        this.session   = session;
        this.intervals = session.getIntervals();
    }

    public SessionProxy(SessionProxy session) {
        this.session   = session.getSession();
        this.intervals = session.getIntervals();
    }

    public boolean conflicts(SessionProxy rhs) {
        return Interval.overlapIntervals(intervals, rhs.getIntervals());
    }

    public Session getSession() {
        return session;
    }

    public List<Interval> getIntervals() {
        return intervals;
    }

    public int getNumIntervals() {
        return intervals.size();
    }

    public Interval getInterval(int i) {
        return intervals.get(i);
    }

    public void nukeInterval(Interval target) {
        ArrayList<Interval> result = new ArrayList<Interval>(); 
        for (Interval interval : intervals) {
            if (! target.conflicts(interval)) {
                result.add(interval);
            }
        }
        intervals = result;
    }

    private Session        session;
    private List<Interval> intervals;
}
