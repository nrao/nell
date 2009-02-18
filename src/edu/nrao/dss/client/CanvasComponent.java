package edu.nrao.dss.client;

import java.util.ArrayList;

import com.extjs.gxt.ui.client.widget.WidgetComponent;
import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.user.client.ui.FocusPanel;
import com.google.gwt.user.client.ui.MouseListener;
import com.google.gwt.widgetideas.graphics.client.Color;
import com.google.gwt.widgetideas.graphics.client.GWTCanvas;

interface CanvasClient {
    public void onPaint(GWTCanvas canvas);
}

class CanvasComponent extends WidgetComponent {
    public CanvasComponent(int width, int height) {
        super(new FocusPanel());

        panel  = (FocusPanel) getWidget();
        canvas = new GWTCanvas(width, height);
        panel.add(canvas);
    }

    public void addClient(CanvasClient client) {
        clients.add(client);
    }

    public void removeClient(CanvasClient client) {
        clients.remove(client);
    }

    public void draw() {
        saveContext();
        eraseBackground(canvas);
        paint(canvas);
        restoreContext();
    }

    public void eraseBackground(GWTCanvas canvas) {
        canvas.clear();
    }

    public void paint(GWTCanvas canvas) {
        for (CanvasClient client : clients) {
            client.onPaint(canvas);
        }
    }

    public native void clip() /*-{
        var context = this.@edu.nrao.dss.client.CanvasComponent::getContext()();
        context.clip();
    }-*/;

    public native JavaScriptObject getContext() /*-{
        var canvas  = this.@edu.nrao.dss.client.CanvasComponent::canvas;
        var impl    = canvas.@com.google.gwt.widgetideas.graphics.client.GWTCanvas::impl;
        return impl.@com.google.gwt.widgetideas.graphics.client.impl.GWTCanvasImplDefault::canvasContext;
    }-*/;

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

    public void translate(int x, int y) {
        getCanvas().translate(x, y);
    }

    public void addMouseListener(MouseListener listener) {
        panel.addMouseListener(listener);
    }

    public GWTCanvas getCanvas() {
        return canvas;
    }

    private ArrayList<CanvasClient> clients = new ArrayList<CanvasClient>();

    private final FocusPanel panel;
    private final GWTCanvas  canvas;
}
