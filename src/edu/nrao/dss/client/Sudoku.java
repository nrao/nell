package edu.nrao.dss.client;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class Sudoku {
	public Set<Session> conflictsWith(Session target, Collection<Session> allocations) {
		List<Interval>      targetIntervals = target.getIntervals();
		HashSet<Session> result          = new HashSet<Session>();
		for (Session a : allocations) {
			if (a == target) { continue; }
			
			if (Interval.overlapIntervals(targetIntervals, a.getIntervals())) {
				result.add(a);
			}
		}
		
		return result;
	}
	
	public Set<Session> findConflicts(Collection<Session> allocations) {
		ArrayList<Interval> intervals = new ArrayList<Interval>();
		for (Session a : allocations) {
			intervals.addAll(a.getIntervals());
		}

		HashSet<Session> result = new HashSet<Session>();
		for (Interval i : findConflicts(intervals)) {
			result.add((Session) i.getAllocation());
		}

		return result;
	}
	
	public Set<Interval> findConflicts(List<Interval> intervals) {
		Collections.sort(intervals, new Comparator<Interval>() {
			public int compare(Interval lhs, Interval rhs) {
				if (lhs.getStartHour() < rhs.getStartHour()) { return -1; }
				if (rhs.getStartHour() < lhs.getStartHour()) { return +1; }
				return 0;
			}
		});
		
		HashSet<Interval> result = new HashSet<Interval>();
		for (int i = 0; i < intervals.size()-1; ++i) {
			if (intervals.get(i+1).getStartHour() < intervals.get(i).getEndHour()) {
				result.add(intervals.get(i));
				result.add(intervals.get(i+1));
			}
		}
		
		return result;
	}
}
