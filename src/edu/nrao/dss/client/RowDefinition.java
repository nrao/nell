package edu.nrao.dss.client;

import java.util.Arrays;
import java.util.List;

import com.extjs.gxt.ui.client.widget.grid.ColumnConfig;
import com.extjs.gxt.ui.client.widget.grid.ColumnModel;

class RowDefinition {
    public ColumnModel getColumnModel(ColumnConfig column) {
        return columns.getColumnModel(column);
    }

    public List<String> getAllFieldNames() {
        return columns.getAllFieldNames();
    }

    public List<String> getAllFieldIds() {
        return columns.getAllFieldIds();
    }

    public List<RowType> getAllRows() {
        return Arrays.asList(rows);
    }

    public ColumnDefinition getColumnDefinition() {
        return columns;
    }

    private final ColumnDefinition columns = new ColumnDefinition();

    private class BaseRowType extends RowType {
        public BaseRowType(String name) {
            super(columns);

            addColumn(ColumnDefinition.NAME,           name);
            addColumn(ColumnDefinition.TYPE,           new STypeField("open"));
            addColumn(ColumnDefinition.SCIENCE,        new ScienceField("spectral line"));
            addColumn(ColumnDefinition.PSC_TIME,       null);
            addColumn(ColumnDefinition.TOTAL_TIME,     null);
            addColumn(ColumnDefinition.GRADE,          new GradeField("A"));
            addColumn(ColumnDefinition.AUTHORIZED,     true);
            addColumn(ColumnDefinition.ENABLED,        false);
            addColumn(ColumnDefinition.COMPLETE,       false);
            addColumn(ColumnDefinition.COORD_MODE,     new CoordModeField("J2000"));
            addColumn(ColumnDefinition.CNTR_SKY_AREA,  null);
            addColumn(ColumnDefinition.FREQ,           null);
            addColumn(ColumnDefinition.FREQ_RANGE,     null);
            addColumn(ColumnDefinition.RECEIVERS,      null);
            addColumn(ColumnDefinition.REQ_MIN,        2.0);
            addColumn(ColumnDefinition.REQ_MAX,        6.0);
            addColumn(ColumnDefinition.ABS_MIN,        1.5);
            addColumn(ColumnDefinition.ABS_MAX,        10.0);
            addColumn(ColumnDefinition.BETWEEN,        0.0);
            addColumn(ColumnDefinition.OBS_EFF_LIMIT,  null);
            addColumn(ColumnDefinition.ATMOS_ST_LIMIT, null);
            addColumn(ColumnDefinition.TR_ERR_LIMIT,   null);
            addColumn(ColumnDefinition.MIN_EFF_TSYS,   null);
            addColumn(ColumnDefinition.HA_LIMIT,       null);
            addColumn(ColumnDefinition.ZA_LIMIT,       85.0);
            addColumn(ColumnDefinition.SOLAR_AVOID,    false);
            addColumn(ColumnDefinition.USE_DEPEND,     false);
            addColumn(ColumnDefinition.TRANSIT,        false);
        }
    }

    private final RowType empty        = new RowType(columns) {
        {
            addColumn(ColumnDefinition.NAME,           "Empty");
        }
    };

    private final RowType lowFreqNoRFI = new BaseRowType("Low Frequency With No RFI") {
        {
            addColumn(ColumnDefinition.ORIG_ID,        0);
            addColumn(ColumnDefinition.ID,             0);
        }
    };

    private final RowType[] rows = new RowType[] {
            empty,
            lowFreqNoRFI,
            new BaseRowType("Low Frequency With RFI"),
            new BaseRowType("High frequency spectral line"),
            new BaseRowType("High frequency continuum"),
            new BaseRowType("Low frequency monitoring with RFI"),
            new BaseRowType("Low and high frequency"),
            new BaseRowType("Large proposal"),
            new BaseRowType("Polarization project"),
            new BaseRowType("PTCS night time"),
            new BaseRowType("PTCS in high winds"),
            new BaseRowType("Fixed maintenance"),
            new BaseRowType("Windowed maintenance"),
            new BaseRowType("Dynamic VLBI"),
            new BaseRowType("Fixed radar"),
            new BaseRowType("Tsys calibration measurement")
    };
}
