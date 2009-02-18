package edu.nrao.dss.client;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import com.google.gwt.user.client.Random;

public class TestData {
	public List<Project> getProjects() {
		ArrayList<Project> projects = new ArrayList<Project>();
		
		projects.add(getMaintenance());
		
		projects.add(simpleFixed("F1", 2, 0, 12));
		projects.add(simpleFixed("F2", 4, 16, 8));
		projects.add(simpleFixed("F3", 4, 12, 8));
		projects.add(simpleFixed("F4", 5, 10, 6));
		projects.add(simpleFixed("F5", 6, 14, 6));
		
		for (int i = 6; i < 40; ++i) {
			projects.add(simpleFixed("F"+i, 7 + Random.nextInt(100), Random.nextInt(24), 2 + Random.nextInt(12)));
		}
		
		projects.add(simpleWindowed("W1", 6, 4, 0, 10));
		projects.add(simpleWindowed("W2", 4, 3, 4, 8));
		
		for (int j = 3; j < 60; ++j) {
			projects.add(simpleWindowed("W"+j, 7 + Random.nextInt(100), 2 + Random.nextInt(6), Random.nextInt(24), 2 + Random.nextInt(12)));
		}

		return projects;
	}

	private Project getMaintenance() {
		ArrayList<Session> fixed = new ArrayList<Session>();

		int[] wednesdays = {3, 10, 17, 24, 31, 38, 45, 52, 59, 66, 73, 80, 87, 94, 101, 108, 115};
		for (int day : wednesdays) {
			fixed.add(new Fixed(day, 8, 10));
		}

		return new Project("Maintenance", fixed);
	}
	
	private Project simpleFixed(String name, int startDay, int startHour, int numHours) {
		return new Project(name, Arrays.asList(new Session[]{new Fixed(startDay, startHour, numHours)}));
	}
	
	private Project simpleWindowed(String name, int startDay, int numDays, int startHour, int numHours) {
		return new Project(name, Arrays.asList(new Session[]{new Windowed(startDay, numDays, startHour, numHours)}));
	}
}
