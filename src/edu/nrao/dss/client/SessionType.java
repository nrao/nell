package edu.nrao.dss.client;

import com.extjs.gxt.ui.client.data.DataField;
import com.extjs.gxt.ui.client.data.ModelType;

class SessionType extends ModelType {
    public SessionType() {
        this.root = "sessions";

        addField("id", Integer.class);
        addField("name", String.class);
        addField("project", String.class);
        addField("session_type", String.class);
        addField("lst", Double.class);
        addField("dec", Double.class);
        addField("frequency", Double.class);
        addField("min_duration", Integer.class);
        addField("max_duration", Integer.class);
        addField("time_between", Integer.class);
        addField("allotted", Integer.class);
    }
    
    @SuppressWarnings("unchecked")
    private void addField(String name, Class type) {
        DataField field = new DataField(name);
        field.type = type;
        addField(field);
    }
}
