package edu.nrao.dss.client.view;

import edu.nrao.dss.client.SessionExplorer;

import java.util.ArrayList;

import com.extjs.gxt.ui.client.data.ModelData;
import com.extjs.gxt.ui.client.event.ComponentEvent;
import com.extjs.gxt.ui.client.event.SelectionListener;
import com.extjs.gxt.ui.client.widget.Dialog;
import com.extjs.gxt.ui.client.widget.button.Button;

public class UndefaultedValuesDialog extends Dialog {
    public UndefaultedValuesDialog(final SessionExplorer sx, ArrayList<String> undefaulted,
    		                       final ModelData model,final ArrayList<String> keys, final ArrayList<String> values) {
		
		// Configure the context for the dialog
		//setHeading(row.getName());
		String last = undefaulted.remove(undefaulted.size() - 1);
    	String text = "The defaulted value in ";
    	if (!undefaulted.isEmpty()) {
			for ( String u : undefaulted){
		        text += u + ", ";
			}
    		text += " and ";
    	}
    	text += last + " has been modified, is this what is intended?";
    	addText(text);
		setButtons(Dialog.YESNO);
		setHeight(200);
		setWidth(350);

		show();

		// They want to re-check the fields' values.
		Button cancel = getButtonById(Dialog.NO);
		cancel.addSelectionListener(new SelectionListener<ComponentEvent>() {
			@Override
			public void componentSelected(ComponentEvent ce) {
				close();
			}
		});

		// Go ahead and save the values
		Button ok = getButtonById(Dialog.YES);
		ok.addSelectionListener(new SelectionListener<ComponentEvent>() {
			@Override
			public void componentSelected(ComponentEvent ce) {
				sx.saveModel(model, keys, values);
				close();
			}
		});
	}
}
