package edu.nrao.dss.client;

class CoordModeField {
    public static final String[] values = new String[] { "J2000"
                                                       , "Galactic"
                                                       };

    public CoordModeField(String value) {
        this.value = value;
    }
    
    public String toString() {
        return value;
    }
    
    private final String value;
}
