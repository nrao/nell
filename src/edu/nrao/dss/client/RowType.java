package edu.nrao.dss.client;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.extjs.gxt.ui.client.widget.form.Field;

public class RowType {
    public RowType(ColumnDefinition columns) {
        this.columns = columns;
    }

    /** Return the name of this row type. */
    public String getName() {
        return (String) getValue("name", null);
    }

    public List<String> getFieldNames() {
        return new ArrayList<String>(values.keySet());
    }

    public void populateDefaultValues(HashMap<String, Object> model) {
        for (String field : this.columns.getAllFieldIds()) {
            if (! model.containsKey(field)) {
                Object value = getValue(field, model);
                if (value != null) {
                    model.put(field, value);
                }
            }
        }
    }
    
    @SuppressWarnings("unchecked")
    public Field getField(String id) {
        return columns.getField(id);
    }

    public Object getValue(String id, Map<String, Object> model) {
        if (model != null && model.get(id) != null) {
            return model.get(id);
        }
        if (values.containsKey(id)) {
        	Object value = values.get(id);
            if (value != null) {
                return value;
            }
        }
        return columns.getValue(id, this, model);
    }

    public List<String> getRequiredFields() {
        ArrayList<String> result = new ArrayList<String>();
        for (String id : values.keySet()) {
            if (values.get(id) == null && !columns.hasColumnDefault(id)) {
                result.add(id);
            }
        }
        return result;
    }

    /** True iff there are fields we need to for the user to supply, via a dialog. */
    public boolean hasRequiredFields() {
        return ! getRequiredFields().isEmpty();
    }

    protected void addColumn(String id, Object value) {
        // Crash early if this column has not been defined.
        if (! columns.hasColumn(id)) {
            throw new Error("missing column: " + id);
        }

        values.put(id, value);
    }

    private final Map<String, Object> values = new HashMap<String, Object>();
    private final ColumnDefinition    columns;
}
