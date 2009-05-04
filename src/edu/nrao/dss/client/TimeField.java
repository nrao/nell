package edu.nrao.dss.client;

class TimeField {
    
    public TimeField(String value) {
        this.value = value;
    }
    
    public String toString() {
        return value;
    }
    
    private final String value;
}
