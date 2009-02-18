package edu.nrao.dss.client;

import com.google.gwt.widgetideas.graphics.client.Color;
import java.util.Arrays;
import java.util.List;

public class Fixed extends Session {
	public Fixed(int startDay, int startHour, int numHours) {
		this.startDay  = startDay;
		this.startHour = startHour;
		this.numHours  = numHours;
	}

	public void draw(Calendar grid) {
		grid.setFillStyle(getColor());
		grid.fillRect(startDay, startHour, 1, numHours);

		grid.setStrokeStyle(new Color(0, 0, 0, getAlpha()));
		grid.setLineWidth(4);
		grid.strokeRect(startHour, startDay, numHours, 1);
	}

	public List<Interval> getIntervals() {
		return Arrays.asList(new Interval[]{new Interval(this, getStartHour(), numHours)});
	}

	public boolean contains(int day, int hour) {
	    if (startHour + numHours > 24) {
	        return (day == startDay && startHour <= hour && hour < 24) ||
	               (day == startDay+1 && 0 <= hour && hour < startHour + numHours - 24);
	    }
		return day == startDay && startHour <= hour && hour < startHour + numHours;
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
	private int startHour;
	private int numHours;
}
