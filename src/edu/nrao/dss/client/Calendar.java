package edu.nrao.dss.client;

import com.google.gwt.widgetideas.graphics.client.Color;

class Calendar extends CanvasComponent {
    public Calendar() {
        super(WIDTH, HEIGHT);
    }

    public void draw() {
		eraseBackground();
		drawGrid();
	}

    public int positionToHour(int y) {
		return y / HOUR_HEIGHT;
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

    public void restoreContext() {
		getCanvas().restoreContext();
	}

    public void saveContext() {
		getCanvas().saveContext();
	}

    public void setFillStyle(Color color) {
		getCanvas().setFillStyle(color);
	}

    public void setLineWidth(double width) {
		getCanvas().setLineWidth(width);
	}

    public void setStrokeStyle(Color color) {
		getCanvas().setStrokeStyle(color);
	}

    public void strokeRect(int startHour, int startDay, int numHours, int numDays) {
		getCanvas().strokeRect(startDay*DAY_WIDTH, startHour*HOUR_HEIGHT, numDays*DAY_WIDTH, numHours*HOUR_HEIGHT);
	}

    public void translate(int x, int y) {
		getCanvas().translate(x, y);
	}

    private void eraseBackground() {
		getCanvas().clear();
	}

    private void drawGrid() {
		getCanvas().setLineWidth(1);
		getCanvas().setStrokeStyle(Color.BLACK);
		getCanvas().strokeRect(0, 0, WIDTH, HEIGHT);

		getCanvas().beginPath();
        for (int j = 1; j < NUM_DAYS; ++j) {
            int x = DAY_WIDTH*j;
            getCanvas().moveTo(x, 0);
            getCanvas().lineTo(x, HEIGHT);
        }
		for (int i = 1; i < NUM_HOURS; ++i) {
			int y = HOUR_HEIGHT*i;
			getCanvas().moveTo(0, y);
			getCanvas().lineTo(WIDTH, y);
		}
		getCanvas().stroke();

		getCanvas().setLineWidth(2);
		getCanvas().setStrokeStyle(Color.BLUE);
		int y1 = 314;
		int y2 = y1 - minutesToPixels(4*NUM_DAYS);
		getCanvas().beginPath();
		getCanvas().moveTo(0, y1);
		getCanvas().lineTo(WIDTH, y2);
		getCanvas().stroke();
	}

    private static final int HOUR_HEIGHT = 12;
    private static final int NUM_HOURS   = 24;
    private static final int DAY_WIDTH   = 12;
    private static final int NUM_DAYS    = 120;

    private static final int WIDTH  = NUM_DAYS  * DAY_WIDTH;
    private static final int HEIGHT = NUM_HOURS * HOUR_HEIGHT;
}
