INSERT INTO pht_scientific_categories VALUES (DEFAULT, 'Extragalactic');
INSERT INTO pht_scientific_categories VALUES (DEFAULT, 'Galactic');
INSERT INTO pht_scientific_categories VALUES (DEFAULT, 'Stellar');
INSERT INTO pht_scientific_categories VALUES (DEFAULT, 'Solar System');
INSERT INTO pht_scientific_categories VALUES (DEFAULT, 'Astrometry/Geodesy');
INSERT INTO pht_scientific_categories VALUES (DEFAULT, 'Extragalactic Structure');
INSERT INTO pht_scientific_categories VALUES (DEFAULT, 'Normal Galaxies; Groups; and Clusters');
INSERT INTO pht_scientific_categories VALUES (DEFAULT, 'Energetic Transients and Pulsars');
INSERT INTO pht_scientific_categories VALUES (DEFAULT, 'Solar System; Stars; Planetary Systems');
INSERT INTO pht_scientific_categories VALUES (DEFAULT, 'Star Formation');
INSERT INTO pht_scientific_categories VALUES (DEFAULT, 'Interstellar Medium');
INSERT INTO pht_scientific_categories VALUES (DEFAULT, 'High Redshift and Source Surveys');
INSERT INTO pht_scientific_categories VALUES (DEFAULT, 'Active Galactic Nuclei');

INSERT INTO pht_status VALUES (DEFAULT, 'Draft');
INSERT INTO pht_status VALUES (DEFAULT, 'Submitted');
INSERT INTO pht_status VALUES (DEFAULT, 'Withdraw');

INSERT INTO pht_proposal_types VALUES (DEFAULT, 'Regular');
INSERT INTO pht_proposal_types VALUES (DEFAULT, 'Rapid Response');
INSERT INTO pht_proposal_types VALUES (DEFAULT, 'Large');
INSERT INTO pht_proposal_types VALUES (DEFAULT, 'Triggered');
INSERT INTO pht_proposal_types VALUES (DEFAULT, 'Director\'s Discretionary Time');

INSERT INTO pht_observing_types VALUES (DEFAULT, 'Spectroscopy');
INSERT INTO pht_observing_types VALUES (DEFAULT, 'Single Pointing(s)');
INSERT INTO pht_observing_types VALUES (DEFAULT, 'Continuum');
INSERT INTO pht_observing_types VALUES (DEFAULT, 'Planetary Radar');
INSERT INTO pht_observing_types VALUES (DEFAULT, 'Triggered Transient');
INSERT INTO pht_observing_types VALUES (DEFAULT, 'Polarmetry');
INSERT INTO pht_observing_types VALUES (DEFAULT, 'Monitoring');
INSERT INTO pht_observing_types VALUES (DEFAULT, 'Grid Mapping/Mosaicing');
INSERT INTO pht_observing_types VALUES (DEFAULT, 'Pulsar');
INSERT INTO pht_observing_types VALUES (DEFAULT, 'Solar');
INSERT INTO pht_observing_types VALUES (DEFAULT, 'High Time Resolution');
INSERT INTO pht_observing_types VALUES (DEFAULT, 'On-the-Fly Mapping');
INSERT INTO pht_observing_types VALUES (DEFAULT, 'Phase Referencing');
INSERT INTO pht_observing_types VALUES (DEFAULT, 'Solar System');
INSERT INTO pht_observing_types VALUES (DEFAULT, 'Astrometry');
INSERT INTO pht_observing_types VALUES (DEFAULT, 'Radar');
INSERT INTO pht_observing_types VALUES (DEFAULT, 'Sun');
INSERT INTO pht_observing_types VALUES (DEFAULT, 'Other');
INSERT INTO pht_observing_types VALUES (DEFAULT, 'Geodesy');


INSERT INTO pht_weather_types VALUES (DEFAULT, 'Poor');
INSERT INTO pht_weather_types VALUES (DEFAULT, 'Fair');
INSERT INTO pht_weather_types VALUES (DEFAULT, 'Good');
INSERT INTO pht_weather_types VALUES (DEFAULT, 'Excellent');

INSERT INTO pht_session_types VALUES (DEFAULT, 'Open');
INSERT INTO pht_session_types VALUES (DEFAULT, 'Fixed');
INSERT INTO pht_session_types VALUES (DEFAULT, 'Windowed');
INSERT INTO pht_session_types VALUES (DEFAULT, 'Elective');

INSERT INTO pht_parameters VALUES (DEFAULT, 'LST Include Low', 'float');
INSERT INTO pht_parameters VALUES (DEFAULT, 'LST Include Hi', 'float');
INSERT INTO pht_parameters VALUES (DEFAULT, 'LST Exclude Low', 'float');
INSERT INTO pht_parameters VALUES (DEFAULT, 'LST Exclude Hi', 'float');

INSERT INTO pht_semesters VALUES (DEFAULT, '09A');
INSERT INTO pht_semesters VALUES (DEFAULT, '09B');
INSERT INTO pht_semesters VALUES (DEFAULT, '09C');
INSERT INTO pht_semesters VALUES (DEFAULT, '08A');
INSERT INTO pht_semesters VALUES (DEFAULT, '08B');
INSERT INTO pht_semesters VALUES (DEFAULT, '08C');
INSERT INTO pht_semesters VALUES (DEFAULT, '07A');
INSERT INTO pht_semesters VALUES (DEFAULT, '07B');
INSERT INTO pht_semesters VALUES (DEFAULT, '07C');
INSERT INTO pht_semesters VALUES (DEFAULT, '06A');
INSERT INTO pht_semesters VALUES (DEFAULT, '06B');
INSERT INTO pht_semesters VALUES (DEFAULT, '06C');
INSERT INTO pht_semesters VALUES (DEFAULT, '05A');
INSERT INTO pht_semesters VALUES (DEFAULT, '05B');
INSERT INTO pht_semesters VALUES (DEFAULT, '05C');
INSERT INTO pht_semesters VALUES (DEFAULT, '04A');
INSERT INTO pht_semesters VALUES (DEFAULT, '10A');
INSERT INTO pht_semesters VALUES (DEFAULT, '10B');
INSERT INTO pht_semesters VALUES (DEFAULT, '10C');
INSERT INTO pht_semesters VALUES (DEFAULT, '11A');
INSERT INTO pht_semesters VALUES (DEFAULT, '11B');
INSERT INTO pht_semesters VALUES (DEFAULT, '12A');
INSERT INTO pht_semesters VALUES (DEFAULT, '12B');

INSERT INTO pht_receivers VALUES (DEFAULT, 'NoiseSource',   'NS',   0.000,   0.000); -- 
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr_RRI',      'RRI',  0.100,   1.600); -- R
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr_342',      '342',  0.290,   0.395); -- 3
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr_450',      '450',  0.385,   0.520); -- 4
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr_600',      '600',  0.510,   0.690); -- 6
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr_800',      '800',  0.680,   0.920); -- 8
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr_1070',    '1070',  0.910,   1.230); -- A
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr1_2',       'L',    1.150,   1.730); -- L
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr2_3',       'S',    1.730,   2.600); -- S
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr4_6',       'C',    3.950,   6.100); -- C
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr8_10',      'X',    8.000,  10.000); -- X
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr12_18',     'Ku',  12.000,  15.400); -- U
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr18_26',     'K',   18.000,  26.500); -- K
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr26_40',     'Ka',  26.000,  39.500); -- B
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr40_52',     'Q',   38.200,  49.800); -- Q
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr_PAR',      'MBA', 80.000, 100.000); -- M
INSERT INTO pht_receivers VALUES (DEFAULT, 'Zpectrometer',  'Z',    0.000,   0.000); -- 
INSERT INTO pht_receivers VALUES (DEFAULT, 'Holography',    'Hol', 11.700,  12.200); -- H
INSERT INTO pht_receivers VALUES (DEFAULT, 'RcvrArray18_26','KFPA',17.000,  27.500); -- F
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr68_92',     'W',   68.000,  92.000); -- W

INSERT INTO pht_backends VALUES (DEFAULT, 'Caltech Continuum Backend', 'CCB');
INSERT INTO pht_backends VALUES (DEFAULT, 'Caltech-Green Bank-Swinbourne Recorder 2', 'CGSR2');
INSERT INTO pht_backends VALUES (DEFAULT, 'GBT Digital Continuum Receiver', 'DCR');
INSERT INTO pht_backends VALUES (DEFAULT, 'GBT Spectrometer', 'gbtSpec');
INSERT INTO pht_backends VALUES (DEFAULT, 'Green Bank Astronomical Signal Processor', 'GASP');
INSERT INTO pht_backends VALUES (DEFAULT, 'Green bank Ultimate Pulsar Processor', 'GUPPY');
INSERT INTO pht_backends VALUES (DEFAULT, 'Haystack Mark 4 High bandwidth (> 1Gb/s)', 'HayMark4');
INSERT INTO pht_backends VALUES (DEFAULT, 'Mark 5 recorder (disks)', 'Mark5');
INSERT INTO pht_backends VALUES (DEFAULT, 'Mustang', 'Mustang');
INSERT INTO pht_backends VALUES (DEFAULT, 'Radar backend', 'Radar');
INSERT INTO pht_backends VALUES (DEFAULT, 'S2 recorder', 'gbtS2');
INSERT INTO pht_backends VALUES (DEFAULT, 'Spectral Processor', 'gbtSpecP');
INSERT INTO pht_backends VALUES (DEFAULT, 'VErsitile GB Astronomical Spectrometer ', 'Vegas');
INSERT INTO pht_backends VALUES (DEFAULT, 'VLBA recorder and DAR ', 'gbtVLBA');
INSERT INTO pht_backends VALUES (DEFAULT, 'Zpectrometer ', 'Zpect');
INSERT INTO pht_backends VALUES (DEFAULT, 'User supplied or new backend ', 'Other');

INSERT INTO pht_session_separations VALUES (DEFAULT, 'day');
INSERT INTO pht_session_separations VALUES (DEFAULT, 'week');

INSERT INTO pht_session_grades VALUES (DEFAULT, 'A');
INSERT INTO pht_session_grades VALUES (DEFAULT, 'B');
INSERT INTO pht_session_grades VALUES (DEFAULT, 'C');
INSERT INTO pht_session_grades VALUES (DEFAULT, 'D');
INSERT INTO pht_session_grades VALUES (DEFAULT, 'H');
