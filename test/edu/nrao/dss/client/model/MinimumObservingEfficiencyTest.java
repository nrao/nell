package edu.nrao.dss.client.model;

import com.google.gwt.junit.client.GWTTestCase;

public class MinimumObservingEfficiencyTest extends GWTTestCase {

	public String getModuleName() {
		return "edu.nrao.dss.Scheduler";
    }
	
	public void test_averageEfficiency() {
		MinimumObservingEfficiency moe = new MinimumObservingEfficiency();
		double[] expected = {
			0.9487231, 0.8573790, 0.6725301, 0.5058167,
			0.6737226, 0.6538979, 0.5655617
		};
		double[] frequencies = {
			2.3, 9.7, 15.8, 25.4, 38.6, 44.3, 55.7
		};
		for (int i = 0; i < 7; ++i) {
			assertEquals(expected[i], moe.efficiency(frequencies[i]), 1e-6);
		}
	}
	
}
