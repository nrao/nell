package edu.nrao.dss.client;

class OrderDependencyField {
    public static final String[] values = new String[] { "start"
                                                       , "tied"
                                                       , "complete"
                                                       };

    public OrderDependencyField(String value) {
        this.value = value;
    }
    
    public String toString() {
        return value;
    }
    
    private final String value;
}
