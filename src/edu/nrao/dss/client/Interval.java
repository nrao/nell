package edu.nrao.dss.client;

import java.util.List;

public class Interval {
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
	
	public Interval(ISession allocation, int startHour, int numHours) {
		this.allocation = allocation;
		this.startHour  = startHour;
		this.numHours   = numHours;
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
	
	public ISession getAllocation() {
		return allocation;
	}
	
	public int getEndHour() {
		return startHour + numHours;
	}
	
	public int getStartHour() {
		return startHour;
	}
	
	public int getNumHours() {
		return numHours;
	}
	
	private ISession allocation;
	private int         startHour;
	private int         numHours;
}
