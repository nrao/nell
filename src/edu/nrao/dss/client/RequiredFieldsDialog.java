package edu.nrao.dss.client;

import java.util.ArrayList;
import java.util.HashMap;

import com.extjs.gxt.ui.client.event.ComponentEvent;
import com.extjs.gxt.ui.client.event.SelectionListener;
import com.extjs.gxt.ui.client.widget.Dialog;
import com.extjs.gxt.ui.client.widget.button.Button;
import com.extjs.gxt.ui.client.widget.form.Field;
import com.extjs.gxt.ui.client.widget.form.FormPanel;

class RequiredFieldsDialog extends Dialog {
	@SuppressWarnings("unchecked")
    public RequiredFieldsDialog(final SessionExplorer sx, final RowType row) {
		setHeading(row.getName());
		addText("Please enter the required fields.");
		setButtons(Dialog.OKCANCEL);
		setHeight(400);
		setWidth(350);

		FormPanel fp = new FormPanel();

		final ArrayList<Field> formFields = new ArrayList<Field>();
		for (String rf : row.getRequiredFields()) {
			Field f = row.getField(rf);
			fp.add(f);
			formFields.add(f);
			//Window.alert(f.getValue());
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
				HashMap<String, Object> sFieldsP =
				    sx.populateSessionFields(row.getRequiredFields(), formFields);
				sx.createNewSessionRow(row, sFieldsP);
				close();
			}
		});
	}
}
