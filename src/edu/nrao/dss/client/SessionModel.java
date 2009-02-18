package edu.nrao.dss.client;

import com.extjs.gxt.ui.client.data.BaseModel;

class SessionModel extends BaseModel {
    private static final long serialVersionUID = 1L;

    public SessionModel() {
        set("id", 0);
        set("name", "");
        set("project", "");
        set("session_type", "open");
        set("lst", 0.0);
        set("dec", 0.0);
        set("frequency", 0.0);
        set("min_duration", 0);
        set("max_duration", 0);
        set("time_between", 0);
        set("allotted", 0);
    }
    
    public int getId() {
        return get("id");
    }

    public String getType() {
        return get("session_type");
    }

    public void setId(int id) {
        set("id", id);
    }

    public void setType(String type) {
        set("session_type", type);
    }
}
