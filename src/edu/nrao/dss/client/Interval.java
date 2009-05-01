package edu.nrao.dss.client;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;

import com.google.gwt.core.client.GWT;
import com.google.gwt.i18n.client.DateTimeFormat;
import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;

/** Represents an opportunity or an overlapping sequence of opportunities. */
@SuppressWarnings("unchecked")
class Interval implements Comparable {
    private static final DateTimeFormat DATE_FORMAT = DateTimeFormat.getFormat("yyyy-MM-dd HH:mm:ss");
    private static final long           DAY_LENGTH  = 24*60*60;

    public static List<Interval> parseIntervals(Window window, JSONArray intervals) {
        ArrayList<Interval> result = new ArrayList<Interval>();
        for (int i = 0; i < intervals.size(); ++i) {
            Interval interval = parseInterval(window, intervals.get(i).isObject());
            if (interval.getStartDay() > 120) {
                break;
            }
            result.add(interval);
        }

        Collections.sort(result);
        return reduce(result);
    }

    private static Interval parseInterval(Window window, JSONObject interval) {
        try {
            Date start_time = DATE_FORMAT.parse(interval.get("start_time").isString().stringValue());
            int  duration   = (int) interval.get("duration").isNumber().doubleValue();

            long today = truncate(new Date().getTime(), DAY_LENGTH*1000);
            long start = (start_time.getTime() - today) / (3600*1000);

            return new Interval(window, (int) start, duration);
        } catch (Exception e) {
            GWT.log("Interval.parseInterval", e);
            return null;
        }
    }

    /** Assumes intervals are sorted and all belong to the same session. */
    private static List<Interval> reduce(List<Interval> intervals) {
        ArrayList<Interval> result = new ArrayList<Interval>();
        if (intervals.size() == 0) {
            return result;
        }

        int start    = intervals.get(0).startHour;
        int duration = intervals.get(0).numHours;
        for (int i = 1; i < intervals.size(); ++i) {
            Interval interval = intervals.get(i);
            if (intervals.get(i).startHour >= start + duration) {
                result.add(new Interval(interval.window, start, duration));
                start    = interval.startHour;
                duration = interval.numHours;
            } else {
                duration = interval.startHour + interval.numHours - start;
            }
        }
        result.add(new Interval(intervals.get(0).window, start, duration));

        return result;
    }

    private static long truncate(long n, long mod) {
        return mod * (n / mod);
    }

    /**
     * Returns true if any of the intervals in the first list overlap any of the
     * intervals in the second list.
     * 
     * @param lhs (left-hand side) a list of intervals
     * @param rhs (right-hand side) a list of intervals
     * @return True if there are any conflicts between the two lists.
     */
    public static boolean overlapIntervals(List<Interval> lhs, List<Interval> rhs) {
        for (int i = 0, j = 0; i < lhs.size() && j < rhs.size(); ) {
            if (lhs.get(i).getEndHour() <= rhs.get(j).getStartHour()) { ++i; continue; }
            if (rhs.get(j).getEndHour() <= lhs.get(i).getStartHour()) { ++j; continue; }
            return true;
        }
        return false;
    }

    public Interval(Window window, int startHour, int numHours) {
        this.window    = window;
        this.startHour = startHour;
        this.numHours  = numHours;
    }

    public boolean conflicts(Interval rhs) {
        return overlap(rhs);
    }

    /**
     * Two intervals overlap only if each begins before the other ends.
     * 
     * @param rhs (right-hand side) interval to compare to
     * @return True only if the two intervals overlap.
     */
    public boolean overlap(Interval rhs) {
        return this.getStartHour() < rhs.getEndHour() && rhs.getStartHour() < this.getEndHour();
    }

    public int compareTo(Object other) {
        Interval rhs = (Interval) other;
        if (startHour <  rhs.startHour)                             { return -1; }
        if (startHour == rhs.startHour && numHours <  rhs.numHours) { return -1; }
        if (startHour == rhs.startHour && numHours == rhs.numHours) { return  0; }
        return +1;
    }

    public Window getWindow() {
        return window;
    }

    // TODO: need to account for LST drift.
    public void setStartHour(int hour) {
        startHour = hour;
    }

    public void setStartDay(int day) {
        int deltaDay   = day - getStartDay();
        int deltaHours = deltaDay * 24;
        setStartHour(getStartHour() + deltaHours);
    }

    public int getStartHour() {
        return startHour;
    }

    public int getStartDay() {
        return startHour / 24;
    }

    public int getNumHours() {
        return numHours;
    }

    public int getEndHour() {
        return startHour + numHours;
    }

    private Window  window;
    private int     startHour;
    private int     numHours;
}
