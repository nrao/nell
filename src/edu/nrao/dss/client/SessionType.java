package edu.nrao.dss.client;

import com.extjs.gxt.ui.client.data.ModelType;

class SessionType extends ModelType {
    public SessionType(ColumnDefinition columns) {
        this.root      = "sessions";
        this.totalName = "total";

        addField("id");
        for (String f : columns.getAllFieldIds()) {
                addField(f);
        }
    }
}
