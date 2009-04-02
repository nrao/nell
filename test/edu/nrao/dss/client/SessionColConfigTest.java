package edu.nrao.dss.client;

import com.extjs.gxt.ui.client.widget.form.CheckBox;
import com.extjs.gxt.ui.client.widget.form.Field;
import com.extjs.gxt.ui.client.widget.form.NumberField;
import com.extjs.gxt.ui.client.widget.form.SimpleComboBox;
import com.extjs.gxt.ui.client.widget.form.TextField;
import com.google.gwt.junit.client.GWTTestCase;

/**
 * GWT JUnit tests must extend GWTTestCase.
 */
public class SessionColConfigTest extends GWTTestCase {

  /**
   * Must refer to a valid module that sources this class.
   */
  public String getModuleName() {
    return "edu.nrao.dss.Scheduler";
  }

  /**
   * Add as many tests as you like.
   */

  public void test_IntegerField() {
	  SessionColConfig sColConf = new SessionColConfig("test", "Test", 100, Integer.class);
	  assertNotNull(sColConf);
	  NumberField result   = (NumberField) sColConf.getEditor().getField();
	  assertEquals(result.getPropertyEditorType(), Integer.class);
  }
 
  public void test_DoubleField() {
	  SessionColConfig sColConf = new SessionColConfig("test", "Test", 100, Double.class);
	  assertNotNull(sColConf);
	  NumberField result   = (NumberField) sColConf.getEditor().getField();
	  assertEquals(result.getPropertyEditorType(), Double.class);
  }
  
  @SuppressWarnings("unchecked")
  public void test_BooleanField() {
	  SessionColConfig sColConf = new SessionColConfig("test", "Test", 100, Boolean.class);
	  assertNotNull(sColConf);
	  Field result   = sColConf.getEditor().getField();
	  assertEquals(result.getClass(), CheckBox.class);
  }

  @SuppressWarnings("unchecked")
  public void test_TextField() {
	  SessionColConfig sColConf = new SessionColConfig("test", "Test", 100, String.class);
	  assertNotNull(sColConf);
	  Field result   = sColConf.getEditor().getField();
	  assertEquals(result.getClass(), TextField.class);
  }

  @SuppressWarnings("unchecked")
  public void test_STypeField() {
	  SessionColConfig sColConf = new SessionColConfig("test", "Test", 100, STypeField.class);
	  assertNotNull(sColConf);
	  Field result   = sColConf.getEditor().getField();
	  assertEquals(result.getClass(), SimpleComboBox.class);
  }
  
  @SuppressWarnings("unchecked")
  public void test_OrderDependencyField() {
	  SessionColConfig sColConf = new SessionColConfig("test", "Test", 100, OrderDependencyField.class);
	  assertNotNull(sColConf);
	  Field result   = sColConf.getEditor().getField();
	  assertEquals(result.getClass(), SimpleComboBox.class);
  }  
  @SuppressWarnings("unchecked")
  public void test_PriorityField() {
	  SessionColConfig sColConf = new SessionColConfig("test", "Test", 100, PriorityField.class);
	  assertNotNull(sColConf);
	  Field result   = sColConf.getEditor().getField();
	  assertEquals(result.getClass(), SimpleComboBox.class);
  }
  
  @SuppressWarnings("unchecked")
  public void test_ScienceField() {
	  SessionColConfig sColConf = new SessionColConfig("test", "Test", 100, ScienceField.class);
	  assertNotNull(sColConf);
	  Field result   = sColConf.getEditor().getField();
	  assertEquals(result.getClass(), SimpleComboBox.class);
  }
  
  @SuppressWarnings("unchecked")
  public void test_TimeOfDayField() {
	  SessionColConfig sColConf = new SessionColConfig("test", "Test", 100, TimeOfDayField.class);
	  assertNotNull(sColConf);
	  Field result   = sColConf.getEditor().getField();
	  assertEquals(result.getClass(), SimpleComboBox.class);
  }


}
