package edu.nrao.dss.client;

import java.util.HashMap;
import java.util.Map;

import com.extjs.gxt.ui.client.event.SelectionChangedEvent;
import com.extjs.gxt.ui.client.event.SelectionChangedListener;
import com.extjs.gxt.ui.client.widget.form.FormPanel;
import com.extjs.gxt.ui.client.widget.form.SimpleComboBox;
import com.extjs.gxt.ui.client.widget.form.SimpleComboValue;
import com.extjs.gxt.ui.client.widget.form.TextField;
import com.extjs.gxt.ui.client.widget.form.ComboBox.TriggerAction;
import com.google.gwt.json.client.JSONObject;

class SessionDetails extends FormPanel {
    public SessionDetails() {
        initLayout();
    }

    public void setSessionSelection(Map<String, Integer> selectedSessions) {
    	this.selectedSessions = selectedSessions;
    	sessions.removeAll();
    	for (String name : selectedSessions.keySet()) {
    		sessions.add(name);
    	}
    }

    private void initLayout() {
        setHeading("Session Details");
        setLabelWidth(100);
        
        initSessionsList();
        
        add(receivers);
        receivers.setFieldLabel("Receivers");
        receivers.setReadOnly(true);
        
        add(duration);
        duration.setFieldLabel("Period Duration");
        duration.setReadOnly(true);
        
        add(frequency);
        frequency.setFieldLabel("Frequency");
        frequency.setReadOnly(true);
        
        add(lst);
        lst.setFieldLabel("LST");
        lst.setReadOnly(true);
        
        add(observing);
        observing.setFieldLabel("Observing Type");
        observing.setReadOnly(true);
        
        sessions.addSelectionChangedListener(new SelectionChangedListener<SimpleComboValue<String>>(){
        	@Override
			public void selectionChanged(SelectionChangedEvent<SimpleComboValue<String>> se) {
        		String s_name = se.getSelectedItem().getValue();
        		String s_id = selectedSessions.get(s_name).toString();
        		JSONRequest.get("/sessions/"+ s_id, new JSONCallbackAdapter() {
        			public void onSuccess(JSONObject json) {
        				Session sess = Session.parseJSON(json);
        				duration.setValue(sess.getMinDuration());
        				receivers.setValue(sess.getReceivers());
        				frequency.setValue(sess.getFrequency());
        				lst.setValue(sess.getHorizontal());
        				observing.setValue(sess.getScience());
        			}
        		});
			}
        });
    }

    private void initSessionsList() {
        add(sessions);
        sessions.setFieldLabel("Choose Session");
        sessions.setToolTip("Pick a session from the working set select in the Session Explorer.");
        
        sessions.setTriggerAction(TriggerAction.ALL);
    }

    public SimpleComboBox<String> getSessions(){
    	return sessions;
    }
    
    private Map<String, Integer> selectedSessions = new HashMap<String, Integer>();
    private final SimpleComboBox<String> sessions  = new SimpleComboBox<String>();
    private final TextField<String>      duration  = new TextField<String>();
    private final TextField<String>      receivers = new TextField<String>();
    private final TextField<String>      frequency = new TextField<String>();
    private final TextField<String>      lst       = new TextField<String>();
    private final TextField<String>      observing = new TextField<String>();
}
