package edu.nrao.dss.client;

class PriorityField {
    public static final String[] values = new String[] { "required"
                                                       , "desired"
                                                       };

    public PriorityField(String value) {
        this.value = value;
    }
    
    public String toString() {
        return value;
    }
    
    private final String value;
}
