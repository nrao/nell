package edu.nrao.dss.client;

class PCodeField {
    public PCodeField(String value) {
        this.value = value;
    }

    public String toString() {
        return value;
    }
    
    private final String value;
}
