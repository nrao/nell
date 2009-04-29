package edu.nrao.dss.client;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;

import com.extjs.gxt.ui.client.Style.Orientation;
import com.extjs.gxt.ui.client.Style.Scroll;
import com.extjs.gxt.ui.client.data.BaseModelData;
import com.extjs.gxt.ui.client.widget.LayoutContainer;
import com.extjs.gxt.ui.client.widget.Text;
import com.extjs.gxt.ui.client.widget.layout.CenterLayout;
import com.extjs.gxt.ui.client.widget.layout.RowData;
import com.extjs.gxt.ui.client.widget.layout.RowLayout;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.MouseListenerAdapter;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.widgetideas.graphics.client.GWTCanvas;

class SemesterCalendar extends LayoutContainer implements CanvasClient {
    public SemesterCalendar() {
        initLayout();
    }

    private void initLayout() {
        setLayout(new RowLayout(Orientation.VERTICAL));
        setScrollMode(Scroll.AUTO);

        LayoutContainer top = new LayoutContainer();
        add(top, new RowData(-1.0, 1.5 * Calendar.HEIGHT));
        top.setLayout(new CenterLayout());
        //top.add(calendar);

        add(info, new RowData(-1.0, 300));

        addListeners();

        Timer timer = new Timer() {
            public void run() {
                if (++blinkCount % 10 == 0) {
                    blinkOn = ! blinkOn;
                }
                draw(blinkOn);
            }

            private int     blinkCount = 0;
            private boolean blinkOn    = true;
        };
        if (animated) {
            timer.scheduleRepeating(1000 / 10);
        }

        //loadData();
        draw(true);
    }
    
    public void loadSelectedSessions(HashMap<String, Integer> selected){
    	info.loadSessions(selected);
    }

    private void addListeners() {
//        calendar.addClient(this);
//
//        calendar.addMouseListener(new MouseListenerAdapter() {
//            public void onMouseDown(Widget sender, int x, int y) {
//                dragTarget = hitTestAllocation(x, y);
//                if (dragTarget != null) {
//                    dragStartX   = x;
//                    dragStartDay = calendar.pixelsToDays(x);
//                }
//            }
//
//            public void onMouseUp(Widget sender, int x, int y) {
//                if (dragTarget != null) {
//                    int deltaDays = calendar.pixelsToDays(x) - dragStartDay;
//                    dragTarget.setStartDay(dragTarget.getStartDay() + deltaDays);
//                    sortSessions();
//                }
//
//                dragTarget = null;
//            }
//
//            public void onMouseMove(Widget sender, int x, int y) {
//                mouseX = x;
//                mouseY = y;
//
//                current = dragTarget;
//                if (current == null) {
//                    current = findCurrentAllocation();
//                }
//
//                if (! animated) {
//                    draw(true);
//                }
//            }
//        });
    }

    private void draw(boolean showConflicts) {
//        this.showConflicts = showConflicts;
//        calendar.draw();
//        this.showConflicts = false;
    }

    public void onPaint(GWTCanvas canvas) {
//        for (Session a : sessions) {
//            if (! showConflicts && problems != null && problems.contains(a)) { continue; }
//            if (a != dragTarget && a != current) {
//                a.setAlpha(0.6f);
//                a.draw(calendar);
//            }
//        }
//
//        if (dragTarget != null) {
//            dragTarget.setAlpha(1.0f);
//            calendar.saveContext();
//            calendar.translate(mouseX - dragStartX, 0);
//            dragTarget.draw(calendar);
//            calendar.restoreContext();
//        } else if (current != null) {
//            current.setAlpha(1.0f);
//            current.draw(calendar);
//        }
    }

    private Session findCurrentAllocation() {
        return hitTestAllocation(mouseX, mouseY);
    }

    private Session hitTestAllocation(int x, int y) {
//        int day  = calendar.positionToDay(x);
//        int hour = calendar.positionToHour(y);
//
        Session result = null;
//        for (Session a : sessions) {
//            if (a.contains(day, hour)) {
//                result = a;
//            }
//        }
//
        return result;
    }

    /** Fetch the calendar data from the server. */
//    private void loadData() {
//        JSONRequest.get("/gen_opportunities", new JSONCallbackAdapter() {
//            @Override
//            public void onSuccess(JSONObject json) {
//                List<Session> allocs = Session.parseJSON(json);
//                sessions = new ArrayList<Session>();
//                for (int i = 0; i < 200; ++i) {
//                    sessions.add(allocs.get(i));
//                }
//                sortSessions();
//
//                ArrayList<Project> projects = new ArrayList<Project>();
//                for (Session a : sessions) {
//                    projects.add(new Project("dummy", Arrays.asList(new Session[]{a})));
//                }
//                Project.allocateColors(projects);
//                draw(false);
//            }
//        });
//    }

    /** Sort sessions chronologically, so they can be drawn such the everything is visible. */
    @SuppressWarnings("unchecked")
    private void sortSessions() {
        Collections.sort(sessions);
        problems = sudoku.findProblem(sessions);
    }

    //private final Calendar    calendar = new Calendar();
    private final SessionInfo info     = new SessionInfo();
    private final Sudoku      sudoku   = new Sudoku();

    /** Set to true to enable annoying blinking effects. */
    private final boolean  animated = false;

    private List<Session> sessions = new ArrayList<Session>();
    private List<Session> problems;
    private Session       dragTarget;
    private Session       current;

    private int dragStartX;
    private int dragStartDay;
    private int mouseX;
    private int mouseY;

    private boolean showConflicts = false;
}
