package edu.nrao.dss.client;
import com.google.gwt.junit.client.GWTTestCase;
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
		return suite;
  }
}