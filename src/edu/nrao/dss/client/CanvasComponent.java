package edu.nrao.dss.client;

import com.extjs.gxt.ui.client.widget.WidgetComponent;
import com.google.gwt.user.client.ui.FocusPanel;
import com.google.gwt.user.client.ui.MouseListener;
import com.google.gwt.widgetideas.graphics.client.GWTCanvas;

class CanvasComponent extends WidgetComponent {
    public CanvasComponent(int width, int height) {
        super(new FocusPanel());

        panel  = (FocusPanel) getWidget();
        canvas = new GWTCanvas(width, height);
        panel.add(canvas);
    }

    public GWTCanvas getCanvas() {
        return canvas;
    }

    public void addMouseListener(MouseListener listener) {
        panel.addMouseListener(listener);
    }

    private final FocusPanel panel;
    private final GWTCanvas  canvas;
}
