package edu.nrao.dss.client;

import com.google.gwt.widgetideas.graphics.client.Color;

public abstract class Session implements ISession {
	public Color getColor() {
		return new Color(red, green, blue, alpha);
	}

	public float getAlpha() {
		return alpha;
	}

	public void setRGB(int red, int green, int blue) {
		this.red   = red;
		this.green = green;
		this.blue  = blue;
	}

	public void setAlpha(float alpha) {
		this.alpha = alpha;
	}
	
	public String getInfoText() {
		return infoText;
	}
	
	public void setInfoText(String infoText) {
		this.infoText = infoText;
	}

	private int   red   = 0;
	private int   green = 0;
	private int   blue  = 0;
	private float alpha = 1.0f;
	
	private String infoText = "";
}
