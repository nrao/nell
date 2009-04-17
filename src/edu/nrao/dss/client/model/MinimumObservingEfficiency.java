package edu.nrao.dss.client.model;

import java.lang.Math;

public class MinimumObservingEfficiency {

    public double efficiency(double frequency) {
    	double af = averageEfficiency(frequency);
    	return af - 0.02 - 0.1*(1.0 - af);
    }
    
    private double averageEfficiency(double frequency) {
    	frequency = Math.min(50.0, frequency);
    	double v = frequency/nu0;
    	return (double)(0.74 + 0.155*Math.cos(v) + 0.12*Math.cos(2.0 * v)
                       - 0.03*Math.cos(3.0*v) - 0.01*Math.cos(4.0*v));
    }
    
    private double nu0 = 12.8;
}
