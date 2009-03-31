package edu.nrao.dss.client;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.extjs.gxt.ui.client.widget.form.Field;
import com.extjs.gxt.ui.client.widget.grid.ColumnConfig;
import com.extjs.gxt.ui.client.widget.grid.ColumnModel;

class ColumnDefinition {
    // Use this enumeration to get compile-time checking of column IDs.
    public static final String ABS_MAX           = "abs_max";
    public static final String ABS_MIN           = "abs_min";
    public static final String ATMOS_ST_LIMIT    = "atmos_st_limit";
    public static final String AUTHORIZED        = "authorized";
    public static final String BETWEEN           = "between";
    public static final String BACKUP            = "backup";
    public static final String CODE              = "proj_code";
    public static final String CNTR_SKY_AREA     = "cntr_sky_area";
    public static final String COMPLETE          = "complete";
    public static final String COORD_MODE        = "coord_mode";
    public static final String ENABLED           = "enabled";
    public static final String FREQ              = "freq";
    public static final String FREQ_RNGE_L       = "freq_range_low";
    public static final String FREQ_RNGE_H       = "freq_range_hi";
    public static final String GRADE             = "grade";
    public static final String HA_LIMIT          = "ha_limit";
    public static final String ID                = "ID";
    public static final String MIN_EFF_TSYS      = "min_eff_tsys";
    public static final String NAME              = "name";
    public static final String OBS_EFF_LIMIT     = "obs_eff_limit";
    public static final String ORIG_ID           = "orig_ID";
    public static final String PRECIP            = "precip";
    public static final String PRI_RCVR          = "receiver";
    public static final String OPT_RCVRS         = "opt_rcvrs";
    public static final String PSC_TIME          = "PSC_time";
    public static final String REQ_MAX           = "req_max";
    public static final String REQ_MIN           = "req_min";
    public static final String SCIENCE           = "science";
    public static final String SEM_TIME          = "sem_time";
    public static final String SOLAR_AVOID       = "solar_avoid";
    public static final String SOURCE            = "source";
    public static final String TIME_DAY          = "time_day";
    public static final String TOTAL_TIME        = "total_time";
    public static final String TRANSIT           = "transit";
    public static final String TRANSIT_AFTER     = "transit_after";
    public static final String TRANSIT_BEFORE    = "transit_before";
    public static final String TR_ERR_LIMIT      = "tr_err_limit";
    public static final String TYPE              = "type";
    public static final String USE_DEPEND        = "use_depend";
    public static final String WIND              = "wind";
    public static final String WINDOW_CADENCE    = "window_cadence";
    public static final String WINDOW_DURATION   = "window_duration";
    public static final String WINDOW_INTERVAL   = "window_interval";
    public static final String WINDOW_PERIOD_LEN = "window_period_len";
    public static final String WINDOW_PRIORITY   = "window_priority";
    public static final String WINDOW_START      = "window_start";
    public static final String ZA_LIMIT          = "za_limit";

    public ColumnDefinition() {
        for (ColumnType column : columns) {
            columnsMap.put(column.getId(), column);
        }
    }

    /** Return a ColumnModel suitable for defining a grid. */
    public ColumnModel getColumnModel(ColumnConfig column) {
        ArrayList<ColumnConfig> columns = new ArrayList<ColumnConfig>();
        columns.add(column);
        columns.addAll(Arrays.asList((ColumnConfig[]) this.columns));

        return new ColumnModel(columns);
    }

    /** Return the master list of all know columns. */
    public List<String> getAllFieldNames() {
        ArrayList<String> result = new ArrayList<String>();
        for (ColumnType column : columns) {
            result.add(column.getHeader());
        }
        return result;
    }

    public List<String> getAllFieldIds() {
        ArrayList<String> result = new ArrayList<String>();
        for (ColumnType column : columns) {
            result.add(column.getId());
        }
        return result;
    }

    public boolean hasColumn(String id) {
        return columnsMap.containsKey(id);
    }

    public ColumnType getColumn(String id) {
        return columnsMap.get(id);
    }

    public Object getValue(String id, RowType row, Map<String, Object> model) {
        return getColumn(id).getValue(row, model);
    }
    
    @SuppressWarnings("unchecked")
	public Field getField(String id) {
    	return getColumn(id).getField();
    }

    private final CalculatedField receivers = new CalculatedField() {
        public Object calculate(RowType row, Map<String, Object> model) {
            return row.getValue(FREQ, model);
        }
    };

    private final CalculatedField obsEffLimit = new CalculatedField() {
        public Object calculate(RowType row, Map<String, Object> model) {
            return row.getValue(FREQ, model);
        }
    };

    private final CalculatedField atmosStLimit = new CalculatedField() {
        public Object calculate(RowType row, Map<String, Object> model) {
            return row.getValue(FREQ, model);
        }
    };

    private final CalculatedField trErrLimit = new CalculatedField() {
        public Object calculate(RowType row, Map<String, Object> model) {
            return row.getValue(FREQ, model);
        }
    };

    private final CalculatedField minEffTsys = new CalculatedField() {
        public Object calculate(RowType row, Map<String, Object> model) {
            return row.getValue(FREQ, model);
        }
    };

    private final CalculatedField haLimit = new CalculatedField() {
        public Object calculate(RowType row, Map<String, Object> model) {
            return row.getValue(FREQ, model);
        }
    };

    private final ColumnType[] columns = new ColumnType[] {
    		new ColumnType(SOURCE,         "Source",         100, Boolean.class,              null),
            new ColumnType(NAME,           "Name",           100, String.class,               null),
            new ColumnType(CODE,           "Proj Code",      100, String.class,               null),
            new ColumnType(ORIG_ID,        "Orig ID",        100, Integer.class,              null),
            new ColumnType(ID,             "ID",             100, Integer.class,              null),
            new ColumnType(TYPE,           "Type",           100, STypeField.class,           null),
            new ColumnType(SCIENCE,        "Science",        100, ScienceField.class,         null),
            new ColumnType(PSC_TIME,       "PSC Time",       100, Integer.class,              null),
            new ColumnType(TOTAL_TIME,     "Total Time",     100, Integer.class,              null),
            new ColumnType(SEM_TIME,       "Semester Time",  100, Integer.class,              null),
            new ColumnType(GRADE,          "Grade",          100, Double.class,               null),
            new ColumnType(AUTHORIZED,     "Authorized",     100, Boolean.class,              null),
            new ColumnType(ENABLED,        "Enabled",        100, Boolean.class,              null),
            new ColumnType(COMPLETE,       "Complete",       100, Boolean.class,              null),
            new ColumnType(COORD_MODE,     "Coord Mode",     100, CoordModeField.class,       null),
            new ColumnType(CNTR_SKY_AREA,  "Cntr Sky Area",  100, String.class,               null),
            new ColumnType(FREQ,           "Freq",            55, Double.class,               null),
            new ColumnType(FREQ_RNGE_L,    "Freq Range Low",  55, Double.class,               null),
            new ColumnType(FREQ_RNGE_H,    "Freq Range Hi",   55, Double.class,               null),
            new ColumnType(PRI_RCVR,       "Receiver",       100, String.class,               receivers),
            new ColumnType(OPT_RCVRS,      "Opt Rcvrs",      100, String.class,               receivers),
            new ColumnType(REQ_MIN,        "Req Min",        100, Double.class,               null),
            new ColumnType(REQ_MAX,        "Req Max",        100, Double.class,               null),
            new ColumnType(ABS_MIN,        "Abs Min",        100, Double.class,               null),
            new ColumnType(ABS_MAX,        "Abs Max",        100, Double.class,               null),
            new ColumnType(BETWEEN,        "Between",        100, Double.class,               null),
            new ColumnType(BACKUP,         "Backup",         100, Boolean.class,               null),
            new ColumnType(OBS_EFF_LIMIT,  "Obs Eff Limit",  100, Double.class,               obsEffLimit),
            new ColumnType(ATMOS_ST_LIMIT, "Atmos St Limit", 100, Double.class,               atmosStLimit),
            new ColumnType(TR_ERR_LIMIT,   "Tr Err Limit",   100, Double.class,               trErrLimit),
            new ColumnType(MIN_EFF_TSYS,   "Min Eff TSys",   100, Double.class,               minEffTsys),
            new ColumnType(HA_LIMIT,       "HA Limit",       100, Double.class,               haLimit),
            new ColumnType(ZA_LIMIT,       "ZA Limit",       100, Double.class,               null),
            new ColumnType(SOLAR_AVOID,    "Solar Avoid",    100, Boolean.class,              null),
            new ColumnType(PRECIP,         "Precip",         100, Double.class,               null),
            new ColumnType(WIND,           "Wind",           100, Double.class,               null),
            new ColumnType(TIME_DAY,       "Time Day",       100, TimeOfDayField.class,       null),
            //new ColumnType(USE_DEPEND,     "Use Depend",     100, Boolean.class,              null),
            //new ColumnType(DEPEND_ID,      "Depend ID",      100, Integer.class,              null),
            //new ColumnType(DEPEND_ORDER,   "Depend Order",   100, OrderDependencyField.class, null),
            new ColumnType(TRANSIT,        "Transit",         60, Boolean.class,              null),
            //new ColumnType(TRANSIT_BEFORE, "Transit Before", 100, Integer.class,              null),
            //new ColumnType(TRANSIT_AFTER,  "Transit After",  100, Integer.class,              null)
    };

    private final HashMap<String, ColumnType> columnsMap = new HashMap<String, ColumnType>();
}
