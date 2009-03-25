package edu.nrao.dss.client;

import com.google.gwt.junit.client.GWTTestCase;

/**
 * GWT JUnit tests must extend GWTTestCase.
 */
public class SchedulerTest extends GWTTestCase {

  /**
   * Must refer to a valid module that sources this class.
   */
  public String getModuleName() {
    return "edu.nrao.dss.Scheduler";
  }

  public void testCreate() {
	  Scheduler s = new Scheduler();
	  assertNotNull(s);
  }
  
}
