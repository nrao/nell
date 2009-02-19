package edu.nrao.dss.client;

import com.google.gwt.user.client.ui.MouseListenerAdapter;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.widgetideas.graphics.client.Color;
import com.google.gwt.widgetideas.graphics.client.GWTCanvas;

class Calendar extends CanvasComponent {
    public Calendar() {
        super(WIDTH, 2*HEIGHT);

        addMouseListener(new MouseListenerAdapter() {
            public void onMouseEnter(Widget sender) {
                mouseEnter = true;
            }
            public void onMouseLeave(Widget sender) {
                mouseEnter = false;
            }
            public void onMouseMove(Widget sender, int x, int y) {
                mouseX = x;
                mouseY = y;
            }
        });
    }

    public void paint(GWTCanvas canvas) {
        doPaint(canvas);

        if (mouseEnter) {
            canvas.beginPath();
            canvas.arc(mouseX, mouseY, 160, 0, 2*Math.PI, true);
            clip();
            canvas.scale(2.0, 2.0);
            canvas.translate(-mouseX/2.0, -mouseY/2.0);
            canvas.clear();
            doPaint(canvas);
        }
	}

    private void doPaint(GWTCanvas canvas) {
        canvas.saveContext();

        canvas.translate(0.0, HEIGHT/2.0);
        canvas.beginPath();
        canvas.moveTo(0, 0);
        canvas.lineTo(WIDTH, 0);
        canvas.lineTo(WIDTH, HEIGHT);
        canvas.lineTo(0, HEIGHT);
        canvas.lineTo(0, 0);
        clip();

        drawGrid(canvas);
        super.paint(canvas);

        canvas.restoreContext();
    }

    public int positionToHour(int y) {
		return (y - HEIGHT/2) / HOUR_HEIGHT;
	}

    public int positionToDay(int x) {
		return x / DAY_WIDTH;
	}

    public int minutesToPixels(int minutes) {
		return (minutes * HOUR_HEIGHT) / 60;
	}

    public int pixelsToDays(int pixels) {
		return pixels / DAY_WIDTH;
	}

    public void fillRect(int startDay, int startHour, int numDays, int numHours) {
        if (startHour + numHours > 24) {
            fillRect(startDay, startHour, numDays, 24 - startHour);
            fillRect(startDay+1, 0, numDays, startHour + numHours - 24);
            return;
        }
        getCanvas().fillRect(startDay*DAY_WIDTH, startHour*HOUR_HEIGHT, numDays*DAY_WIDTH, numHours*HOUR_HEIGHT);
	}

    public void strokeRect(int startHour, int startDay, int numHours, int numDays) {
        getCanvas().strokeRect(startDay*DAY_WIDTH, startHour*HOUR_HEIGHT, numDays*DAY_WIDTH, numHours*HOUR_HEIGHT);
    }

    private void drawGrid(GWTCanvas canvas) {
        canvas.setLineWidth(1);
		canvas.setStrokeStyle(Color.BLACK);
        canvas.strokeRect(0, 0, WIDTH, HEIGHT);

		canvas.beginPath();
        for (int j = 1; j < NUM_DAYS; ++j) {
            int x = DAY_WIDTH*j;
            canvas.moveTo(x, 0);
            canvas.lineTo(x, HEIGHT);
        }
		for (int i = 1; i < NUM_HOURS; ++i) {
			int y = HOUR_HEIGHT*i;
			canvas.moveTo(0, y);
			canvas.lineTo(WIDTH, y);
		}
		canvas.stroke();

		canvas.setLineWidth(2);
		canvas.setStrokeStyle(Color.BLUE);
		int y1 = 314;
		int y2 = y1 - minutesToPixels(4*NUM_DAYS);
		canvas.beginPath();
		canvas.moveTo(0, y1);
		canvas.lineTo(WIDTH, y2);
		canvas.stroke();
	}

    boolean mouseEnter = false;
    int     mouseX;
    int     mouseY;

    private static final int HOUR_HEIGHT = 12;
    private static final int NUM_HOURS   = 24;
    private static final int DAY_WIDTH   = 12;
    private static final int NUM_DAYS    = 120;

    public static final int WIDTH  = NUM_DAYS  * DAY_WIDTH;
    public static final int HEIGHT = NUM_HOURS * HOUR_HEIGHT;
}
