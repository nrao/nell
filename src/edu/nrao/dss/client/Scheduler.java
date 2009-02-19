package edu.nrao.dss.client;

import com.extjs.gxt.ui.client.widget.LayoutContainer;
import com.extjs.gxt.ui.client.widget.TabItem;
import com.extjs.gxt.ui.client.widget.TabPanel;
import com.extjs.gxt.ui.client.widget.Viewport;
import com.extjs.gxt.ui.client.widget.layout.FitLayout;
import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.user.client.ui.RootPanel;

public class Scheduler extends Viewport implements EntryPoint {
    public void onModuleLoad() {
        RootPanel.get().add(this);
        initLayout();
    }

    private void initLayout() {
        setLayout(new FitLayout());
        add(tabPanel);

        addTab(new SessionExplorer(), "Session Explorer", "Define and edit sessions.");
        
        // TBF: Comment to disable SemesterCalendar due to lack of canvas support in gwt-linux :(
        addTab(new SemesterCalendar(), "Semester Calendar", "Schedule windowed, fixed, and maintenance sessions.");
    }

    private void addTab(LayoutContainer container, String title, String toolTip) {
        TabItem item = new TabItem(title);
        item.getHeader().setToolTip(toolTip);
        item.setLayout(new FitLayout());
        tabPanel.add(item);

        if (container != null) {
            item.add(container);
        }
    }

    private final TabPanel tabPanel = new TabPanel();
}
