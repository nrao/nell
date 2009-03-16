package edu.nrao.dss.client;

import java.util.HashMap;

import com.google.gwt.junit.client.GWTTestCase;

/**
 * GWT JUnit tests must extend GWTTestCase.
 */
public class SessionMapTest extends GWTTestCase {

  /**
   * Must refer to a valid module that sources this class.
   */
  public String getModuleName() {
    return "edu.nrao.dss.Scheduler";
  }

  public void testCreate(){
	  SessionMap sm = new SessionMap();
	  assertNotNull(sm);
  }
  
  public void test_typeMap(){
	  HashMap<String, Class> tm = SessionMap.typeMap;
	  assertNotNull(tm);
	  assertEquals(Float.class,  tm.get("freq"));
	  assertEquals(String.class, tm.get("ra"));
	  assertEquals(String.class, tm.get("dec"));
  }
  
  public void test_createTypeMap(){
	  HashMap<String, Class> tm = SessionMap.createTypeMap();
	  assertNotNull(tm);
	  assertEquals(tm.get("authorized"), Boolean.class);
  }

}
