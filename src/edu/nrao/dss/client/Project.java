package edu.nrao.dss.client;

import java.util.ArrayList;
import java.util.List;

public class Project {
	public static void allocateColors(List<Project> projects) {
		int c = 0;
		for (Project p : projects) {
			if (p.isMaintenance()) {
				p.setRGB(0, 0, 0);
				continue;
			}
			p.setRGB(COLORS[c++ % COLORS.length]);
		}
	}

	public static List<Session> collectAllocations(List<Project> projects) {
		ArrayList<Session> allocations = new ArrayList<Session>();
		for (Project p : projects) {
			allocations.addAll(p.allocations);
		}
		return allocations;
	}

	private static final int[][] COLORS = {
        {0xFF, 0x00, 0x00}, {0x00, 0xFF, 0x00}, {0x00, 0x00, 0xFF}, {0x00, 0xFF, 0xFF},
        {0xFF, 0x00, 0xFF}, {0xFF, 0xFF, 0x00}, {0xFF, 0x77, 0x00}, {0x77, 0xFF, 0x00},
        {0x00, 0xFF, 0x77}, {0x00, 0x77, 0xFF}, {0x77, 0x00, 0xFF}, {0xFF, 0x00, 0x77},
        {0x00, 0x00, 0xFF}, {0x00, 0x66, 0xFF}, {0x00, 0xCC, 0x00}, {0x66, 0x66, 0x00},
        {0x99, 0x00, 0x00}, {0x99, 0x00, 0xFF}, {0xCC, 0x33, 0xFF}, {0xCC, 0x66, 0x00},
        {0xCC, 0xCC, 0xFF}, {0xCC, 0x99, 0x99}, {0xFF, 0xCC, 0x33}, {0xFF, 0xFF, 0x00},
        {0xFF, 0x99, 0x33}
	};

	public Project(String name, List<Session> allocations) {
		this.name        = name;
		this.allocations = allocations;
		
		for (Session a : this.allocations) {
			a.setInfoText(this.name);
		}
	}

	public boolean isMaintenance() {
		return name == "Maintenance";
	}

	public void setRGB(int[] rgb) {
		setRGB(rgb[0], rgb[1], rgb[2]);
	}

	public void setRGB(int red, int green, int blue) {
		for (Session a : allocations) {
			a.setRGB(red, green, blue);
		}
	}

	private String           name;
	private List<Session> allocations;
}
