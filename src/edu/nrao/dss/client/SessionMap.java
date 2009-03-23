package edu.nrao.dss.client;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;

class SessionMap {
    public static final HashMap<String, HashMap<String, Object>> master =
                    new HashMap<String, HashMap<String,Object>>();

    @SuppressWarnings("unchecked")
    public static final HashMap<String, Class> typeMap;

    static {
        HashMap<String, Object> sFields = new HashMap<String, Object>();
        String handle = "Empty";
        master.put(handle, sFields);
        sFields.put("name", handle);

        sFields = new HashMap<String, Object>();
        handle = "Low frequency with no RFI";
        master.put(handle, sFields);
        sFields.put("name", handle);
        sFields.put("orig_ID", 0);
        sFields.put("ID", 0);
        sFields.put("type", new STypeField("open"));
        sFields.put("science", new ScienceField("spectral line"));
        sFields.put("PSC_time", null);
        sFields.put("total_time", null);
        //sFields.put("tri_time", 25);
        sFields.put("grade", new GradeField("A"));
        sFields.put("authorized", true);
        sFields.put("enabled", false);
        sFields.put("complete", false);
        sFields.put("coord_mode", new CoordModeField("J2000"));
        sFields.put("cntr_sky_area", null);
        sFields.put("freq", null);
        sFields.put("freq_range", null);
        sFields.put("receivers", "f(freq)");
        sFields.put("req_min", 2.0);
        sFields.put("req_max", 6.0);
        sFields.put("abs_min", 1.5);
        sFields.put("abs_max", 10.0);
        sFields.put("between", 0.0);
        sFields.put("obs_eff_limit", "f(freq)");
        sFields.put("atmos_st_limit", "f(freq,science)");
        sFields.put("tr_err_limit", "f(freq)");
        sFields.put("min_eff_tsys", "f(freq)");
        sFields.put("ha_limit", "f(transit)");
        sFields.put("za_limit", 85.0);
        sFields.put("solar_avoid", false);
        //sFields.put("precip", 0.0);
        //sFields.put("wind", 0.0);
        //sFields.put("time_day", new TimeOfDay("RFI"));
        // inter-session dependency
        sFields.put("use_depend", false);
        //sFields.put("depend_id", null);
        //sFields.put("depend_order", null);
        // transit
        sFields.put("transit", false);
        //sFields.put("transit_before", 25);
        //sFields.put("transit_after", 25);
        // windowed
        //sFields.put("window_cadence", null);
        //sFields.put("window_start(s)", null);
        //sFields.put("window_repeats", null);
        //sFields.put("window_interval(s)", null);
        //sFields.put("window_duration", null);
        //sFields.put("window_period_len", null);
        //sFields.put("window_priority", null);

        sFields = new HashMap<String, Object>();
        handle = "Low frequency with RFI";
        master.put(handle, sFields);
        sFields.put("name", handle);

        sFields = new HashMap<String, Object>();
        handle = "High frequency spectral line";
        master.put(handle, sFields);
        sFields.put("name", handle);

        sFields = new HashMap<String, Object>();
        handle = "High frequency continuum";
        master.put(handle, sFields);
        sFields.put("name", handle);

        sFields = new HashMap<String, Object>();
        handle = "Low frequency monitoring with RFI";
        master.put(handle, sFields);
        sFields.put("name", handle);
        
        sFields = new HashMap<String, Object>();
        handle = "Low and high frequency";
        master.put(handle, sFields);
        sFields.put("name", handle);

        sFields = new HashMap<String, Object>();
        handle = "Large proposal";
        master.put(handle, sFields);
        sFields.put("name", handle);

        sFields = new HashMap<String, Object>();
        handle = "Polarization project";
        master.put(handle, sFields);
        sFields.put("name", handle);

        sFields = new HashMap<String, Object>();
        handle = "PTCS night time";
        master.put(handle, sFields);
        sFields.put("name", handle);

        sFields = new HashMap<String, Object>();
        handle = "PTCS in high winds";
        master.put(handle, sFields);
        sFields.put("name", handle);

        sFields = new HashMap<String, Object>();
        handle = "Fixed maintenance";
        master.put(handle, sFields);
        sFields.put("name", handle);

        sFields = new HashMap<String, Object>();
        handle = "Windowed maintenance";
        master.put(handle, sFields);
        sFields.put("name", handle);

        sFields = new HashMap<String, Object>();
        handle = "Dynamic VLBI";
        master.put(handle, sFields);
        sFields.put("name", handle);

        sFields = new HashMap<String, Object>();
        handle = "Fixed radar";
        master.put(handle, sFields);
        sFields.put("name", handle);

        sFields = new HashMap<String, Object>();
        handle = "Tsys calibration measurement";
        master.put(handle, sFields);
        sFields.put("name", handle);

        // Use the above maps to figure out what all the types are.
        typeMap = createTypeMap();
        // Here are the one's that are defined as null above:
        typeMap.put("freq", Float.class);
        typeMap.put("PSC_time", Float.class);
        typeMap.put("total_time", Float.class);
        typeMap.put("cntr_sky_area", String.class);
        typeMap.put("freq", Float.class);
        typeMap.put("freq_range", String.class);
        typeMap.put("depend_id", Boolean.class);
        typeMap.put("depend_order", OrderDependencyField.class);
        typeMap.put("window_cadence", CadenceField.class);
        typeMap.put("window_start(s)", String.class);
        typeMap.put("window_repeats", Integer.class);
        typeMap.put("window_interval(s)", Float.class);
        typeMap.put("window_duration", Integer.class);
        typeMap.put("window_period_len", Integer.class);
        typeMap.put("window_priority", PriorityField.class);
        
    }

    public static Set<String> getAllFields() {
        Set<String> fields = new HashSet<String>();
        for (HashMap<String, Object> m : master.values()) {
            for (String k : m.keySet()) {
                    fields.add(k);
            }
        }
        return fields;
    }

    @SuppressWarnings("unchecked")
    public static HashMap<String, Class> createTypeMap() {
        HashMap<String, Class> fields = new HashMap<String, Class>();
        for (HashMap<String, Object> m : master.values()) {
            for (String k : m.keySet()) {
                    if (m.get(k) != null) {
                        fields.put(k, m.get(k).getClass());
                }
            }
        }
        return fields;
    }

    @SuppressWarnings("unchecked")
    public static HashMap<String, Class> getAllFieldsWithClass() {
        HashMap<String, Class> fields = new HashMap<String, Class>();
        for (HashMap<String, Object> m : master.values()) {
            for (String k : m.keySet()) {
                if (m.get(k) != null){
                        fields.put(k, m.get(k).getClass());
                }
            }
        }
        return fields;
    }

    public static Set<String> getNames(String sType) {
        return master.get(sType).keySet();
    }
    
    @SuppressWarnings("unchecked")
    public static Class getFieldClass(String fName) {
        return getAllFieldsWithClass().get(fName);
    }

    public static Set<String> getRequiredFields(String sType) {
        HashMap<String, Object> sFields = master.get(sType);
        Set<String> requiredFields = new HashSet<String>();
        for (String k : sFields.keySet()) {
            // if no value here, then user must specify it
            if (sFields.get(k) == null) {
                    requiredFields.add(k);
            }
        }
        return requiredFields;
    }
}
