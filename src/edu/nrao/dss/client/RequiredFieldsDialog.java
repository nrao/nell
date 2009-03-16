package edu.nrao.dss.client;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Set;

import com.extjs.gxt.ui.client.event.ComponentEvent;
import com.extjs.gxt.ui.client.event.SelectionListener;
import com.extjs.gxt.ui.client.widget.Dialog;
import com.extjs.gxt.ui.client.widget.button.Button;
import com.extjs.gxt.ui.client.widget.form.Field;
import com.extjs.gxt.ui.client.widget.form.FormPanel;
import com.extjs.gxt.ui.client.widget.form.TextField;

public class RequiredFieldsDialog extends Dialog {
	
	@SuppressWarnings("unchecked")
	public RequiredFieldsDialog(final String sType,
			                     Set<String> requiredFields,
			                     final HashMap<String, Object> sFields,
			                     final SessionExplorer sx) {
		setHeading(sType);
		addText("Please enter the required fields.");
		setButtons(Dialog.OKCANCEL);
		setHeight(200);
		setWidth(400);

		FormPanel fp = new FormPanel();

		final ArrayList<Field> formFields = new ArrayList<Field>();
		for (String rf : requiredFields) {
			// TBF need to make this data type sensitive
			TextField<String> f = new TextField<String>();
			f.setFieldLabel(rf);
			f.setEmptyText(rf);
			f.setAllowBlank(false);
			f.setMinLength(4);
			fp.add(f);
			formFields.add(f);
		}

		add(fp);
		show();

		Button cancel = getButtonById(Dialog.CANCEL);
		cancel.addSelectionListener(new SelectionListener<ComponentEvent>() {
			@Override
			public void componentSelected(ComponentEvent ce) {
				close();
			}
		});

		Button ok = getButtonById(Dialog.OK);
		ok.addSelectionListener(new SelectionListener<ComponentEvent>() {
			@Override
			public void componentSelected(ComponentEvent ce) {
				HashMap<String, Object> sFieldsP = sx.populateSessionFields(
						sFields, formFields);
				sx.createNewSessionRow(sType, sFieldsP);
				close();
			}
		});
	}
}
