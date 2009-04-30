package edu.nrao.dss.client;

import java.util.HashMap;
import java.util.Map;

import com.extjs.gxt.ui.client.event.SelectionChangedEvent;
import com.extjs.gxt.ui.client.event.SelectionChangedListener;
import com.extjs.gxt.ui.client.widget.form.DateField;
import com.extjs.gxt.ui.client.widget.form.FormPanel;
import com.extjs.gxt.ui.client.widget.form.NumberField;
import com.extjs.gxt.ui.client.widget.form.SimpleComboBox;
import com.extjs.gxt.ui.client.widget.form.SimpleComboValue;
import com.extjs.gxt.ui.client.widget.form.TextField;
import com.google.gwt.i18n.client.DateTimeFormat;
import com.google.gwt.json.client.JSONObject;

class CadenceDetails extends FormPanel {
    public CadenceDetails(SimpleComboBox<String> sessions) {
    	initLayout(sessions);
    }

    private void initLayout(SimpleComboBox<String> sessions) {
        setHeading("Cadence Details");
        setLabelWidth(100);

        add(startDate);
        startDate.setFieldLabel("Start Date");
        startDate.setFormatValue(true);
        startDate.getPropertyEditor().setFormat(DateTimeFormat.getFormat("yyyy-MM-dd"));
        
        add(endDate);
        endDate.setFieldLabel("End Date");
        endDate.setFormatValue(true);
        endDate.getPropertyEditor().setFormat(DateTimeFormat.getFormat("yyyy-MM-dd"));
        
        add(repeats);
        repeats.setFieldLabel("Count");
        repeats.setAllowDecimals(false);
        repeats.setAllowNegative(false);
        
        add(intervals);
        intervals.setFieldLabel("Intervals");
        
        add(fullSize);
        fullSize.setFieldLabel("Full Size");
        
        sessions.addSelectionChangedListener(new SelectionChangedListener<SimpleComboValue<String>>(){
        	@Override
			public void selectionChanged(SelectionChangedEvent<SimpleComboValue<String>> se) {
        		String s_name = se.getSelectedItem().getValue();
        		String s_id = selectedSessions.get(s_name).toString();
        		JSONRequest.get("/sessions/cadences/"+ s_id, new JSONCallbackAdapter() {
        			public void onSuccess(JSONObject json) {
        				Cadence cad = Cadence.parseJSON(json);
        				startDate.setValue(cad.getStartDate());
        				endDate.setValue(cad.getEndDate());
        				repeats.setValue(cad.getRepeats());
        				intervals.setValue(cad.getIntervals());
        				fullSize.setValue(cad.getFullSize());
        			}
        		});
			}
        });
    }

    public void setSessionSelection(Map<String, Integer> selectedSessions) {
    	this.selectedSessions = selectedSessions;
    }
    
    private Map<String, Integer> selectedSessions = new HashMap<String, Integer>();
    private final DateField         startDate = new DateField();
    private final DateField         endDate   = new DateField();
    private final NumberField       repeats   = new NumberField();
    private final TextField<String> intervals = new TextField<String>();
    private final TextField<String> fullSize  = new TextField<String>();
}
