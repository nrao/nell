-- Example project
INSERT INTO projects VALUES (NULL, 1, 1, 1, 'GBT09A-001', '', 0, 0, 0, NULL, NULL);
INSERT INTO allotment VALUES (NULL, 100.5, 100.5, 100.5);

INSERT INTO semesters VALUES (NULL, '09A');
INSERT INTO semesters VALUES (NULL, '09B');
INSERT INTO semesters VALUES (NULL, '09C');

INSERT INTO project_types VALUES (NULL, 'science');
INSERT INTO project_types VALUES (NULL, 'non-science');

INSERT INTO session_types VALUES (NULL, 'open');
INSERT INTO session_types VALUES (NULL, 'fixed');
INSERT INTO session_types VALUES (NULL, 'windowed');
INSERT INTO session_types VALUES (NULL, 'vlbi');
INSERT INTO session_types VALUES (NULL, 'maintenance');
INSERT INTO session_types VALUES (NULL, 'commissioning');

INSERT INTO observing_types VALUES (NULL, 'pulsar');
INSERT INTO observing_types VALUES (NULL, 'continuum');
INSERT INTO observing_types VALUES (NULL, 'spectral line');
INSERT INTO observing_types VALUES (NULL, 'maintenance');
INSERT INTO observing_types VALUES (NULL, 'calibration');
INSERT INTO observing_types VALUES (NULL, 'testing');

INSERT INTO receivers VALUES (NULL, 'NoiseSource',  'NS',   0.000,   0.000);
INSERT INTO receivers VALUES (NULL, 'Rcvr_RRI',     'RRI',  0.100,   1.600);
INSERT INTO receivers VALUES (NULL, 'Rcvr_342',     'PF1',  0.290,   0.395);
INSERT INTO receivers VALUES (NULL, 'Rcvr_450',     'PF1',  0.385,   0.520);
INSERT INTO receivers VALUES (NULL, 'Rcvr_600',     'PF1',  0.510,   0.690);
INSERT INTO receivers VALUES (NULL, 'Rcvr_800',     'PF1',  0.680,   0.920);
INSERT INTO receivers VALUES (NULL, 'Rcvr_1070',    'PF2',  0.910,   1.230);
INSERT INTO receivers VALUES (NULL, 'Rcvr1_2',      'L',    1.150,   1.730);
INSERT INTO receivers VALUES (NULL, 'Rcvr2_3',      'S',    1.730,   2.600);
INSERT INTO receivers VALUES (NULL, 'Rcvr4_6',      'C',    3.950,   6.100);
INSERT INTO receivers VALUES (NULL, 'Rcvr8_10',     'X',    8.000,  10.000);
INSERT INTO receivers VALUES (NULL, 'Rcvr12_18',    'Ku',  12.000,  15.400);
INSERT INTO receivers VALUES (NULL, 'Rcvr18_22',    'K',   18.000,  22.400);
INSERT INTO receivers VALUES (NULL, 'Rcvr22_26',    'K',   22.000,  26.500);
INSERT INTO receivers VALUES (NULL, 'Rcvr26_40',    'Ka',  26.000,  39.500);
INSERT INTO receivers VALUES (NULL, 'Rcvr40_52',    'Q',   38.200,  49.800);
INSERT INTO receivers VALUES (NULL, 'Rcvr_PAR',     'MBA', 80.000, 100.000);
INSERT INTO receivers VALUES (NULL, 'Zpectrometer', 'Z',    0.000,   0.000);
INSERT INTO receivers VALUES (NULL, 'Holography',   'Hol', 11.700,  12.200);

INSERT INTO systems VALUES (NULL, 'J2000',         'ra',  'dec');
INSERT INTO systems VALUES (NULL, 'B1950',         'ra',  'dec');
INSERT INTO systems VALUES (NULL, 'Galactic',      'lat', 'long');
INSERT INTO systems VALUES (NULL, 'RaDecOfDate',   'ra',  'dec');
INSERT INTO systems VALUES (NULL, 'AzEl',          'az',  'el');
INSERT INTO systems VALUES (NULL, 'HaDec',         'ra',  'dec');
INSERT INTO systems VALUES (NULL, 'ApparentRaDec', 'ra',  'dec');
INSERT INTO systems VALUES (NULL, 'CableWrap',     'az',  'el');
INSERT INTO systems VALUES (NULL, 'Encoder',       'az',  'el');

INSERT INTO parameters VALUES (NULL, 'Obs Eff Limit', 'float');
INSERT INTO parameters VALUES (NULL, 'Atmos St Limit', 'float');
INSERT INTO parameters VALUES (NULL, 'Tr Err Limit', 'float');
INSERT INTO parameters VALUES (NULL, 'Min Eff TSys', 'float');
INSERT INTO parameters VALUES (NULL, 'HA Limit', 'float');
INSERT INTO parameters VALUES (NULL, 'ZA Limit', 'float');
INSERT INTO parameters VALUES (NULL, 'Solar Avoid', 'float');
INSERT INTO parameters VALUES (NULL, 'Precip', 'float');
INSERT INTO parameters VALUES (NULL, 'Wind', 'float');
INSERT INTO parameters VALUES (NULL, 'Time Day', 'datetime');
INSERT INTO parameters VALUES (NULL, 'Transit', 'boolean');
INSERT INTO parameters VALUES (NULL, 'Transit Before', 'float');
INSERT INTO parameters VALUES (NULL, 'Transit After', 'float');
