package edu.nrao.dss.client;

import java.util.ArrayList;
import java.util.List;

public class Windowed extends Session {
	public Windowed(int startDay, int numDays, int startHour, int numHours) {
		this.startDay  = startDay;
		this.numDays   = numDays;
		this.startHour = startHour;
		this.numHours  = numHours;
	}

	public void draw(Calendar grid) {
		grid.setFillStyle(getColor());
		grid.fillRect(startDay, startHour, numDays, numHours);
	}

	public List<Interval> getIntervals() {
		ArrayList<Interval> result = new ArrayList<Interval>();
		for (int i = 0; i < numDays; ++i) {
			result.add(new Interval(this, 24*(startDay+i) + startHour, numHours));
		}
		return result;
	}

	public boolean contains(int day, int hour) {
	    if (startHour + numHours > 24) {
	        return (startDay <= day && day < startDay + numDays && startHour <= hour && hour < 24) ||
	               (startDay+1 <= day && day < startDay + numDays + 1 && 0 <= hour && hour < startHour + numHours - 24);
	    }
		return startDay <= day && day < startDay + numDays && startHour <= hour && hour < startHour + numHours;
	}

	public int getStartHour() {
		return 24*startDay + startHour;
	}
	
	public int getStartDay() {
		return startDay;
	}
	
	public void setStartDay(int day) {
		startDay = day;
	}

	private int startDay;
	private int numDays;
	private int startHour;
	private int numHours;
}
