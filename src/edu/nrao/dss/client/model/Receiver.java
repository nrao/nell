package edu.nrao.dss.client.model;


public class Receiver {

    static public String deriveReceiver(double frequency) {
        String receiver_name = "NS";
        int cnt = names.length;
        for (int i = 0; i < cnt; ++i) {
        	if (frequency <= uppers[i]) {
        		receiver_name = names[i];
        		break;
        	}
        }
        return receiver_name;
    }
    
    static public String[] getNames() {
    	return names;
    }
    
    // TBF cardinal sin: code duplicated in server - Generate.py
    static private String[] names = {
    	"NS",
    	"RRI",
    	"342",
    	"450",
    	"600",
    	"800",
    	"1070",
    	"L", 
    	"S",
    	"C",
    	"X",
    	"Ku",
    	"K",
    	"Ka",
    	"Q",
    	"MBA"
    };
    
    static private double[] uppers = {
    	 0.0,
      	  .012,
    	  .395,
    	  .52,
    	  .69,
    	  .92,
         1.23,
    	 1.73,
    	 3.275,
    	 6.925,
    	11.0,
    	16.7,
    	26.25,
    	40.5,
    	52.0,
    	91.0
    };
}
