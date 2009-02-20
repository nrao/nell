package edu.nrao.dss.client;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;

class SessionMap {
	public static final HashMap<String, HashMap<String, Object>> master =
		new HashMap<String, HashMap<String,Object>>();

	static {
		HashMap<String, Object> empty = new HashMap<String, Object>();
		master.put("Empty", empty);
		empty.put("name", "");

		//empty.put("project", "");
		//empty.put("type", "");
		//empty.put("ra", "");
		//empty.put("dec", "");
		//empty.put("frequency", "");
		//empty.put("min_duration", "");
		//empty.put("max_duration", "");
		//empty.put("time_between", "");
		//empty.put("allotted", "");
		//empty.put("grade", "A");
		//empty.put("enabled", true);

		HashMap<String, Object> lowfreq = new HashMap<String, Object>();
		master.put("Low Frequency No RFI", lowfreq);
		lowfreq.put("name", "");
		lowfreq.put("enabled", "true");
		lowfreq.put("authorized", "true");
		lowfreq.put("complete", "false");
		lowfreq.put("contact", "Joe");
		lowfreq.put("thesis", "N");
		lowfreq.put("ra", "12:00:00");
		lowfreq.put("dec", "12:00:00");
		lowfreq.put("onsite", "f");
		lowfreq.put("total_session", 25);
		lowfreq.put("grade", new GradeField("A"));
		lowfreq.put("req_rx(s)", "1_2");
		lowfreq.put("min", 2);
		lowfreq.put("max", 5);
		lowfreq.put("between", 0);
		lowfreq.put("rfi_night", "false");
		lowfreq.put("ptcs_night", "false");

		HashMap<String, Object> lowfreq_rfi = new HashMap<String, Object>();
		master.put("Low Frequency RFI", lowfreq_rfi);
		lowfreq_rfi.put("name", "");
		lowfreq_rfi.put("enabled", "true");
		lowfreq_rfi.put("authorized", "true");
		lowfreq_rfi.put("complete", "false");
		lowfreq_rfi.put("contact", "Joe");
		lowfreq_rfi.put("thesis", "N");
		lowfreq_rfi.put("ra", "12:00:00");
		lowfreq_rfi.put("dec", "12:00:00");
		lowfreq_rfi.put("onsite", "f");
		lowfreq_rfi.put("total_session", 25);
		lowfreq_rfi.put("grade", new GradeField("A"));
		lowfreq_rfi.put("req_rx(s)", "1_2");
		lowfreq_rfi.put("min", 2);
		lowfreq_rfi.put("max", 5);
		lowfreq_rfi.put("between", 0);
		lowfreq_rfi.put("rfi_night", "true");
		lowfreq_rfi.put("freq_range", "1-1.7");
		lowfreq_rfi.put("ptcs_night", "false");
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
 }
