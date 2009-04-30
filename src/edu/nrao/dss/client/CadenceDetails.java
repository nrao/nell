package edu.nrao.dss.client;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

import com.extjs.gxt.ui.client.event.ComponentEvent;
import com.extjs.gxt.ui.client.event.SelectionChangedEvent;
import com.extjs.gxt.ui.client.event.SelectionChangedListener;
import com.extjs.gxt.ui.client.event.SelectionListener;
import com.extjs.gxt.ui.client.widget.button.Button;
import com.extjs.gxt.ui.client.widget.form.DateField;
import com.extjs.gxt.ui.client.widget.form.FormPanel;
import com.extjs.gxt.ui.client.widget.form.NumberField;
import com.extjs.gxt.ui.client.widget.form.SimpleComboBox;
import com.extjs.gxt.ui.client.widget.form.SimpleComboValue;
import com.extjs.gxt.ui.client.widget.form.TextField;
import com.google.gwt.i18n.client.DateTimeFormat;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.user.client.Window;

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
        		selectedSession_id = selectedSessions.get(s_name).toString();
        		JSONRequest.get("/sessions/"+ selectedSession_id + "/cadences", new JSONCallbackAdapter() {
        			public void onSuccess(JSONObject json) {
        				Cadence cad = Cadence.parseJSON(json);
        				if (cad == null) {
        					create = true;
        					startDate.reset();
        					endDate.reset();
        					repeats.reset();
        					intervals.reset();
        					fullSize.reset();
        				} else {
        					create = false;
	        				startDate.setValue(cad.getStartDate());
	        				endDate.setValue(cad.getEndDate());
	        				repeats.setValue(cad.getRepeats());
	        				intervals.setValue(cad.getIntervals());
	        				fullSize.setValue(cad.getFullSize());
        				}
        			}
        		});
			}
        });

        Button apply = new Button("Apply", new SelectionListener<ComponentEvent>() {
        	public void componentSelected(ComponentEvent event) {

        		// Possible keys and values
        		String[] pkeys = {"start_date", "end_date", "repeats", "intervals", "full_size"};
        		// Handling the null case for repeats
        		String r_str = null;
        		Number r_value = repeats.getValue();
        		if (r_value != null){
        			r_str = ((Double)r_value.doubleValue()).toString();	
        		}
                String[] pvalues = {safeFormatDate(startDate.getValue())
		                          , safeFormatDate(endDate.getValue())
		                          , r_str
		                          , intervals.getValue()
		                          , fullSize.getValue()};
                
                // Populate actual (non-null) keys and values
        		ArrayList<String> keys   = new ArrayList<String>();
        		ArrayList<String> values = new ArrayList<String>();
                for (int i = 0; i< pkeys.length; ++i) {
                	if (pvalues[i] != null) {
                		keys.add(pkeys[i]);
                		values.add(pvalues[i]);
                	}
                }
                
				if (!create) {
					keys.add("_method");
					values.add("put");
				}
				
        		JSONRequest.post("/sessions/" + selectedSession_id + "/cadences"
        				       , keys.toArray(new String[]{})
        				       , values.toArray(new String[]{})
        				       , null);
        	}
        });
        add(apply);
    }

    private String safeFormatDate(Date date){
    	if (date == null){
    		return null;
    	}
    	DateTimeFormat fmt = DateTimeFormat.getFormat("MM/dd/yyyy");
		return fmt.format(date);
    }
    
    public void setSessionSelection(HashMap<String, Integer> selectedSessions) {
    	this.selectedSessions = selectedSessions;
    }

    private String                 selectedSession_id = new String();
    private boolean                            create = false;
    private HashMap<String, Integer> selectedSessions = new HashMap<String, Integer>();
    private final DateField                 startDate = new DateField();
    private final DateField                 endDate   = new DateField();
    private final NumberField               repeats   = new NumberField();
    private final TextField<String>         intervals = new TextField<String>();
    private final TextField<String>         fullSize  = new TextField<String>();
}
