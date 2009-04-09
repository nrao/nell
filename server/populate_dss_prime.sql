-- Example project
INSERT INTO allotment VALUES (DEFAULT, '100.5', '100.5', '100.5', '4.0');

INSERT INTO semesters VALUES (DEFAULT, '09A');
INSERT INTO semesters VALUES (DEFAULT, '09B');
INSERT INTO semesters VALUES (DEFAULT, '09C');
INSERT INTO semesters VALUES (DEFAULT, '08A');
INSERT INTO semesters VALUES (DEFAULT, '08B');
INSERT INTO semesters VALUES (DEFAULT, '08C');
INSERT INTO semesters VALUES (DEFAULT, '07A');
INSERT INTO semesters VALUES (DEFAULT, '07B');
INSERT INTO semesters VALUES (DEFAULT, '07C');
INSERT INTO semesters VALUES (DEFAULT, '06A');
INSERT INTO semesters VALUES (DEFAULT, '06B');
INSERT INTO semesters VALUES (DEFAULT, '06C');
INSERT INTO semesters VALUES (DEFAULT, '05A');
INSERT INTO semesters VALUES (DEFAULT, '05B');
INSERT INTO semesters VALUES (DEFAULT, '05C');
INSERT INTO semesters VALUES (DEFAULT, '04A');

INSERT INTO project_types VALUES (DEFAULT, 'science');
INSERT INTO project_types VALUES (DEFAULT, 'non-science');

INSERT INTO session_types VALUES (DEFAULT, 'open');
INSERT INTO session_types VALUES (DEFAULT, 'fixed');
INSERT INTO session_types VALUES (DEFAULT, 'windowed');
INSERT INTO session_types VALUES (DEFAULT, 'vlbi');
INSERT INTO session_types VALUES (DEFAULT, 'maintenance');
INSERT INTO session_types VALUES (DEFAULT, 'commissioning');

INSERT INTO observing_types VALUES (DEFAULT, 'radar');
INSERT INTO observing_types VALUES (DEFAULT, 'vlbi');
INSERT INTO observing_types VALUES (DEFAULT, 'pulsar');
INSERT INTO observing_types VALUES (DEFAULT, 'continuum');
INSERT INTO observing_types VALUES (DEFAULT, 'spectral line');
INSERT INTO observing_types VALUES (DEFAULT, 'maintenance');
INSERT INTO observing_types VALUES (DEFAULT, 'calibration');
INSERT INTO observing_types VALUES (DEFAULT, 'testing');

INSERT INTO receivers VALUES (DEFAULT, 'NoiseSource',  'NS',   '0.000',   '0.000');
INSERT INTO receivers VALUES (DEFAULT, 'Rcvr_RRI',     'RRI',  '0.100',   '1.600');
INSERT INTO receivers VALUES (DEFAULT, 'Rcvr_342',     'PF1',  '0.290',   '0.395');
INSERT INTO receivers VALUES (DEFAULT, 'Rcvr_450',     'PF1',  '0.385',   '0.520');
INSERT INTO receivers VALUES (DEFAULT, 'Rcvr_600',     'PF1',  '0.510',   '0.690');
INSERT INTO receivers VALUES (DEFAULT, 'Rcvr_800',     'PF1',  '0.680',   '0.920');
INSERT INTO receivers VALUES (DEFAULT, 'Rcvr_1070',    'PF2',  '0.910',   '1.230');
INSERT INTO receivers VALUES (DEFAULT, 'Rcvr1_2',      'L',    '1.150',   '1.730');
INSERT INTO receivers VALUES (DEFAULT, 'Rcvr2_3',      'S',    '1.730',   '2.600');
INSERT INTO receivers VALUES (DEFAULT, 'Rcvr4_6',      'C',    '3.950',   '6.100');
INSERT INTO receivers VALUES (DEFAULT, 'Rcvr8_10',     'X',    '8.000',  '10.000');
INSERT INTO receivers VALUES (DEFAULT, 'Rcvr12_18',    'Ku',  '12.000',  '15.400');
INSERT INTO receivers VALUES (DEFAULT, 'Rcvr18_22',    'K',   '18.000',  '22.400');
INSERT INTO receivers VALUES (DEFAULT, 'Rcvr22_26',    'K',   '22.000',  '26.500');
INSERT INTO receivers VALUES (DEFAULT, 'Rcvr26_40',    'Ka',  '26.000',  '39.500');
INSERT INTO receivers VALUES (DEFAULT, 'Rcvr40_52',    'Q',   '38.200',  '49.800');
INSERT INTO receivers VALUES (DEFAULT, 'Rcvr_PAR',     'MBA', '80.000', '100.000');
INSERT INTO receivers VALUES (DEFAULT, 'Zpectrometer', 'Z',    '0.000',   '0.000');
INSERT INTO receivers VALUES (DEFAULT, 'Holography',   'Hol', '11.700',  '12.200');

INSERT INTO systems VALUES (DEFAULT, 'J2000',         'ra',  'dec');
INSERT INTO systems VALUES (DEFAULT, 'B1950',         'ra',  'dec');
INSERT INTO systems VALUES (DEFAULT, 'Galactic',      'lat', 'long');
INSERT INTO systems VALUES (DEFAULT, 'RaDecOfDate',   'ra',  'dec');
INSERT INTO systems VALUES (DEFAULT, 'AzEl',          'az',  'el');
INSERT INTO systems VALUES (DEFAULT, 'HaDec',         'ra',  'dec');
INSERT INTO systems VALUES (DEFAULT, 'ApparentRaDec', 'ra',  'dec');
INSERT INTO systems VALUES (DEFAULT, 'CableWrap',     'az',  'el');
INSERT INTO systems VALUES (DEFAULT, 'Encoder',       'az',  'el');

INSERT INTO parameters VALUES (DEFAULT, 'UTC Flag', 'boolean');
INSERT INTO parameters VALUES (DEFAULT, 'Night-time Flag', 'boolean');
INSERT INTO parameters VALUES (DEFAULT, 'Atmos St Limit', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'Tr Err Limit', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'Min Eff TSys', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'HA Limit', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'ZA Limit', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'Solar Avoid', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'Precip', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'Wind', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'Time Day', 'datetime');
INSERT INTO parameters VALUES (DEFAULT, 'Transit', 'boolean');
INSERT INTO parameters VALUES (DEFAULT, 'Transit Before', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'Transit After', 'float');
