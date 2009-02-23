package edu.nrao.dss.client;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;

class SessionMap {
	public static final HashMap<String, HashMap<String, Object>> master = new HashMap<String, HashMap<String, Object>>();

	public static final HashMap<String, String> typeMap;

	static {
		
		HashMap<String, Object> sFields = new HashMap<String, Object>();
		master.put("Empty", sFields);
		sFields.put("name", "");

		// sFields.put("project", "");
		// sFields.put("type", "");
		// sFields.put("ra", "");
		// sFields.put("dec", "");
		// sFields.put("frequency", "");
		// sFields.put("min_duration", "");
		// sFields.put("max_duration", "");
		// sFields.put("time_between", "");
		// sFields.put("allotted", "");
		// sFields.put("grade", "A");
		// sFields.put("enabled", true);

		sFields = new HashMap<String, Object>();
		master.put("Low frequency observations with no RFI", sFields);
		sFields.put("name", "");
		sFields.put("enabled", "true");
		sFields.put("authorized", "true");
		sFields.put("complete", "false");
		sFields.put("contact", "Joe");
		sFields.put("thesis", "false");
		sFields.put("ra", "12:00:00");
		sFields.put("dec", "12:00:00");
		sFields.put("onsite", "f");
		sFields.put("total_session", 25);
		sFields.put("grade", "A");
		sFields.put("req_rx(s)", "1_2");
		sFields.put("min", 2);
		sFields.put("max", 5);
		sFields.put("between", 0);
		sFields.put("rfi_night", "false");
		sFields.put("ptcs_night", "false");

		sFields = new HashMap<String, Object>();
		master.put("Low frequency observations with RFI", sFields);
		sFields.put("name", "");
		sFields.put("enabled", "true");
		sFields.put("authorized", "true");
		sFields.put("complete", "false");
		sFields.put("contact", "Joe");
		sFields.put("thesis", "false");
		sFields.put("ra", "12:00:00");
		sFields.put("dec", "12:00:00");
		sFields.put("onsite", "f");
		sFields.put("total_session", 25);
		sFields.put("grade", "A");
		sFields.put("req_rx(s)", "1_2");
		sFields.put("min", 2);
		sFields.put("max", 5);
		sFields.put("between", 0);
		sFields.put("rfi_night", "true");
		sFields.put("freq_range", null);
		sFields.put("ptcs_night", "false");

		sFields = new HashMap<String, Object>();
		master.put("High frequency spectral line observations", sFields);
		sFields.put("name", "");
		sFields.put("enabled", "true");
		sFields.put("authorized", "true");
		sFields.put("complete", "false");
		sFields.put("contact", "Joe");
		sFields.put("thesis", "false");
		sFields.put("ra", "12:00:00");
		sFields.put("dec", "12:00:00");
		sFields.put("onsite", "f");
		sFields.put("total_session", 25);
		sFields.put("grade", "A");
		sFields.put("req_rx(s)", "18_26");
		sFields.put("min", 2);
		sFields.put("max", 5);
		sFields.put("between", 0);
		sFields.put("rfi_night", "false");
		sFields.put("ptcs_night", "false");

		sFields = new HashMap<String, Object>();
		master.put("High frequency continuum observations", sFields);
		sFields.put("name", "");
		sFields.put("enabled", "true");
		sFields.put("authorized", "true");
		sFields.put("complete", "false");
		sFields.put("contact", "Joe");
		sFields.put("thesis", "false");
		sFields.put("ra", "12:00:00");
		sFields.put("dec", "12:00:00");
		sFields.put("onsite", "f");
		sFields.put("total_session", 25);
		sFields.put("grade", "A");
		sFields.put("req_rx(s)", "18_26");
		sFields.put("min", 2);
		sFields.put("max", 5);
		sFields.put("between", 0);
		sFields.put("rfi_night", "false");
		sFields.put("clouds", .25);
		sFields.put("ptcs_night", "false");

		sFields = new HashMap<String, Object>();
		master.put("High frequency continuum observations", sFields);
		sFields.put("name", "");
		sFields.put("enabled", "true");
		sFields.put("authorized", "true");
		sFields.put("complete", "false");
		sFields.put("contact", "Joe");
		sFields.put("thesis", "false");
		sFields.put("ra", "12:00:00");
		sFields.put("dec", "12:00:00");
		sFields.put("onsite", "f");
		sFields.put("total_session", 25);
		sFields.put("grade", "A");
		sFields.put("req_rx(s)", "18_26");
		sFields.put("min", 2);
		sFields.put("max", 5);
		sFields.put("between", 0);
		sFields.put("rfi_night", "false");
		sFields.put("clouds", .25);
		sFields.put("ptcs_night", "false");

		sFields = new HashMap<String, Object>();
		master.put("Low frequency monitoring observations with RFI", sFields);
		sFields.put("name", "");
		sFields.put("enabled", "true");
		sFields.put("authorized", "true");
		sFields.put("complete", "false");
		sFields.put("contact", "Joe");
		sFields.put("thesis", "false");
		sFields.put("ra", "12:00:00");
		sFields.put("dec", "12:00:00");
		sFields.put("onsite", "f");
		sFields.put("total_session", 25);
		sFields.put("grade", "A");
		sFields.put("req_rx(s)", "1_2");
		sFields.put("min", 2);
		sFields.put("max", 5);
		sFields.put("between", 0);
		sFields.put("rfi_night", "false");
		sFields.put("freq_range", "1-1.7");
		sFields.put("ptcs_night", "false");
		sFields.put("required?", "true");
		
		sFields = new HashMap<String, Object>();
		master.put("Low and high frequency observations", sFields);
		sFields.put("name", "");
		sFields.put("enabled", "true");
		sFields.put("authorized", "true");
		sFields.put("complete", "false");
		sFields.put("contact", "Joe");
		sFields.put("thesis", "false");
		sFields.put("ra", "12:00:00");
		sFields.put("dec", "12:00:00");
		sFields.put("onsite", "false");
		sFields.put("total_session", 25);
		sFields.put("grade", "B");
		sFields.put("req_rx(s)", "40_50");
		sFields.put("desired_rx(s)", "1_2 or 2_3");
		sFields.put("min", 2);
		sFields.put("max", 5);
		sFields.put("between", 0);
		sFields.put("rfi_night", "false");
		sFields.put("ptcs_night", "false");

		sFields = new HashMap<String, Object>();
		master.put("Large proposal", sFields);
		sFields.put("name", "");
		sFields.put("enabled", "true");
		sFields.put("authorized", "true");
		sFields.put("complete", "false");
		sFields.put("contact", "Joe");
		sFields.put("thesis", "false");
		sFields.put("ra", "12:00:00");
		sFields.put("dec", "12:00:00");
		sFields.put("onsite", "false");
		sFields.put("total_session", 300);
		sFields.put("grade", "A");
		sFields.put("req_rx(s)", "1_2");
		sFields.put("min", 2);
		sFields.put("max", 5);
		sFields.put("between", 0);
		sFields.put("rfi_night", "false");
		sFields.put("ptcs_night", "false");

		sFields = new HashMap<String, Object>();
		master.put("Polarization project", sFields);
		sFields.put("name", "");
		sFields.put("enabled", "true");
		sFields.put("authorized", "true");
		sFields.put("complete", "false");
		sFields.put("contact", "Joe");
		sFields.put("thesis", "false");
		sFields.put("ra", "12:00:00");
		sFields.put("dec", "12:00:00");
		sFields.put("onsite", "false");
		sFields.put("total_session", 25);
		sFields.put("grade", "A");
		sFields.put("req_rx(s)", "1_2");
		sFields.put("min", 2);
		sFields.put("max", 5);
		sFields.put("between", 0);
		sFields.put("rfi_night", "false");
		sFields.put("ptcs_night", "false");

		sFields = new HashMap<String, Object>();
		master.put("PTCS night time holography", sFields);
		sFields.put("name", "");
		sFields.put("enabled", "true");
		sFields.put("authorized", "true");
		sFields.put("complete", "false");
		sFields.put("contact", "Joe");
		sFields.put("onsite", "false");
		sFields.put("total_session", 25);
		sFields.put("req_rx(s)", "Holo");
		sFields.put("min", 4);
		sFields.put("max", 6);
		sFields.put("between", 0);
		sFields.put("rfi_night", "false");
		sFields.put("ptcs_night", "true");

		sFields = new HashMap<String, Object>();
		master.put("PTCS servo tests in high winds", sFields);
		sFields.put("name", "");
		sFields.put("enabled", "true");
		sFields.put("authorized", "true");
		sFields.put("complete", "false");
		sFields.put("contact", "Joe");
		sFields.put("onsite", "false");
		sFields.put("total_session", 25);
		sFields.put("grade", "B");
		sFields.put("req_rx(s)", "40_50");
		sFields.put("min", 2);
		sFields.put("max", 5);
		sFields.put("between", 0);
		sFields.put("rfi_night", "false");
		sFields.put("ptcs_night", "false");

		sFields = new HashMap<String, Object>();
		master.put("Fixed maintenance", sFields);
		sFields.put("name", "");
		sFields.put("enabled", "true");
		sFields.put("authorized", "true");
		sFields.put("complete", "false");
		sFields.put("contact", "Joe");
		sFields.put("req_rx(s)", "40_50");
                sFields.put("length", 10);
                sFields.put("start", "12 Dec 09 09:00 EST");

		sFields = new HashMap<String, Object>();
		master.put("Windowed maintenance", sFields);
		sFields.put("name", "");
		sFields.put("enabled", "true");
		sFields.put("authorized", "true");
		sFields.put("complete", "false");
		sFields.put("contact", "Joe");
                sFields.put("length", 10);

		sFields = new HashMap<String, Object>();
		master.put("Dynamic VLBI", sFields);
		sFields.put("name", "");
		sFields.put("enabled", "true");
		sFields.put("authorized", "true");
		sFields.put("complete", "false");
		sFields.put("contact", "Joe");
		sFields.put("ra", "12:00:00");
		sFields.put("dec", "12:00:00");
		sFields.put("onsite", "false");
		sFields.put("total_session", 25);
		sFields.put("grade", "A");
		sFields.put("req_rx(s)", "18_26");
                sFields.put("length", 6);
		sFields.put("rfi_night", "false");
		sFields.put("ptcs_night", "false");

		sFields = new HashMap<String, Object>();
		master.put("Fixed radar", sFields);
		sFields.put("name", "");
		sFields.put("enabled", "true");
		sFields.put("authorized", "true");
		sFields.put("complete", "false");
		sFields.put("contact", "Joe");
		sFields.put("thesis", "N");
		sFields.put("ra", "12:00:00");
		sFields.put("dec", "12:00:00");
		sFields.put("onsite", "false");
		sFields.put("total_session", 25);
		sFields.put("grade", "A");
		sFields.put("req_rx(s)", "1_2");
		sFields.put("desired_rx(s)", "1_2 or 2_3");
                sFields.put("length", 4);
		sFields.put("between", 0);
		sFields.put("rfi_night", "false");
		sFields.put("ptcs_night", "false");
                sFields.put("start", "12 Dec 09 09:00 EST");

		sFields = new HashMap<String, Object>();
		master.put("Tsys calibration measurement", sFields);
		sFields.put("name", "");
		sFields.put("enabled", "true");
		sFields.put("authorized", "true");
		sFields.put("complete", "false");
		sFields.put("contact", "Joe");
		sFields.put("min", 2);
		sFields.put("max", 5);
		sFields.put("between", 0);
		sFields.put("rfi_night", "false");
		sFields.put("ptcs_night", "false");
		sFields.put("required?", "false");

		// use the above maps to figure out what all the types are.
		typeMap = createTypeMap();
		// here are the one's that are defined as null above
		typeMap.put("freq_range", "java.lang.String");
		
		
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

	public static HashMap<String, String> createTypeMap() {
		HashMap<String, String> fields = new HashMap<String, String>();
		for (HashMap<String, Object> m : master.values()) {
			for (String k : m.keySet()) {
				if (m.get(k) != null) {
				    fields.put(k, m.get(k).getClass().getName());
			    }
			}
		}
		return fields;
	}

	public static HashMap<String, String> getAllFieldsWithClass() {
		HashMap<String, String> fields = new HashMap<String, String>();
		for (HashMap<String, Object> m : master.values()) {
			for (String k : m.keySet()) {
				fields.put(k, m.get(k).getClass().getName());
			}
		}
		return fields;
	}

	public static Set<String> getNames(String sType) {
		return master.get(sType).keySet();
	}

	public static String getFieldClass(String sType, String fName) {
		return master.get(sType).get(fName).getClass().getName();
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
