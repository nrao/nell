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
                sFields.put("authorized", true);
                sFields.put("enabled", true);
                sFields.put("complete", false);
                sFields.put("ra", null);
                sFields.put("dec", null);
                sFields.put("total_session", 25);
                sFields.put("grade", new GradeField("A"));
                sFields.put("freq", null);
                sFields.put("science", new ScienceField("spectral line"));
                sFields.put("req_min", 2);
                sFields.put("req_max", 5);
                sFields.put("abs_min", 2);
                sFields.put("abs_max", 5);
                sFields.put("between", 0);
                sFields.put("rfi_night", false);
                sFields.put("ptcs_night", false);

                sFields = new HashMap<String, Object>();
                handle = "Low frequency with RFI";
                master.put(handle, sFields);
                sFields.put("name", handle);
                sFields.put("authorized", true);
                sFields.put("enabled", true);
                sFields.put("complete", false);
                sFields.put("ra", null);
                sFields.put("dec", null);
                sFields.put("total_session", 25);
                sFields.put("grade", new GradeField("A"));
                sFields.put("freq", null);
                sFields.put("science", new ScienceField("spectral line"));
                sFields.put("req_min", 2);
                sFields.put("req_max", 5);
                sFields.put("abs_min", 2);
                sFields.put("abs_max", 5);
                sFields.put("between", 0);
                sFields.put("rfi_night", true);
                sFields.put("freq_range", "1-1.7");
                sFields.put("ptcs_night", false);

                sFields = new HashMap<String, Object>();
                handle = "High frequency spectral line";
                master.put(handle, sFields);
                sFields.put("name", handle);
                sFields.put("authorized", true);
                sFields.put("enabled", true);
                sFields.put("complete", false);
                sFields.put("ra", null);
                sFields.put("dec", null);
                sFields.put("total_session", 25);
                sFields.put("grade", new GradeField("A"));
                sFields.put("freq", null);
                sFields.put("science", new ScienceField("spectral line"));
                sFields.put("req_min", 2);
                sFields.put("req_max", 5);
                sFields.put("abs_min", 2);
                sFields.put("abs_max", 5);
                sFields.put("between", 0);
                sFields.put("rfi_night", false);
                sFields.put("ptcs_night", false);

                sFields = new HashMap<String, Object>();
                handle = "High frequency continuum";
                master.put(handle, sFields);
                sFields.put("name", handle);
                sFields.put("authorized", true);
                sFields.put("enabled", true);
                sFields.put("complete", false);
                sFields.put("ra", null);
                sFields.put("dec", null);
                sFields.put("total_session", 25);
                sFields.put("grade", new GradeField("A"));
                sFields.put("freq", null);
                sFields.put("science", new ScienceField("continuum"));
                sFields.put("req_min", 2);
                sFields.put("req_max", 5);
                sFields.put("abs_min", 2);
                sFields.put("abs_max", 5);
                sFields.put("between", 0);
                sFields.put("rfi_night", false);
                sFields.put("atmo_st", .25);
                sFields.put("ptcs_night", false);

                sFields = new HashMap<String, Object>();
                handle = "Low frequency monitoring with RFI";
                master.put(handle, sFields);
                sFields.put("name", handle);
                sFields.put("authorized", true);
                sFields.put("enabled", true);
                sFields.put("complete", false);
                sFields.put("ra", null);
                sFields.put("dec", null);
                sFields.put("total_session", 25);
                sFields.put("grade", new GradeField("A"));
                sFields.put("freq", null);
                sFields.put("science", new ScienceField("pulsar"));
                sFields.put("req_min", 2);
                sFields.put("req_max", 5);
                sFields.put("abs_min", 2);
                sFields.put("abs_max", 5);
                sFields.put("between", 0);
                sFields.put("rfi_night", true);
                sFields.put("freq_range", "1-1.7");
                sFields.put("ptcs_night", false);
                sFields.put("required?", true);
                
                sFields = new HashMap<String, Object>();
                handle = "Low and high frequency";
                master.put(handle, sFields);
                sFields.put("name", handle);
                sFields.put("authorized", true);
                sFields.put("enabled", true);
                sFields.put("complete", false);
                sFields.put("ra", null);
                sFields.put("dec", null);
                sFields.put("total_session", 25);
                sFields.put("grade", new GradeField("B"));
                sFields.put("freq", null);
                sFields.put("science", new ScienceField("spectral line"));
                sFields.put("desired_rx(s)", "40_50 and (1_2 or 2_3)");
                sFields.put("req_min", 2);
                sFields.put("req_max", 5);
                sFields.put("abs_min", 2);
                sFields.put("abs_max", 5);
                sFields.put("between", 0);
                sFields.put("rfi_night", false);
                sFields.put("ptcs_night", false);

                sFields = new HashMap<String, Object>();
                handle = "Large proposal";
                master.put(handle, sFields);
                sFields.put("name", handle);
                sFields.put("authorized", true);
                sFields.put("enabled", true);
                sFields.put("complete", false);
                sFields.put("ra", null);
                sFields.put("dec", null);
                sFields.put("total_session", 300);
                sFields.put("grade", new GradeField("A"));
                sFields.put("freq", null);
                sFields.put("science", new ScienceField("pulsar"));
                sFields.put("req_min", 2);
                sFields.put("req_max", 5);
                sFields.put("abs_min", 2);
                sFields.put("abs_max", 5);
                sFields.put("between", 0);
                sFields.put("rfi_night", false);
                sFields.put("ptcs_night", false);
                sFields.put("trimester_time", 100);

                sFields = new HashMap<String, Object>();
                handle = "Polarization project";
                master.put(handle, sFields);
                sFields.put("name", handle);
                sFields.put("authorized", true);
                sFields.put("enabled", true);
                sFields.put("complete", false);
                sFields.put("ra", null);
                sFields.put("dec", null);
                sFields.put("total_session", 25);
                sFields.put("grade", new GradeField("A"));
                sFields.put("freq", null);
                sFields.put("science", new ScienceField("pulsar"));
                sFields.put("req_min", 2);
                sFields.put("req_max", 5);
                sFields.put("abs_min", 2);
                sFields.put("abs_max", 5);
                sFields.put("between", 0);
                sFields.put("rfi_night", false);
                sFields.put("ptcs_night", false);

                sFields = new HashMap<String, Object>();
                handle = "PTCS night time";
                master.put(handle, sFields);
                sFields.put("name", handle);
                sFields.put("authorized", true);
                sFields.put("enabled", true);
                sFields.put("complete", false);
                sFields.put("total_session", 25);
                sFields.put("grade", new GradeField("A"));
                sFields.put("req_rx(s)", "holo");
                sFields.put("req_min", 4);
                sFields.put("req_max", 6);
                sFields.put("abs_min", 2);
                sFields.put("abs_max", 5);
                sFields.put("between", 0);
                sFields.put("rfi_night", false);
                sFields.put("ptcs_night", true);

                sFields = new HashMap<String, Object>();
                handle = "PTCS in high winds";
                master.put(handle, sFields);
                sFields.put("name", handle);
                sFields.put("authorized", true);
                sFields.put("enabled", true);
                sFields.put("complete", false);
                sFields.put("total_session", 25);
                sFields.put("grade", new GradeField("A"));
                sFields.put("req_min", 2);
                sFields.put("req_max", 5);
                sFields.put("abs_min", 2);
                sFields.put("abs_max", 5);
                sFields.put("between", 0);
                sFields.put("rfi_night", false);
                sFields.put("ptcs_night", false);
                sFields.put("T_Eff min", "default");
                sFields.put("Tr_limit", .5);

                sFields = new HashMap<String, Object>();
                handle = "Fixed maintenance";
                master.put(handle, sFields);
                sFields.put("name", handle);
                sFields.put("authorized", true);
                sFields.put("enabled", true);
                sFields.put("complete", false);
                sFields.put("length", 10);
                sFields.put("maint_time", true);
                sFields.put("wind", 25);
                sFields.put("start", "12 Dec 09 09:00 EST");

                sFields = new HashMap<String, Object>();
                handle = "Windowed maintenance";
                master.put(handle, sFields);
                sFields.put("name", handle);
                sFields.put("authorized", true);
                sFields.put("enabled", true);
                sFields.put("complete", false);
                sFields.put("req_min", 10);
                sFields.put("percip", true);
                sFields.put("maint_time", true);
                sFields.put("wind", 25);

                sFields = new HashMap<String, Object>();
                handle = "Dynamic VLBI";
                master.put(handle, sFields);
                sFields.put("name", handle);
                sFields.put("authorized", true);
                sFields.put("enabled", true);
                sFields.put("complete", false);
                sFields.put("ra", null);
                sFields.put("dec", null);
                sFields.put("total_session", 25);
                sFields.put("grade", new GradeField("A"));
                sFields.put("freq", null);
                sFields.put("science", new ScienceField("vlbi"));
                sFields.put("length", 6);
                sFields.put("rfi_night", false);
                sFields.put("ptcs_night", false);

                sFields = new HashMap<String, Object>();
                handle = "Fixed radar";
                master.put(handle, sFields);
                sFields.put("name", handle);
                sFields.put("authorized", true);
                sFields.put("enabled", true);
                sFields.put("complete", false);
                sFields.put("ra", null);
                sFields.put("dec", null);
                sFields.put("total_session", 25);
                sFields.put("grade", new GradeField("A"));
                sFields.put("freq", null);
                sFields.put("science", new ScienceField("spectral line"));
                sFields.put("length", 4);
                sFields.put("rfi_night", false);
                sFields.put("start", "12 Dec 09 09:00 EST");

                sFields = new HashMap<String, Object>();
                handle = "Tsys calibration measurement";
                master.put(handle, sFields);
                sFields.put("name", handle);
                sFields.put("authorized", true);
                sFields.put("enabled", true);
                sFields.put("complete", false);
                sFields.put("req_rx(s)", "any");
                sFields.put("req_min", 2);
                sFields.put("req_max", 5);
                sFields.put("abs_min", 2);
                sFields.put("abs_max", 5);
                sFields.put("between", 0);
                sFields.put("rfi_night", false);
                sFields.put("ptcs_night", false);
                sFields.put("required?", false);

                // Use the above maps to figure out what all the types are.
                typeMap = createTypeMap();
                // Here are the one's that are defined as null above:
                typeMap.put("freq", Float.class);
                typeMap.put("ra", String.class);
                typeMap.put("dec", String.class);
                
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
                                fields.put(k, m.get(k).getClass());
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
