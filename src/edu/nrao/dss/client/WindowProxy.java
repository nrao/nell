package edu.nrao.dss.client;

import java.util.ArrayList;
import java.util.List;

class WindowProxy {
    public WindowProxy(Window window) {
        this.window    = window;
        this.intervals = window.getIntervals();
    }

    public WindowProxy(WindowProxy session) {
        this.window    = session.getWindow();
        this.intervals = session.getIntervals();
    }

    public boolean conflicts(WindowProxy rhs) {
        return Interval.overlapIntervals(intervals, rhs.getIntervals());
    }

    public Window getWindow() {
        return window;
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

    private Window         window;
    private List<Interval> intervals;
}
