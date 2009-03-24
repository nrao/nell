package edu.nrao.dss.client;

import java.util.Map;

interface CalculatedField {
    public abstract Object calculate(RowType row, Map<String, Object> model);
}
