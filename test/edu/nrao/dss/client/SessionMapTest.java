package edu.nrao.dss.client;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;

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

  /*
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
  
  public void test_getAllFields(){
	  Set<String> fields = SessionMap.getAllFields();
	  assertNotNull(fields);
	  for (HashMap<String, Object> m : SessionMap.master.values()){
		  for (String k : m.keySet()){
			  assertTrue(fields.contains(k));
		  }
	  }
  }
  
  public void test_createTypeMap(){
	  HashMap<String, Class> tm = SessionMap.createTypeMap();
	  assertNotNull(tm);
	  assertEquals(tm.get("authorized"), Boolean.class);
  }

  public void test_getAllFieldsWithClass(){
	  HashMap<String, Class> fields = SessionMap.getAllFieldsWithClass();
	  assertNotNull(fields);
	  for (HashMap<String, Object> m : SessionMap.master.values()){
		  for (String k : m.keySet()){
			  if (m.get(k) != null){
				  assertEquals(fields.get(k), m.get(k).getClass());
			  }
		  }
	  }
  }
  
  public void test_getNames(){
	  String sType = "Empty";
	  Set<String> expected = SessionMap.master.get(sType).keySet();
	  Set<String> result   = SessionMap.getNames(sType);
	  assertEquals(expected, result);
  }
  
  public void test_getFieldClass(){
	  String fName = "name";
	  Class result = SessionMap.getFieldClass(fName);
	  assertEquals(String.class, result);
  }
  
  public void test_getRequiredFields(){
	  String sType = "Empty";
	  Set<String> result = SessionMap.getRequiredFields(sType);
	  Set<String> expected = new HashSet<String>();
	  assertEquals(expected, result);
  }
  	  */
}
