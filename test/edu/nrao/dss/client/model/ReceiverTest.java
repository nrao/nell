package edu.nrao.dss.client.model;

import com.google.gwt.junit.client.GWTTestCase;

public class ReceiverTest extends GWTTestCase {

	public String getModuleName() {
		return "edu.nrao.dss.Scheduler";
    }
	
	public void test_deriveReceiver() {
		assertEquals(Receiver.deriveReceiver(.011), "Rcvr_RRI");
		assertEquals(Receiver.deriveReceiver(.013), "Rcvr_342");
		assertEquals(Receiver.deriveReceiver(10.9), "Rcvr8_10");
		assertEquals(Receiver.deriveReceiver(11.1), "Rcvr12_18");
		assertEquals(Receiver.deriveReceiver(51.9), "Rcvr40_52");
		assertEquals(Receiver.deriveReceiver(52.1), "NoiseSource");
		assertEquals(Receiver.deriveReceiver(55.9), "NoiseSource");
		assertEquals(Receiver.deriveReceiver(90.9), "Rcvr_PAR");
	}
}
