package edu.nrao.dss.client.model;

import com.google.gwt.junit.client.GWTTestCase;

public class ReceiverTest extends GWTTestCase {

	public String getModuleName() {
		return "edu.nrao.dss.Scheduler";
    }
	
	public void test_deriveReceiver() {
		assertEquals("RRI", Receiver.deriveReceiver(.011));
		assertEquals("342", Receiver.deriveReceiver(.013));
		assertEquals("X",   Receiver.deriveReceiver(10.9));
		assertEquals("Ku",  Receiver.deriveReceiver(11.1));
		assertEquals("Q",   Receiver.deriveReceiver(51.9));
		assertEquals("K",   Receiver.deriveReceiver(24.1));
		assertEquals("MBA", Receiver.deriveReceiver(55.9));
		assertEquals("MBA", Receiver.deriveReceiver(90.9));
	}
}
