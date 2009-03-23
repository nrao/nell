package edu.nrao.dss.client;

class TimeOfDayField {
    public static final String[] values = new String[] { "any"
                                                       , "RFI"
                                                       , "work"
                                                       , "PTCS"
                                                       , "other!?"
                                                       };

    public TimeOfDayField(String value) {
        this.value = value;
    }
    
    public String toString() {
        return value;
    }
    
    private final String value;
}
