package edu.nrao.dss.client;

import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Set;

import com.extjs.gxt.ui.client.Style.Scroll;
import com.extjs.gxt.ui.client.widget.LayoutContainer;
import com.extjs.gxt.ui.client.widget.Text;
import com.extjs.gxt.ui.client.widget.layout.CenterLayout;
import com.extjs.gxt.ui.client.widget.layout.RowData;
import com.extjs.gxt.ui.client.widget.layout.RowLayout;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.MouseListenerAdapter;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.widgetideas.graphics.client.GWTCanvas;

class SemesterCalendar extends LayoutContainer implements CanvasClient {
    public SemesterCalendar() {
        initLayout();
    }

    private void initLayout() {
        setLayout(new RowLayout());
        setScrollMode(Scroll.AUTO);
        
        LayoutContainer top = new LayoutContainer();
        add(top, new RowData(-1.0, 1.0));
        top.setLayout(new CenterLayout());
        top.add(calendar);

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

        generateTestData();
        draw(true);
    }

    private void addListeners() {
        calendar.addClient(this);

        calendar.addMouseListener(new MouseListenerAdapter() {
            public void onMouseDown(Widget sender, int x, int y) {
                dragTarget = hitTestAllocation(x, y);
                if (dragTarget != null) {
                    dragStartX   = x;
                    dragStartDay = dragTarget.getStartDay();
                }
            }

            public void onMouseUp(Widget sender, int x, int y) {
                if (dragTarget != null) {
                    dragTarget.setStartDay(dragStartDay + calendar.pixelsToDays(x - dragStartX));
                    sortAllocations();
                }

                dragTarget = null;
            }

            public void onMouseMove(Widget sender, int x, int y) {
                mouseX = x;
                mouseY = y;

                current = dragTarget;
                if (current == null) {
                    current = findCurrentAllocation();
                }
                label.setText(current != null ? current.getInfoText() : "");

                if (! animated) {
                    draw(true);
                }
            }
        });
    }

    private void draw(boolean showConflicts) {
        this.showConflicts = showConflicts;
        calendar.draw();
        this.showConflicts = false;
    }

    public void onPaint(GWTCanvas canvas) {
        // If there is a drag target or current allocation, only blink its conflicts.
        Set<Session> conflicts = null;
        if (dragTarget != null) {
            dragTarget.setStartDay(dragStartDay + calendar.pixelsToDays(mouseX - dragStartX));
            conflicts = sudoku.conflictsWith(dragTarget, allocations);
            dragTarget.setStartDay(dragStartDay);
        } else if (current != null) {
            conflicts = sudoku.conflictsWith(current, allocations);
            if (conflicts.isEmpty()) {
                conflicts = sudoku.findConflicts(allocations);
            }
        } else {
            conflicts = sudoku.findConflicts(allocations);
        }

        for (Session a : allocations) {
            if (! showConflicts && conflicts.contains(a)) { continue; }
            if (a != dragTarget && a != current) {
                a.setAlpha(0.6f);
                a.draw(calendar);
            }
        }

        if (dragTarget != null) {
            dragTarget.setAlpha(1.0f);
            calendar.saveContext();
            calendar.translate(mouseX - dragStartX, 0);
            dragTarget.draw(calendar);
            calendar.restoreContext();
        } else if (current != null) {
            current.setAlpha(1.0f);
            current.draw(calendar);
        }
    }

    private Session findCurrentAllocation() {
        return hitTestAllocation(mouseX, mouseY);
    }

    private Session hitTestAllocation(int x, int y) {
        int day  = calendar.positionToDay(x);
        int hour = calendar.positionToHour(y);

        Session result = null;
        for (Session a : allocations) {
            if (a.contains(day, hour)) {
                result = a;
            }
        }

        return result;
    }

    private void generateTestData() {
        TestData data = new TestData();
        projects    = data.getProjects();
        allocations = Project.collectAllocations(projects);
        
        sortAllocations();
        
        Project.allocateColors(projects);
    }

    private void sortAllocations() {
        Collections.sort(allocations, new Comparator<Session>() {
            public int compare(Session lhs, Session rhs) {
                if (lhs.getStartHour() < rhs.getStartHour()) {
                    return -1;
                }
                if (rhs.getStartHour() < lhs.getStartHour()) {
                    return +1;
                }
                return 0;
            }
        });
    }

    private final Calendar calendar = new Calendar();
    private final Text     label    = new Text();
    private final Sudoku   sudoku   = new Sudoku();

    /** Set to true to enable annoying blinking effects. */
    private final boolean  animated = false;

    private List<Project> projects;
    private List<Session> allocations;
    private Session       dragTarget;
    private Session       current;

    private int dragStartX;
    private int dragStartDay;
    private int mouseX;
    private int mouseY;
    
    private boolean showConflicts = false;
}
