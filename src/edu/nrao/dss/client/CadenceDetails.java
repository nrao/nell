package edu.nrao.dss.client;

import com.extjs.gxt.ui.client.widget.form.DateField;
import com.extjs.gxt.ui.client.widget.form.FormPanel;
import com.extjs.gxt.ui.client.widget.form.NumberField;
import com.extjs.gxt.ui.client.widget.form.TextField;
import com.google.gwt.i18n.client.DateTimeFormat;

class CadenceDetails extends FormPanel {
    public CadenceDetails() {
        initLayout();
    }

    private void initLayout() {
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
        
        add(count);
        count.setFieldLabel("Count");
        count.setAllowDecimals(false);
        count.setAllowNegative(false);
        
        add(intervals);
        intervals.setFieldLabel("Intervals");
    }

    private final DateField         startDate = new DateField();
    private final DateField         endDate   = new DateField();
    private final NumberField       count     = new NumberField();
    private final TextField<String> intervals = new TextField<String>();
}
