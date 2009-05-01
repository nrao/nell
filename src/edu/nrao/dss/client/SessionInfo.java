package edu.nrao.dss.client;

import java.util.Map;

import com.extjs.gxt.ui.client.Style.Orientation;
import com.extjs.gxt.ui.client.util.Margins;
import com.extjs.gxt.ui.client.widget.LayoutContainer;
import com.extjs.gxt.ui.client.widget.layout.RowData;
import com.extjs.gxt.ui.client.widget.layout.RowLayout;
import com.google.gwt.core.client.GWT;

/** Display session and cadence details on the overview calendar page. */
class SessionInfo extends LayoutContainer {
    public SessionInfo(SemesterCalendar cal) {
        cadence = new CadenceDetails(cal, details.getSessions());
        window  = cal.getWindowDetails();
        initLayout();
    }

    private void initLayout() {
        setLayout(new RowLayout(Orientation.HORIZONTAL));

        add(details, new RowData(0.25, 1.0, new Margins(10)));
        add(cadence, new RowData(0.25, 1.0, new Margins(10)));
        add(window,  new RowData(0.5,  1.0, new Margins(10)));
    }

    public void loadSessions(Map<String, Integer> selected){
    	details.setSessionSelection(selected);
    	cadence.setSessionSelection(selected);
    }

    private final SessionDetails details   = new SessionDetails();
    private final CadenceDetails cadence;
    private final WindowDetails  window;
}
