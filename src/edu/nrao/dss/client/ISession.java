package edu.nrao.dss.client;

import java.util.List;

public interface ISession {
	public void draw(Calendar grid);
	
	public List<Interval> getIntervals();
	
	public boolean contains(int day, int hour);

	public int getStartHour();
	public int getStartDay();
	
	public void setStartDay(int day);
}
