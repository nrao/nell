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

COPY calculator_switching (id, name) FROM stdin;
1	NA
2	BSW
3	BSW-PS
4	BSW-NOD
5	BSW-SRN
6	TP
7	TP-PS
8	TP-NOD
9	TP-SRN
10	IFSW
11	IFSW-PS
12	IFSW-NOD
13	IFSW-SRN
14	OFSW
15	OFSW-PS
16	OFSW-NOD
17	OFSW-SRN
\.


--
-- PostgreSQL database dump complete
--

