--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'LATIN1';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

--
-- Name: calculator_switching_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('calculator_switching_id_seq', 17, true);


--
-- Data for Name: calculator_switching; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY calculator_switching (id, name, abbreviation) FROM stdin USING DELIMITERS ',';
1,NA,NA
2,Beam switching,BSW
3,Beam Switching - Position Switching,BSW-PS
4,Beam Switching - Nodding between beams,BSW-NOD
5,Beam Switching - Sub-reflector nodding between beams,BSW-SRN
6,Total Power,TP
7,Total Power - Position Switching,TP-PS
8,Total Power - Nodding between beams,TP-NOD
9,Total Power - Sub-reflector nodding between beams,TP-SRN
10,In-Band Frequency Switching,IFSW
11,In-Band Frequency Switching - Position Switching,IFSW-PS
12,In-Band Frequency Switching - Nodding between beams,IFSW-NOD
13,In-Band Frequency Switching - Sub-reflector nodding between beams,IFSW-SRN
14,Out-of-Band Frequency Switching,OFSW
15,Out-of-Band Frequency Switching - Position Switching,OFSW-PS
16,Out-of-Band Frequency Switching - Nodding between beams,OFSW-NOD
17,Out-of-Band Frequency Switching - Sub-reflector nodding between beams,OFSW-SRN
\.


--
-- PostgreSQL database dump complete
--

