package edu.nrao.dss.client;

class TimeOfDayField {
    public static final String[] values = new String[] { "Any"
                                                       , "RFI"
                                                       , "PTCS"
                                                       , "Maintenance"
                                                       , "SolarDay"
                                                       };

    public TimeOfDayField(String value) {
        this.value = value;
    }
    
    public String toString() {
        return value;
    }
    
    private final String value;
}
