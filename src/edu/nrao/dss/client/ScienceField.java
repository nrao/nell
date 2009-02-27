package edu.nrao.dss.client;

class ScienceField {
    public static final String[] values = new String[] { "pulsar"
                                                       , "continuum"
                                                       , "spectral line"
                                                       , "vlib"
                                                       };

    public ScienceField(String value) {
        this.value = value;
    }
    
    public String toString() {
        return value;
    }
    
    private final String value;
}
