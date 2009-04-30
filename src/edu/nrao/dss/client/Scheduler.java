package edu.nrao.dss.client;

import com.extjs.gxt.ui.client.Events;
import com.extjs.gxt.ui.client.event.ComponentEvent;
import com.extjs.gxt.ui.client.event.SelectionListener;
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

        addTab(se, "Session Explorer", "Define and edit sessions.");
        addTab(sc, "Semester Calendar", "Schedule windowed, fixed, and maintenance sessions.")
        .addListener(Events.Select, new SelectionListener<ComponentEvent>() {
            @Override
            public void componentSelected(ComponentEvent ce) {
                sc.load();
            }
        });
    }

    private TabItem addTab(LayoutContainer container, String title, String toolTip) {
        TabItem item = new TabItem(title);
        tabPanel.add(item);

        item.add(container);
        item.getHeader().setToolTip(toolTip);
        item.setLayout(new FitLayout());

        return item;
    }

    private final TabPanel         tabPanel = new TabPanel();
    private final SessionExplorer  se       = new SessionExplorer();
    private final SemesterCalendar sc       = new SemesterCalendar();
}
