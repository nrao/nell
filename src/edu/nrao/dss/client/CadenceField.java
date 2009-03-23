package edu.nrao.dss.client;

class CadenceField {
    public static final String[] values = new String[] { "regular"
                                                       , "irregular"
                                                       , "fixed"
                                                       };

    public CadenceField(String value) {
        this.value = value;
    }
    
    public String toString() {
        return value;
    }
    
    private final String value;
}
