package edu.nrao.dss.client;

import com.extjs.gxt.ui.client.widget.grid.ColumnModel;
import com.google.gwt.junit.client.GWTTestCase;

/**
 * GWT JUnit tests must extend GWTTestCase.
 */
public class ColumnDefinitionTest extends GWTTestCase {

  /**
   * Must refer to a valid module that sources this class.
   */
  public String getModuleName() {
    return "edu.nrao.dss.Scheduler";
  }

  /**
   * Add as many tests as you like.
   */
  public void testPublic() {
    assertTrue(true);
    ColumnDefinition colDef = new ColumnDefinition();
    assertNotNull(colDef);
    SessionColConfig sColConf = new SessionColConfig("test", "Test", 100, Integer.class);
    ColumnModel colMod = colDef.getColumnModel(sColConf);
    assertEquals(44, colMod.getColumnCount());
    assertEquals("Proj Code", colMod.getColumnHeader(1));
    assertTrue(colDef.getAllFieldNames().contains("Proj Code"));
    assertTrue(colDef.hasColumn(ColumnDefinition.TR_ERR_LIMIT));
    assertFalse(colDef.hasColumn("Pinky_Hippo"));
    assertEquals("Precip", colDef.getColumn(ColumnDefinition.PRECIP).getHeader());
    //assertEquals(colDef.getValue( ??
    assertEquals(ScienceField.class, colDef.getClasz("science"));
    assertEquals(null, colDef.getField(ColumnDefinition.COORD_MODE).getOriginalValue());
    assertEquals(ColumnDefinition.COORD_MODE, colDef.getField(ColumnDefinition.COORD_MODE).getFieldLabel());
  }
}
