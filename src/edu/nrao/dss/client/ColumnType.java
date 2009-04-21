package edu.nrao.dss.client;

import java.util.Map;

class ColumnType extends SessionColConfig {
    @SuppressWarnings("unchecked")
    public ColumnType(String id, String name, int width, Class type, Object value) {
        super(id, name, width, type);
        this.value = value;
    }

    public Object getValue(RowType row, Map<String, Object> model) {
        if (value == null) {
            return null;
        }

        if (value instanceof CalculatedField) {
            return ((CalculatedField) value).calculate(row, model);
        }

        return value;
    }
    
    public boolean hasColumnDefault() {
    	return value != null;
    }

    @SuppressWarnings("unchecked")
	public Class getClasz(String id) {
    	return this.clasz;
    }
    
    private final Object value;
}
