package edu.nrao.dss.client;

class STypeField {
    public static final String[] values = new String[] { "open"
                                                       , "windowed"
                                                       , "fixed"
                                                       , "VLBI"
                                                       };

    public STypeField(String value) {
        this.value = value;
    }
    
    public String toString() {
        return value;
    }
    
    private final String value;
}
