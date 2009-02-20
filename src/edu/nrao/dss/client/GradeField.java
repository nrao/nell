package edu.nrao.dss.client;

class GradeField {
    public static final String[] values = new String[] {"A", "B", "C"};

    public GradeField(String value) {
        this.value = value;
    }
    
    public String toString() {
        return value;
    }
    
    private final String value;
}
