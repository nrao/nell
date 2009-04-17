package edu.nrao.dss.client;

import com.google.gwt.junit.client.GWTTestCase;

import edu.nrao.dss.client.model.MinimumObservingEfficiencyTest;
import edu.nrao.dss.client.model.ReceiverTest;
import junit.framework.Test;
import junit.framework.TestSuite;

public class SchedulerTestSuite extends GWTTestCase {
	
	public String getModuleName() {
            return "test.Test";
    } 
	
	public static Test suite() {
		TestSuite suite = new TestSuite("Test for a Scheduler Application");
		suite.addTestSuite(SchedulerTest.class); 
		suite.addTestSuite(SessionColConfigTest.class);
		suite.addTestSuite(ColumnDefinitionTest.class);
		suite.addTestSuite(ReceiverTest.class);
		suite.addTestSuite(MinimumObservingEfficiencyTest.class);
		return suite;
  }
}