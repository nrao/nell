-- we don't want time zones in the DB
alter table projects alter column start_date type timestamp without time zone;
alter table projects alter column end_date type timestamp without time zone;
alter table receiver_schedule alter column start_date type timestamp without time zone;
alter table observing_parameters alter column datetime_value type timestamp without time zone;
-- alter table opportunities alter column start_time type timestamp without time zone;
alter table periods alter column start type timestamp without time zone;
alter table periods alter column forecast type timestamp without time zone;
alter table blackouts alter column start_date type timestamp without time zone;
alter table blackouts alter column end_date type timestamp without time zone;
alter table blackouts alter column until type timestamp without time zone;
alter table reservations alter column start_date type timestamp without time zone;
alter table reservations alter column end_date type timestamp without time zone;

-- Example project
INSERT INTO allotment VALUES (DEFAULT, 100.5, 100.5, 100.5, 4.0);
--INSERT INTO projects VALUES (DEFAULT, 1, 1, 'GBT-M09A', 'Maintenance', false, false, null, null, null, null, null, null);
--INSERT INTO status VALUES (DEFAULT, false, false, false, false);
--INSERT INTO sessions VALUES (DEFAULT, 1, 1, 1, 1, 1, 0, 'Maintenance', null, null, null, null, null, null);
--INSERT INTO periods VALUES (DEFAULT, 1, null, null, '2009-4-30 00:00:00', 6, null, null, false, false);

INSERT INTO roles VALUES (DEFAULT, 'Administrator');
INSERT INTO roles VALUES (DEFAULT, 'Observer');
INSERT INTO roles VALUES (DEFAULT, 'Operator');

INSERT INTO repeats VALUES (DEFAULT, 'Once');
INSERT INTO repeats VALUES (DEFAULT, 'Weekly');
INSERT INTO repeats VALUES (DEFAULT, 'Monthly');

INSERT INTO timezones VALUES (DEFAULT, 'UTC-11');
INSERT INTO timezones VALUES (DEFAULT, 'UTC-10');
INSERT INTO timezones VALUES (DEFAULT, 'UTC-9');
INSERT INTO timezones VALUES (DEFAULT, 'UTC-8');
INSERT INTO timezones VALUES (DEFAULT, 'UTC-7');
INSERT INTO timezones VALUES (DEFAULT, 'UTC-6');
INSERT INTO timezones VALUES (DEFAULT, 'UTC-5');
INSERT INTO timezones VALUES (DEFAULT, 'UTC-4');
INSERT INTO timezones VALUES (DEFAULT, 'UTC-3');
INSERT INTO timezones VALUES (DEFAULT, 'UTC-2');
INSERT INTO timezones VALUES (DEFAULT, 'UTC-1');
INSERT INTO timezones VALUES (DEFAULT, 'UTC');
INSERT INTO timezones VALUES (DEFAULT, 'UTC+1');
INSERT INTO timezones VALUES (DEFAULT, 'UTC+2');
INSERT INTO timezones VALUES (DEFAULT, 'UTC+3');
INSERT INTO timezones VALUES (DEFAULT, 'UTC+4');
INSERT INTO timezones VALUES (DEFAULT, 'UTC+5');
INSERT INTO timezones VALUES (DEFAULT, 'UTC+6');
INSERT INTO timezones VALUES (DEFAULT, 'UTC+7');
INSERT INTO timezones VALUES (DEFAULT, 'UTC+8');
INSERT INTO timezones VALUES (DEFAULT, 'UTC+9');
INSERT INTO timezones VALUES (DEFAULT, 'UTC+10');
INSERT INTO timezones VALUES (DEFAULT, 'UTC+11');
INSERT INTO timezones VALUES (DEFAULT, 'UTC+12');

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
INSERT INTO semesters VALUES (DEFAULT, '10A');
INSERT INTO semesters VALUES (DEFAULT, '10B');
INSERT INTO semesters VALUES (DEFAULT, '10C');
INSERT INTO semesters VALUES (DEFAULT, '11A');
INSERT INTO semesters VALUES (DEFAULT, '11B');
INSERT INTO semesters VALUES (DEFAULT, '12A');
INSERT INTO semesters VALUES (DEFAULT, '12B');

INSERT INTO project_types VALUES (DEFAULT, 'science');
INSERT INTO project_types VALUES (DEFAULT, 'non-science');

INSERT INTO projects VALUES (DEFAULT, 1, 1, 'GBT09A-001', '', false, false, false, NULL, NULL, NULL);

INSERT INTO session_types VALUES (DEFAULT, 'open');
INSERT INTO session_types VALUES (DEFAULT, 'fixed');
INSERT INTO session_types VALUES (DEFAULT, 'windowed');
INSERT INTO session_types VALUES (DEFAULT, 'elective');
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

INSERT INTO period_states VALUES (DEFAULT, 'Pending',   'P');
INSERT INTO period_states VALUES (DEFAULT, 'Scheduled', 'S');
INSERT INTO period_states VALUES (DEFAULT, 'Deleted',   'D');
INSERT INTO period_states VALUES (DEFAULT, 'Complete',  'C');

--                                                                                Carl's
-- Moved to scheduler/fixtures/initial_data.json
--INSERT INTO receivers VALUES (DEFAULT, 'NoiseSource',   'NS',   0.000,   0.000); -- 
--INSERT INTO receivers VALUES (DEFAULT, 'Rcvr_RRI',      'RRI',  0.100,   1.600); -- R
--INSERT INTO receivers VALUES (DEFAULT, 'Rcvr_342',      '342',  0.290,   0.395); -- 3
--INSERT INTO receivers VALUES (DEFAULT, 'Rcvr_450',      '450',  0.385,   0.520); -- 4
--INSERT INTO receivers VALUES (DEFAULT, 'Rcvr_600',      '600',  0.510,   0.690); -- 6
--INSERT INTO receivers VALUES (DEFAULT, 'Rcvr_800',      '800',  0.680,   0.920); -- 8
--INSERT INTO receivers VALUES (DEFAULT, 'Rcvr_1070',    '1070',  0.910,   1.230); -- A
--INSERT INTO receivers VALUES (DEFAULT, 'Rcvr1_2',       'L',    1.150,   1.730); -- L
--INSERT INTO receivers VALUES (DEFAULT, 'Rcvr2_3',       'S',    1.730,   2.600); -- S
--INSERT INTO receivers VALUES (DEFAULT, 'Rcvr4_6',       'C',    3.950,   6.100); -- C
--INSERT INTO receivers VALUES (DEFAULT, 'Rcvr8_10',      'X',    8.000,  10.000); -- X
--INSERT INTO receivers VALUES (DEFAULT, 'Rcvr12_18',     'Ku',  12.000,  15.400); -- U
--INSERT INTO receivers VALUES (DEFAULT, 'Rcvr18_26',     'K',   18.000,  26.500); -- K
--INSERT INTO receivers VALUES (DEFAULT, 'Rcvr26_40',     'Ka',  26.000,  39.500); -- B
--INSERT INTO receivers VALUES (DEFAULT, 'Rcvr40_52',     'Q',   38.200,  49.800); -- Q
--INSERT INTO receivers VALUES (DEFAULT, 'Rcvr_PAR',      'MBA', 80.000, 100.000); -- M
--INSERT INTO receivers VALUES (DEFAULT, 'Zpectrometer',  'Z',    0.000,   0.000); -- 
--INSERT INTO receivers VALUES (DEFAULT, 'Holography',    'Hol', 11.700,  12.200); -- H
--INSERT INTO receivers VALUES (DEFAULT, 'RcvrArray18_26','KFPA',17.000,  27.500); -- F
--INSERT INTO receivers VALUES (DEFAULT, 'Rcvr68_92',     'W',   68.000,  92.000); -- W

INSERT INTO systems VALUES (DEFAULT, 'J2000',         'ra',  'dec');
INSERT INTO systems VALUES (DEFAULT, 'B1950',         'ra',  'dec');
INSERT INTO systems VALUES (DEFAULT, 'Galactic',      'lat', 'long');
INSERT INTO systems VALUES (DEFAULT, 'RaDecOfDate',   'ra',  'dec');
INSERT INTO systems VALUES (DEFAULT, 'AzEl',          'az',  'el');
INSERT INTO systems VALUES (DEFAULT, 'HaDec',         'ra',  'dec');
INSERT INTO systems VALUES (DEFAULT, 'ApparentRaDec', 'ra',  'dec');
INSERT INTO systems VALUES (DEFAULT, 'CableWrap',     'az',  'el');
INSERT INTO systems VALUES (DEFAULT, 'Encoder',       'az',  'el');
INSERT INTO systems VALUES (DEFAULT, 'Ephemeris',     'ra',  'dec');

INSERT INTO parameters VALUES (DEFAULT , 'Instruments', 'string');
INSERT INTO parameters VALUES (DEFAULT, 'LST Include Low', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'LST Include Hi', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'LST Exclude Low', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'LST Exclude Hi', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'UTC Flag', 'boolean');
INSERT INTO parameters VALUES (DEFAULT, 'Obs Eff Limit', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'Atmos St Limit', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'Tr Err Limit', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'Min Eff TSys', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'HA Limit', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'ZA Limit', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'Solar Avoid', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'Precip', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'Wind', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'Time Of Day', 'string');
INSERT INTO parameters VALUES (DEFAULT, 'Transit', 'boolean');
INSERT INTO parameters VALUES (DEFAULT, 'Transit Before', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'Transit After', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'El Limit', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'Not Guaranteed', 'boolean');
INSERT INTO parameters VALUES (DEFAULT, 'Source Size', 'float');
INSERT INTO parameters VALUES (DEFAULT, 'Keyhole', 'boolean');
INSERT INTO parameters VALUES (DEFAULT, 'Good Atmospheric Stability', 'boolean');
INSERT INTO parameters VALUES (DEFAULT, 'Irradiance Threshold', 'float');

INSERT INTO maintenance_telescope_resources VALUES (DEFAULT, 'Telescope motion required', 'M', 'N');
INSERT INTO maintenance_telescope_resources VALUES (DEFAULT, 'No telescope required ', 'N', 'MNBASDZE');
INSERT INTO maintenance_telescope_resources VALUES (DEFAULT, 'Tipping structure in Bird Bath positon ', 'B', 'NBZ');
INSERT INTO maintenance_telescope_resources VALUES (DEFAULT, 'Tipping structure in Access positon', 'A', 'NAZ');
INSERT INTO maintenance_telescope_resources VALUES (DEFAULT, 'Tipping structure in Survival positon ', 'S', 'NSZ');
INSERT INTO maintenance_telescope_resources VALUES (DEFAULT, 'Tipping structure in Snow Dump positon ', 'D', 'NDZ');
INSERT INTO maintenance_telescope_resources VALUES (DEFAULT, 'Azimuth system lockout only or Azimuth is specified', 'Z', 'NBASD');
INSERT INTO maintenance_telescope_resources VALUES (DEFAULT, 'Elevation axis movement only; Az locked out.', 'E', 'N');

INSERT INTO maintenance_software_resources VALUES (DEFAULT, 'Full M&C system', 'F', 'PN');
INSERT INTO maintenance_software_resources VALUES (DEFAULT, 'Full M&C - Not available for others ', 'U', 'N');
INSERT INTO maintenance_software_resources VALUES (DEFAULT, 'Partial M&C system without telescope control', 'P', 'PFNA');
INSERT INTO maintenance_software_resources VALUES (DEFAULT, 'No M&C system required ', 'N', 'FUPNA');
INSERT INTO maintenance_software_resources VALUES (DEFAULT, 'M&C control of antenna only ', 'A', 'PN');

INSERT INTO maintenance_other_resources VALUES (DEFAULT, 'LO System', 'L', 'INB');
INSERT INTO maintenance_other_resources VALUES (DEFAULT, 'IF System', 'I', 'LNRUD');

INSERT INTO backends VALUES (DEFAULT, 'Caltech Continuum Backend', 'CCB', 'K', 'false');
INSERT INTO backends VALUES (DEFAULT, 'Caltech-Green Bank-Swinbourne Recorder 2', 'CGSR2', 'R', 'false');
INSERT INTO backends VALUES (DEFAULT, 'GBT Digital Continuum Receiver', 'DCR', 'D', 'false');
INSERT INTO backends VALUES (DEFAULT, 'GBT Spectrometer', 'gbtSpec', 'S', 'false');
INSERT INTO backends VALUES (DEFAULT, 'Green Bank Astronomical Signal Processor', 'GASP', 'Y', 'false');
INSERT INTO backends VALUES (DEFAULT, 'Green bank Ultimate Pulsar Processor', 'GUPPY', 'U', 'false');
INSERT INTO backends VALUES (DEFAULT, 'Haystack Mark 4 High bandwidth (> 1Gb/s)', 'HayMark4', '4', 'false');
INSERT INTO backends VALUES (DEFAULT, 'Mark 5 recorder (disks)', 'Mark5', '5', 'false');
INSERT INTO backends VALUES (DEFAULT, 'Radar backend', 'Radar', 'X', 'false');
INSERT INTO backends VALUES (DEFAULT, 'S2 recorder', 'gbtS2', '2', 'false');
INSERT INTO backends VALUES (DEFAULT, 'Spectral Processor', 'gbtSpecP', 'P', 'false');
INSERT INTO backends VALUES (DEFAULT, 'VLBA recorder and DAR ', 'gbtVLBA', 'V', 'false');
INSERT INTO backends VALUES (DEFAULT, 'Zpectrometer ', 'Zpect', 'Z', 'false');
INSERT INTO backends VALUES (DEFAULT, 'User supplied or new backend ', 'Other', 'O', 'false');

INSERT INTO email_templates VALUES (DEFAULT, 'Blank', '', '');
