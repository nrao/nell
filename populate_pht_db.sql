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

INSERT INTO pht_session_types VALUES (DEFAULT, 'Open - Low Freq', 'LF');
INSERT INTO pht_session_types VALUES (DEFAULT, 'Open - High Freq 1', 'HF1');
INSERT INTO pht_session_types VALUES (DEFAULT, 'Open - High Freq 2', 'HF2');
INSERT INTO pht_session_types VALUES (DEFAULT, 'Fixed', 'F');
INSERT INTO pht_session_types VALUES (DEFAULT, 'Windowed', 'W');
INSERT INTO pht_session_types VALUES (DEFAULT, 'Elective', 'E');

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

INSERT INTO pht_receivers VALUES (DEFAULT, 'NoiseSource',   'NS',   'N', 0.000,   0.000); -- 
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr_RRI',      'RRI',  'R', 0.100,   1.600); -- R
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr_342',      '342',  '3', 0.290,   0.395); -- 3
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr_450',      '450',  '4', 0.385,   0.520); -- 4
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr_600',      '600',  '6', 0.510,   0.690); -- 6
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr_800',      '800',  '8', 0.680,   0.920); -- 8
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr_1070',    '1070',  'A', 0.910,   1.230); -- A
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr1_2',       'L',    'L', 1.150,   1.730); -- L
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr2_3',       'S',    'S', 1.730,   2.600); -- S
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr4_6',       'C',    'C', 3.950,   6.100); -- C
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr8_10',      'X',    'X', 8.000,  10.000); -- X
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr12_18',     'Ku',   'U', 12.000,  15.400); -- U
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr18_26',     'K',    'K', 18.000,  26.500); -- K
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr26_40',     'Ka',   'B', 26.000,  39.500); -- B
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr40_52',     'Q',    'Q', 38.200,  49.800); -- Q
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr_PAR',      'MBA',  'M', 80.000, 100.000); -- M
INSERT INTO pht_receivers VALUES (DEFAULT, 'Zpectrometer',  'Z',    'Z', 0.000,   0.000); -- 
INSERT INTO pht_receivers VALUES (DEFAULT, 'Holography',    'Hol',  'H', 11.700,  12.200); -- H
INSERT INTO pht_receivers VALUES (DEFAULT, 'RcvrArray18_26','KFPA', 'F', 17.000,  27.500); -- F
INSERT INTO pht_receivers VALUES (DEFAULT, 'Rcvr68_92',     'W',    'W', 68.000,  92.000); -- W

INSERT INTO pht_backends VALUES (DEFAULT, 'Caltech Continuum Backend', 'CCB', 'C');
INSERT INTO pht_backends VALUES (DEFAULT, 'Caltech-Green Bank-Swinbourne Recorder 2', 'CGSR2', '2');
INSERT INTO pht_backends VALUES (DEFAULT, 'GBT Digital Continuum Receiver', 'DCR', 'D');
INSERT INTO pht_backends VALUES (DEFAULT, 'GBT Spectrometer', 'gbtSpec', 'S');
INSERT INTO pht_backends VALUES (DEFAULT, 'Green Bank Astronomical Signal Processor', 'GASP', 'G');
INSERT INTO pht_backends VALUES (DEFAULT, 'Green bank Ultimate Pulsar Processor', 'GUPPY', 'U');
INSERT INTO pht_backends VALUES (DEFAULT, 'Haystack Mark 4 High bandwidth (> 1Gb/s)', 'HayMark4', 'H');
INSERT INTO pht_backends VALUES (DEFAULT, 'Mark 5 recorder (disks)', 'Mark5', '5');
INSERT INTO pht_backends VALUES (DEFAULT, 'Mustang', 'Mustang', 'M');
INSERT INTO pht_backends VALUES (DEFAULT, 'Radar backend', 'Radar', 'R');
INSERT INTO pht_backends VALUES (DEFAULT, 'S2 recorder', 'gbtS2', 'E');
INSERT INTO pht_backends VALUES (DEFAULT, 'Spectral Processor', 'gbtSpecP', 'P');
INSERT INTO pht_backends VALUES (DEFAULT, 'VErsitile GB Astronomical Spectrometer ', 'Vegas', 'V');
INSERT INTO pht_backends VALUES (DEFAULT, 'VLBA recorder and DAR ', 'gbtVLBA', 'B');
INSERT INTO pht_backends VALUES (DEFAULT, 'Zpectrometer ', 'Zpect', 'Z');
INSERT INTO pht_backends VALUES (DEFAULT, 'User supplied or new backend ', 'Other', 'O');

INSERT INTO pht_session_separations VALUES (DEFAULT, 'hour');
INSERT INTO pht_session_separations VALUES (DEFAULT, 'day');
INSERT INTO pht_session_separations VALUES (DEFAULT, 'week');

INSERT INTO pht_session_grades VALUES (DEFAULT, 'A');
INSERT INTO pht_session_grades VALUES (DEFAULT, 'B');
INSERT INTO pht_session_grades VALUES (DEFAULT, 'C');
INSERT INTO pht_session_grades VALUES (DEFAULT, 'D');
INSERT INTO pht_session_grades VALUES (DEFAULT, 'H');

INSERT INTO pht_coordinate_epochs VALUES (DEFAULT, 'J2000');
INSERT INTO pht_coordinate_epochs VALUES (DEFAULT, 'B1950');

INSERT INTO pht_coordinate_systems VALUES (DEFAULT, 'Equatorial');
INSERT INTO pht_coordinate_systems VALUES (DEFAULT, 'Galactic');

INSERT INTO pht_velocity_types VALUES (DEFAULT, 'Velocity');
INSERT INTO pht_velocity_types VALUES (DEFAULT, 'Redshift');

INSERT INTO pht_conventions VALUES (DEFAULT, 'Radio');
INSERT INTO pht_conventions VALUES (DEFAULT, 'Optical');
INSERT INTO pht_conventions VALUES (DEFAULT, 'Redshift');

INSERT INTO pht_reference_frames VALUES (DEFAULT, 'LSRK');
INSERT INTO pht_reference_frames VALUES (DEFAULT, 'Barycentric');
INSERT INTO pht_reference_frames VALUES (DEFAULT, 'Topocentric');
INSERT INTO pht_reference_frames VALUES (DEFAULT, 'LSRD');
INSERT INTO pht_reference_frames VALUES (DEFAULT, 'Heliocentric');
INSERT INTO pht_reference_frames VALUES (DEFAULT, 'Galactic');
INSERT INTO pht_reference_frames VALUES (DEFAULT, 'CMB');

