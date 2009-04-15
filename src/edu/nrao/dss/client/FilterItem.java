package edu.nrao.dss.client;

import com.extjs.gxt.ui.client.event.ComponentEvent;
import com.extjs.gxt.ui.client.event.KeyListener;
import com.extjs.gxt.ui.client.widget.form.TextField;
import com.extjs.gxt.ui.client.widget.toolbar.AdapterToolItem;
import com.google.gwt.user.client.Window;

public class FilterItem extends AdapterToolItem {
	@SuppressWarnings("unchecked")
	public FilterItem(final SessionExplorer sx) {
		super(new TextField<String>());
		textField = (TextField<String>) getWidget();
		setTitle("Display sessions containing ...");
		defineListener(sx);
	}
	
	private void defineListener(final SessionExplorer sx) {
		textField.addKeyListener(new KeyListener() {
			@Override
			public void componentKeyPress(ComponentEvent e) {
				/*
				// Note: entry does NOT hold the current key stroke
				String entry = textField.getValue();
				if (entry == null) {
					entry = "";
				}
				
				// Handle the newly added character and possible backspaces
				String filter;
				int keycode = e.getKeyCode();
				int entry_length = entry.length();
				if (32 <= keycode && keycode <= 137) {
					String suffix = Character.toString((char) keycode);
					filter = entry + suffix;
				} else if (keycode == 8 && entry_length > 0) {
					filter = entry.substring(0, entry.length() - 1);
				} else {
					filter = entry;
				}
				*/
				//System.out.print(e.getKeyCode());
				if (e.getKeyCode() == 13) {
					sx.filterSessions(textField.getValue());
				}
				//focus();
				
			}
		});
	}
	
	private final TextField<String> textField;

}
