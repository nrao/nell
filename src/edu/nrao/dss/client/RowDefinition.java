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
        }
    }

    private final RowType empty        = new BaseRowType("Empty") {
        {
        }
    };

    private final RowType lowFreqNoRFI = new BaseRowType("Low Frequency With No RFI") {
        {
            addColumn(ColumnDefinition.CODE,           null);
            addColumn(ColumnDefinition.ORIG_ID,        0);
            addColumn(ColumnDefinition.ID,             0);
            addColumn(ColumnDefinition.TYPE,           new STypeField("open"));
            addColumn(ColumnDefinition.SCIENCE,        null); //new ScienceField("spectral line"));
            addColumn(ColumnDefinition.PSC_TIME,       null);
            addColumn(ColumnDefinition.TOTAL_TIME,     null);
            //addColumn(ColumnDefinition.TRI_TIME,       100);
            addColumn(ColumnDefinition.GRADE,          null);
            addColumn(ColumnDefinition.AUTHORIZED,     true);
            addColumn(ColumnDefinition.ENABLED,        false);
            addColumn(ColumnDefinition.COMPLETE,       false);
            addColumn(ColumnDefinition.COORD_MODE,     new CoordModeField("J2000"));
            addColumn(ColumnDefinition.CNTR_SKY_AREA,  null);
            addColumn(ColumnDefinition.FREQ,           null);
            //addColumn(ColumnDefinition.FREQ_RNGE_L,    null);
            //addColumn(ColumnDefinition.FREQ_RNGE_H,    null);
            //addColumn(ColumnDefinition.RECEIVER,       null);
            addColumn(ColumnDefinition.REQ_MIN,        2.0);
            addColumn(ColumnDefinition.REQ_MAX,        6.0);
            addColumn(ColumnDefinition.ABS_MIN,        1.5);
            addColumn(ColumnDefinition.ABS_MAX,        10.0);
            addColumn(ColumnDefinition.BETWEEN,        0.0);
            //addColumn(ColumnDefinition.OBS_EFF_LIMIT,  0.0);
            //addColumn(ColumnDefinition.ATMOS_ST_LIMIT, 0.0);
            //addColumn(ColumnDefinition.TR_ERR_LIMIT,   0.0);
            //addColumn(ColumnDefinition.MIN_EFF_TSYS,   0.0);
            //addColumn(ColumnDefinition.HA_LIMIT,       0.0);
            addColumn(ColumnDefinition.ZA_LIMIT,       85.0);
            addColumn(ColumnDefinition.SOLAR_AVOID,    false);
            //addColumn(ColumnDefinition.PRECIP,         0.0);
            //addColumn(ColumnDefinition.WIND,           0.0);
            //addColumn(ColumnDefinition.TIME,           new TimeOfDayField("RFI");
            addColumn(ColumnDefinition.TRANSIT,        false);
            //addColumn(ColumnDefinition.CADENCE,        new CadenceField("regular");
        }
    };

    private final RowType lowFreqRFI = new BaseRowType("Low Frequency With RFI") {
        {
            addColumn(ColumnDefinition.CODE,           null);
            addColumn(ColumnDefinition.ORIG_ID,        0);
            addColumn(ColumnDefinition.ID,             0);
            addColumn(ColumnDefinition.TYPE,           new STypeField("open"));
            addColumn(ColumnDefinition.SCIENCE,        null); //new ScienceField("spectral line"));
            addColumn(ColumnDefinition.PSC_TIME,       null);
            addColumn(ColumnDefinition.TOTAL_TIME,     null);
            //addColumn(ColumnDefinition.TRI_TIME,       100);
            addColumn(ColumnDefinition.GRADE,          null);
            addColumn(ColumnDefinition.AUTHORIZED,     true);
            addColumn(ColumnDefinition.ENABLED,        false);
            addColumn(ColumnDefinition.COMPLETE,       false);
            addColumn(ColumnDefinition.COORD_MODE,     new CoordModeField("J2000"));
            addColumn(ColumnDefinition.CNTR_SKY_AREA,  null);
            addColumn(ColumnDefinition.FREQ,           null);
            addColumn(ColumnDefinition.FREQ_RNGE_L,    1.0);
            addColumn(ColumnDefinition.FREQ_RNGE_H,    1.7);
            //addColumn(ColumnDefinition.RECEIVER,       null);
            addColumn(ColumnDefinition.REQ_MIN,        2.0);
            addColumn(ColumnDefinition.REQ_MAX,        6.0);
            addColumn(ColumnDefinition.ABS_MIN,        1.5);
            addColumn(ColumnDefinition.ABS_MAX,        10.0);
            addColumn(ColumnDefinition.BETWEEN,        0.0);
            //addColumn(ColumnDefinition.OBS_EFF_LIMIT,  0.0);
            //addColumn(ColumnDefinition.ATMOS_ST_LIMIT, 0.0);
            //addColumn(ColumnDefinition.TR_ERR_LIMIT,   0.0);
            //addColumn(ColumnDefinition.MIN_EFF_TSYS,   0.0);
            //addColumn(ColumnDefinition.HA_LIMIT,       0.0);
            addColumn(ColumnDefinition.ZA_LIMIT,       85.0);
            addColumn(ColumnDefinition.SOLAR_AVOID,    false);
            //addColumn(ColumnDefinition.PRECIP,         0.0);
            //addColumn(ColumnDefinition.WIND,           0.0);
            addColumn(ColumnDefinition.TIME_DAY,       new TimeOfDayField("RFI"));
            addColumn(ColumnDefinition.TRANSIT,        false);
            //addColumn(ColumnDefinition.CADENCE,        new CadenceField("regular"));
        }
    };

    private final RowType hiFreqSpecLine = new BaseRowType("High Frequency Spectral Line") {
        {
            addColumn(ColumnDefinition.CODE,           null);
            addColumn(ColumnDefinition.ORIG_ID,        0);
            addColumn(ColumnDefinition.ID,             0);
            addColumn(ColumnDefinition.TYPE,           new STypeField("open"));
            addColumn(ColumnDefinition.SCIENCE,        null); //new ScienceField("spectral line"));
            addColumn(ColumnDefinition.PSC_TIME,       null);
            addColumn(ColumnDefinition.TOTAL_TIME,     null);
            //addColumn(ColumnDefinition.TRI_TIME,       100);
            addColumn(ColumnDefinition.GRADE,          null);
            addColumn(ColumnDefinition.AUTHORIZED,     true);
            addColumn(ColumnDefinition.ENABLED,        false);
            addColumn(ColumnDefinition.COMPLETE,       false);
            addColumn(ColumnDefinition.COORD_MODE,     new CoordModeField("J2000"));
            addColumn(ColumnDefinition.CNTR_SKY_AREA,  null);
            addColumn(ColumnDefinition.FREQ,           null);
            //addColumn(ColumnDefinition.FREQ_RNGE_L,    null);
            //addColumn(ColumnDefinition.FREQ_RNGE_H,    null);
            //addColumn(ColumnDefinition.RECEIVER,       null);
            addColumn(ColumnDefinition.REQ_MIN,        2.0);
            addColumn(ColumnDefinition.REQ_MAX,        6.0);
            addColumn(ColumnDefinition.ABS_MIN,        1.5);
            addColumn(ColumnDefinition.ABS_MAX,        10.0);
            addColumn(ColumnDefinition.BETWEEN,        0.0);
            //addColumn(ColumnDefinition.OBS_EFF_LIMIT,  0.0);
            //addColumn(ColumnDefinition.ATMOS_ST_LIMIT, 0.0);
            //addColumn(ColumnDefinition.TR_ERR_LIMIT,   0.0);
            //addColumn(ColumnDefinition.MIN_EFF_TSYS,   0.0);
            //addColumn(ColumnDefinition.HA_LIMIT,       0.0);
            addColumn(ColumnDefinition.ZA_LIMIT,       85.0);
            addColumn(ColumnDefinition.SOLAR_AVOID,    false);
            //addColumn(ColumnDefinition.PRECIP,         0.0);
            //addColumn(ColumnDefinition.WIND,           0.0);
            //addColumn(ColumnDefinition.TIME,           new TimeOfDayField("RFI");
            addColumn(ColumnDefinition.TRANSIT,        false);
            //addColumn(ColumnDefinition.CADENCE,        new CadenceField("regular");
        }
    };

    private final RowType hiFreqCont = new BaseRowType("High Frequency Continuum") {
        {
            addColumn(ColumnDefinition.CODE,           null);
            addColumn(ColumnDefinition.ORIG_ID,        0);
            addColumn(ColumnDefinition.ID,             0);
            addColumn(ColumnDefinition.TYPE,           new STypeField("open"));
            addColumn(ColumnDefinition.SCIENCE,        null); //new ScienceField("continuum"));
            addColumn(ColumnDefinition.PSC_TIME,       null);
            addColumn(ColumnDefinition.TOTAL_TIME,     null);
            //addColumn(ColumnDefinition.TRI_TIME,       100);
            addColumn(ColumnDefinition.GRADE,          null);
            addColumn(ColumnDefinition.AUTHORIZED,     true);
            addColumn(ColumnDefinition.ENABLED,        false);
            addColumn(ColumnDefinition.COMPLETE,       false);
            addColumn(ColumnDefinition.COORD_MODE,     new CoordModeField("J2000"));
            addColumn(ColumnDefinition.CNTR_SKY_AREA,  null);
            addColumn(ColumnDefinition.FREQ,           null);
            //addColumn(ColumnDefinition.FREQ_RNGE_L,    null);
            //addColumn(ColumnDefinition.FREQ_RNGE_H,    null);
            //addColumn(ColumnDefinition.RECEIVER,       null);
            addColumn(ColumnDefinition.REQ_MIN,        2.0);
            addColumn(ColumnDefinition.REQ_MAX,        6.0);
            addColumn(ColumnDefinition.ABS_MIN,        1.5);
            addColumn(ColumnDefinition.ABS_MAX,        10.0);
            addColumn(ColumnDefinition.BETWEEN,        0.0);
            //addColumn(ColumnDefinition.OBS_EFF_LIMIT,  0.0);
            //addColumn(ColumnDefinition.ATMOS_ST_LIMIT, 0.0);
            //addColumn(ColumnDefinition.TR_ERR_LIMIT,   0.0);
            //addColumn(ColumnDefinition.MIN_EFF_TSYS,   0.0);
            //addColumn(ColumnDefinition.HA_LIMIT,       0.0);
            addColumn(ColumnDefinition.ZA_LIMIT,       85.0);
            addColumn(ColumnDefinition.SOLAR_AVOID,    false);
            //addColumn(ColumnDefinition.PRECIP,         0.0);
            //addColumn(ColumnDefinition.WIND,           0.0);
            //addColumn(ColumnDefinition.TIME,           new TimeOfDayField("RFI");
            addColumn(ColumnDefinition.TRANSIT,        false);
            //addColumn(ColumnDefinition.CADENCE,        new CadenceField("regular");
        }
    };

    private final RowType[] rows = new RowType[] {
            empty,
            lowFreqNoRFI,
            lowFreqRFI,
            hiFreqSpecLine,
            hiFreqCont,
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
