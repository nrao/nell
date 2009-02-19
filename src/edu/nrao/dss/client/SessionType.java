package edu.nrao.dss.client;

import com.extjs.gxt.ui.client.data.ModelType;

class SessionType extends ModelType {
    public SessionType() {
        this.root = "sessions";

        addField("id");
        for (String f : SessionMap.getAllFields()) {
        	addField(f);
        }
        
    }
}
