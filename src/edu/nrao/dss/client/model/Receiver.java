package edu.nrao.dss.client.model;

public class Receiver {
    // TBF cardinal sin: code duplicated in server - Generate.py
    static public String deriveReceiver(double frequency) {
        String receiver_name = "NoiseSource";
        if (frequency <= .012) {
            receiver_name = "Rcvr_RRI";
        }
        else if (frequency <= .395) {
            receiver_name = "Rcvr_342";
        }
        else if (frequency <= .52) {
            receiver_name = "Rcvr_450";
        }
        else if (frequency <= .69) {
            receiver_name = "Rcvr_600";
        }
        else if (frequency <= .92) {
            receiver_name = "Rcvr_800";;
        }
        else if (frequency <= 1.23) {
            receiver_name = "Rcvr_1070";;
        }
        else if (frequency <= 1.73) {
            receiver_name = "Rcvr1_2";
        }
        else if (frequency <= 3.275) {
            receiver_name = "Rcvr2_3";;
        }
        else if (frequency <= 6.925) {
            receiver_name = "Rcvr4_6";
        }
        else if (frequency <= 11.0) {
            receiver_name = "Rcvr8_10";
        }
        else if (frequency <= 16.7) {
            receiver_name = "Rcvr12_18";
        }
        else if (frequency <= 22.0) {
            receiver_name = "Rcvr18_22";;
        }
        else if (frequency <= 26.25) {
            receiver_name = "Rcvr22_26";
        }
        else if (frequency <= 40.5) {
            receiver_name = "Rcvr26_40";
        }
        else if (frequency <= 52.0) {
            receiver_name = "Rcvr40_52";
        } else if (87.0 <= frequency && frequency <= 91.0) {
            receiver_name = "Rcvr_PAR";
        }

        return receiver_name;
    }

}
