package edu.nrao.dss.client;

import com.extjs.gxt.ui.client.widget.form.TextField;
import com.extjs.gxt.ui.client.widget.toolbar.AdapterToolItem;

public class FilterItem extends AdapterToolItem {
	@SuppressWarnings("unchecked")
	public FilterItem(final SessionExplorer sx) {
		super(new TextField<String>());
		textField = (TextField<String>) getWidget();
		//setTitle("Filter");
		setTitle("Display sessions containing ...");
	}
	
	private void defineListeners() {
		//textField.addListener(new )
	}
	
	private final TextField<String> textField;

}
