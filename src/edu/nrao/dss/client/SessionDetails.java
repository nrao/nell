package edu.nrao.dss.client;

import com.extjs.gxt.ui.client.widget.form.FormPanel;
import com.extjs.gxt.ui.client.widget.form.SimpleComboBox;
import com.extjs.gxt.ui.client.widget.form.TextField;
import com.extjs.gxt.ui.client.widget.form.ComboBox.TriggerAction;

class SessionDetails extends FormPanel {
    public SessionDetails() {
        initLayout();
    }

    private void initLayout() {
        setHeading("Session Details");
        setLabelWidth(100);
        
        initSessionsList();
        
        add(receivers);
        receivers.setFieldLabel("Receivers");
        receivers.disable();
        
        add(frequency);
        frequency.setFieldLabel("Frequency");
        frequency.disable();
        
        add(lst);
        lst.setFieldLabel("LST");
        lst.disable();
        
        add(observing);
        observing.setFieldLabel("Observing Type");
        observing.disable();
    }

    private void initSessionsList() {
        add(sessions);
        sessions.setFieldLabel("Choose Session");
        sessions.setToolTip("Pick a session from the working set.");
        
        sessions.setTriggerAction(TriggerAction.ALL);
        sessions.add("Dummy #1");
        sessions.add("Dummy #2");
        sessions.add("Dummy #3");
    }

    private final SimpleComboBox<String> sessions  = new SimpleComboBox<String>();
    private final TextField<String>      receivers = new TextField<String>();
    private final TextField<String>      frequency = new TextField<String>();
    private final TextField<String>      lst       = new TextField<String>();
    private final TextField<String>      observing = new TextField<String>();
}
