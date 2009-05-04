package edu.nrao.dss.client;

import java.util.HashMap;
import java.util.List;

import com.extjs.gxt.ui.client.Events;
import com.extjs.gxt.ui.client.data.BaseModelData;
import com.extjs.gxt.ui.client.event.ComponentEvent;
import com.extjs.gxt.ui.client.event.SelectionListener;
import com.extjs.gxt.ui.client.widget.LayoutContainer;
import com.extjs.gxt.ui.client.widget.TabItem;
import com.extjs.gxt.ui.client.widget.TabPanel;
import com.extjs.gxt.ui.client.widget.Viewport;
import com.extjs.gxt.ui.client.widget.grid.EditorGrid;
import com.extjs.gxt.ui.client.widget.layout.FitLayout;
import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.RootPanel;

public class Scheduler extends Viewport implements EntryPoint {
    public void onModuleLoad() {
        RootPanel.get().add(this);
        initLayout();
    }

    private void initLayout() {
        setLayout(new FitLayout());
        add(tabPanel);

        addTab(se, "Session Explorer", "Define and edit sessions.");

        // TBF: Comment to disable SemesterCalendar due to lack of canvas support in gwt-linux :(
        addTab(sc, "Semester Calendar", "Schedule windowed, fixed, and maintenance sessions.");
    }

    private void addTab(LayoutContainer container, String title, String toolTip) {
        TabItem item = new TabItem(title);
        item.getHeader().setToolTip(toolTip);
        item.setLayout(new FitLayout());
        tabPanel.add(item);

        if (container != null) {
            item.add(container);
        }
        if (title == "Semester Calendar"){
        	item.addListener(Events.Select, new SelectionListener<ComponentEvent>() {
        		@Override
    			public void componentSelected(ComponentEvent ce) {
    				final HashMap<String, Integer> selectedSessions = new HashMap<String, Integer>();
    				JSONRequest.get("/sessions/selected", new JSONCallbackAdapter() {
    					public void onSuccess(JSONObject json){
    						JSONArray sessions = json.get("sessions").isArray();
    						for (int i = 0; i < sessions.size(); ++i){
    							JSONObject s = sessions.get(i).isObject();
            					selectedSessions.put(s.get("name").isString().toString().toString().replace('"', ' ').trim()
            							           , (Integer) (int) s.get("id").isNumber().doubleValue());
    						}
    						sc.loadSelectedSessions(selectedSessions);
    					}
    				});
    			}
        	});
        }
        
    }

    private final TabPanel tabPanel = new TabPanel();
    private SessionExplorer se = new SessionExplorer();
    private SemesterCalendar sc = new SemesterCalendar();
}
