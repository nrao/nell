package edu.nrao.dss.client;

import com.extjs.gxt.ui.client.data.ModelType;

class SessionType extends ModelType {
    public SessionType() {
        this.root = "sessions";

        addField("id");
        addField("name");
        addField("project");
        addField("type");
        addField("lst");
        addField("dec");
        addField("frequency");
        addField("min_duration");
        addField("max_duration");
        addField("time_between");
        addField("allotted");
    }
}
