package edu.nrao.dss.client;

import com.extjs.gxt.ui.client.widget.form.FormPanel;
import com.extjs.gxt.ui.client.widget.form.TextField;

public class WindowDetails extends FormPanel{
	
	public WindowDetails() {
		initLayout();
	}
	
	public void showWindowDetails(Window widow) {
	}
	
	private void initLayout() {
		setHeading("Window Details");
		
		add(project);
		project.setFieldLabel("Project");
		project.setReadOnly(true);
		
		add(session);
		session.setFieldLabel("Session");
		session.setReadOnly(true);
		
		add(type);
		type.setFieldLabel("Type");
		type.setReadOnly(true);
		
		add(observing);
		observing.setFieldLabel("Science");
		observing.setReadOnly(true);
		
		add(receivers);
		receivers.setFieldLabel("Receiver(s)");
		receivers.setReadOnly(true);
		
		add(frequency);
		frequency.setFieldLabel("Frequency (GHz)");
		frequency.setReadOnly(true);
		
		add(lst);
		lst.setFieldLabel("LST");
		lst.setReadOnly(true);
		
		add(start);
		start.setFieldLabel("Start Time");
		start.setReadOnly(true);
		
		add(duration);
		duration.setFieldLabel("Duration");
		duration.setReadOnly(true);
		
	}
	
	private final TextField<String> project   = new TextField<String>();
	private final TextField<String> session   = new TextField<String>();
	private final TextField<String> type      = new TextField<String>();
	private final TextField<String> observing = new TextField<String>();
	private final TextField<String> receivers = new TextField<String>();
    private final TextField<String> frequency = new TextField<String>();
    private final TextField<String> lst       = new TextField<String>();
    private final TextField<String> start     = new TextField<String>();
    private final TextField<String> duration  = new TextField<String>();
}
