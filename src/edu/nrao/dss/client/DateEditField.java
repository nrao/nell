package edu.nrao.dss.client;

import java.util.Date;

class DateEditField {
    
    public DateEditField(Date value) {
        this.value = value;
    }
    
    public String toString() {
        return value.toString();
    }
    
    private final Date value;
}
