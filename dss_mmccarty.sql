--
-- PostgreSQL database dump
--

SET client_encoding = 'LATIN1';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: allotment; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE allotment (
    id integer NOT NULL,
    psc_time double precision NOT NULL,
    total_time double precision NOT NULL,
    max_semester_time double precision NOT NULL,
    grade double precision NOT NULL
);


ALTER TABLE public.allotment OWNER TO dss;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE auth_group (
    id integer NOT NULL,
    name character varying(80) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO dss;

--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO dss;

--
-- Name: auth_message; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE auth_message (
    id integer NOT NULL,
    user_id integer NOT NULL,
    message text NOT NULL
);


ALTER TABLE public.auth_message OWNER TO dss;

--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE auth_permission (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO dss;

--
-- Name: auth_user; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE auth_user (
    id integer NOT NULL,
    username character varying(30) NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(30) NOT NULL,
    email character varying(75) NOT NULL,
    password character varying(128) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    is_superuser boolean NOT NULL,
    last_login timestamp with time zone NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


ALTER TABLE public.auth_user OWNER TO dss;

--
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE auth_user_groups (
    id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.auth_user_groups OWNER TO dss;

--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE auth_user_user_permissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_user_user_permissions OWNER TO dss;

--
-- Name: cadences; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE cadences (
    id integer NOT NULL,
    session_id integer NOT NULL,
    start_date timestamp with time zone,
    end_date timestamp with time zone,
    repeats integer,
    full_size character varying(64),
    intervals character varying(64)
);


ALTER TABLE public.cadences OWNER TO dss;

--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    user_id integer NOT NULL,
    content_type_id integer,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO dss;

--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE django_content_type (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO dss;

--
-- Name: django_session; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO dss;

--
-- Name: django_site; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE django_site (
    id integer NOT NULL,
    domain character varying(100) NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.django_site OWNER TO dss;

--
-- Name: investigators; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE investigators (
    id integer NOT NULL,
    project_id integer NOT NULL,
    user_id integer NOT NULL,
    friend boolean NOT NULL,
    observer boolean NOT NULL,
    principal_contact boolean NOT NULL,
    priority integer NOT NULL
);


ALTER TABLE public.investigators OWNER TO dss;

--
-- Name: observing_parameters; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE observing_parameters (
    id integer NOT NULL,
    session_id integer NOT NULL,
    parameter_id integer NOT NULL,
    string_value character varying(64),
    integer_value integer,
    float_value double precision,
    boolean_value boolean,
    datetime_value timestamp with time zone
);


ALTER TABLE public.observing_parameters OWNER TO dss;

--
-- Name: observing_types; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE observing_types (
    id integer NOT NULL,
    type character varying(64) NOT NULL
);


ALTER TABLE public.observing_types OWNER TO dss;

--
-- Name: opportunities; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE opportunities (
    id integer NOT NULL,
    window_id integer NOT NULL,
    start_time timestamp with time zone NOT NULL,
    duration double precision NOT NULL
);


ALTER TABLE public.opportunities OWNER TO dss;

--
-- Name: parameters; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE parameters (
    id integer NOT NULL,
    name character varying(64) NOT NULL,
    type character varying(32) NOT NULL
);


ALTER TABLE public.parameters OWNER TO dss;

--
-- Name: project_types; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE project_types (
    id integer NOT NULL,
    type character varying(64) NOT NULL
);


ALTER TABLE public.project_types OWNER TO dss;

--
-- Name: projects; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE projects (
    id integer NOT NULL,
    semester_id integer NOT NULL,
    project_type_id integer NOT NULL,
    pcode character varying(32) NOT NULL,
    name character varying(150) NOT NULL,
    thesis boolean NOT NULL,
    complete boolean NOT NULL,
    ignore_grade boolean NOT NULL,
    start_date timestamp with time zone,
    end_date timestamp with time zone
);


ALTER TABLE public.projects OWNER TO dss;

--
-- Name: projects_allotments; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE projects_allotments (
    id integer NOT NULL,
    project_id integer NOT NULL,
    allotment_id integer NOT NULL
);


ALTER TABLE public.projects_allotments OWNER TO dss;

--
-- Name: receiver_groups; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE receiver_groups (
    id integer NOT NULL,
    session_id integer NOT NULL
);


ALTER TABLE public.receiver_groups OWNER TO dss;

--
-- Name: receiver_groups_receivers; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE receiver_groups_receivers (
    id integer NOT NULL,
    receiver_group_id integer NOT NULL,
    receiver_id integer NOT NULL
);


ALTER TABLE public.receiver_groups_receivers OWNER TO dss;

--
-- Name: receiver_schedule; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE receiver_schedule (
    id integer NOT NULL,
    receiver_id integer NOT NULL,
    start_date timestamp with time zone
);


ALTER TABLE public.receiver_schedule OWNER TO dss;

--
-- Name: receivers; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE receivers (
    id integer NOT NULL,
    name character varying(32) NOT NULL,
    abbreviation character varying(32) NOT NULL,
    freq_low double precision NOT NULL,
    freq_hi double precision NOT NULL
);


ALTER TABLE public.receivers OWNER TO dss;

--
-- Name: semesters; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE semesters (
    id integer NOT NULL,
    semester character varying(64) NOT NULL
);


ALTER TABLE public.semesters OWNER TO dss;

--
-- Name: sesshuns_email; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE sesshuns_email (
    id integer NOT NULL,
    user_id integer NOT NULL,
    email character varying(255) NOT NULL
);


ALTER TABLE public.sesshuns_email OWNER TO dss;

--
-- Name: session_types; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE session_types (
    id integer NOT NULL,
    type character varying(64) NOT NULL
);


ALTER TABLE public.session_types OWNER TO dss;

--
-- Name: sessions; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE sessions (
    id integer NOT NULL,
    project_id integer NOT NULL,
    session_type_id integer NOT NULL,
    observing_type_id integer NOT NULL,
    allotment_id integer NOT NULL,
    status_id integer NOT NULL,
    original_id integer,
    name character varying(64),
    frequency double precision,
    max_duration double precision,
    min_duration double precision,
    time_between double precision,
    selected boolean NOT NULL
);


ALTER TABLE public.sessions OWNER TO dss;

--
-- Name: status; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE status (
    id integer NOT NULL,
    enabled boolean NOT NULL,
    authorized boolean NOT NULL,
    complete boolean NOT NULL,
    backup boolean NOT NULL
);


ALTER TABLE public.status OWNER TO dss;

--
-- Name: systems; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE systems (
    id integer NOT NULL,
    name character varying(32) NOT NULL,
    v_unit character varying(32) NOT NULL,
    h_unit character varying(32) NOT NULL
);


ALTER TABLE public.systems OWNER TO dss;

--
-- Name: targets; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE targets (
    id integer NOT NULL,
    session_id integer NOT NULL,
    system_id integer NOT NULL,
    source character varying(32),
    vertical double precision NOT NULL,
    horizontal double precision NOT NULL
);


ALTER TABLE public.targets OWNER TO dss;

--
-- Name: users; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE users (
    id integer NOT NULL,
    original_id integer NOT NULL,
    pst_id integer,
    username character varying(32),
    sancioned boolean NOT NULL,
    first_name character varying(32) NOT NULL,
    last_name character varying(150) NOT NULL
);


ALTER TABLE public.users OWNER TO dss;

--
-- Name: windows; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE windows (
    id integer NOT NULL,
    session_id integer NOT NULL,
    required boolean NOT NULL
);


ALTER TABLE public.windows OWNER TO dss;

--
-- Name: allotment_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE allotment_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.allotment_id_seq OWNER TO dss;

--
-- Name: allotment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE allotment_id_seq OWNED BY allotment.id;


--
-- Name: allotment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('allotment_id_seq', 359, true);


--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO dss;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE auth_group_id_seq OWNED BY auth_group.id;


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO dss;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE auth_group_permissions_id_seq OWNED BY auth_group_permissions.id;


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_message_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE auth_message_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_message_id_seq OWNER TO dss;

--
-- Name: auth_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE auth_message_id_seq OWNED BY auth_message.id;


--
-- Name: auth_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('auth_message_id_seq', 1, true);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE auth_permission_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO dss;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE auth_permission_id_seq OWNED BY auth_permission.id;


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('auth_permission_id_seq', 87, true);


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_user_groups_id_seq OWNER TO dss;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE auth_user_groups_id_seq OWNED BY auth_user_groups.id;


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('auth_user_groups_id_seq', 1, false);


--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE auth_user_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_user_id_seq OWNER TO dss;

--
-- Name: auth_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE auth_user_id_seq OWNED BY auth_user.id;


--
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('auth_user_id_seq', 1, true);


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.auth_user_user_permissions_id_seq OWNER TO dss;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE auth_user_user_permissions_id_seq OWNED BY auth_user_user_permissions.id;


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('auth_user_user_permissions_id_seq', 1, false);


--
-- Name: cadences_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE cadences_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.cadences_id_seq OWNER TO dss;

--
-- Name: cadences_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE cadences_id_seq OWNED BY cadences.id;


--
-- Name: cadences_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('cadences_id_seq', 52, true);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE django_admin_log_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO dss;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE django_admin_log_id_seq OWNED BY django_admin_log.id;


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('django_admin_log_id_seq', 1, true);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE django_content_type_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO dss;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE django_content_type_id_seq OWNED BY django_content_type.id;


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('django_content_type_id_seq', 29, true);


--
-- Name: django_site_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE django_site_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.django_site_id_seq OWNER TO dss;

--
-- Name: django_site_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE django_site_id_seq OWNED BY django_site.id;


--
-- Name: django_site_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('django_site_id_seq', 1, true);


--
-- Name: investigators_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE investigators_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.investigators_id_seq OWNER TO dss;

--
-- Name: investigators_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE investigators_id_seq OWNED BY investigators.id;


--
-- Name: investigators_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('investigators_id_seq', 607, true);


--
-- Name: observing_parameters_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE observing_parameters_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.observing_parameters_id_seq OWNER TO dss;

--
-- Name: observing_parameters_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE observing_parameters_id_seq OWNED BY observing_parameters.id;


--
-- Name: observing_parameters_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('observing_parameters_id_seq', 87, true);


--
-- Name: observing_types_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE observing_types_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.observing_types_id_seq OWNER TO dss;

--
-- Name: observing_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE observing_types_id_seq OWNED BY observing_types.id;


--
-- Name: observing_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('observing_types_id_seq', 8, true);


--
-- Name: opportunities_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE opportunities_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.opportunities_id_seq OWNER TO dss;

--
-- Name: opportunities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE opportunities_id_seq OWNED BY opportunities.id;


--
-- Name: opportunities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('opportunities_id_seq', 97, true);


--
-- Name: parameters_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE parameters_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.parameters_id_seq OWNER TO dss;

--
-- Name: parameters_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE parameters_id_seq OWNED BY parameters.id;


--
-- Name: parameters_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('parameters_id_seq', 20, true);


--
-- Name: project_types_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE project_types_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.project_types_id_seq OWNER TO dss;

--
-- Name: project_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE project_types_id_seq OWNED BY project_types.id;


--
-- Name: project_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('project_types_id_seq', 2, true);


--
-- Name: projects_allotments_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE projects_allotments_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.projects_allotments_id_seq OWNER TO dss;

--
-- Name: projects_allotments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE projects_allotments_id_seq OWNED BY projects_allotments.id;


--
-- Name: projects_allotments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('projects_allotments_id_seq', 104, true);


--
-- Name: projects_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE projects_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.projects_id_seq OWNER TO dss;

--
-- Name: projects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE projects_id_seq OWNED BY projects.id;


--
-- Name: projects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('projects_id_seq', 101, true);


--
-- Name: receiver_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE receiver_groups_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.receiver_groups_id_seq OWNER TO dss;

--
-- Name: receiver_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE receiver_groups_id_seq OWNED BY receiver_groups.id;


--
-- Name: receiver_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('receiver_groups_id_seq', 254, true);


--
-- Name: receiver_groups_receivers_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE receiver_groups_receivers_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.receiver_groups_receivers_id_seq OWNER TO dss;

--
-- Name: receiver_groups_receivers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE receiver_groups_receivers_id_seq OWNED BY receiver_groups_receivers.id;


--
-- Name: receiver_groups_receivers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('receiver_groups_receivers_id_seq', 292, true);


--
-- Name: receiver_schedule_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE receiver_schedule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.receiver_schedule_id_seq OWNER TO dss;

--
-- Name: receiver_schedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE receiver_schedule_id_seq OWNED BY receiver_schedule.id;


--
-- Name: receiver_schedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('receiver_schedule_id_seq', 1, false);


--
-- Name: receivers_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE receivers_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.receivers_id_seq OWNER TO dss;

--
-- Name: receivers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE receivers_id_seq OWNED BY receivers.id;


--
-- Name: receivers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('receivers_id_seq', 18, true);


--
-- Name: semesters_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE semesters_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.semesters_id_seq OWNER TO dss;

--
-- Name: semesters_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE semesters_id_seq OWNED BY semesters.id;


--
-- Name: semesters_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('semesters_id_seq', 16, true);


--
-- Name: sesshuns_email_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE sesshuns_email_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.sesshuns_email_id_seq OWNER TO dss;

--
-- Name: sesshuns_email_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE sesshuns_email_id_seq OWNED BY sesshuns_email.id;


--
-- Name: sesshuns_email_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('sesshuns_email_id_seq', 356, true);


--
-- Name: session_types_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE session_types_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.session_types_id_seq OWNER TO dss;

--
-- Name: session_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE session_types_id_seq OWNED BY session_types.id;


--
-- Name: session_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('session_types_id_seq', 6, true);


--
-- Name: sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE sessions_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.sessions_id_seq OWNER TO dss;

--
-- Name: sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE sessions_id_seq OWNED BY sessions.id;


--
-- Name: sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('sessions_id_seq', 254, true);


--
-- Name: status_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE status_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.status_id_seq OWNER TO dss;

--
-- Name: status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE status_id_seq OWNED BY status.id;


--
-- Name: status_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('status_id_seq', 254, true);


--
-- Name: systems_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE systems_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.systems_id_seq OWNER TO dss;

--
-- Name: systems_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE systems_id_seq OWNED BY systems.id;


--
-- Name: systems_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('systems_id_seq', 9, true);


--
-- Name: targets_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE targets_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.targets_id_seq OWNER TO dss;

--
-- Name: targets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE targets_id_seq OWNED BY targets.id;


--
-- Name: targets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('targets_id_seq', 253, true);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE users_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO dss;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE users_id_seq OWNED BY users.id;


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('users_id_seq', 287, true);


--
-- Name: windows_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE windows_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.windows_id_seq OWNER TO dss;

--
-- Name: windows_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE windows_id_seq OWNED BY windows.id;


--
-- Name: windows_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('windows_id_seq', 83, true);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE allotment ALTER COLUMN id SET DEFAULT nextval('allotment_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE auth_group ALTER COLUMN id SET DEFAULT nextval('auth_group_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('auth_group_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE auth_message ALTER COLUMN id SET DEFAULT nextval('auth_message_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE auth_permission ALTER COLUMN id SET DEFAULT nextval('auth_permission_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE auth_user ALTER COLUMN id SET DEFAULT nextval('auth_user_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE auth_user_groups ALTER COLUMN id SET DEFAULT nextval('auth_user_groups_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('auth_user_user_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE cadences ALTER COLUMN id SET DEFAULT nextval('cadences_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE django_admin_log ALTER COLUMN id SET DEFAULT nextval('django_admin_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE django_content_type ALTER COLUMN id SET DEFAULT nextval('django_content_type_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE django_site ALTER COLUMN id SET DEFAULT nextval('django_site_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE investigators ALTER COLUMN id SET DEFAULT nextval('investigators_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE observing_parameters ALTER COLUMN id SET DEFAULT nextval('observing_parameters_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE observing_types ALTER COLUMN id SET DEFAULT nextval('observing_types_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE opportunities ALTER COLUMN id SET DEFAULT nextval('opportunities_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE parameters ALTER COLUMN id SET DEFAULT nextval('parameters_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE project_types ALTER COLUMN id SET DEFAULT nextval('project_types_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE projects ALTER COLUMN id SET DEFAULT nextval('projects_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE projects_allotments ALTER COLUMN id SET DEFAULT nextval('projects_allotments_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE receiver_groups ALTER COLUMN id SET DEFAULT nextval('receiver_groups_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE receiver_groups_receivers ALTER COLUMN id SET DEFAULT nextval('receiver_groups_receivers_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE receiver_schedule ALTER COLUMN id SET DEFAULT nextval('receiver_schedule_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE receivers ALTER COLUMN id SET DEFAULT nextval('receivers_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE semesters ALTER COLUMN id SET DEFAULT nextval('semesters_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE sesshuns_email ALTER COLUMN id SET DEFAULT nextval('sesshuns_email_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE session_types ALTER COLUMN id SET DEFAULT nextval('session_types_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE sessions ALTER COLUMN id SET DEFAULT nextval('sessions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE status ALTER COLUMN id SET DEFAULT nextval('status_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE systems ALTER COLUMN id SET DEFAULT nextval('systems_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE targets ALTER COLUMN id SET DEFAULT nextval('targets_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval('users_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE windows ALTER COLUMN id SET DEFAULT nextval('windows_id_seq'::regclass);


--
-- Data for Name: allotment; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO allotment VALUES (1, 100.5, 100.5, 100.5, 4);
INSERT INTO allotment VALUES (2, 808, 808, 808, 4);
INSERT INTO allotment VALUES (3, 96, 96, 96, 4);
INSERT INTO allotment VALUES (4, 32, 32, 32, 4);
INSERT INTO allotment VALUES (5, 10, 10, 10, 4);
INSERT INTO allotment VALUES (6, 8, 8, 8, 4);
INSERT INTO allotment VALUES (7, 6, 6, 6, 4);
INSERT INTO allotment VALUES (8, 40, 40, 40, 4);
INSERT INTO allotment VALUES (9, 5.5, 5.5, 5.5, 4);
INSERT INTO allotment VALUES (10, 5, 5, 5, 4);
INSERT INTO allotment VALUES (11, 1.5, 1.5, 1.5, 4);
INSERT INTO allotment VALUES (12, 5, 5, 5, 4);
INSERT INTO allotment VALUES (13, 204, 204, 204, 4);
INSERT INTO allotment VALUES (14, 14.5, 14.5, 14.5, 4);
INSERT INTO allotment VALUES (15, 45, 45, 45, 4);
INSERT INTO allotment VALUES (16, 10, 10, 10, 4);
INSERT INTO allotment VALUES (17, 12, 12, 12, 4);
INSERT INTO allotment VALUES (18, 4.5, 4.5, 4.5, 3);
INSERT INTO allotment VALUES (19, 3, 3, 3, 4);
INSERT INTO allotment VALUES (20, 4.4000000000000004, 4.4000000000000004, 4.4000000000000004, 4);
INSERT INTO allotment VALUES (21, 27, 27, 27, 4);
INSERT INTO allotment VALUES (22, 26.75, 26.75, 26.75, 4);
INSERT INTO allotment VALUES (23, 6, 6, 6, 4);
INSERT INTO allotment VALUES (24, 11, 11, 11, 4);
INSERT INTO allotment VALUES (25, 20, 20, 20, 4);
INSERT INTO allotment VALUES (26, 10, 10, 10, 4);
INSERT INTO allotment VALUES (27, 24, 24, 24, 4);
INSERT INTO allotment VALUES (28, 6, 6, 6, 4);
INSERT INTO allotment VALUES (29, 37.75, 37.75, 37.75, 4);
INSERT INTO allotment VALUES (30, 24, 24, 24, 4);
INSERT INTO allotment VALUES (31, 120, 120, 120, 4);
INSERT INTO allotment VALUES (32, 12, 12, 12, 4);
INSERT INTO allotment VALUES (33, 6, 6, 6, 4);
INSERT INTO allotment VALUES (34, 18.670000000000002, 18.670000000000002, 18.670000000000002, 4);
INSERT INTO allotment VALUES (35, 7, 7, 7, 4);
INSERT INTO allotment VALUES (36, 44, 44, 44, 4);
INSERT INTO allotment VALUES (37, 17, 17, 17, 4);
INSERT INTO allotment VALUES (38, 8.5, 8.5, 8.5, 4);
INSERT INTO allotment VALUES (39, 25, 25, 25, 3);
INSERT INTO allotment VALUES (40, 12, 12, 12, 4);
INSERT INTO allotment VALUES (41, 30, 30, 30, 3);
INSERT INTO allotment VALUES (42, 30, 30, 30, 3);
INSERT INTO allotment VALUES (43, 35.75, 35.75, 35.75, 4);
INSERT INTO allotment VALUES (44, 5, 5, 5, 3);
INSERT INTO allotment VALUES (45, 25.02, 25.02, 25.02, 4);
INSERT INTO allotment VALUES (46, 17.600000000000001, 17.600000000000001, 17.600000000000001, 3);
INSERT INTO allotment VALUES (47, 4, 4, 4, 4);
INSERT INTO allotment VALUES (48, 60, 60, 60, 4);
INSERT INTO allotment VALUES (49, 53.880000000000003, 53.880000000000003, 53.880000000000003, 3);
INSERT INTO allotment VALUES (50, 10.4, 10.4, 10.4, 3);
INSERT INTO allotment VALUES (51, 10, 10, 10, 4);
INSERT INTO allotment VALUES (52, 10.550000000000001, 10.550000000000001, 10.550000000000001, 3);
INSERT INTO allotment VALUES (53, 10, 10, 10, 4);
INSERT INTO allotment VALUES (54, 7, 7, 7, 3);
INSERT INTO allotment VALUES (55, 16, 16, 16, 3);
INSERT INTO allotment VALUES (56, 34, 34, 34, 4);
INSERT INTO allotment VALUES (57, 20, 20, 20, 4);
INSERT INTO allotment VALUES (58, 6, 6, 6, 4);
INSERT INTO allotment VALUES (59, 18.5, 18.5, 18.5, 4);
INSERT INTO allotment VALUES (60, 50, 50, 50, 4);
INSERT INTO allotment VALUES (61, 50, 50, 50, 4);
INSERT INTO allotment VALUES (62, 11.5, 11.5, 11.5, 3);
INSERT INTO allotment VALUES (63, 11, 11, 11, 3);
INSERT INTO allotment VALUES (64, 19.399999999999999, 19.399999999999999, 19.399999999999999, 4);
INSERT INTO allotment VALUES (65, 21, 21, 21, 4);
INSERT INTO allotment VALUES (66, 18, 18, 18, 4);
INSERT INTO allotment VALUES (67, 14, 14, 14, 4);
INSERT INTO allotment VALUES (68, 8, 8, 8, 3);
INSERT INTO allotment VALUES (69, 11, 11, 11, 3);
INSERT INTO allotment VALUES (70, 71.599999999999994, 71.599999999999994, 71.599999999999994, 4);
INSERT INTO allotment VALUES (71, 15, 15, 15, 4);
INSERT INTO allotment VALUES (72, 15, 15, 15, 3);
INSERT INTO allotment VALUES (73, 4.5, 4.5, 4.5, 3);
INSERT INTO allotment VALUES (74, 20, 20, 20, 4);
INSERT INTO allotment VALUES (75, 20, 20, 20, 3);
INSERT INTO allotment VALUES (76, 20, 20, 20, 4);
INSERT INTO allotment VALUES (77, 20, 20, 20, 3);
INSERT INTO allotment VALUES (78, 16.25, 16.25, 16.25, 3);
INSERT INTO allotment VALUES (79, 15, 15, 15, 4);
INSERT INTO allotment VALUES (80, 9.5, 9.5, 9.5, 4);
INSERT INTO allotment VALUES (81, 7, 7, 7, 3);
INSERT INTO allotment VALUES (82, 11, 11, 11, 4);
INSERT INTO allotment VALUES (83, 31.5, 31.5, 31.5, 4);
INSERT INTO allotment VALUES (84, 18, 18, 18, 4);
INSERT INTO allotment VALUES (85, 4, 4, 4, 4);
INSERT INTO allotment VALUES (86, 38.5, 38.5, 38.5, 3);
INSERT INTO allotment VALUES (87, 104.5, 104.5, 104.5, 4);
INSERT INTO allotment VALUES (88, 12, 12, 12, 4);
INSERT INTO allotment VALUES (89, 82.400000000000006, 82.400000000000006, 82.400000000000006, 4);
INSERT INTO allotment VALUES (90, 21, 21, 21, 3);
INSERT INTO allotment VALUES (91, 152, 152, 152, 3);
INSERT INTO allotment VALUES (92, 4, 4, 4, 3);
INSERT INTO allotment VALUES (93, 80, 80, 80, 3);
INSERT INTO allotment VALUES (94, 2, 2, 2, 3);
INSERT INTO allotment VALUES (95, 3.5, 3.5, 3.5, 4);
INSERT INTO allotment VALUES (96, 28, 28, 28, 4);
INSERT INTO allotment VALUES (97, 672, 672, 672, 4);
INSERT INTO allotment VALUES (98, 88, 88, 88, 3);
INSERT INTO allotment VALUES (99, 15, 15, 15, 3);
INSERT INTO allotment VALUES (100, 30, 30, 30, 3);
INSERT INTO allotment VALUES (101, 10.5, 10.5, 10.5, 4);
INSERT INTO allotment VALUES (102, 14, 14, 14, 3);
INSERT INTO allotment VALUES (103, 16, 16, 16, 4);
INSERT INTO allotment VALUES (104, 9, 9, 9, 4);
INSERT INTO allotment VALUES (105, 12, 12, 12, 4);
INSERT INTO allotment VALUES (110, 64, 64, 64, 4);
INSERT INTO allotment VALUES (111, 48, 48, 48, 4);
INSERT INTO allotment VALUES (112, 56, 56, 56, 4);
INSERT INTO allotment VALUES (113, 56, 56, 56, 4);
INSERT INTO allotment VALUES (114, 40, 40, 40, 4);
INSERT INTO allotment VALUES (115, 40, 40, 40, 4);
INSERT INTO allotment VALUES (116, 40, 40, 40, 4);
INSERT INTO allotment VALUES (117, 48, 48, 48, 4);
INSERT INTO allotment VALUES (118, 56, 56, 56, 4);
INSERT INTO allotment VALUES (119, 48, 48, 48, 4);
INSERT INTO allotment VALUES (120, 56, 56, 56, 4);
INSERT INTO allotment VALUES (121, 48, 48, 48, 4);
INSERT INTO allotment VALUES (122, 96, 96, 96, 4);
INSERT INTO allotment VALUES (123, 32, 32, 32, 4);
INSERT INTO allotment VALUES (124, 10, 10, 10, 4);
INSERT INTO allotment VALUES (127, 10, 10, 10, 4);
INSERT INTO allotment VALUES (128, 10, 10, 10, 4);
INSERT INTO allotment VALUES (129, 10, 10, 10, 4);
INSERT INTO allotment VALUES (130, 10, 10, 10, 4);
INSERT INTO allotment VALUES (131, 2.75, 2.75, 2.75, 4);
INSERT INTO allotment VALUES (132, 2.75, 2.75, 2.75, 4);
INSERT INTO allotment VALUES (133, 5, 5, 5, 4);
INSERT INTO allotment VALUES (134, 1.5, 1.5, 1.5, 4);
INSERT INTO allotment VALUES (135, 5, 5, 5, 4);
INSERT INTO allotment VALUES (136, 102, 102, 102, 4);
INSERT INTO allotment VALUES (137, 96, 96, 96, 4);
INSERT INTO allotment VALUES (138, 6, 6, 6, 4);
INSERT INTO allotment VALUES (139, 5.7999999999999998, 5.7999999999999998, 5.7999999999999998, 4);
INSERT INTO allotment VALUES (140, 8.6999999999999993, 8.6999999999999993, 8.6999999999999993, 4);
INSERT INTO allotment VALUES (143, 10, 10, 10, 4);
INSERT INTO allotment VALUES (144, 12, 12, 12, 4);
INSERT INTO allotment VALUES (145, 4.5, 4.5, 4.5, 3);
INSERT INTO allotment VALUES (146, 3, 3, 3, 4);
INSERT INTO allotment VALUES (147, 2.3999999999999999, 2.3999999999999999, 2.3999999999999999, 4);
INSERT INTO allotment VALUES (148, 2, 2, 2, 4);
INSERT INTO allotment VALUES (149, 7, 7, 7, 4);
INSERT INTO allotment VALUES (150, 7, 7, 7, 4);
INSERT INTO allotment VALUES (151, 6, 6, 6, 4);
INSERT INTO allotment VALUES (152, 7, 7, 7, 4);
INSERT INTO allotment VALUES (157, 6, 6, 6, 4);
INSERT INTO allotment VALUES (158, 5.5, 5.5, 5.5, 4);
INSERT INTO allotment VALUES (159, 5.5, 5.5, 5.5, 4);
INSERT INTO allotment VALUES (160, 20, 20, 20, 4);
INSERT INTO allotment VALUES (161, 10, 10, 10, 4);
INSERT INTO allotment VALUES (162, 8, 8, 8, 4);
INSERT INTO allotment VALUES (163, 16, 16, 16, 4);
INSERT INTO allotment VALUES (164, 6, 6, 6, 4);
INSERT INTO allotment VALUES (167, 24, 24, 24, 4);
INSERT INTO allotment VALUES (168, 8, 8, 8, 4);
INSERT INTO allotment VALUES (169, 20, 20, 20, 4);
INSERT INTO allotment VALUES (170, 20, 20, 20, 4);
INSERT INTO allotment VALUES (171, 72, 72, 72, 4);
INSERT INTO allotment VALUES (172, 6, 6, 6, 4);
INSERT INTO allotment VALUES (173, 6, 6, 6, 4);
INSERT INTO allotment VALUES (174, 6, 6, 6, 4);
INSERT INTO allotment VALUES (175, 14.67, 14.67, 14.67, 4);
INSERT INTO allotment VALUES (176, 4, 4, 4, 4);
INSERT INTO allotment VALUES (177, 7, 7, 7, 4);
INSERT INTO allotment VALUES (178, 15.199999999999999, 15.199999999999999, 15.199999999999999, 4);
INSERT INTO allotment VALUES (179, 9, 9, 9, 4);
INSERT INTO allotment VALUES (180, 19.800000000000001, 19.800000000000001, 19.800000000000001, 4);
INSERT INTO allotment VALUES (181, 8, 8, 8, 4);
INSERT INTO allotment VALUES (182, 9, 9, 9, 4);
INSERT INTO allotment VALUES (183, 8.5, 8.5, 8.5, 4);
INSERT INTO allotment VALUES (184, 25, 25, 25, 3);
INSERT INTO allotment VALUES (185, 12, 12, 12, 4);
INSERT INTO allotment VALUES (186, 10, 10, 10, 3);
INSERT INTO allotment VALUES (187, 10, 10, 10, 3);
INSERT INTO allotment VALUES (188, 10, 10, 10, 3);
INSERT INTO allotment VALUES (189, 17.5, 17.5, 17.5, 3);
INSERT INTO allotment VALUES (190, 12.5, 12.5, 12.5, 3);
INSERT INTO allotment VALUES (191, 7.1500000000000004, 7.1500000000000004, 7.1500000000000004, 4);
INSERT INTO allotment VALUES (192, 10.4, 10.4, 10.4, 4);
INSERT INTO allotment VALUES (193, 5.2000000000000002, 5.2000000000000002, 5.2000000000000002, 4);
INSERT INTO allotment VALUES (194, 13, 13, 13, 4);
INSERT INTO allotment VALUES (195, 5, 5, 5, 3);
INSERT INTO allotment VALUES (196, 1.3999999999999999, 1.3999999999999999, 1.3999999999999999, 4);
INSERT INTO allotment VALUES (197, 3.3999999999999999, 3.3999999999999999, 3.3999999999999999, 4);
INSERT INTO allotment VALUES (198, 1.3999999999999999, 1.3999999999999999, 1.3999999999999999, 4);
INSERT INTO allotment VALUES (199, 4.4199999999999999, 4.4199999999999999, 4.4199999999999999, 4);
INSERT INTO allotment VALUES (200, 6.4000000000000004, 6.4000000000000004, 6.4000000000000004, 4);
INSERT INTO allotment VALUES (201, 1.3999999999999999, 1.3999999999999999, 1.3999999999999999, 4);
INSERT INTO allotment VALUES (202, 1.3999999999999999, 1.3999999999999999, 1.3999999999999999, 4);
INSERT INTO allotment VALUES (203, 1.3999999999999999, 1.3999999999999999, 1.3999999999999999, 4);
INSERT INTO allotment VALUES (204, 1.3999999999999999, 1.3999999999999999, 1.3999999999999999, 4);
INSERT INTO allotment VALUES (205, 2.3999999999999999, 2.3999999999999999, 2.3999999999999999, 4);
INSERT INTO allotment VALUES (206, 2.2000000000000002, 2.2000000000000002, 2.2000000000000002, 3);
INSERT INTO allotment VALUES (207, 2.2000000000000002, 2.2000000000000002, 2.2000000000000002, 3);
INSERT INTO allotment VALUES (208, 2.2000000000000002, 2.2000000000000002, 2.2000000000000002, 3);
INSERT INTO allotment VALUES (209, 2.2000000000000002, 2.2000000000000002, 2.2000000000000002, 3);
INSERT INTO allotment VALUES (210, 2.2000000000000002, 2.2000000000000002, 2.2000000000000002, 3);
INSERT INTO allotment VALUES (211, 2.2000000000000002, 2.2000000000000002, 2.2000000000000002, 3);
INSERT INTO allotment VALUES (212, 2.2000000000000002, 2.2000000000000002, 2.2000000000000002, 3);
INSERT INTO allotment VALUES (213, 2.2000000000000002, 2.2000000000000002, 2.2000000000000002, 3);
INSERT INTO allotment VALUES (214, 4, 4, 4, 4);
INSERT INTO allotment VALUES (215, 40, 40, 40, 4);
INSERT INTO allotment VALUES (216, 20, 20, 20, 4);
INSERT INTO allotment VALUES (217, 15.75, 15.75, 15.75, 3);
INSERT INTO allotment VALUES (218, 33, 33, 33, 3);
INSERT INTO allotment VALUES (219, 5.1299999999999999, 5.1299999999999999, 5.1299999999999999, 3);
INSERT INTO allotment VALUES (220, 0, 0, 0, 3);
INSERT INTO allotment VALUES (221, 1.73, 1.73, 1.73, 3);
INSERT INTO allotment VALUES (222, 4.7699999999999996, 4.7699999999999996, 4.7699999999999996, 3);
INSERT INTO allotment VALUES (223, 1.3, 1.3, 1.3, 3);
INSERT INTO allotment VALUES (224, 2.6000000000000001, 2.6000000000000001, 2.6000000000000001, 3);
INSERT INTO allotment VALUES (225, 2, 2, 2, 4);
INSERT INTO allotment VALUES (226, 8, 8, 8, 4);
INSERT INTO allotment VALUES (227, 10.550000000000001, 10.550000000000001, 10.550000000000001, 3);
INSERT INTO allotment VALUES (228, 10, 10, 10, 4);
INSERT INTO allotment VALUES (229, 3.5, 3.5, 3.5, 3);
INSERT INTO allotment VALUES (230, 3.5, 3.5, 3.5, 3);
INSERT INTO allotment VALUES (231, 0, 0, 0, 3);
INSERT INTO allotment VALUES (232, 8, 8, 8, 3);
INSERT INTO allotment VALUES (233, 8, 8, 8, 3);
INSERT INTO allotment VALUES (234, 12, 12, 12, 4);
INSERT INTO allotment VALUES (235, 10, 10, 10, 4);
INSERT INTO allotment VALUES (236, 12, 12, 12, 4);
INSERT INTO allotment VALUES (237, 4, 4, 4, 4);
INSERT INTO allotment VALUES (238, 6, 6, 6, 4);
INSERT INTO allotment VALUES (239, 3, 3, 3, 4);
INSERT INTO allotment VALUES (240, 5, 5, 5, 4);
INSERT INTO allotment VALUES (241, 2, 2, 2, 4);
INSERT INTO allotment VALUES (242, 6, 6, 6, 4);
INSERT INTO allotment VALUES (243, 4, 4, 4, 4);
INSERT INTO allotment VALUES (244, 3.5, 3.5, 3.5, 4);
INSERT INTO allotment VALUES (245, 3, 3, 3, 4);
INSERT INTO allotment VALUES (246, 2, 2, 2, 4);
INSERT INTO allotment VALUES (247, 3, 3, 3, 4);
INSERT INTO allotment VALUES (248, 3, 3, 3, 4);
INSERT INTO allotment VALUES (249, 50, 50, 50, 4);
INSERT INTO allotment VALUES (250, 50, 50, 50, 4);
INSERT INTO allotment VALUES (251, 3.5, 3.5, 3.5, 3);
INSERT INTO allotment VALUES (252, 3.5, 3.5, 3.5, 3);
INSERT INTO allotment VALUES (253, 4.5, 4.5, 4.5, 3);
INSERT INTO allotment VALUES (254, 5.5, 5.5, 5.5, 3);
INSERT INTO allotment VALUES (255, 5.5, 5.5, 5.5, 3);
INSERT INTO allotment VALUES (256, 1.73, 1.73, 1.73, 4);
INSERT INTO allotment VALUES (257, 6.3600000000000003, 6.3600000000000003, 6.3600000000000003, 4);
INSERT INTO allotment VALUES (258, 1.3, 1.3, 1.3, 4);
INSERT INTO allotment VALUES (259, 4.7699999999999996, 4.7699999999999996, 4.7699999999999996, 4);
INSERT INTO allotment VALUES (260, 3.8999999999999999, 3.8999999999999999, 3.8999999999999999, 4);
INSERT INTO allotment VALUES (261, 1.3, 1.3, 1.3, 4);
INSERT INTO allotment VALUES (262, 15, 15, 15, 4);
INSERT INTO allotment VALUES (263, 2, 2, 2, 4);
INSERT INTO allotment VALUES (264, 1, 1, 1, 4);
INSERT INTO allotment VALUES (265, 3, 3, 3, 4);
INSERT INTO allotment VALUES (266, 18, 18, 18, 4);
INSERT INTO allotment VALUES (267, 4, 4, 4, 3);
INSERT INTO allotment VALUES (268, 4, 4, 4, 3);
INSERT INTO allotment VALUES (269, 14, 14, 14, 4);
INSERT INTO allotment VALUES (270, 11, 11, 11, 3);
INSERT INTO allotment VALUES (271, 44.799999999999997, 44.799999999999997, 44.799999999999997, 4);
INSERT INTO allotment VALUES (272, 26.800000000000001, 26.800000000000001, 26.800000000000001, 4);
INSERT INTO allotment VALUES (273, 0.01, 0.01, 0.01, 4);
INSERT INTO allotment VALUES (274, 15, 15, 15, 3);
INSERT INTO allotment VALUES (275, 15, 15, 15, 4);
INSERT INTO allotment VALUES (276, 4.5, 4.5, 4.5, 3);
INSERT INTO allotment VALUES (277, 20, 20, 20, 4);
INSERT INTO allotment VALUES (278, 20, 20, 20, 3);
INSERT INTO allotment VALUES (279, 10, 10, 10, 4);
INSERT INTO allotment VALUES (280, 10, 10, 10, 4);
INSERT INTO allotment VALUES (281, 7, 7, 7, 3);
INSERT INTO allotment VALUES (282, 7, 7, 7, 3);
INSERT INTO allotment VALUES (283, 3, 3, 3, 3);
INSERT INTO allotment VALUES (284, 3, 3, 3, 3);
INSERT INTO allotment VALUES (285, 7, 7, 7, 3);
INSERT INTO allotment VALUES (286, 2, 2, 2, 3);
INSERT INTO allotment VALUES (287, 2, 2, 2, 3);
INSERT INTO allotment VALUES (288, 5.25, 5.25, 5.25, 3);
INSERT INTO allotment VALUES (289, 3.5, 3.5, 3.5, 4);
INSERT INTO allotment VALUES (290, 11.5, 11.5, 11.5, 4);
INSERT INTO allotment VALUES (291, 9.5, 9.5, 9.5, 4);
INSERT INTO allotment VALUES (292, 7, 7, 7, 3);
INSERT INTO allotment VALUES (293, 4.5, 4.5, 4.5, 4);
INSERT INTO allotment VALUES (294, 6.5, 6.5, 6.5, 4);
INSERT INTO allotment VALUES (295, 19, 19, 19, 4);
INSERT INTO allotment VALUES (296, 12.5, 12.5, 12.5, 4);
INSERT INTO allotment VALUES (297, 18, 18, 18, 4);
INSERT INTO allotment VALUES (298, 4, 4, 4, 4);
INSERT INTO allotment VALUES (299, 5.5, 5.5, 5.5, 3);
INSERT INTO allotment VALUES (300, 22, 22, 22, 3);
INSERT INTO allotment VALUES (301, 5.5, 5.5, 5.5, 3);
INSERT INTO allotment VALUES (302, 5.5, 5.5, 5.5, 3);
INSERT INTO allotment VALUES (303, 8.5, 8.5, 8.5, 4);
INSERT INTO allotment VALUES (304, 33, 33, 33, 4);
INSERT INTO allotment VALUES (305, 33, 33, 33, 4);
INSERT INTO allotment VALUES (306, 15, 15, 15, 4);
INSERT INTO allotment VALUES (307, 15, 15, 15, 4);
INSERT INTO allotment VALUES (308, 12, 12, 12, 4);
INSERT INTO allotment VALUES (309, 16.219999999999999, 16.219999999999999, 16.219999999999999, 4);
INSERT INTO allotment VALUES (310, 25.629999999999999, 25.629999999999999, 25.629999999999999, 4);
INSERT INTO allotment VALUES (312, 24.75, 24.75, 24.75, 4);
INSERT INTO allotment VALUES (313, 21, 21, 21, 3);
INSERT INTO allotment VALUES (314, 62, 62, 62, 3);
INSERT INTO allotment VALUES (315, 90, 90, 90, 3);
INSERT INTO allotment VALUES (316, 4, 4, 4, 3);
INSERT INTO allotment VALUES (317, 26, 26, 26, 3);
INSERT INTO allotment VALUES (318, 54, 54, 54, 3);
INSERT INTO allotment VALUES (319, 2, 2, 2, 3);
INSERT INTO allotment VALUES (320, 2, 2, 2, 4);
INSERT INTO allotment VALUES (321, 1.5, 1.5, 1.5, 4);
INSERT INTO allotment VALUES (322, 18, 18, 18, 4);
INSERT INTO allotment VALUES (323, 10, 10, 10, 4);
INSERT INTO allotment VALUES (324, 306, 306, 306, 4);
INSERT INTO allotment VALUES (325, 306, 306, 306, 4);
INSERT INTO allotment VALUES (326, 60, 60, 60, 4);
INSERT INTO allotment VALUES (327, 88, 88, 88, 3);
INSERT INTO allotment VALUES (328, 1, 1, 1, 3);
INSERT INTO allotment VALUES (329, 1, 1, 1, 3);
INSERT INTO allotment VALUES (330, 1, 1, 1, 3);
INSERT INTO allotment VALUES (331, 1, 1, 1, 3);
INSERT INTO allotment VALUES (332, 1, 1, 1, 3);
INSERT INTO allotment VALUES (333, 1, 1, 1, 3);
INSERT INTO allotment VALUES (334, 1, 1, 1, 3);
INSERT INTO allotment VALUES (335, 1, 1, 1, 3);
INSERT INTO allotment VALUES (336, 1, 1, 1, 3);
INSERT INTO allotment VALUES (337, 1, 1, 1, 3);
INSERT INTO allotment VALUES (338, 1, 1, 1, 3);
INSERT INTO allotment VALUES (339, 1, 1, 1, 3);
INSERT INTO allotment VALUES (340, 1, 1, 1, 3);
INSERT INTO allotment VALUES (341, 1, 1, 1, 3);
INSERT INTO allotment VALUES (342, 1, 1, 1, 3);
INSERT INTO allotment VALUES (343, 30, 30, 30, 3);
INSERT INTO allotment VALUES (344, 3.5, 3.5, 3.5, 3);
INSERT INTO allotment VALUES (345, 3.5, 3.5, 3.5, 3);
INSERT INTO allotment VALUES (346, 3.5, 3.5, 3.5, 3);
INSERT INTO allotment VALUES (347, 3.5, 3.5, 3.5, 3);
INSERT INTO allotment VALUES (348, 3.5, 3.5, 3.5, 4);
INSERT INTO allotment VALUES (349, 3.5, 3.5, 3.5, 4);
INSERT INTO allotment VALUES (350, 3.5, 3.5, 3.5, 4);
INSERT INTO allotment VALUES (351, 12, 12, 12, 4);
INSERT INTO allotment VALUES (352, 4, 4, 4, 4);
INSERT INTO allotment VALUES (353, 1.5, 1.5, 1.5, 4);
INSERT INTO allotment VALUES (354, 1.5, 1.5, 1.5, 4);
INSERT INTO allotment VALUES (355, 1.5, 1.5, 1.5, 4);
INSERT INTO allotment VALUES (356, 1.5, 1.5, 1.5, 4);
INSERT INTO allotment VALUES (357, 1.5, 1.5, 1.5, 4);
INSERT INTO allotment VALUES (358, 1.5, 1.5, 1.5, 4);
INSERT INTO allotment VALUES (359, 12, 12, 12, 4);
INSERT INTO allotment VALUES (311, 15.75, 15.75, 15.75, 4);
INSERT INTO allotment VALUES (107, 48, 48, 48, 4);
INSERT INTO allotment VALUES (108, 56, 56, 56, 4);
INSERT INTO allotment VALUES (109, 56, 56, 56, 4);
INSERT INTO allotment VALUES (166, 4, 4, 4, 4);
INSERT INTO allotment VALUES (165, 33.75, 33.75, 33.75, 4);
INSERT INTO allotment VALUES (142, 22.5, 22.5, 22.5, 4);
INSERT INTO allotment VALUES (141, 22.5, 22.5, 22.5, 4);
INSERT INTO allotment VALUES (125, 8, 8, 8, 4);
INSERT INTO allotment VALUES (154, 3.75, 3.75, 3.75, 4);
INSERT INTO allotment VALUES (106, 48, 48, 48, 4);
INSERT INTO allotment VALUES (126, 6, 6, 6, 4);
INSERT INTO allotment VALUES (155, 3.5, 3.5, 3.5, 4);
INSERT INTO allotment VALUES (156, 3.5, 3.5, 3.5, 4);
INSERT INTO allotment VALUES (153, 16, 16, 16, 4);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: dss
--



--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: dss
--



--
-- Data for Name: auth_message; Type: TABLE DATA; Schema: public; Owner: dss
--



--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO auth_permission VALUES (1, 'Can add log entry', 1, 'add_logentry');
INSERT INTO auth_permission VALUES (2, 'Can change log entry', 1, 'change_logentry');
INSERT INTO auth_permission VALUES (3, 'Can delete log entry', 1, 'delete_logentry');
INSERT INTO auth_permission VALUES (4, 'Can add permission', 2, 'add_permission');
INSERT INTO auth_permission VALUES (5, 'Can change permission', 2, 'change_permission');
INSERT INTO auth_permission VALUES (6, 'Can delete permission', 2, 'delete_permission');
INSERT INTO auth_permission VALUES (7, 'Can add group', 3, 'add_group');
INSERT INTO auth_permission VALUES (8, 'Can change group', 3, 'change_group');
INSERT INTO auth_permission VALUES (9, 'Can delete group', 3, 'delete_group');
INSERT INTO auth_permission VALUES (10, 'Can add user', 4, 'add_user');
INSERT INTO auth_permission VALUES (11, 'Can change user', 4, 'change_user');
INSERT INTO auth_permission VALUES (12, 'Can delete user', 4, 'delete_user');
INSERT INTO auth_permission VALUES (13, 'Can add message', 5, 'add_message');
INSERT INTO auth_permission VALUES (14, 'Can change message', 5, 'change_message');
INSERT INTO auth_permission VALUES (15, 'Can delete message', 5, 'delete_message');
INSERT INTO auth_permission VALUES (16, 'Can add content type', 6, 'add_contenttype');
INSERT INTO auth_permission VALUES (17, 'Can change content type', 6, 'change_contenttype');
INSERT INTO auth_permission VALUES (18, 'Can delete content type', 6, 'delete_contenttype');
INSERT INTO auth_permission VALUES (19, 'Can add session', 7, 'add_session');
INSERT INTO auth_permission VALUES (20, 'Can change session', 7, 'change_session');
INSERT INTO auth_permission VALUES (21, 'Can delete session', 7, 'delete_session');
INSERT INTO auth_permission VALUES (22, 'Can add site', 8, 'add_site');
INSERT INTO auth_permission VALUES (23, 'Can change site', 8, 'change_site');
INSERT INTO auth_permission VALUES (24, 'Can delete site', 8, 'delete_site');
INSERT INTO auth_permission VALUES (25, 'Can add user', 9, 'add_user');
INSERT INTO auth_permission VALUES (26, 'Can change user', 9, 'change_user');
INSERT INTO auth_permission VALUES (27, 'Can delete user', 9, 'delete_user');
INSERT INTO auth_permission VALUES (28, 'Can add email', 10, 'add_email');
INSERT INTO auth_permission VALUES (29, 'Can change email', 10, 'change_email');
INSERT INTO auth_permission VALUES (30, 'Can delete email', 10, 'delete_email');
INSERT INTO auth_permission VALUES (31, 'Can add semester', 11, 'add_semester');
INSERT INTO auth_permission VALUES (32, 'Can change semester', 11, 'change_semester');
INSERT INTO auth_permission VALUES (33, 'Can delete semester', 11, 'delete_semester');
INSERT INTO auth_permission VALUES (34, 'Can add project_ type', 12, 'add_project_type');
INSERT INTO auth_permission VALUES (35, 'Can change project_ type', 12, 'change_project_type');
INSERT INTO auth_permission VALUES (36, 'Can delete project_ type', 12, 'delete_project_type');
INSERT INTO auth_permission VALUES (37, 'Can add allotment', 13, 'add_allotment');
INSERT INTO auth_permission VALUES (38, 'Can change allotment', 13, 'change_allotment');
INSERT INTO auth_permission VALUES (39, 'Can delete allotment', 13, 'delete_allotment');
INSERT INTO auth_permission VALUES (40, 'Can add project', 14, 'add_project');
INSERT INTO auth_permission VALUES (41, 'Can change project', 14, 'change_project');
INSERT INTO auth_permission VALUES (42, 'Can delete project', 14, 'delete_project');
INSERT INTO auth_permission VALUES (43, 'Can add investigators', 15, 'add_investigators');
INSERT INTO auth_permission VALUES (44, 'Can change investigators', 15, 'change_investigators');
INSERT INTO auth_permission VALUES (45, 'Can delete investigators', 15, 'delete_investigators');
INSERT INTO auth_permission VALUES (46, 'Can add session_ type', 16, 'add_session_type');
INSERT INTO auth_permission VALUES (47, 'Can change session_ type', 16, 'change_session_type');
INSERT INTO auth_permission VALUES (48, 'Can delete session_ type', 16, 'delete_session_type');
INSERT INTO auth_permission VALUES (49, 'Can add observing_ type', 17, 'add_observing_type');
INSERT INTO auth_permission VALUES (50, 'Can change observing_ type', 17, 'change_observing_type');
INSERT INTO auth_permission VALUES (51, 'Can delete observing_ type', 17, 'delete_observing_type');
INSERT INTO auth_permission VALUES (52, 'Can add receiver', 18, 'add_receiver');
INSERT INTO auth_permission VALUES (53, 'Can change receiver', 18, 'change_receiver');
INSERT INTO auth_permission VALUES (54, 'Can delete receiver', 18, 'delete_receiver');
INSERT INTO auth_permission VALUES (55, 'Can add receiver_ schedule', 19, 'add_receiver_schedule');
INSERT INTO auth_permission VALUES (56, 'Can change receiver_ schedule', 19, 'change_receiver_schedule');
INSERT INTO auth_permission VALUES (57, 'Can delete receiver_ schedule', 19, 'delete_receiver_schedule');
INSERT INTO auth_permission VALUES (58, 'Can add parameter', 20, 'add_parameter');
INSERT INTO auth_permission VALUES (59, 'Can change parameter', 20, 'change_parameter');
INSERT INTO auth_permission VALUES (60, 'Can delete parameter', 20, 'delete_parameter');
INSERT INTO auth_permission VALUES (61, 'Can add status', 21, 'add_status');
INSERT INTO auth_permission VALUES (62, 'Can change status', 21, 'change_status');
INSERT INTO auth_permission VALUES (63, 'Can delete status', 21, 'delete_status');
INSERT INTO auth_permission VALUES (64, 'Can add sesshun', 22, 'add_sesshun');
INSERT INTO auth_permission VALUES (65, 'Can change sesshun', 22, 'change_sesshun');
INSERT INTO auth_permission VALUES (66, 'Can delete sesshun', 22, 'delete_sesshun');
INSERT INTO auth_permission VALUES (67, 'Can add cadence', 23, 'add_cadence');
INSERT INTO auth_permission VALUES (68, 'Can change cadence', 23, 'change_cadence');
INSERT INTO auth_permission VALUES (69, 'Can delete cadence', 23, 'delete_cadence');
INSERT INTO auth_permission VALUES (70, 'Can add receiver_ group', 24, 'add_receiver_group');
INSERT INTO auth_permission VALUES (71, 'Can change receiver_ group', 24, 'change_receiver_group');
INSERT INTO auth_permission VALUES (72, 'Can delete receiver_ group', 24, 'delete_receiver_group');
INSERT INTO auth_permission VALUES (73, 'Can add observing_ parameter', 25, 'add_observing_parameter');
INSERT INTO auth_permission VALUES (74, 'Can change observing_ parameter', 25, 'change_observing_parameter');
INSERT INTO auth_permission VALUES (75, 'Can delete observing_ parameter', 25, 'delete_observing_parameter');
INSERT INTO auth_permission VALUES (76, 'Can add window', 26, 'add_window');
INSERT INTO auth_permission VALUES (77, 'Can change window', 26, 'change_window');
INSERT INTO auth_permission VALUES (78, 'Can delete window', 26, 'delete_window');
INSERT INTO auth_permission VALUES (79, 'Can add opportunity', 27, 'add_opportunity');
INSERT INTO auth_permission VALUES (80, 'Can change opportunity', 27, 'change_opportunity');
INSERT INTO auth_permission VALUES (81, 'Can delete opportunity', 27, 'delete_opportunity');
INSERT INTO auth_permission VALUES (82, 'Can add system', 28, 'add_system');
INSERT INTO auth_permission VALUES (83, 'Can change system', 28, 'change_system');
INSERT INTO auth_permission VALUES (84, 'Can delete system', 28, 'delete_system');
INSERT INTO auth_permission VALUES (85, 'Can add target', 29, 'add_target');
INSERT INTO auth_permission VALUES (86, 'Can change target', 29, 'change_target');
INSERT INTO auth_permission VALUES (87, 'Can delete target', 29, 'delete_target');


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO auth_user VALUES (1, 'mmccarty', '', '', 'mmccarty@nrao.edu', 'sha1$9529a$a31be4abb536e75fbb7268e622f41f913f9a2dac', true, true, true, '2009-05-07 09:36:36.675704-04', '2009-05-05 09:50:24.64354-04');


--
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: dss
--



--
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: dss
--



--
-- Data for Name: cadences; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO cadences VALUES (5, 5, '2009-06-23 20:00:00-04', NULL, 8, '24', '120');
INSERT INTO cadences VALUES (6, 6, '2009-06-30 20:00:00-04', NULL, 6, '24', '120');
INSERT INTO cadences VALUES (7, 7, '2009-07-07 20:00:00-04', NULL, 7, '24', '120');
INSERT INTO cadences VALUES (8, 8, '2009-07-14 20:00:00-04', NULL, 7, '24', '120');
INSERT INTO cadences VALUES (9, 9, '2009-07-25 20:00:00-04', NULL, 5, '24', '120');
INSERT INTO cadences VALUES (10, 10, '2009-08-01 20:00:00-04', NULL, 5, '24', '120');
INSERT INTO cadences VALUES (11, 11, '2009-08-08 20:00:00-04', NULL, 5, '24', '120');
INSERT INTO cadences VALUES (12, 12, '2009-08-15 20:00:00-04', NULL, 6, '24', '120');
INSERT INTO cadences VALUES (13, 13, '2009-08-22 20:00:00-04', NULL, 7, '24', '120');
INSERT INTO cadences VALUES (14, 14, '2009-08-29 20:00:00-04', NULL, 6, '24', '120');
INSERT INTO cadences VALUES (15, 15, '2009-09-05 20:00:00-04', NULL, 7, '24', '120');
INSERT INTO cadences VALUES (16, 16, '2009-09-12 20:00:00-04', NULL, 6, '24', '120');
INSERT INTO cadences VALUES (17, 19, '2009-08-16 20:00:00-04', NULL, 2, '18', '90');
INSERT INTO cadences VALUES (20, 40, '2009-06-07 20:00:00-04', NULL, 1, '12', '60');
INSERT INTO cadences VALUES (21, 41, '2010-03-27 20:00:00-04', NULL, 2, '74', '365');
INSERT INTO cadences VALUES (22, 53, '2009-06-12 20:00:00-04', NULL, 1, '12', '60');
INSERT INTO cadences VALUES (23, 54, '2009-07-17 20:00:00-04', NULL, 1, '12', '60');
INSERT INTO cadences VALUES (24, 59, '2009-06-06 20:00:00-04', NULL, 8, '4', '15');
INSERT INTO cadences VALUES (27, 63, '2009-07-26 20:00:00-04', NULL, 1, '36', '180');
INSERT INTO cadences VALUES (28, 66, '2009-09-28 20:00:00-04', NULL, 4, '6', '30');
INSERT INTO cadences VALUES (29, 67, '2009-07-01 20:00:00-04', NULL, 1, '10', '45');
INSERT INTO cadences VALUES (30, 76, '2009-08-03 20:00:00-04', NULL, 1, '18', '91');
INSERT INTO cadences VALUES (31, 77, '2009-07-29 20:00:00-04', NULL, 1, '18', '91');
INSERT INTO cadences VALUES (32, 80, '2009-07-01 20:00:00-04', NULL, 4, '12', '60');
INSERT INTO cadences VALUES (33, 109, NULL, NULL, 8, '6', '30');
INSERT INTO cadences VALUES (34, 157, '2009-06-11 20:00:00-04', NULL, 12, '6', '30');
INSERT INTO cadences VALUES (35, 160, '2009-06-30 20:00:00-04', NULL, 4, '1,1,1,1', '1,1,2,3');
INSERT INTO cadences VALUES (36, 161, '2009-06-30 20:00:00-04', NULL, 2, '0', '2');
INSERT INTO cadences VALUES (37, 180, '2009-06-06 20:00:00-04', NULL, 4, '1,1,1,2', '1,2,3,10');
INSERT INTO cadences VALUES (38, 183, '2009-07-01 20:00:00-04', NULL, 3, '6', '30');
INSERT INTO cadences VALUES (39, 195, NULL, NULL, 4, '6', '30');
INSERT INTO cadences VALUES (40, 198, '2009-11-01 19:00:00-05', NULL, 2, '36', '180');
INSERT INTO cadences VALUES (41, 199, '2009-08-11 20:00:00-04', NULL, 6, '12', '60');
INSERT INTO cadences VALUES (42, 200, '2009-09-15 20:00:00-04', NULL, 6, '12', '60');
INSERT INTO cadences VALUES (43, 204, '2009-06-22 20:00:00-04', NULL, 7, '1,1,1,1,1,2,2', '1,2,3,6,11,18,28');
INSERT INTO cadences VALUES (44, 205, '2009-08-17 20:00:00-04', NULL, 11, '6', '30');
INSERT INTO cadences VALUES (46, 207, '2009-08-17 20:00:00-04', NULL, 11, '6', '30');
INSERT INTO cadences VALUES (47, 219, '2009-09-16 20:00:00-04', NULL, 36, '6', '30');
INSERT INTO cadences VALUES (48, 220, '2009-09-18 20:00:00-04', NULL, 36, '6', '30');
INSERT INTO cadences VALUES (49, 221, NULL, NULL, 20, '2', '14');
INSERT INTO cadences VALUES (50, 238, NULL, NULL, 5, '2', '5');
INSERT INTO cadences VALUES (51, 254, '2009-06-01 20:00:00-04', NULL, 6, '2', '7');
INSERT INTO cadences VALUES (2, 2, '2009-05-30 00:00:00-04', NULL, 6, NULL, '120');
INSERT INTO cadences VALUES (3, 3, '2009-06-06 00:00:00-04', NULL, 7, NULL, '120');
INSERT INTO cadences VALUES (18, 36, '2009-06-26 00:00:00-04', NULL, 3, '3', '30');
INSERT INTO cadences VALUES (26, 61, '2009-06-16 00:00:00-04', NULL, 4, '3', '30');
INSERT INTO cadences VALUES (25, 60, '2009-06-10 00:00:00-04', NULL, 9, '2', '14');
INSERT INTO cadences VALUES (4, 4, '2009-06-13 00:00:00-04', NULL, 7, '10', '120');
INSERT INTO cadences VALUES (1, 1, '2009-05-23 00:00:00-04', NULL, 6, NULL, '120');
INSERT INTO cadences VALUES (52, 21, '2009-07-01 00:00:00-04', NULL, 1, NULL, '2');
INSERT INTO cadences VALUES (19, 37, '2009-06-17 00:00:00-04', NULL, 3, '2', '5');
INSERT INTO cadences VALUES (45, 206, '2009-06-22 00:00:00-04', NULL, 7, '1,2,2,3,3,3,3', '1,2,3,6,11,18,28');


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO django_admin_log VALUES (1, '2009-05-06 14:31:53.845006-04', 1, 26, '83', 'Window (83) for Sess (49), Num Opts: 1', 1, '');


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO django_content_type VALUES (1, 'log entry', 'admin', 'logentry');
INSERT INTO django_content_type VALUES (2, 'permission', 'auth', 'permission');
INSERT INTO django_content_type VALUES (3, 'group', 'auth', 'group');
INSERT INTO django_content_type VALUES (4, 'user', 'auth', 'user');
INSERT INTO django_content_type VALUES (5, 'message', 'auth', 'message');
INSERT INTO django_content_type VALUES (6, 'content type', 'contenttypes', 'contenttype');
INSERT INTO django_content_type VALUES (7, 'session', 'sessions', 'session');
INSERT INTO django_content_type VALUES (8, 'site', 'sites', 'site');
INSERT INTO django_content_type VALUES (9, 'user', 'sesshuns', 'user');
INSERT INTO django_content_type VALUES (10, 'email', 'sesshuns', 'email');
INSERT INTO django_content_type VALUES (11, 'semester', 'sesshuns', 'semester');
INSERT INTO django_content_type VALUES (12, 'project_ type', 'sesshuns', 'project_type');
INSERT INTO django_content_type VALUES (13, 'allotment', 'sesshuns', 'allotment');
INSERT INTO django_content_type VALUES (14, 'project', 'sesshuns', 'project');
INSERT INTO django_content_type VALUES (15, 'investigators', 'sesshuns', 'investigators');
INSERT INTO django_content_type VALUES (16, 'session_ type', 'sesshuns', 'session_type');
INSERT INTO django_content_type VALUES (17, 'observing_ type', 'sesshuns', 'observing_type');
INSERT INTO django_content_type VALUES (18, 'receiver', 'sesshuns', 'receiver');
INSERT INTO django_content_type VALUES (19, 'receiver_ schedule', 'sesshuns', 'receiver_schedule');
INSERT INTO django_content_type VALUES (20, 'parameter', 'sesshuns', 'parameter');
INSERT INTO django_content_type VALUES (21, 'status', 'sesshuns', 'status');
INSERT INTO django_content_type VALUES (22, 'sesshun', 'sesshuns', 'sesshun');
INSERT INTO django_content_type VALUES (23, 'cadence', 'sesshuns', 'cadence');
INSERT INTO django_content_type VALUES (24, 'receiver_ group', 'sesshuns', 'receiver_group');
INSERT INTO django_content_type VALUES (25, 'observing_ parameter', 'sesshuns', 'observing_parameter');
INSERT INTO django_content_type VALUES (26, 'window', 'sesshuns', 'window');
INSERT INTO django_content_type VALUES (27, 'opportunity', 'sesshuns', 'opportunity');
INSERT INTO django_content_type VALUES (28, 'system', 'sesshuns', 'system');
INSERT INTO django_content_type VALUES (29, 'target', 'sesshuns', 'target');


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO django_session VALUES ('a47428f347012206dfc8f0f059fe1391', 'gAJ9cQEoVRJfYXV0aF91c2VyX2JhY2tlbmRxAlUpZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5k
cy5Nb2RlbEJhY2tlbmRxA1UNX2F1dGhfdXNlcl9pZHEESwF1LjQyNGUzNDQ4N2FiMmM1ZGFiN2Zl
MDViYzYyYTZlZDA3
', '2009-05-20 14:18:45.607085-04');
INSERT INTO django_session VALUES ('e9e38522a40e9434ccac72e00492c133', 'gAJ9cQEoVRJfYXV0aF91c2VyX2JhY2tlbmRxAlUpZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5k
cy5Nb2RlbEJhY2tlbmRxA1UNX2F1dGhfdXNlcl9pZHEESwF1LjQyNGUzNDQ4N2FiMmM1ZGFiN2Zl
MDViYzYyYTZlZDA3
', '2009-05-21 09:36:36.684031-04');


--
-- Data for Name: django_site; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO django_site VALUES (1, 'example.com', 'example.com');


--
-- Data for Name: investigators; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO investigators VALUES (1, 2, 1, true, false, false, 1);
INSERT INTO investigators VALUES (2, 3, 2, true, false, false, 1);
INSERT INTO investigators VALUES (3, 4, 3, true, false, false, 1);
INSERT INTO investigators VALUES (4, 5, 1, true, false, false, 1);
INSERT INTO investigators VALUES (5, 6, 3, true, false, false, 1);
INSERT INTO investigators VALUES (6, 7, 1, true, false, false, 1);
INSERT INTO investigators VALUES (7, 8, 3, true, false, false, 1);
INSERT INTO investigators VALUES (8, 9, 4, true, false, false, 1);
INSERT INTO investigators VALUES (9, 10, 5, true, false, false, 1);
INSERT INTO investigators VALUES (10, 11, 6, true, false, false, 1);
INSERT INTO investigators VALUES (11, 12, 6, true, false, false, 1);
INSERT INTO investigators VALUES (12, 13, 7, true, false, false, 1);
INSERT INTO investigators VALUES (13, 14, 2, true, false, false, 1);
INSERT INTO investigators VALUES (14, 15, 8, true, false, false, 1);
INSERT INTO investigators VALUES (15, 16, 1, true, false, false, 1);
INSERT INTO investigators VALUES (16, 17, 4, true, false, false, 1);
INSERT INTO investigators VALUES (17, 18, 8, true, false, false, 1);
INSERT INTO investigators VALUES (18, 19, 2, true, false, false, 1);
INSERT INTO investigators VALUES (19, 20, 3, true, false, false, 1);
INSERT INTO investigators VALUES (20, 21, 9, true, false, false, 1);
INSERT INTO investigators VALUES (21, 22, 1, true, false, false, 1);
INSERT INTO investigators VALUES (22, 23, 10, true, false, false, 1);
INSERT INTO investigators VALUES (23, 24, 8, true, false, false, 1);
INSERT INTO investigators VALUES (24, 25, 6, true, false, false, 1);
INSERT INTO investigators VALUES (25, 26, 1, true, false, false, 1);
INSERT INTO investigators VALUES (26, 27, 1, true, false, false, 1);
INSERT INTO investigators VALUES (27, 28, 8, true, false, false, 1);
INSERT INTO investigators VALUES (28, 29, 8, true, false, false, 1);
INSERT INTO investigators VALUES (29, 30, 11, true, false, false, 1);
INSERT INTO investigators VALUES (30, 31, 2, true, false, false, 1);
INSERT INTO investigators VALUES (31, 32, 8, true, false, false, 1);
INSERT INTO investigators VALUES (32, 33, 1, true, false, false, 1);
INSERT INTO investigators VALUES (33, 34, 6, true, false, false, 1);
INSERT INTO investigators VALUES (34, 35, 7, true, false, false, 1);
INSERT INTO investigators VALUES (35, 36, 6, true, false, false, 1);
INSERT INTO investigators VALUES (36, 37, 8, true, false, false, 1);
INSERT INTO investigators VALUES (37, 38, 11, true, false, false, 1);
INSERT INTO investigators VALUES (38, 39, 5, true, false, false, 1);
INSERT INTO investigators VALUES (39, 40, 8, true, false, false, 1);
INSERT INTO investigators VALUES (40, 41, 3, true, false, false, 1);
INSERT INTO investigators VALUES (41, 42, 12, true, false, false, 1);
INSERT INTO investigators VALUES (42, 43, 6, true, false, false, 1);
INSERT INTO investigators VALUES (43, 44, 2, true, false, false, 1);
INSERT INTO investigators VALUES (44, 45, 3, true, false, false, 1);
INSERT INTO investigators VALUES (45, 46, 3, true, false, false, 1);
INSERT INTO investigators VALUES (46, 47, 8, true, false, false, 1);
INSERT INTO investigators VALUES (47, 48, 9, true, false, false, 1);
INSERT INTO investigators VALUES (48, 49, 13, true, false, false, 1);
INSERT INTO investigators VALUES (49, 50, 3, true, false, false, 1);
INSERT INTO investigators VALUES (50, 51, 8, true, false, false, 1);
INSERT INTO investigators VALUES (51, 52, 8, true, false, false, 1);
INSERT INTO investigators VALUES (52, 53, 1, true, false, false, 1);
INSERT INTO investigators VALUES (53, 54, 8, true, false, false, 1);
INSERT INTO investigators VALUES (54, 55, 14, true, false, false, 1);
INSERT INTO investigators VALUES (55, 56, 14, true, false, false, 1);
INSERT INTO investigators VALUES (56, 57, 15, true, false, false, 1);
INSERT INTO investigators VALUES (57, 58, 8, true, false, false, 1);
INSERT INTO investigators VALUES (58, 59, 9, true, false, false, 1);
INSERT INTO investigators VALUES (59, 60, 5, true, false, false, 1);
INSERT INTO investigators VALUES (60, 61, 5, true, false, false, 1);
INSERT INTO investigators VALUES (61, 62, 8, true, false, false, 1);
INSERT INTO investigators VALUES (62, 63, 6, true, false, false, 1);
INSERT INTO investigators VALUES (63, 64, 3, true, false, false, 1);
INSERT INTO investigators VALUES (64, 65, 8, true, false, false, 1);
INSERT INTO investigators VALUES (65, 66, 8, true, false, false, 1);
INSERT INTO investigators VALUES (66, 67, 16, true, false, false, 1);
INSERT INTO investigators VALUES (67, 68, 17, true, false, false, 1);
INSERT INTO investigators VALUES (68, 69, 3, true, false, false, 1);
INSERT INTO investigators VALUES (69, 70, 6, true, false, false, 1);
INSERT INTO investigators VALUES (70, 71, 8, true, false, false, 1);
INSERT INTO investigators VALUES (71, 72, 2, true, false, false, 1);
INSERT INTO investigators VALUES (72, 73, 18, true, false, false, 1);
INSERT INTO investigators VALUES (73, 74, 8, true, false, false, 1);
INSERT INTO investigators VALUES (74, 75, 8, true, false, false, 1);
INSERT INTO investigators VALUES (75, 76, 11, true, false, false, 1);
INSERT INTO investigators VALUES (76, 77, 8, true, false, false, 1);
INSERT INTO investigators VALUES (77, 78, 5, true, false, false, 1);
INSERT INTO investigators VALUES (78, 79, 8, true, false, false, 1);
INSERT INTO investigators VALUES (79, 80, 8, true, false, false, 1);
INSERT INTO investigators VALUES (80, 81, 2, true, false, false, 1);
INSERT INTO investigators VALUES (81, 82, 8, true, false, false, 1);
INSERT INTO investigators VALUES (82, 83, 8, true, false, false, 1);
INSERT INTO investigators VALUES (83, 84, 8, true, false, false, 1);
INSERT INTO investigators VALUES (84, 85, 1, true, false, false, 1);
INSERT INTO investigators VALUES (85, 86, 8, true, false, false, 1);
INSERT INTO investigators VALUES (86, 87, 8, true, false, false, 1);
INSERT INTO investigators VALUES (87, 88, 13, true, false, false, 1);
INSERT INTO investigators VALUES (88, 89, 6, true, false, false, 1);
INSERT INTO investigators VALUES (89, 90, 7, true, false, false, 1);
INSERT INTO investigators VALUES (90, 91, 2, true, false, false, 1);
INSERT INTO investigators VALUES (91, 92, 7, true, false, false, 1);
INSERT INTO investigators VALUES (92, 93, 7, true, false, false, 1);
INSERT INTO investigators VALUES (93, 94, 8, true, false, false, 1);
INSERT INTO investigators VALUES (94, 95, 12, true, false, false, 1);
INSERT INTO investigators VALUES (95, 96, 8, true, false, false, 1);
INSERT INTO investigators VALUES (96, 97, 13, true, false, false, 1);
INSERT INTO investigators VALUES (97, 98, 8, true, false, false, 1);
INSERT INTO investigators VALUES (98, 99, 2, true, false, false, 1);
INSERT INTO investigators VALUES (99, 100, 1, true, false, false, 1);
INSERT INTO investigators VALUES (100, 101, 2, true, false, false, 1);
INSERT INTO investigators VALUES (101, 2, 19, false, false, true, 1);
INSERT INTO investigators VALUES (102, 2, 20, false, false, false, 1);
INSERT INTO investigators VALUES (103, 2, 21, false, false, false, 1);
INSERT INTO investigators VALUES (104, 2, 22, false, false, false, 1);
INSERT INTO investigators VALUES (105, 3, 2, false, false, true, 1);
INSERT INTO investigators VALUES (106, 3, 23, false, false, false, 1);
INSERT INTO investigators VALUES (107, 3, 24, false, false, false, 1);
INSERT INTO investigators VALUES (108, 3, 25, false, false, false, 1);
INSERT INTO investigators VALUES (109, 3, 26, false, false, false, 1);
INSERT INTO investigators VALUES (110, 3, 27, false, false, false, 1);
INSERT INTO investigators VALUES (111, 3, 28, false, false, false, 1);
INSERT INTO investigators VALUES (112, 3, 29, false, false, false, 1);
INSERT INTO investigators VALUES (113, 3, 30, false, false, false, 1);
INSERT INTO investigators VALUES (114, 3, 31, false, false, false, 1);
INSERT INTO investigators VALUES (115, 3, 32, false, false, false, 1);
INSERT INTO investigators VALUES (116, 4, 33, false, false, true, 1);
INSERT INTO investigators VALUES (117, 4, 34, false, false, false, 1);
INSERT INTO investigators VALUES (118, 4, 35, false, false, false, 1);
INSERT INTO investigators VALUES (119, 4, 36, false, false, false, 1);
INSERT INTO investigators VALUES (120, 5, 37, false, false, true, 1);
INSERT INTO investigators VALUES (121, 5, 38, false, false, false, 1);
INSERT INTO investigators VALUES (122, 5, 39, false, false, false, 1);
INSERT INTO investigators VALUES (123, 5, 40, false, false, false, 1);
INSERT INTO investigators VALUES (124, 5, 41, false, false, false, 1);
INSERT INTO investigators VALUES (125, 5, 42, false, false, false, 1);
INSERT INTO investigators VALUES (126, 5, 43, false, false, false, 1);
INSERT INTO investigators VALUES (127, 6, 44, false, false, true, 1);
INSERT INTO investigators VALUES (128, 6, 45, false, false, false, 1);
INSERT INTO investigators VALUES (129, 6, 46, false, false, false, 1);
INSERT INTO investigators VALUES (130, 7, 39, false, false, true, 1);
INSERT INTO investigators VALUES (131, 7, 47, false, false, false, 1);
INSERT INTO investigators VALUES (132, 7, 36, false, false, false, 1);
INSERT INTO investigators VALUES (133, 8, 48, false, false, true, 1);
INSERT INTO investigators VALUES (134, 8, 49, false, false, false, 1);
INSERT INTO investigators VALUES (135, 8, 50, false, false, false, 1);
INSERT INTO investigators VALUES (136, 9, 51, false, false, true, 1);
INSERT INTO investigators VALUES (137, 9, 52, false, false, false, 1);
INSERT INTO investigators VALUES (138, 9, 53, false, false, false, 1);
INSERT INTO investigators VALUES (139, 9, 54, false, false, false, 1);
INSERT INTO investigators VALUES (140, 9, 55, false, false, false, 1);
INSERT INTO investigators VALUES (141, 9, 56, false, false, false, 1);
INSERT INTO investigators VALUES (142, 9, 57, false, false, false, 1);
INSERT INTO investigators VALUES (143, 10, 15, false, false, true, 1);
INSERT INTO investigators VALUES (144, 10, 58, false, false, false, 1);
INSERT INTO investigators VALUES (145, 11, 59, false, false, true, 1);
INSERT INTO investigators VALUES (146, 11, 60, false, false, false, 1);
INSERT INTO investigators VALUES (147, 11, 61, false, false, false, 1);
INSERT INTO investigators VALUES (148, 11, 62, false, false, false, 1);
INSERT INTO investigators VALUES (149, 12, 59, false, false, true, 1);
INSERT INTO investigators VALUES (150, 12, 63, false, false, false, 1);
INSERT INTO investigators VALUES (151, 13, 64, false, false, true, 1);
INSERT INTO investigators VALUES (152, 13, 16, false, false, false, 1);
INSERT INTO investigators VALUES (153, 13, 65, false, false, false, 1);
INSERT INTO investigators VALUES (154, 13, 66, false, false, false, 1);
INSERT INTO investigators VALUES (155, 14, 67, false, false, true, 1);
INSERT INTO investigators VALUES (156, 14, 68, false, false, false, 1);
INSERT INTO investigators VALUES (157, 15, 69, false, false, true, 1);
INSERT INTO investigators VALUES (158, 15, 70, false, false, false, 1);
INSERT INTO investigators VALUES (159, 15, 71, false, false, false, 1);
INSERT INTO investigators VALUES (160, 15, 72, false, false, false, 1);
INSERT INTO investigators VALUES (161, 15, 73, false, false, false, 1);
INSERT INTO investigators VALUES (162, 15, 74, false, false, false, 1);
INSERT INTO investigators VALUES (163, 15, 75, false, false, false, 1);
INSERT INTO investigators VALUES (164, 15, 8, false, false, false, 1);
INSERT INTO investigators VALUES (165, 15, 76, false, false, false, 1);
INSERT INTO investigators VALUES (166, 15, 77, false, false, false, 1);
INSERT INTO investigators VALUES (167, 16, 78, false, false, true, 1);
INSERT INTO investigators VALUES (168, 16, 79, false, false, false, 1);
INSERT INTO investigators VALUES (169, 16, 80, false, false, false, 1);
INSERT INTO investigators VALUES (170, 16, 81, false, false, false, 1);
INSERT INTO investigators VALUES (171, 16, 82, false, false, false, 1);
INSERT INTO investigators VALUES (172, 17, 51, false, false, true, 1);
INSERT INTO investigators VALUES (173, 17, 83, false, false, false, 1);
INSERT INTO investigators VALUES (174, 17, 52, false, false, false, 1);
INSERT INTO investigators VALUES (175, 17, 20, false, false, false, 1);
INSERT INTO investigators VALUES (176, 17, 53, false, false, false, 1);
INSERT INTO investigators VALUES (177, 17, 4, false, false, false, 1);
INSERT INTO investigators VALUES (178, 18, 84, false, false, true, 1);
INSERT INTO investigators VALUES (179, 18, 85, false, false, false, 1);
INSERT INTO investigators VALUES (180, 18, 86, false, false, false, 1);
INSERT INTO investigators VALUES (181, 18, 87, false, false, false, 1);
INSERT INTO investigators VALUES (182, 18, 88, false, false, false, 1);
INSERT INTO investigators VALUES (183, 18, 89, false, false, false, 1);
INSERT INTO investigators VALUES (184, 19, 90, false, false, true, 1);
INSERT INTO investigators VALUES (185, 19, 91, false, false, false, 1);
INSERT INTO investigators VALUES (186, 19, 92, false, false, false, 1);
INSERT INTO investigators VALUES (187, 19, 50, false, false, false, 1);
INSERT INTO investigators VALUES (188, 19, 93, false, false, false, 1);
INSERT INTO investigators VALUES (189, 19, 94, false, false, false, 1);
INSERT INTO investigators VALUES (190, 20, 59, false, false, false, 1);
INSERT INTO investigators VALUES (191, 20, 95, false, false, true, 1);
INSERT INTO investigators VALUES (192, 21, 96, false, false, true, 1);
INSERT INTO investigators VALUES (193, 21, 97, false, false, false, 1);
INSERT INTO investigators VALUES (194, 22, 98, false, false, true, 1);
INSERT INTO investigators VALUES (195, 22, 99, false, false, false, 1);
INSERT INTO investigators VALUES (196, 22, 100, false, false, false, 1);
INSERT INTO investigators VALUES (197, 22, 101, false, false, false, 1);
INSERT INTO investigators VALUES (198, 22, 102, false, false, false, 1);
INSERT INTO investigators VALUES (199, 23, 10, false, false, true, 1);
INSERT INTO investigators VALUES (200, 23, 103, false, false, false, 1);
INSERT INTO investigators VALUES (201, 23, 104, false, false, false, 1);
INSERT INTO investigators VALUES (202, 23, 105, false, false, false, 1);
INSERT INTO investigators VALUES (203, 23, 106, false, false, false, 1);
INSERT INTO investigators VALUES (204, 24, 107, false, false, true, 1);
INSERT INTO investigators VALUES (205, 24, 73, false, false, false, 1);
INSERT INTO investigators VALUES (206, 24, 87, false, false, false, 1);
INSERT INTO investigators VALUES (207, 24, 71, false, false, false, 1);
INSERT INTO investigators VALUES (208, 24, 108, false, false, false, 1);
INSERT INTO investigators VALUES (209, 24, 109, false, false, false, 1);
INSERT INTO investigators VALUES (210, 24, 110, false, false, false, 1);
INSERT INTO investigators VALUES (211, 24, 111, false, false, false, 1);
INSERT INTO investigators VALUES (212, 24, 112, false, false, false, 1);
INSERT INTO investigators VALUES (213, 24, 113, false, false, false, 1);
INSERT INTO investigators VALUES (214, 24, 114, false, false, false, 1);
INSERT INTO investigators VALUES (215, 25, 6, false, false, true, 1);
INSERT INTO investigators VALUES (216, 25, 115, false, false, false, 1);
INSERT INTO investigators VALUES (217, 25, 116, false, false, false, 1);
INSERT INTO investigators VALUES (218, 26, 117, false, false, true, 1);
INSERT INTO investigators VALUES (219, 26, 118, false, false, false, 1);
INSERT INTO investigators VALUES (220, 27, 119, false, false, true, 1);
INSERT INTO investigators VALUES (221, 27, 120, false, false, false, 1);
INSERT INTO investigators VALUES (222, 27, 121, false, false, false, 1);
INSERT INTO investigators VALUES (223, 27, 122, false, false, false, 1);
INSERT INTO investigators VALUES (224, 27, 123, false, false, false, 1);
INSERT INTO investigators VALUES (225, 27, 124, false, false, false, 1);
INSERT INTO investigators VALUES (226, 27, 125, false, false, false, 1);
INSERT INTO investigators VALUES (227, 27, 126, false, false, false, 1);
INSERT INTO investigators VALUES (228, 27, 127, false, false, false, 1);
INSERT INTO investigators VALUES (229, 27, 128, false, false, false, 1);
INSERT INTO investigators VALUES (230, 27, 129, false, false, false, 1);
INSERT INTO investigators VALUES (231, 27, 130, false, false, false, 1);
INSERT INTO investigators VALUES (232, 27, 131, false, false, false, 1);
INSERT INTO investigators VALUES (233, 27, 132, false, false, false, 1);
INSERT INTO investigators VALUES (234, 28, 108, false, false, true, 1);
INSERT INTO investigators VALUES (235, 28, 8, false, false, false, 1);
INSERT INTO investigators VALUES (236, 28, 133, false, false, false, 1);
INSERT INTO investigators VALUES (237, 28, 134, false, false, false, 1);
INSERT INTO investigators VALUES (238, 29, 108, false, false, true, 1);
INSERT INTO investigators VALUES (239, 29, 8, false, false, false, 1);
INSERT INTO investigators VALUES (240, 29, 135, false, false, false, 1);
INSERT INTO investigators VALUES (241, 29, 87, false, false, false, 1);
INSERT INTO investigators VALUES (242, 29, 136, false, false, false, 1);
INSERT INTO investigators VALUES (243, 29, 114, false, false, false, 1);
INSERT INTO investigators VALUES (244, 29, 137, false, false, false, 1);
INSERT INTO investigators VALUES (245, 29, 133, false, false, false, 1);
INSERT INTO investigators VALUES (246, 29, 138, false, false, false, 1);
INSERT INTO investigators VALUES (247, 30, 139, false, false, true, 1);
INSERT INTO investigators VALUES (248, 30, 140, false, false, false, 1);
INSERT INTO investigators VALUES (249, 30, 11, false, false, false, 1);
INSERT INTO investigators VALUES (250, 31, 2, false, false, true, 1);
INSERT INTO investigators VALUES (251, 31, 23, false, false, false, 1);
INSERT INTO investigators VALUES (252, 31, 24, false, false, false, 1);
INSERT INTO investigators VALUES (253, 31, 25, false, false, false, 1);
INSERT INTO investigators VALUES (254, 31, 26, false, false, false, 1);
INSERT INTO investigators VALUES (255, 31, 27, false, false, false, 1);
INSERT INTO investigators VALUES (256, 31, 28, false, false, false, 1);
INSERT INTO investigators VALUES (257, 31, 29, false, false, false, 1);
INSERT INTO investigators VALUES (258, 31, 30, false, false, false, 1);
INSERT INTO investigators VALUES (259, 31, 31, false, false, false, 1);
INSERT INTO investigators VALUES (260, 31, 32, false, false, false, 1);
INSERT INTO investigators VALUES (261, 32, 141, false, false, true, 1);
INSERT INTO investigators VALUES (262, 32, 8, false, false, false, 1);
INSERT INTO investigators VALUES (263, 32, 114, false, false, false, 1);
INSERT INTO investigators VALUES (264, 32, 73, false, false, false, 1);
INSERT INTO investigators VALUES (265, 33, 36, false, false, true, 1);
INSERT INTO investigators VALUES (266, 33, 142, false, false, false, 1);
INSERT INTO investigators VALUES (267, 33, 143, false, false, false, 1);
INSERT INTO investigators VALUES (268, 33, 144, false, false, false, 1);
INSERT INTO investigators VALUES (269, 33, 64, false, false, false, 1);
INSERT INTO investigators VALUES (270, 33, 16, false, false, false, 1);
INSERT INTO investigators VALUES (271, 33, 145, false, false, false, 1);
INSERT INTO investigators VALUES (272, 34, 146, false, false, true, 1);
INSERT INTO investigators VALUES (273, 34, 147, false, false, false, 1);
INSERT INTO investigators VALUES (274, 34, 148, false, false, false, 1);
INSERT INTO investigators VALUES (275, 34, 149, false, false, false, 1);
INSERT INTO investigators VALUES (276, 34, 61, false, false, false, 1);
INSERT INTO investigators VALUES (277, 35, 150, false, false, true, 1);
INSERT INTO investigators VALUES (278, 35, 129, false, false, false, 1);
INSERT INTO investigators VALUES (279, 35, 130, false, false, false, 1);
INSERT INTO investigators VALUES (280, 35, 151, false, false, false, 1);
INSERT INTO investigators VALUES (281, 35, 152, false, false, false, 1);
INSERT INTO investigators VALUES (282, 35, 7, false, false, false, 1);
INSERT INTO investigators VALUES (283, 36, 129, false, false, true, 1);
INSERT INTO investigators VALUES (284, 36, 130, false, false, false, 1);
INSERT INTO investigators VALUES (285, 36, 150, false, false, false, 1);
INSERT INTO investigators VALUES (286, 36, 151, false, false, false, 1);
INSERT INTO investigators VALUES (287, 37, 8, false, false, true, 1);
INSERT INTO investigators VALUES (288, 37, 114, false, false, false, 1);
INSERT INTO investigators VALUES (289, 37, 73, false, false, false, 1);
INSERT INTO investigators VALUES (290, 37, 153, false, false, false, 1);
INSERT INTO investigators VALUES (291, 37, 141, false, false, false, 1);
INSERT INTO investigators VALUES (292, 38, 154, false, false, true, 1);
INSERT INTO investigators VALUES (293, 38, 11, false, false, false, 1);
INSERT INTO investigators VALUES (294, 38, 155, false, false, false, 1);
INSERT INTO investigators VALUES (295, 38, 156, false, false, false, 1);
INSERT INTO investigators VALUES (296, 38, 157, false, false, false, 1);
INSERT INTO investigators VALUES (297, 39, 158, false, false, true, 1);
INSERT INTO investigators VALUES (298, 39, 159, false, false, false, 1);
INSERT INTO investigators VALUES (299, 39, 5, false, false, false, 1);
INSERT INTO investigators VALUES (300, 39, 160, false, false, false, 1);
INSERT INTO investigators VALUES (301, 40, 114, false, false, true, 1);
INSERT INTO investigators VALUES (302, 40, 8, false, false, false, 1);
INSERT INTO investigators VALUES (303, 40, 141, false, false, false, 1);
INSERT INTO investigators VALUES (304, 41, 161, false, false, true, 1);
INSERT INTO investigators VALUES (305, 41, 162, false, false, false, 1);
INSERT INTO investigators VALUES (306, 41, 163, false, false, false, 1);
INSERT INTO investigators VALUES (307, 41, 164, false, false, false, 1);
INSERT INTO investigators VALUES (308, 42, 12, false, false, true, 1);
INSERT INTO investigators VALUES (309, 42, 165, false, false, false, 1);
INSERT INTO investigators VALUES (310, 43, 46, false, false, true, 1);
INSERT INTO investigators VALUES (311, 43, 166, false, false, false, 1);
INSERT INTO investigators VALUES (312, 43, 167, false, false, false, 1);
INSERT INTO investigators VALUES (313, 43, 168, false, false, false, 1);
INSERT INTO investigators VALUES (314, 43, 169, false, false, false, 1);
INSERT INTO investigators VALUES (315, 43, 170, false, false, false, 1);
INSERT INTO investigators VALUES (316, 43, 171, false, false, false, 1);
INSERT INTO investigators VALUES (317, 43, 172, false, false, false, 1);
INSERT INTO investigators VALUES (318, 43, 173, false, false, false, 1);
INSERT INTO investigators VALUES (319, 43, 174, false, false, false, 1);
INSERT INTO investigators VALUES (320, 43, 175, false, false, false, 1);
INSERT INTO investigators VALUES (321, 44, 145, false, false, true, 1);
INSERT INTO investigators VALUES (322, 44, 176, false, false, false, 1);
INSERT INTO investigators VALUES (323, 44, 177, false, false, false, 1);
INSERT INTO investigators VALUES (324, 44, 178, false, false, false, 1);
INSERT INTO investigators VALUES (325, 44, 179, false, false, false, 1);
INSERT INTO investigators VALUES (326, 44, 180, false, false, false, 1);
INSERT INTO investigators VALUES (327, 44, 181, false, false, false, 1);
INSERT INTO investigators VALUES (328, 44, 182, false, false, false, 1);
INSERT INTO investigators VALUES (329, 45, 59, false, false, true, 1);
INSERT INTO investigators VALUES (330, 46, 183, false, false, true, 1);
INSERT INTO investigators VALUES (331, 46, 184, false, false, false, 1);
INSERT INTO investigators VALUES (332, 46, 185, false, false, false, 1);
INSERT INTO investigators VALUES (333, 46, 186, false, false, false, 1);
INSERT INTO investigators VALUES (334, 46, 187, false, false, false, 1);
INSERT INTO investigators VALUES (335, 46, 188, false, false, false, 1);
INSERT INTO investigators VALUES (336, 46, 189, false, false, false, 1);
INSERT INTO investigators VALUES (337, 47, 141, false, false, true, 1);
INSERT INTO investigators VALUES (338, 47, 8, false, false, false, 1);
INSERT INTO investigators VALUES (339, 47, 73, false, false, false, 1);
INSERT INTO investigators VALUES (340, 47, 114, false, false, false, 1);
INSERT INTO investigators VALUES (341, 48, 190, false, false, true, 1);
INSERT INTO investigators VALUES (342, 48, 119, false, false, false, 1);
INSERT INTO investigators VALUES (343, 48, 191, false, false, false, 1);
INSERT INTO investigators VALUES (344, 48, 192, false, false, false, 1);
INSERT INTO investigators VALUES (345, 48, 193, false, false, false, 1);
INSERT INTO investigators VALUES (346, 48, 130, false, false, false, 1);
INSERT INTO investigators VALUES (347, 48, 129, false, false, false, 1);
INSERT INTO investigators VALUES (348, 48, 194, false, false, false, 1);
INSERT INTO investigators VALUES (349, 48, 195, false, false, false, 1);
INSERT INTO investigators VALUES (350, 48, 196, false, false, false, 1);
INSERT INTO investigators VALUES (351, 48, 197, false, false, false, 1);
INSERT INTO investigators VALUES (352, 49, 198, false, false, true, 1);
INSERT INTO investigators VALUES (353, 49, 13, false, false, false, 1);
INSERT INTO investigators VALUES (354, 49, 199, false, false, false, 1);
INSERT INTO investigators VALUES (355, 50, 200, false, false, true, 1);
INSERT INTO investigators VALUES (356, 50, 83, false, false, false, 1);
INSERT INTO investigators VALUES (357, 50, 201, false, false, false, 1);
INSERT INTO investigators VALUES (358, 51, 14, false, false, true, 1);
INSERT INTO investigators VALUES (359, 51, 87, false, false, false, 1);
INSERT INTO investigators VALUES (360, 51, 86, false, false, false, 1);
INSERT INTO investigators VALUES (361, 51, 202, false, false, false, 1);
INSERT INTO investigators VALUES (362, 52, 108, false, false, true, 1);
INSERT INTO investigators VALUES (363, 52, 133, false, false, false, 1);
INSERT INTO investigators VALUES (364, 52, 8, false, false, false, 1);
INSERT INTO investigators VALUES (365, 52, 203, false, false, false, 1);
INSERT INTO investigators VALUES (366, 53, 117, false, false, true, 1);
INSERT INTO investigators VALUES (367, 53, 118, false, false, false, 1);
INSERT INTO investigators VALUES (368, 53, 100, false, false, false, 1);
INSERT INTO investigators VALUES (369, 54, 88, false, false, true, 1);
INSERT INTO investigators VALUES (370, 54, 86, false, false, false, 1);
INSERT INTO investigators VALUES (371, 54, 87, false, false, false, 1);
INSERT INTO investigators VALUES (372, 55, 202, false, false, true, 1);
INSERT INTO investigators VALUES (373, 55, 14, false, false, false, 1);
INSERT INTO investigators VALUES (374, 56, 202, false, false, true, 1);
INSERT INTO investigators VALUES (375, 56, 14, false, false, false, 1);
INSERT INTO investigators VALUES (376, 57, 15, false, false, true, 1);
INSERT INTO investigators VALUES (377, 57, 6, false, false, false, 1);
INSERT INTO investigators VALUES (378, 58, 141, false, false, true, 1);
INSERT INTO investigators VALUES (379, 58, 8, false, false, false, 1);
INSERT INTO investigators VALUES (380, 58, 86, false, false, false, 1);
INSERT INTO investigators VALUES (381, 58, 87, false, false, false, 1);
INSERT INTO investigators VALUES (382, 58, 73, false, false, false, 1);
INSERT INTO investigators VALUES (383, 58, 204, false, false, false, 1);
INSERT INTO investigators VALUES (384, 58, 205, false, false, false, 1);
INSERT INTO investigators VALUES (385, 58, 206, false, false, false, 1);
INSERT INTO investigators VALUES (386, 58, 207, false, false, false, 1);
INSERT INTO investigators VALUES (387, 58, 88, false, false, false, 1);
INSERT INTO investigators VALUES (388, 58, 208, false, false, false, 1);
INSERT INTO investigators VALUES (389, 58, 153, false, false, false, 1);
INSERT INTO investigators VALUES (390, 58, 209, false, false, false, 1);
INSERT INTO investigators VALUES (391, 58, 135, false, false, false, 1);
INSERT INTO investigators VALUES (392, 58, 210, false, false, false, 1);
INSERT INTO investigators VALUES (393, 58, 211, false, false, false, 1);
INSERT INTO investigators VALUES (394, 58, 212, false, false, false, 1);
INSERT INTO investigators VALUES (395, 59, 9, false, false, true, 1);
INSERT INTO investigators VALUES (396, 60, 159, false, false, true, 1);
INSERT INTO investigators VALUES (397, 60, 5, false, false, false, 1);
INSERT INTO investigators VALUES (398, 60, 158, false, false, false, 1);
INSERT INTO investigators VALUES (399, 60, 160, false, false, false, 1);
INSERT INTO investigators VALUES (400, 61, 158, false, false, true, 1);
INSERT INTO investigators VALUES (401, 61, 159, false, false, false, 1);
INSERT INTO investigators VALUES (402, 61, 5, false, false, false, 1);
INSERT INTO investigators VALUES (403, 61, 160, false, false, false, 1);
INSERT INTO investigators VALUES (404, 62, 213, false, false, true, 1);
INSERT INTO investigators VALUES (405, 62, 86, false, false, false, 1);
INSERT INTO investigators VALUES (406, 62, 87, false, false, false, 1);
INSERT INTO investigators VALUES (407, 62, 214, false, false, false, 1);
INSERT INTO investigators VALUES (408, 62, 107, false, false, false, 1);
INSERT INTO investigators VALUES (409, 62, 109, false, false, false, 1);
INSERT INTO investigators VALUES (410, 62, 73, false, false, false, 1);
INSERT INTO investigators VALUES (411, 62, 108, false, false, false, 1);
INSERT INTO investigators VALUES (412, 62, 113, false, false, false, 1);
INSERT INTO investigators VALUES (413, 62, 111, false, false, false, 1);
INSERT INTO investigators VALUES (414, 62, 112, false, false, false, 1);
INSERT INTO investigators VALUES (415, 62, 215, false, false, false, 1);
INSERT INTO investigators VALUES (416, 63, 216, false, false, true, 1);
INSERT INTO investigators VALUES (417, 63, 217, false, false, false, 1);
INSERT INTO investigators VALUES (418, 63, 6, false, false, false, 1);
INSERT INTO investigators VALUES (419, 63, 69, false, false, false, 1);
INSERT INTO investigators VALUES (420, 63, 88, false, false, false, 1);
INSERT INTO investigators VALUES (421, 63, 218, false, false, false, 1);
INSERT INTO investigators VALUES (422, 64, 200, false, false, true, 1);
INSERT INTO investigators VALUES (423, 64, 83, false, false, false, 1);
INSERT INTO investigators VALUES (424, 64, 201, false, false, false, 1);
INSERT INTO investigators VALUES (425, 65, 108, false, false, true, 1);
INSERT INTO investigators VALUES (426, 65, 8, false, false, false, 1);
INSERT INTO investigators VALUES (427, 65, 219, false, false, false, 1);
INSERT INTO investigators VALUES (428, 65, 138, false, false, false, 1);
INSERT INTO investigators VALUES (429, 65, 86, false, false, false, 1);
INSERT INTO investigators VALUES (430, 66, 220, false, false, true, 1);
INSERT INTO investigators VALUES (431, 66, 221, false, false, false, 1);
INSERT INTO investigators VALUES (432, 66, 153, false, false, false, 1);
INSERT INTO investigators VALUES (433, 67, 16, false, false, true, 1);
INSERT INTO investigators VALUES (434, 67, 222, false, false, false, 1);
INSERT INTO investigators VALUES (435, 67, 223, false, false, false, 1);
INSERT INTO investigators VALUES (436, 68, 224, false, false, true, 1);
INSERT INTO investigators VALUES (437, 68, 225, false, false, false, 1);
INSERT INTO investigators VALUES (438, 68, 226, false, false, false, 1);
INSERT INTO investigators VALUES (439, 68, 227, false, false, false, 1);
INSERT INTO investigators VALUES (440, 68, 228, false, false, false, 1);
INSERT INTO investigators VALUES (441, 69, 229, false, false, true, 1);
INSERT INTO investigators VALUES (442, 69, 230, false, false, false, 1);
INSERT INTO investigators VALUES (443, 69, 231, false, false, false, 1);
INSERT INTO investigators VALUES (444, 70, 168, false, false, true, 1);
INSERT INTO investigators VALUES (445, 70, 167, false, false, false, 1);
INSERT INTO investigators VALUES (446, 70, 139, false, false, false, 1);
INSERT INTO investigators VALUES (447, 70, 232, false, false, false, 1);
INSERT INTO investigators VALUES (448, 70, 46, false, false, false, 1);
INSERT INTO investigators VALUES (449, 70, 233, false, false, false, 1);
INSERT INTO investigators VALUES (450, 71, 84, false, false, true, 1);
INSERT INTO investigators VALUES (451, 71, 85, false, false, false, 1);
INSERT INTO investigators VALUES (452, 71, 86, false, false, false, 1);
INSERT INTO investigators VALUES (453, 71, 87, false, false, false, 1);
INSERT INTO investigators VALUES (454, 71, 88, false, false, false, 1);
INSERT INTO investigators VALUES (455, 71, 208, false, false, false, 1);
INSERT INTO investigators VALUES (456, 71, 89, false, false, false, 1);
INSERT INTO investigators VALUES (457, 72, 234, false, false, true, 1);
INSERT INTO investigators VALUES (458, 72, 235, false, false, false, 1);
INSERT INTO investigators VALUES (459, 72, 236, false, false, false, 1);
INSERT INTO investigators VALUES (460, 72, 237, false, false, false, 1);
INSERT INTO investigators VALUES (461, 72, 238, false, false, false, 1);
INSERT INTO investigators VALUES (462, 73, 18, false, false, true, 1);
INSERT INTO investigators VALUES (463, 74, 212, false, false, true, 1);
INSERT INTO investigators VALUES (464, 74, 205, false, false, false, 1);
INSERT INTO investigators VALUES (465, 74, 239, false, false, false, 1);
INSERT INTO investigators VALUES (466, 75, 212, false, false, true, 1);
INSERT INTO investigators VALUES (467, 75, 205, false, false, false, 1);
INSERT INTO investigators VALUES (468, 75, 239, false, false, false, 1);
INSERT INTO investigators VALUES (469, 76, 240, false, false, true, 1);
INSERT INTO investigators VALUES (470, 76, 241, false, false, false, 1);
INSERT INTO investigators VALUES (471, 76, 242, false, false, false, 1);
INSERT INTO investigators VALUES (472, 76, 243, false, false, false, 1);
INSERT INTO investigators VALUES (473, 76, 244, false, false, false, 1);
INSERT INTO investigators VALUES (474, 76, 11, false, false, false, 1);
INSERT INTO investigators VALUES (475, 76, 245, false, false, false, 1);
INSERT INTO investigators VALUES (476, 76, 246, false, false, false, 1);
INSERT INTO investigators VALUES (477, 76, 247, false, false, false, 1);
INSERT INTO investigators VALUES (478, 77, 89, false, false, true, 1);
INSERT INTO investigators VALUES (479, 77, 86, false, false, false, 1);
INSERT INTO investigators VALUES (480, 77, 87, false, false, false, 1);
INSERT INTO investigators VALUES (481, 78, 160, false, false, true, 1);
INSERT INTO investigators VALUES (482, 78, 159, false, false, false, 1);
INSERT INTO investigators VALUES (483, 78, 5, false, false, false, 1);
INSERT INTO investigators VALUES (484, 79, 138, false, false, true, 1);
INSERT INTO investigators VALUES (485, 79, 108, false, false, false, 1);
INSERT INTO investigators VALUES (486, 79, 8, false, false, false, 1);
INSERT INTO investigators VALUES (487, 79, 135, false, false, false, 1);
INSERT INTO investigators VALUES (488, 80, 8, false, false, true, 1);
INSERT INTO investigators VALUES (489, 80, 108, false, false, false, 1);
INSERT INTO investigators VALUES (490, 80, 138, false, false, false, 1);
INSERT INTO investigators VALUES (491, 80, 135, false, false, false, 1);
INSERT INTO investigators VALUES (492, 81, 248, false, false, true, 1);
INSERT INTO investigators VALUES (493, 81, 249, false, false, false, 1);
INSERT INTO investigators VALUES (494, 81, 250, false, false, false, 1);
INSERT INTO investigators VALUES (495, 81, 251, false, false, false, 1);
INSERT INTO investigators VALUES (496, 82, 69, false, false, true, 1);
INSERT INTO investigators VALUES (497, 82, 252, false, false, false, 1);
INSERT INTO investigators VALUES (498, 82, 253, false, false, false, 1);
INSERT INTO investigators VALUES (499, 82, 254, false, false, false, 1);
INSERT INTO investigators VALUES (500, 83, 87, false, false, true, 1);
INSERT INTO investigators VALUES (501, 83, 109, false, false, false, 1);
INSERT INTO investigators VALUES (502, 83, 107, false, false, false, 1);
INSERT INTO investigators VALUES (503, 83, 255, false, false, false, 1);
INSERT INTO investigators VALUES (504, 83, 86, false, false, false, 1);
INSERT INTO investigators VALUES (505, 83, 256, false, false, false, 1);
INSERT INTO investigators VALUES (506, 84, 107, false, false, true, 1);
INSERT INTO investigators VALUES (507, 84, 73, false, false, false, 1);
INSERT INTO investigators VALUES (508, 84, 87, false, false, false, 1);
INSERT INTO investigators VALUES (509, 84, 71, false, false, false, 1);
INSERT INTO investigators VALUES (510, 84, 108, false, false, false, 1);
INSERT INTO investigators VALUES (511, 84, 109, false, false, false, 1);
INSERT INTO investigators VALUES (512, 84, 110, false, false, false, 1);
INSERT INTO investigators VALUES (513, 84, 111, false, false, false, 1);
INSERT INTO investigators VALUES (514, 84, 112, false, false, false, 1);
INSERT INTO investigators VALUES (515, 84, 113, false, false, false, 1);
INSERT INTO investigators VALUES (516, 84, 114, false, false, false, 1);
INSERT INTO investigators VALUES (517, 84, 257, false, false, false, 1);
INSERT INTO investigators VALUES (518, 85, 258, false, false, true, 1);
INSERT INTO investigators VALUES (519, 85, 259, false, false, false, 1);
INSERT INTO investigators VALUES (520, 85, 260, false, false, false, 1);
INSERT INTO investigators VALUES (521, 86, 141, false, false, true, 1);
INSERT INTO investigators VALUES (522, 86, 8, false, false, false, 1);
INSERT INTO investigators VALUES (523, 86, 86, false, false, false, 1);
INSERT INTO investigators VALUES (524, 86, 87, false, false, false, 1);
INSERT INTO investigators VALUES (525, 86, 73, false, false, false, 1);
INSERT INTO investigators VALUES (526, 86, 204, false, false, false, 1);
INSERT INTO investigators VALUES (527, 86, 205, false, false, false, 1);
INSERT INTO investigators VALUES (528, 86, 206, false, false, false, 1);
INSERT INTO investigators VALUES (529, 86, 207, false, false, false, 1);
INSERT INTO investigators VALUES (530, 86, 88, false, false, false, 1);
INSERT INTO investigators VALUES (531, 86, 208, false, false, false, 1);
INSERT INTO investigators VALUES (532, 86, 153, false, false, false, 1);
INSERT INTO investigators VALUES (533, 86, 209, false, false, false, 1);
INSERT INTO investigators VALUES (534, 86, 135, false, false, false, 1);
INSERT INTO investigators VALUES (535, 86, 210, false, false, false, 1);
INSERT INTO investigators VALUES (536, 86, 211, false, false, false, 1);
INSERT INTO investigators VALUES (537, 86, 212, false, false, false, 1);
INSERT INTO investigators VALUES (538, 87, 207, false, false, true, 1);
INSERT INTO investigators VALUES (539, 87, 204, false, false, false, 1);
INSERT INTO investigators VALUES (540, 87, 73, false, false, false, 1);
INSERT INTO investigators VALUES (541, 87, 8, false, false, false, 1);
INSERT INTO investigators VALUES (542, 87, 135, false, false, false, 1);
INSERT INTO investigators VALUES (543, 87, 86, false, false, false, 1);
INSERT INTO investigators VALUES (544, 88, 198, false, false, true, 1);
INSERT INTO investigators VALUES (545, 88, 13, false, false, false, 1);
INSERT INTO investigators VALUES (546, 88, 199, false, false, false, 1);
INSERT INTO investigators VALUES (547, 89, 59, false, false, true, 1);
INSERT INTO investigators VALUES (548, 89, 60, false, false, false, 1);
INSERT INTO investigators VALUES (549, 90, 261, false, false, true, 1);
INSERT INTO investigators VALUES (550, 90, 170, false, false, false, 1);
INSERT INTO investigators VALUES (551, 90, 46, false, false, false, 1);
INSERT INTO investigators VALUES (552, 90, 167, false, false, false, 1);
INSERT INTO investigators VALUES (553, 91, 59, false, false, true, 1);
INSERT INTO investigators VALUES (554, 91, 262, false, false, false, 1);
INSERT INTO investigators VALUES (555, 92, 263, false, false, true, 1);
INSERT INTO investigators VALUES (556, 92, 83, false, false, false, 1);
INSERT INTO investigators VALUES (557, 93, 59, false, false, true, 1);
INSERT INTO investigators VALUES (558, 93, 167, false, false, false, 1);
INSERT INTO investigators VALUES (559, 93, 46, false, false, false, 1);
INSERT INTO investigators VALUES (560, 94, 69, false, false, true, 1);
INSERT INTO investigators VALUES (561, 94, 74, false, false, false, 1);
INSERT INTO investigators VALUES (562, 94, 73, false, false, false, 1);
INSERT INTO investigators VALUES (563, 94, 8, false, false, false, 1);
INSERT INTO investigators VALUES (564, 94, 71, false, false, false, 1);
INSERT INTO investigators VALUES (565, 94, 75, false, false, false, 1);
INSERT INTO investigators VALUES (566, 94, 72, false, false, false, 1);
INSERT INTO investigators VALUES (567, 94, 264, false, false, false, 1);
INSERT INTO investigators VALUES (568, 95, 265, false, false, true, 1);
INSERT INTO investigators VALUES (569, 95, 266, false, false, false, 1);
INSERT INTO investigators VALUES (570, 95, 12, false, false, false, 1);
INSERT INTO investigators VALUES (571, 95, 267, false, false, false, 1);
INSERT INTO investigators VALUES (572, 95, 268, false, false, false, 1);
INSERT INTO investigators VALUES (573, 95, 269, false, false, false, 1);
INSERT INTO investigators VALUES (574, 96, 270, false, false, true, 1);
INSERT INTO investigators VALUES (575, 96, 8, false, false, false, 1);
INSERT INTO investigators VALUES (576, 96, 73, false, false, false, 1);
INSERT INTO investigators VALUES (577, 96, 86, false, false, false, 1);
INSERT INTO investigators VALUES (578, 96, 87, false, false, false, 1);
INSERT INTO investigators VALUES (579, 96, 204, false, false, false, 1);
INSERT INTO investigators VALUES (580, 96, 207, false, false, false, 1);
INSERT INTO investigators VALUES (581, 96, 211, false, false, false, 1);
INSERT INTO investigators VALUES (582, 96, 271, false, false, false, 1);
INSERT INTO investigators VALUES (583, 97, 272, false, false, true, 1);
INSERT INTO investigators VALUES (584, 97, 273, false, false, false, 1);
INSERT INTO investigators VALUES (585, 97, 274, false, false, false, 1);
INSERT INTO investigators VALUES (586, 97, 275, false, false, false, 1);
INSERT INTO investigators VALUES (587, 97, 13, false, false, false, 1);
INSERT INTO investigators VALUES (588, 97, 72, false, false, false, 1);
INSERT INTO investigators VALUES (589, 98, 141, false, false, true, 1);
INSERT INTO investigators VALUES (590, 98, 8, false, false, false, 1);
INSERT INTO investigators VALUES (591, 99, 276, false, false, true, 1);
INSERT INTO investigators VALUES (592, 99, 25, false, false, false, 1);
INSERT INTO investigators VALUES (593, 99, 277, false, false, false, 1);
INSERT INTO investigators VALUES (594, 99, 2, false, false, false, 1);
INSERT INTO investigators VALUES (595, 99, 278, false, false, false, 1);
INSERT INTO investigators VALUES (596, 99, 232, false, false, false, 1);
INSERT INTO investigators VALUES (597, 100, 279, false, false, true, 1);
INSERT INTO investigators VALUES (598, 100, 99, false, false, false, 1);
INSERT INTO investigators VALUES (599, 100, 280, false, false, false, 1);
INSERT INTO investigators VALUES (600, 100, 279, false, false, true, 1);
INSERT INTO investigators VALUES (601, 101, 281, false, false, true, 1);
INSERT INTO investigators VALUES (602, 101, 282, false, false, false, 1);
INSERT INTO investigators VALUES (603, 101, 283, false, false, false, 1);
INSERT INTO investigators VALUES (604, 101, 284, false, false, false, 1);
INSERT INTO investigators VALUES (605, 101, 285, false, false, false, 1);
INSERT INTO investigators VALUES (606, 101, 286, false, false, false, 1);
INSERT INTO investigators VALUES (607, 101, 287, false, false, false, 1);


--
-- Data for Name: observing_parameters; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO observing_parameters VALUES (1, 1, 1, 'Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (2, 2, 1, 'Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (3, 3, 1, 'Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (4, 4, 1, 'Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (5, 5, 1, 'Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (6, 6, 1, 'Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (7, 7, 1, 'Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (8, 8, 1, 'Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (9, 9, 1, 'Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (10, 10, 1, 'Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (11, 11, 1, 'Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (12, 12, 1, 'Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (13, 13, 1, 'Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (14, 14, 1, 'Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (15, 15, 1, 'Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (16, 16, 1, 'Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (17, 17, 1, 'Eb,Gb,Y27,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (18, 18, 1, 'Eb,Gb,Y27,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (19, 19, 1, 'Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (20, 20, 1, 'Gb,Y27,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (21, 21, 1, 'Eb,Gb,Y27,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (22, 22, 1, 'Eb,Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (23, 23, 1, 'Eb,Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (24, 23, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (25, 24, 1, 'Eb,Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (26, 24, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (27, 25, 1, 'Eb,Gb,VLBA', NULL, NULL, NULL, NULL);
INSERT INTO observing_parameters VALUES (28, 25, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (29, 26, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (30, 27, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (31, 29, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (32, 33, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (33, 39, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (34, 42, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (35, 43, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (36, 49, 6, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (37, 50, 6, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (38, 51, 6, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (39, 81, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (40, 82, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (41, 83, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (42, 91, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (43, 92, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (44, 93, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (45, 94, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (46, 95, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (47, 96, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (48, 97, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (49, 98, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (50, 99, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (51, 100, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (52, 101, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (53, 102, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (54, 103, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (55, 104, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (56, 105, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (57, 106, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (58, 107, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (59, 108, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (60, 112, 4, NULL, NULL, 15, NULL, NULL);
INSERT INTO observing_parameters VALUES (61, 112, 5, NULL, NULL, 21, NULL, NULL);
INSERT INTO observing_parameters VALUES (62, 116, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (63, 117, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (64, 118, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (65, 119, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (66, 125, 4, NULL, NULL, 15, NULL, NULL);
INSERT INTO observing_parameters VALUES (67, 125, 5, NULL, NULL, 21, NULL, NULL);
INSERT INTO observing_parameters VALUES (68, 136, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (69, 150, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (70, 151, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (71, 152, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (72, 153, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (73, 154, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (74, 155, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (75, 156, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (76, 164, 4, NULL, NULL, 15, NULL, NULL);
INSERT INTO observing_parameters VALUES (77, 164, 5, NULL, NULL, 21, NULL, NULL);
INSERT INTO observing_parameters VALUES (78, 165, 2, NULL, NULL, 9, NULL, NULL);
INSERT INTO observing_parameters VALUES (79, 165, 3, NULL, NULL, 14, NULL, NULL);
INSERT INTO observing_parameters VALUES (80, 214, 7, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (81, 248, 6, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (82, 249, 6, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (83, 250, 6, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (84, 251, 6, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (85, 252, 6, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (86, 253, 6, NULL, NULL, NULL, true, NULL);
INSERT INTO observing_parameters VALUES (87, 254, 7, NULL, NULL, NULL, true, NULL);


--
-- Data for Name: observing_types; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO observing_types VALUES (1, 'radar');
INSERT INTO observing_types VALUES (2, 'vlbi');
INSERT INTO observing_types VALUES (3, 'pulsar');
INSERT INTO observing_types VALUES (4, 'continuum');
INSERT INTO observing_types VALUES (5, 'spectral line');
INSERT INTO observing_types VALUES (6, 'maintenance');
INSERT INTO observing_types VALUES (7, 'calibration');
INSERT INTO observing_types VALUES (8, 'testing');


--
-- Data for Name: opportunities; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO opportunities VALUES (1, 10, '2009-07-15 04:00:00-04', 3.75);
INSERT INTO opportunities VALUES (2, 11, '2009-07-16 05:00:00-04', 3.5);
INSERT INTO opportunities VALUES (3, 12, '2009-07-17 06:00:00-04', 3.5);
INSERT INTO opportunities VALUES (4, 13, '2009-06-19 13:45:00-04', 1.5);
INSERT INTO opportunities VALUES (5, 14, '2009-06-26 13:00:00-04', 1.5);
INSERT INTO opportunities VALUES (7, 16, '2009-06-14 13:00:00-04', 1.5);
INSERT INTO opportunities VALUES (8, 17, '2009-06-16 13:00:00-04', 1.5);
INSERT INTO opportunities VALUES (9, 18, '2009-06-21 12:30:00-04', 1.5);
INSERT INTO opportunities VALUES (23, 29, '2009-07-26 00:00:00-04', 72);
INSERT INTO opportunities VALUES (24, 30, '2009-08-25 00:00:00-04', 72);
INSERT INTO opportunities VALUES (26, 32, '2009-07-16 00:00:00-04', 72);
INSERT INTO opportunities VALUES (27, 33, '2009-08-15 00:00:00-04', 72);
INSERT INTO opportunities VALUES (28, 34, '2009-09-14 00:00:00-04', 72);
INSERT INTO opportunities VALUES (32, 38, '2009-07-22 00:00:00-04', 48);
INSERT INTO opportunities VALUES (33, 39, '2009-08-05 00:00:00-04', 48);
INSERT INTO opportunities VALUES (34, 40, '2009-08-19 00:00:00-04', 48);
INSERT INTO opportunities VALUES (35, 41, '2009-09-02 00:00:00-04', 48);
INSERT INTO opportunities VALUES (36, 42, '2009-09-16 00:00:00-04', 48);
INSERT INTO opportunities VALUES (37, 43, '2009-09-30 00:00:00-04', 48);
INSERT INTO opportunities VALUES (46, 51, '2009-06-13 00:00:00-04', 240);
INSERT INTO opportunities VALUES (47, 52, '2009-10-11 00:00:00-04', 240);
INSERT INTO opportunities VALUES (48, 53, '2010-02-08 00:00:00-05', 240);
INSERT INTO opportunities VALUES (49, 54, '2010-06-08 00:00:00-04', 240);
INSERT INTO opportunities VALUES (50, 55, '2010-10-06 00:00:00-04', 240);
INSERT INTO opportunities VALUES (51, 56, '2011-02-03 00:00:00-05', 240);
INSERT INTO opportunities VALUES (52, 57, '2011-06-03 00:00:00-04', 240);
INSERT INTO opportunities VALUES (53, 58, '2009-07-02 00:00:00-04', 24);
INSERT INTO opportunities VALUES (57, 31, '2009-06-26 00:00:00-04', 72);
INSERT INTO opportunities VALUES (63, 61, '2009-07-02 00:00:00-04', 48);
INSERT INTO opportunities VALUES (64, 59, '2009-06-22 00:00:00-04', 48);
INSERT INTO opportunities VALUES (65, 60, '2009-06-08 00:00:00-04', 48);
INSERT INTO opportunities VALUES (66, 35, '2009-06-04 00:00:00-04', 48);
INSERT INTO opportunities VALUES (67, 37, '2009-07-07 00:00:00-04', 48);
INSERT INTO opportunities VALUES (84, 76, '2009-06-22 00:00:00-04', 24);
INSERT INTO opportunities VALUES (85, 77, '2009-06-23 00:00:00-04', 48);
INSERT INTO opportunities VALUES (86, 78, '2009-06-24 00:00:00-04', 48);
INSERT INTO opportunities VALUES (87, 79, '2009-06-27 00:00:00-04', 72);
INSERT INTO opportunities VALUES (88, 80, '2009-07-02 00:00:00-04', 72);
INSERT INTO opportunities VALUES (89, 81, '2009-07-09 00:00:00-04', 72);
INSERT INTO opportunities VALUES (90, 82, '2009-07-19 00:00:00-04', 72);
INSERT INTO opportunities VALUES (92, 15, '2009-06-09 13:30:00-04', 13);
INSERT INTO opportunities VALUES (93, 28, '2009-06-27 00:00:00-04', 72);
INSERT INTO opportunities VALUES (95, 36, '2009-07-02 00:00:00-04', 48);
INSERT INTO opportunities VALUES (97, 83, '2009-07-19 06:00:00-04', 6);


--
-- Data for Name: parameters; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO parameters VALUES (1, 'Instruments', 'string');
INSERT INTO parameters VALUES (2, 'LST Include Low', 'float');
INSERT INTO parameters VALUES (3, 'LST Include Hi', 'float');
INSERT INTO parameters VALUES (4, 'LST Exclude Low', 'float');
INSERT INTO parameters VALUES (5, 'LST Exclude Hi', 'float');
INSERT INTO parameters VALUES (6, 'UTC Flag', 'boolean');
INSERT INTO parameters VALUES (7, 'Night-time Flag', 'boolean');
INSERT INTO parameters VALUES (8, 'Obs Eff Limit', 'float');
INSERT INTO parameters VALUES (9, 'Atmos St Limit', 'float');
INSERT INTO parameters VALUES (10, 'Tr Err Limit', 'float');
INSERT INTO parameters VALUES (11, 'Min Eff TSys', 'float');
INSERT INTO parameters VALUES (12, 'HA Limit', 'float');
INSERT INTO parameters VALUES (13, 'ZA Limit', 'float');
INSERT INTO parameters VALUES (14, 'Solar Avoid', 'float');
INSERT INTO parameters VALUES (15, 'Precip', 'float');
INSERT INTO parameters VALUES (16, 'Wind', 'float');
INSERT INTO parameters VALUES (17, 'Time Day', 'datetime');
INSERT INTO parameters VALUES (18, 'Transit', 'boolean');
INSERT INTO parameters VALUES (19, 'Transit Before', 'float');
INSERT INTO parameters VALUES (20, 'Transit After', 'float');


--
-- Data for Name: project_types; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO project_types VALUES (1, 'science');
INSERT INTO project_types VALUES (2, 'non-science');


--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO projects VALUES (1, 1, 1, 'GBT09A-001', '', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (2, 7, 1, 'BB240', 'RIPL: Radio Interferometric PLanet Search', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (3, 6, 1, 'BB261', 'The Megamaser Cosmology Project: Year 2', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (4, 2, 1, 'BB268', 'Detecting the nucleus of M31', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (5, 6, 1, 'BM290', 'A direct geometric distance to a quiescent black hole Xray binary', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (6, 2, 1, 'BM305', 'Resolving the Radio Emission of the Luminous SMM Galaxy GOODS 850-16 Resolving the Radio Emission of the Luminous SMM Galaxy GOODS 850-16', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (7, 2, 1, 'BM306', 'Imaging the interacting young binary V773 Tau A/B', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (8, 2, 1, 'BP157', 'Confirmation of Large Coronal Loops on an RS CVN Binary', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (9, 16, 1, 'GBT04A-003', 'Highly Redshifted HI and OH Absorption in Red Quasars', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (10, 15, 1, 'GBT05C-027', 'An Exact Identification of High Densities in Molecular Clouds', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (11, 12, 1, 'GBT06C-048', 'HI 21cm absorption in strong MgII and CI absorbers in the redshift desert', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (12, 7, 1, 'GBT07A-035', 'Using CCH lines to measure changes in fundamental constants', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (13, 7, 1, 'GBT07A-051', 'A GBT Legacy Survey of Prebiotic Molecules Toward SgrB2(N-LMH) and TMC-1', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (14, 7, 1, 'GBT07A-086', 'The Detection of  the Missing Baryons with the NVII Line', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (15, 7, 1, 'GBT07A-087', 'Detecting nHz Gravitational Radiation using a Pulsar Timing Array', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (16, 9, 1, 'GBT07C-032', 'What is the gas temperature in the nearest cluster-forming region?', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (17, 4, 1, 'GBT08A-004', 'OH Absorption In the Lensing and Host Galaxies of J0414+0534', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (18, 4, 1, 'GBT08A-037', 'Radio monitoring of magnetars', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (19, 4, 1, 'GBT08A-048', 'Correlated Variability of Astrophysical Masers I: monitoring of NGC7538 IRS1', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (20, 4, 1, 'GBT08A-073', 'A deep search for associated HI 21cm absorption in red quasars', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (21, 4, 1, 'GBT08A-085', '"Tomography" of Pulsar Polar Emission Region', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (22, 5, 1, 'GBT08B-005', 'High-Resolution 12.6-cm Radar Mapping of the Nearside of the Moon', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (23, 5, 1, 'GBT08B-010', 'Molecular Line Survey of Edge Cloud 2 Southern Core', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (24, 5, 1, 'GBT08B-025', 'Timing and General Relativity in the Double Pulsar System', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (25, 5, 1, 'GBT08B-026', 'The H 2p-2s fine-structure line toward HII Regions and Planetary Nebulae', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (26, 5, 1, 'GBT08B-049', 'Observations of the Chandrayaan-1 and Lunar Reconnaissance Orbiter Spacecraft', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (27, 6, 1, 'GBT08C-009', 'A Combined GBT/PdBI CO Survey of Submm Galaxies', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (28, 6, 1, 'GBT08C-014', 'Studying the magnetar XTE J1810-197', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (29, 6, 1, 'GBT08C-023', 'GLAST timing at GBT: six key radio-faint pulsars', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (30, 6, 1, 'GBT08C-026', '3.3 mm MUSTANG Imaging of the Vega Debris Disk', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (31, 6, 1, 'GBT08C-035', 'The Megamaser Cosmology Project: Year 2', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (32, 6, 1, 'GBT08C-049', 'Timing of Newly Discovered MSPs in the Globular Cluster NGC6517', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (33, 6, 1, 'GBT08C-061', 'Search for prebiotic molecules in the Solar-type protostar IRAS 16293-2422', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (34, 6, 1, 'GBT08C-065', 'Search for Zeeman Splitting at High Redshift', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (35, 6, 1, 'GBT08C-070', 'Deep Zpectrometer integration toward the Cloverleaf galaxy', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (36, 6, 1, 'GBT08C-073', 'A CO(1-0) Survey of Dusty Galaxies at High Redshift', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (37, 6, 1, 'GBT08C-076', 'Long Term Timing of 55 Recycled Pulsars in Bulge Globular Clusters', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (38, 6, 1, 'GBT08C-078', 'MUSTANG Observations of Cygnus A', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (39, 1, 1, 'GBT09A-002', 'Discovering Milky Way HII Regions', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (40, 1, 1, 'GBT09A-003', 'Timing the pulsars in M62, NGC 6544 and NGC 6624', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (41, 1, 1, 'GBT09A-004', 'Search for HI 21cm absorption in a complete sample of DLAs at z>2.', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (42, 1, 1, 'GBT09A-007', 'Straightening Out the Galactic Warp', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (43, 1, 1, 'GBT09A-012', 'Study of the ISM conditions in normal star forming galaxies at $z \\sim 1.5$', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (44, 1, 1, 'GBT09A-021', 'SO2: A molecule with maser emission and line absorption line in cold dark clouds', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (45, 1, 1, 'GBT09A-025', 'The spin temperature of high redshift damped Lyman-alpha systems', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (46, 1, 1, 'GBT09A-034', '21 cm HI Observations of intermediate-z Clusters of Galaxies', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (47, 1, 1, 'GBT09A-038', 'Continued Timing of Pulsars in M22', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (48, 1, 1, 'GBT09A-040', 'Probing the Gas Properties of Star-Forming Galaxies at High-z via Strong Lensing', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (49, 1, 1, 'GBT09A-046', 'A Search for Faint Extended HI in Nearby Galaxy Groups - copy', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (50, 1, 1, 'GBT09A-055', 'A New Approach to Discovering Highly Obscured Radio-Loud Quasars', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (51, 1, 1, 'GBT09A-058', 'Confirmation Observations of New Pulsars Discovered by the PSC', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (52, 1, 1, 'GBT09A-062', 'New pulsar identifications of TeV gamma-ray sources', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (53, 1, 1, 'GBT09A-070', 'Calibrating the Transmitted Radar Signal from the LRO Spacecraft', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (54, 1, 1, 'GBT09A-081', 'A search for giant pulses in interpulse pulsars', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (55, 1, 1, 'GBT09A-092', 'Maintenance Observing with the GBT', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (56, 1, 1, 'GBT09A-093', 'Educational Projects on the GBT', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (57, 1, 1, 'GBT09A-094', 'NRAO 2009 CV/GB Summer Student Observing Project', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (58, 1, 1, 'GBT09A-095', 'Searching for Variability in PSR J0348+04', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (59, 1, 1, 'GBT09A-096', 'Observations for the 5th NAIC/NRAO Single Dish School', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (60, 2, 1, 'GBT09B-001', 'Searching for Star Formation in the 3 kpc Arm', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (61, 2, 1, 'GBT09B-002', 'Discovering Milky Way HII Regions', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (62, 2, 1, 'GBT09B-003', 'On the Trail of the Enigmatic Millisecond Binary Pulsar PSR J1723-28', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (63, 2, 1, 'GBT09B-004', 'Noise and Signal in Pulsar Scintillation', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (64, 2, 1, 'GBT09B-005', 'A Search for HI Absorption Toward Red AGN in Non-Elliptical Host Galaxies', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (65, 2, 1, 'GBT09B-006', 'Three newly discovered pulsars', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (66, 2, 1, 'GBT09B-008', 'Confirmation of Radio Pulsar Candidates in M31', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (67, 2, 1, 'GBT09B-010', 'Surveying Cyanoformaldehyde (CNCHO) in Galactic Environments', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (68, 2, 1, 'GBT09B-011', 'HI Mass Determinations of Compact Groups of Galaxies', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (69, 2, 1, 'GBT09B-012', 'Relativistic Probes of the WHIM  (redux)', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (70, 2, 1, 'GBT09B-013', 'A search for luminous H2O maser emission in lensed, FIR luminous QSOs at z~4', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (71, 2, 1, 'GBT09B-014', 'GBT radio monitoring of magnetars', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (72, 2, 1, 'GBT09B-015', 'Chemical complexity in the nuclei of galaxies. The nucleus of the Milky way', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (73, 2, 1, 'GBT09B-016', 'Searching for low column density HI around NGC 2997 and NGC 6946', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (74, 2, 1, 'GBT09B-017', 'Are the Arches and Quintuplet Clusters Pulsar Nurseries?', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (75, 2, 1, 'GBT09B-018', 'Two Very Dispersed Pulsars Near SgrA*: Continued Timing and Spectrum Estimation', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (76, 2, 1, 'GBT09B-019', 'Constraining the Anomalous Emission in the Perseus Region on Arcminute Scales', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (77, 2, 1, 'GBT09B-021', 'A search for the youngest pulsar in the Galaxy', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (78, 2, 1, 'GBT09B-022', 'Constraining Galactic Chemical Evolution:  3-Helium Benchmark Abundances in S209', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (79, 2, 1, 'GBT09B-023', 'Search for Radio Pulsations from Gamma-Ray Pulsars Discovered with Fermi', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (80, 2, 1, 'GBT09B-024', 'Searching for Radio Pulsars in Fermi Bright Unidentified Sources', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (81, 2, 1, 'GBT09B-025', 'An OH Absorption Line Survey of the Galactic Scale Molecular Loops', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (82, 2, 1, 'GBT09B-026', 'Cyclic Spectroscopy of Three Pulsars', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (83, 2, 1, 'GBT09B-028', 'Timing of New and Old Rotating Radio Transient Sources', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (84, 2, 1, 'GBT09B-029', 'Timing and General Relativity in the Double Pulsar System', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (85, 2, 1, 'GBT09B-030', 'Optically Compact Dwarf Galaxies', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (86, 2, 1, 'GBT09B-031', 'Timing the New GBT 350 MHz Drift Scan Pulsars', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (87, 2, 1, 'GBT09B-032', 'Ionized Material in the LMXB-MSP Transition System FIRST J102347.67+003841', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (88, 2, 1, 'GBT09B-034', 'Deep Observations of Possible HVC Analogs in the NGC 2403 Group', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (89, 2, 1, 'GBT09B-035', 'Confirming a tentative detection of HI 21cm absorption at z ~ 2.193', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (90, 2, 1, 'GBT09B-036', 'CS(1-0) survey of dense gas at high-redshift', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (91, 2, 1, 'GBT09B-037', 'A search for CH3CHO 1065 MHz emission in Galactic molecular clouds', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (92, 2, 1, 'GBT09B-039', 'C3H2 in the Gravitational Lens B0218+357: Chemical Evolution and Densitometry', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (93, 2, 1, 'GBT09B-040', 'A search for CS 1-0 emission at high redshifts', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (94, 2, 1, 'GBT09B-041', 'Detecting nHz Gravitational Radiation using a Pulsar Timing Array', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (95, 2, 1, 'GBT09B-042', 'Establishing a scenario of molecule formation from high Galactic latitude sites', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (96, 2, 1, 'GBT09B-043', 'A Search for Radio Pulsations from Low-Mass X-ray Binaries', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (97, 2, 1, 'GBT09B-044', 'Cyclotron emission from the exo-planet HD 189733b - copy', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (98, 2, 1, 'GBT09B-045', 'Searching For New Pulsars in Eight Low Metallicity Globular Clusters', true, false, false, NULL, NULL);
INSERT INTO projects VALUES (99, 2, 1, 'GBT09B-046', 'Tracing the Physical Conditions in NGC 3079 and Mrk 348 with Methanol', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (100, 2, 1, 'GBT09B-048', 'Venus spin dynamics', false, false, false, NULL, NULL);
INSERT INTO projects VALUES (101, 4, 1, 'GLST011217', 'Probing the High Energy Emission of Microquasars with Multi-wavelength observations', false, false, false, NULL, NULL);


--
-- Data for Name: projects_allotments; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO projects_allotments VALUES (1, 2, 2);
INSERT INTO projects_allotments VALUES (2, 3, 3);
INSERT INTO projects_allotments VALUES (3, 4, 4);
INSERT INTO projects_allotments VALUES (4, 5, 5);
INSERT INTO projects_allotments VALUES (5, 6, 6);
INSERT INTO projects_allotments VALUES (6, 7, 7);
INSERT INTO projects_allotments VALUES (7, 8, 8);
INSERT INTO projects_allotments VALUES (8, 9, 9);
INSERT INTO projects_allotments VALUES (9, 10, 10);
INSERT INTO projects_allotments VALUES (10, 11, 11);
INSERT INTO projects_allotments VALUES (11, 12, 12);
INSERT INTO projects_allotments VALUES (12, 13, 13);
INSERT INTO projects_allotments VALUES (13, 14, 14);
INSERT INTO projects_allotments VALUES (14, 15, 15);
INSERT INTO projects_allotments VALUES (15, 16, 16);
INSERT INTO projects_allotments VALUES (16, 17, 17);
INSERT INTO projects_allotments VALUES (17, 18, 18);
INSERT INTO projects_allotments VALUES (18, 19, 19);
INSERT INTO projects_allotments VALUES (19, 20, 20);
INSERT INTO projects_allotments VALUES (20, 21, 21);
INSERT INTO projects_allotments VALUES (21, 22, 22);
INSERT INTO projects_allotments VALUES (22, 23, 23);
INSERT INTO projects_allotments VALUES (23, 24, 24);
INSERT INTO projects_allotments VALUES (24, 25, 25);
INSERT INTO projects_allotments VALUES (25, 26, 26);
INSERT INTO projects_allotments VALUES (26, 27, 27);
INSERT INTO projects_allotments VALUES (27, 28, 28);
INSERT INTO projects_allotments VALUES (28, 29, 29);
INSERT INTO projects_allotments VALUES (29, 30, 30);
INSERT INTO projects_allotments VALUES (30, 31, 31);
INSERT INTO projects_allotments VALUES (31, 32, 32);
INSERT INTO projects_allotments VALUES (32, 33, 33);
INSERT INTO projects_allotments VALUES (33, 34, 34);
INSERT INTO projects_allotments VALUES (34, 35, 35);
INSERT INTO projects_allotments VALUES (35, 36, 36);
INSERT INTO projects_allotments VALUES (36, 37, 37);
INSERT INTO projects_allotments VALUES (37, 38, 38);
INSERT INTO projects_allotments VALUES (38, 39, 39);
INSERT INTO projects_allotments VALUES (39, 40, 40);
INSERT INTO projects_allotments VALUES (40, 41, 41);
INSERT INTO projects_allotments VALUES (41, 42, 42);
INSERT INTO projects_allotments VALUES (42, 43, 43);
INSERT INTO projects_allotments VALUES (43, 44, 44);
INSERT INTO projects_allotments VALUES (44, 45, 45);
INSERT INTO projects_allotments VALUES (45, 46, 46);
INSERT INTO projects_allotments VALUES (46, 47, 47);
INSERT INTO projects_allotments VALUES (47, 48, 48);
INSERT INTO projects_allotments VALUES (48, 49, 49);
INSERT INTO projects_allotments VALUES (49, 50, 50);
INSERT INTO projects_allotments VALUES (50, 51, 51);
INSERT INTO projects_allotments VALUES (51, 52, 52);
INSERT INTO projects_allotments VALUES (52, 53, 53);
INSERT INTO projects_allotments VALUES (53, 54, 54);
INSERT INTO projects_allotments VALUES (54, 55, 55);
INSERT INTO projects_allotments VALUES (55, 56, 56);
INSERT INTO projects_allotments VALUES (56, 57, 57);
INSERT INTO projects_allotments VALUES (57, 58, 58);
INSERT INTO projects_allotments VALUES (58, 59, 59);
INSERT INTO projects_allotments VALUES (59, 60, 60);
INSERT INTO projects_allotments VALUES (60, 61, 61);
INSERT INTO projects_allotments VALUES (61, 62, 62);
INSERT INTO projects_allotments VALUES (62, 63, 63);
INSERT INTO projects_allotments VALUES (63, 64, 64);
INSERT INTO projects_allotments VALUES (64, 65, 65);
INSERT INTO projects_allotments VALUES (65, 66, 66);
INSERT INTO projects_allotments VALUES (66, 67, 67);
INSERT INTO projects_allotments VALUES (67, 67, 68);
INSERT INTO projects_allotments VALUES (68, 68, 69);
INSERT INTO projects_allotments VALUES (69, 69, 70);
INSERT INTO projects_allotments VALUES (70, 70, 71);
INSERT INTO projects_allotments VALUES (71, 70, 72);
INSERT INTO projects_allotments VALUES (72, 71, 73);
INSERT INTO projects_allotments VALUES (73, 72, 74);
INSERT INTO projects_allotments VALUES (74, 72, 75);
INSERT INTO projects_allotments VALUES (75, 73, 76);
INSERT INTO projects_allotments VALUES (76, 74, 77);
INSERT INTO projects_allotments VALUES (77, 75, 78);
INSERT INTO projects_allotments VALUES (78, 76, 79);
INSERT INTO projects_allotments VALUES (79, 77, 80);
INSERT INTO projects_allotments VALUES (80, 78, 81);
INSERT INTO projects_allotments VALUES (81, 79, 82);
INSERT INTO projects_allotments VALUES (82, 80, 83);
INSERT INTO projects_allotments VALUES (83, 81, 84);
INSERT INTO projects_allotments VALUES (84, 82, 85);
INSERT INTO projects_allotments VALUES (85, 83, 86);
INSERT INTO projects_allotments VALUES (86, 84, 87);
INSERT INTO projects_allotments VALUES (87, 85, 88);
INSERT INTO projects_allotments VALUES (88, 86, 89);
INSERT INTO projects_allotments VALUES (89, 87, 90);
INSERT INTO projects_allotments VALUES (90, 88, 91);
INSERT INTO projects_allotments VALUES (91, 89, 92);
INSERT INTO projects_allotments VALUES (92, 90, 93);
INSERT INTO projects_allotments VALUES (93, 91, 94);
INSERT INTO projects_allotments VALUES (94, 92, 95);
INSERT INTO projects_allotments VALUES (95, 93, 96);
INSERT INTO projects_allotments VALUES (96, 94, 97);
INSERT INTO projects_allotments VALUES (97, 95, 98);
INSERT INTO projects_allotments VALUES (98, 96, 99);
INSERT INTO projects_allotments VALUES (99, 97, 100);
INSERT INTO projects_allotments VALUES (100, 98, 101);
INSERT INTO projects_allotments VALUES (101, 98, 102);
INSERT INTO projects_allotments VALUES (102, 99, 103);
INSERT INTO projects_allotments VALUES (103, 100, 104);
INSERT INTO projects_allotments VALUES (104, 101, 105);


--
-- Data for Name: receiver_groups; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO receiver_groups VALUES (1, 1);
INSERT INTO receiver_groups VALUES (2, 2);
INSERT INTO receiver_groups VALUES (3, 3);
INSERT INTO receiver_groups VALUES (4, 4);
INSERT INTO receiver_groups VALUES (5, 5);
INSERT INTO receiver_groups VALUES (6, 6);
INSERT INTO receiver_groups VALUES (7, 7);
INSERT INTO receiver_groups VALUES (8, 8);
INSERT INTO receiver_groups VALUES (9, 9);
INSERT INTO receiver_groups VALUES (10, 10);
INSERT INTO receiver_groups VALUES (11, 11);
INSERT INTO receiver_groups VALUES (12, 12);
INSERT INTO receiver_groups VALUES (13, 13);
INSERT INTO receiver_groups VALUES (14, 14);
INSERT INTO receiver_groups VALUES (15, 15);
INSERT INTO receiver_groups VALUES (16, 16);
INSERT INTO receiver_groups VALUES (17, 17);
INSERT INTO receiver_groups VALUES (18, 18);
INSERT INTO receiver_groups VALUES (19, 19);
INSERT INTO receiver_groups VALUES (20, 20);
INSERT INTO receiver_groups VALUES (21, 21);
INSERT INTO receiver_groups VALUES (22, 22);
INSERT INTO receiver_groups VALUES (23, 23);
INSERT INTO receiver_groups VALUES (24, 24);
INSERT INTO receiver_groups VALUES (25, 25);
INSERT INTO receiver_groups VALUES (26, 26);
INSERT INTO receiver_groups VALUES (27, 27);
INSERT INTO receiver_groups VALUES (28, 28);
INSERT INTO receiver_groups VALUES (29, 29);
INSERT INTO receiver_groups VALUES (30, 30);
INSERT INTO receiver_groups VALUES (31, 31);
INSERT INTO receiver_groups VALUES (32, 32);
INSERT INTO receiver_groups VALUES (33, 33);
INSERT INTO receiver_groups VALUES (34, 34);
INSERT INTO receiver_groups VALUES (35, 35);
INSERT INTO receiver_groups VALUES (36, 36);
INSERT INTO receiver_groups VALUES (37, 37);
INSERT INTO receiver_groups VALUES (38, 38);
INSERT INTO receiver_groups VALUES (39, 39);
INSERT INTO receiver_groups VALUES (40, 40);
INSERT INTO receiver_groups VALUES (41, 41);
INSERT INTO receiver_groups VALUES (42, 42);
INSERT INTO receiver_groups VALUES (43, 43);
INSERT INTO receiver_groups VALUES (44, 44);
INSERT INTO receiver_groups VALUES (45, 45);
INSERT INTO receiver_groups VALUES (46, 46);
INSERT INTO receiver_groups VALUES (47, 47);
INSERT INTO receiver_groups VALUES (48, 48);
INSERT INTO receiver_groups VALUES (49, 49);
INSERT INTO receiver_groups VALUES (50, 50);
INSERT INTO receiver_groups VALUES (51, 51);
INSERT INTO receiver_groups VALUES (52, 52);
INSERT INTO receiver_groups VALUES (53, 53);
INSERT INTO receiver_groups VALUES (54, 54);
INSERT INTO receiver_groups VALUES (55, 55);
INSERT INTO receiver_groups VALUES (56, 56);
INSERT INTO receiver_groups VALUES (57, 57);
INSERT INTO receiver_groups VALUES (58, 58);
INSERT INTO receiver_groups VALUES (59, 59);
INSERT INTO receiver_groups VALUES (60, 60);
INSERT INTO receiver_groups VALUES (61, 61);
INSERT INTO receiver_groups VALUES (62, 62);
INSERT INTO receiver_groups VALUES (63, 63);
INSERT INTO receiver_groups VALUES (64, 64);
INSERT INTO receiver_groups VALUES (65, 65);
INSERT INTO receiver_groups VALUES (66, 66);
INSERT INTO receiver_groups VALUES (67, 67);
INSERT INTO receiver_groups VALUES (68, 68);
INSERT INTO receiver_groups VALUES (69, 69);
INSERT INTO receiver_groups VALUES (70, 70);
INSERT INTO receiver_groups VALUES (71, 71);
INSERT INTO receiver_groups VALUES (72, 72);
INSERT INTO receiver_groups VALUES (73, 73);
INSERT INTO receiver_groups VALUES (74, 74);
INSERT INTO receiver_groups VALUES (75, 75);
INSERT INTO receiver_groups VALUES (76, 76);
INSERT INTO receiver_groups VALUES (77, 77);
INSERT INTO receiver_groups VALUES (78, 78);
INSERT INTO receiver_groups VALUES (79, 79);
INSERT INTO receiver_groups VALUES (80, 80);
INSERT INTO receiver_groups VALUES (81, 81);
INSERT INTO receiver_groups VALUES (82, 82);
INSERT INTO receiver_groups VALUES (83, 83);
INSERT INTO receiver_groups VALUES (84, 84);
INSERT INTO receiver_groups VALUES (85, 85);
INSERT INTO receiver_groups VALUES (86, 86);
INSERT INTO receiver_groups VALUES (87, 87);
INSERT INTO receiver_groups VALUES (88, 88);
INSERT INTO receiver_groups VALUES (89, 89);
INSERT INTO receiver_groups VALUES (90, 90);
INSERT INTO receiver_groups VALUES (91, 91);
INSERT INTO receiver_groups VALUES (92, 92);
INSERT INTO receiver_groups VALUES (93, 93);
INSERT INTO receiver_groups VALUES (94, 94);
INSERT INTO receiver_groups VALUES (95, 95);
INSERT INTO receiver_groups VALUES (96, 96);
INSERT INTO receiver_groups VALUES (97, 97);
INSERT INTO receiver_groups VALUES (98, 98);
INSERT INTO receiver_groups VALUES (99, 99);
INSERT INTO receiver_groups VALUES (100, 100);
INSERT INTO receiver_groups VALUES (101, 101);
INSERT INTO receiver_groups VALUES (102, 102);
INSERT INTO receiver_groups VALUES (103, 103);
INSERT INTO receiver_groups VALUES (104, 104);
INSERT INTO receiver_groups VALUES (105, 105);
INSERT INTO receiver_groups VALUES (106, 106);
INSERT INTO receiver_groups VALUES (107, 107);
INSERT INTO receiver_groups VALUES (108, 108);
INSERT INTO receiver_groups VALUES (109, 109);
INSERT INTO receiver_groups VALUES (110, 110);
INSERT INTO receiver_groups VALUES (111, 111);
INSERT INTO receiver_groups VALUES (112, 112);
INSERT INTO receiver_groups VALUES (113, 113);
INSERT INTO receiver_groups VALUES (114, 114);
INSERT INTO receiver_groups VALUES (115, 115);
INSERT INTO receiver_groups VALUES (116, 116);
INSERT INTO receiver_groups VALUES (117, 117);
INSERT INTO receiver_groups VALUES (118, 118);
INSERT INTO receiver_groups VALUES (119, 119);
INSERT INTO receiver_groups VALUES (120, 120);
INSERT INTO receiver_groups VALUES (121, 121);
INSERT INTO receiver_groups VALUES (122, 122);
INSERT INTO receiver_groups VALUES (123, 123);
INSERT INTO receiver_groups VALUES (124, 124);
INSERT INTO receiver_groups VALUES (125, 125);
INSERT INTO receiver_groups VALUES (126, 126);
INSERT INTO receiver_groups VALUES (127, 127);
INSERT INTO receiver_groups VALUES (128, 128);
INSERT INTO receiver_groups VALUES (129, 129);
INSERT INTO receiver_groups VALUES (130, 130);
INSERT INTO receiver_groups VALUES (131, 131);
INSERT INTO receiver_groups VALUES (132, 132);
INSERT INTO receiver_groups VALUES (133, 133);
INSERT INTO receiver_groups VALUES (134, 134);
INSERT INTO receiver_groups VALUES (135, 135);
INSERT INTO receiver_groups VALUES (136, 136);
INSERT INTO receiver_groups VALUES (137, 137);
INSERT INTO receiver_groups VALUES (138, 138);
INSERT INTO receiver_groups VALUES (139, 139);
INSERT INTO receiver_groups VALUES (140, 140);
INSERT INTO receiver_groups VALUES (141, 141);
INSERT INTO receiver_groups VALUES (142, 142);
INSERT INTO receiver_groups VALUES (143, 143);
INSERT INTO receiver_groups VALUES (144, 144);
INSERT INTO receiver_groups VALUES (145, 145);
INSERT INTO receiver_groups VALUES (146, 146);
INSERT INTO receiver_groups VALUES (147, 147);
INSERT INTO receiver_groups VALUES (148, 148);
INSERT INTO receiver_groups VALUES (149, 149);
INSERT INTO receiver_groups VALUES (150, 150);
INSERT INTO receiver_groups VALUES (151, 151);
INSERT INTO receiver_groups VALUES (152, 152);
INSERT INTO receiver_groups VALUES (153, 153);
INSERT INTO receiver_groups VALUES (154, 154);
INSERT INTO receiver_groups VALUES (155, 155);
INSERT INTO receiver_groups VALUES (156, 156);
INSERT INTO receiver_groups VALUES (157, 157);
INSERT INTO receiver_groups VALUES (158, 158);
INSERT INTO receiver_groups VALUES (159, 159);
INSERT INTO receiver_groups VALUES (160, 160);
INSERT INTO receiver_groups VALUES (161, 161);
INSERT INTO receiver_groups VALUES (162, 162);
INSERT INTO receiver_groups VALUES (163, 163);
INSERT INTO receiver_groups VALUES (164, 164);
INSERT INTO receiver_groups VALUES (165, 165);
INSERT INTO receiver_groups VALUES (166, 166);
INSERT INTO receiver_groups VALUES (167, 167);
INSERT INTO receiver_groups VALUES (168, 168);
INSERT INTO receiver_groups VALUES (169, 169);
INSERT INTO receiver_groups VALUES (170, 170);
INSERT INTO receiver_groups VALUES (171, 171);
INSERT INTO receiver_groups VALUES (172, 172);
INSERT INTO receiver_groups VALUES (173, 173);
INSERT INTO receiver_groups VALUES (174, 174);
INSERT INTO receiver_groups VALUES (175, 175);
INSERT INTO receiver_groups VALUES (176, 176);
INSERT INTO receiver_groups VALUES (177, 177);
INSERT INTO receiver_groups VALUES (178, 178);
INSERT INTO receiver_groups VALUES (179, 179);
INSERT INTO receiver_groups VALUES (180, 180);
INSERT INTO receiver_groups VALUES (181, 181);
INSERT INTO receiver_groups VALUES (182, 182);
INSERT INTO receiver_groups VALUES (183, 183);
INSERT INTO receiver_groups VALUES (184, 184);
INSERT INTO receiver_groups VALUES (185, 185);
INSERT INTO receiver_groups VALUES (186, 186);
INSERT INTO receiver_groups VALUES (187, 187);
INSERT INTO receiver_groups VALUES (188, 188);
INSERT INTO receiver_groups VALUES (189, 189);
INSERT INTO receiver_groups VALUES (190, 190);
INSERT INTO receiver_groups VALUES (191, 191);
INSERT INTO receiver_groups VALUES (192, 192);
INSERT INTO receiver_groups VALUES (193, 193);
INSERT INTO receiver_groups VALUES (194, 194);
INSERT INTO receiver_groups VALUES (195, 195);
INSERT INTO receiver_groups VALUES (196, 196);
INSERT INTO receiver_groups VALUES (197, 197);
INSERT INTO receiver_groups VALUES (198, 198);
INSERT INTO receiver_groups VALUES (199, 199);
INSERT INTO receiver_groups VALUES (200, 200);
INSERT INTO receiver_groups VALUES (201, 201);
INSERT INTO receiver_groups VALUES (202, 202);
INSERT INTO receiver_groups VALUES (203, 203);
INSERT INTO receiver_groups VALUES (204, 204);
INSERT INTO receiver_groups VALUES (205, 205);
INSERT INTO receiver_groups VALUES (206, 206);
INSERT INTO receiver_groups VALUES (207, 207);
INSERT INTO receiver_groups VALUES (208, 208);
INSERT INTO receiver_groups VALUES (209, 209);
INSERT INTO receiver_groups VALUES (210, 210);
INSERT INTO receiver_groups VALUES (211, 211);
INSERT INTO receiver_groups VALUES (212, 212);
INSERT INTO receiver_groups VALUES (213, 213);
INSERT INTO receiver_groups VALUES (214, 214);
INSERT INTO receiver_groups VALUES (215, 215);
INSERT INTO receiver_groups VALUES (216, 216);
INSERT INTO receiver_groups VALUES (217, 217);
INSERT INTO receiver_groups VALUES (218, 218);
INSERT INTO receiver_groups VALUES (219, 219);
INSERT INTO receiver_groups VALUES (220, 220);
INSERT INTO receiver_groups VALUES (221, 221);
INSERT INTO receiver_groups VALUES (222, 222);
INSERT INTO receiver_groups VALUES (223, 223);
INSERT INTO receiver_groups VALUES (224, 224);
INSERT INTO receiver_groups VALUES (225, 225);
INSERT INTO receiver_groups VALUES (226, 226);
INSERT INTO receiver_groups VALUES (227, 227);
INSERT INTO receiver_groups VALUES (228, 228);
INSERT INTO receiver_groups VALUES (229, 229);
INSERT INTO receiver_groups VALUES (230, 230);
INSERT INTO receiver_groups VALUES (231, 231);
INSERT INTO receiver_groups VALUES (232, 232);
INSERT INTO receiver_groups VALUES (233, 233);
INSERT INTO receiver_groups VALUES (234, 234);
INSERT INTO receiver_groups VALUES (235, 235);
INSERT INTO receiver_groups VALUES (236, 236);
INSERT INTO receiver_groups VALUES (237, 237);
INSERT INTO receiver_groups VALUES (238, 238);
INSERT INTO receiver_groups VALUES (239, 239);
INSERT INTO receiver_groups VALUES (240, 240);
INSERT INTO receiver_groups VALUES (241, 241);
INSERT INTO receiver_groups VALUES (242, 242);
INSERT INTO receiver_groups VALUES (243, 243);
INSERT INTO receiver_groups VALUES (244, 244);
INSERT INTO receiver_groups VALUES (245, 245);
INSERT INTO receiver_groups VALUES (246, 246);
INSERT INTO receiver_groups VALUES (247, 247);
INSERT INTO receiver_groups VALUES (248, 248);
INSERT INTO receiver_groups VALUES (249, 249);
INSERT INTO receiver_groups VALUES (250, 250);
INSERT INTO receiver_groups VALUES (251, 251);
INSERT INTO receiver_groups VALUES (252, 252);
INSERT INTO receiver_groups VALUES (253, 253);
INSERT INTO receiver_groups VALUES (254, 254);


--
-- Data for Name: receiver_groups_receivers; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO receiver_groups_receivers VALUES (1, 1, 11);
INSERT INTO receiver_groups_receivers VALUES (2, 2, 11);
INSERT INTO receiver_groups_receivers VALUES (3, 3, 11);
INSERT INTO receiver_groups_receivers VALUES (4, 4, 11);
INSERT INTO receiver_groups_receivers VALUES (5, 5, 11);
INSERT INTO receiver_groups_receivers VALUES (6, 6, 11);
INSERT INTO receiver_groups_receivers VALUES (7, 7, 11);
INSERT INTO receiver_groups_receivers VALUES (8, 8, 11);
INSERT INTO receiver_groups_receivers VALUES (9, 9, 11);
INSERT INTO receiver_groups_receivers VALUES (10, 10, 11);
INSERT INTO receiver_groups_receivers VALUES (11, 11, 11);
INSERT INTO receiver_groups_receivers VALUES (12, 12, 11);
INSERT INTO receiver_groups_receivers VALUES (13, 13, 11);
INSERT INTO receiver_groups_receivers VALUES (14, 14, 11);
INSERT INTO receiver_groups_receivers VALUES (15, 15, 11);
INSERT INTO receiver_groups_receivers VALUES (16, 16, 11);
INSERT INTO receiver_groups_receivers VALUES (17, 17, 13);
INSERT INTO receiver_groups_receivers VALUES (18, 18, 10);
INSERT INTO receiver_groups_receivers VALUES (19, 19, 11);
INSERT INTO receiver_groups_receivers VALUES (20, 20, 8);
INSERT INTO receiver_groups_receivers VALUES (21, 21, 11);
INSERT INTO receiver_groups_receivers VALUES (22, 22, 12);
INSERT INTO receiver_groups_receivers VALUES (23, 23, 12);
INSERT INTO receiver_groups_receivers VALUES (24, 24, 12);
INSERT INTO receiver_groups_receivers VALUES (25, 25, 12);
INSERT INTO receiver_groups_receivers VALUES (26, 26, 6);
INSERT INTO receiver_groups_receivers VALUES (27, 27, 7);
INSERT INTO receiver_groups_receivers VALUES (28, 28, 12);
INSERT INTO receiver_groups_receivers VALUES (29, 28, 14);
INSERT INTO receiver_groups_receivers VALUES (30, 29, 5);
INSERT INTO receiver_groups_receivers VALUES (31, 30, 15);
INSERT INTO receiver_groups_receivers VALUES (32, 31, 13);
INSERT INTO receiver_groups_receivers VALUES (33, 31, 15);
INSERT INTO receiver_groups_receivers VALUES (34, 31, 14);
INSERT INTO receiver_groups_receivers VALUES (35, 32, 13);
INSERT INTO receiver_groups_receivers VALUES (36, 32, 15);
INSERT INTO receiver_groups_receivers VALUES (37, 32, 14);
INSERT INTO receiver_groups_receivers VALUES (38, 33, 5);
INSERT INTO receiver_groups_receivers VALUES (39, 34, 14);
INSERT INTO receiver_groups_receivers VALUES (40, 35, 14);
INSERT INTO receiver_groups_receivers VALUES (41, 36, 6);
INSERT INTO receiver_groups_receivers VALUES (42, 37, 8);
INSERT INTO receiver_groups_receivers VALUES (43, 38, 13);
INSERT INTO receiver_groups_receivers VALUES (44, 39, 4);
INSERT INTO receiver_groups_receivers VALUES (45, 40, 9);
INSERT INTO receiver_groups_receivers VALUES (46, 41, 10);
INSERT INTO receiver_groups_receivers VALUES (47, 41, 12);
INSERT INTO receiver_groups_receivers VALUES (48, 41, 13);
INSERT INTO receiver_groups_receivers VALUES (49, 42, 5);
INSERT INTO receiver_groups_receivers VALUES (50, 43, 4);
INSERT INTO receiver_groups_receivers VALUES (51, 44, 2);
INSERT INTO receiver_groups_receivers VALUES (52, 45, 2);
INSERT INTO receiver_groups_receivers VALUES (53, 46, 2);
INSERT INTO receiver_groups_receivers VALUES (54, 47, 2);
INSERT INTO receiver_groups_receivers VALUES (55, 48, 9);
INSERT INTO receiver_groups_receivers VALUES (56, 49, 9);
INSERT INTO receiver_groups_receivers VALUES (57, 50, 9);
INSERT INTO receiver_groups_receivers VALUES (58, 51, 9);
INSERT INTO receiver_groups_receivers VALUES (59, 52, 12);
INSERT INTO receiver_groups_receivers VALUES (60, 53, 6);
INSERT INTO receiver_groups_receivers VALUES (61, 54, 8);
INSERT INTO receiver_groups_receivers VALUES (62, 55, 11);
INSERT INTO receiver_groups_receivers VALUES (63, 56, 9);
INSERT INTO receiver_groups_receivers VALUES (64, 57, 14);
INSERT INTO receiver_groups_receivers VALUES (65, 58, 14);
INSERT INTO receiver_groups_receivers VALUES (66, 59, 9);
INSERT INTO receiver_groups_receivers VALUES (67, 60, 9);
INSERT INTO receiver_groups_receivers VALUES (68, 61, 6);
INSERT INTO receiver_groups_receivers VALUES (69, 62, 16);
INSERT INTO receiver_groups_receivers VALUES (70, 63, 13);
INSERT INTO receiver_groups_receivers VALUES (71, 64, 13);
INSERT INTO receiver_groups_receivers VALUES (72, 65, 13);
INSERT INTO receiver_groups_receivers VALUES (73, 66, 13);
INSERT INTO receiver_groups_receivers VALUES (74, 67, 9);
INSERT INTO receiver_groups_receivers VALUES (75, 68, 9);
INSERT INTO receiver_groups_receivers VALUES (76, 69, 15);
INSERT INTO receiver_groups_receivers VALUES (77, 70, 4);
INSERT INTO receiver_groups_receivers VALUES (78, 71, 4);
INSERT INTO receiver_groups_receivers VALUES (79, 72, 14);
INSERT INTO receiver_groups_receivers VALUES (80, 73, 14);
INSERT INTO receiver_groups_receivers VALUES (81, 74, 14);
INSERT INTO receiver_groups_receivers VALUES (82, 75, 14);
INSERT INTO receiver_groups_receivers VALUES (83, 76, 9);
INSERT INTO receiver_groups_receivers VALUES (84, 77, 9);
INSERT INTO receiver_groups_receivers VALUES (85, 78, 16);
INSERT INTO receiver_groups_receivers VALUES (86, 79, 11);
INSERT INTO receiver_groups_receivers VALUES (87, 80, 9);
INSERT INTO receiver_groups_receivers VALUES (88, 81, 3);
INSERT INTO receiver_groups_receivers VALUES (89, 82, 3);
INSERT INTO receiver_groups_receivers VALUES (90, 83, 3);
INSERT INTO receiver_groups_receivers VALUES (91, 84, 8);
INSERT INTO receiver_groups_receivers VALUES (92, 85, 8);
INSERT INTO receiver_groups_receivers VALUES (93, 86, 15);
INSERT INTO receiver_groups_receivers VALUES (94, 87, 15);
INSERT INTO receiver_groups_receivers VALUES (95, 88, 15);
INSERT INTO receiver_groups_receivers VALUES (96, 89, 15);
INSERT INTO receiver_groups_receivers VALUES (97, 90, 12);
INSERT INTO receiver_groups_receivers VALUES (98, 91, 4);
INSERT INTO receiver_groups_receivers VALUES (99, 92, 4);
INSERT INTO receiver_groups_receivers VALUES (100, 93, 4);
INSERT INTO receiver_groups_receivers VALUES (101, 94, 4);
INSERT INTO receiver_groups_receivers VALUES (102, 95, 4);
INSERT INTO receiver_groups_receivers VALUES (103, 96, 4);
INSERT INTO receiver_groups_receivers VALUES (104, 97, 4);
INSERT INTO receiver_groups_receivers VALUES (105, 98, 4);
INSERT INTO receiver_groups_receivers VALUES (106, 99, 4);
INSERT INTO receiver_groups_receivers VALUES (107, 100, 4);
INSERT INTO receiver_groups_receivers VALUES (108, 101, 7);
INSERT INTO receiver_groups_receivers VALUES (109, 102, 7);
INSERT INTO receiver_groups_receivers VALUES (110, 103, 7);
INSERT INTO receiver_groups_receivers VALUES (111, 104, 7);
INSERT INTO receiver_groups_receivers VALUES (112, 105, 7);
INSERT INTO receiver_groups_receivers VALUES (113, 106, 7);
INSERT INTO receiver_groups_receivers VALUES (114, 107, 7);
INSERT INTO receiver_groups_receivers VALUES (115, 108, 7);
INSERT INTO receiver_groups_receivers VALUES (116, 109, 9);
INSERT INTO receiver_groups_receivers VALUES (117, 110, 14);
INSERT INTO receiver_groups_receivers VALUES (118, 111, 14);
INSERT INTO receiver_groups_receivers VALUES (119, 112, 8);
INSERT INTO receiver_groups_receivers VALUES (120, 113, 8);
INSERT INTO receiver_groups_receivers VALUES (121, 114, 8);
INSERT INTO receiver_groups_receivers VALUES (122, 115, 8);
INSERT INTO receiver_groups_receivers VALUES (123, 116, 5);
INSERT INTO receiver_groups_receivers VALUES (124, 117, 6);
INSERT INTO receiver_groups_receivers VALUES (125, 118, 7);
INSERT INTO receiver_groups_receivers VALUES (126, 119, 7);
INSERT INTO receiver_groups_receivers VALUES (127, 120, 3);
INSERT INTO receiver_groups_receivers VALUES (128, 121, 6);
INSERT INTO receiver_groups_receivers VALUES (129, 122, 9);
INSERT INTO receiver_groups_receivers VALUES (130, 123, 9);
INSERT INTO receiver_groups_receivers VALUES (131, 124, 3);
INSERT INTO receiver_groups_receivers VALUES (132, 125, 3);
INSERT INTO receiver_groups_receivers VALUES (133, 126, 3);
INSERT INTO receiver_groups_receivers VALUES (134, 127, 6);
INSERT INTO receiver_groups_receivers VALUES (135, 128, 8);
INSERT INTO receiver_groups_receivers VALUES (136, 129, 8);
INSERT INTO receiver_groups_receivers VALUES (137, 129, 10);
INSERT INTO receiver_groups_receivers VALUES (138, 129, 11);
INSERT INTO receiver_groups_receivers VALUES (139, 130, 3);
INSERT INTO receiver_groups_receivers VALUES (140, 130, 6);
INSERT INTO receiver_groups_receivers VALUES (141, 131, 8);
INSERT INTO receiver_groups_receivers VALUES (142, 131, 10);
INSERT INTO receiver_groups_receivers VALUES (143, 131, 11);
INSERT INTO receiver_groups_receivers VALUES (144, 132, 8);
INSERT INTO receiver_groups_receivers VALUES (145, 132, 12);
INSERT INTO receiver_groups_receivers VALUES (146, 132, 11);
INSERT INTO receiver_groups_receivers VALUES (147, 132, 9);
INSERT INTO receiver_groups_receivers VALUES (148, 132, 10);
INSERT INTO receiver_groups_receivers VALUES (149, 133, 8);
INSERT INTO receiver_groups_receivers VALUES (150, 133, 12);
INSERT INTO receiver_groups_receivers VALUES (151, 133, 11);
INSERT INTO receiver_groups_receivers VALUES (152, 133, 9);
INSERT INTO receiver_groups_receivers VALUES (153, 133, 10);
INSERT INTO receiver_groups_receivers VALUES (154, 134, 8);
INSERT INTO receiver_groups_receivers VALUES (155, 134, 12);
INSERT INTO receiver_groups_receivers VALUES (156, 134, 11);
INSERT INTO receiver_groups_receivers VALUES (157, 134, 9);
INSERT INTO receiver_groups_receivers VALUES (158, 134, 10);
INSERT INTO receiver_groups_receivers VALUES (159, 135, 8);
INSERT INTO receiver_groups_receivers VALUES (160, 135, 12);
INSERT INTO receiver_groups_receivers VALUES (161, 135, 11);
INSERT INTO receiver_groups_receivers VALUES (162, 135, 9);
INSERT INTO receiver_groups_receivers VALUES (163, 135, 10);
INSERT INTO receiver_groups_receivers VALUES (164, 136, 8);
INSERT INTO receiver_groups_receivers VALUES (165, 136, 12);
INSERT INTO receiver_groups_receivers VALUES (166, 136, 11);
INSERT INTO receiver_groups_receivers VALUES (167, 136, 9);
INSERT INTO receiver_groups_receivers VALUES (168, 136, 10);
INSERT INTO receiver_groups_receivers VALUES (169, 137, 3);
INSERT INTO receiver_groups_receivers VALUES (170, 137, 9);
INSERT INTO receiver_groups_receivers VALUES (171, 138, 11);
INSERT INTO receiver_groups_receivers VALUES (172, 139, 8);
INSERT INTO receiver_groups_receivers VALUES (173, 140, 9);
INSERT INTO receiver_groups_receivers VALUES (174, 141, 8);
INSERT INTO receiver_groups_receivers VALUES (175, 142, 8);
INSERT INTO receiver_groups_receivers VALUES (176, 143, 8);
INSERT INTO receiver_groups_receivers VALUES (177, 144, 11);
INSERT INTO receiver_groups_receivers VALUES (178, 145, 11);
INSERT INTO receiver_groups_receivers VALUES (179, 146, 6);
INSERT INTO receiver_groups_receivers VALUES (180, 147, 3);
INSERT INTO receiver_groups_receivers VALUES (181, 148, 9);
INSERT INTO receiver_groups_receivers VALUES (182, 149, 3);
INSERT INTO receiver_groups_receivers VALUES (183, 150, 3);
INSERT INTO receiver_groups_receivers VALUES (184, 151, 5);
INSERT INTO receiver_groups_receivers VALUES (185, 152, 6);
INSERT INTO receiver_groups_receivers VALUES (186, 153, 7);
INSERT INTO receiver_groups_receivers VALUES (187, 154, 6);
INSERT INTO receiver_groups_receivers VALUES (188, 155, 7);
INSERT INTO receiver_groups_receivers VALUES (189, 156, 7);
INSERT INTO receiver_groups_receivers VALUES (190, 157, 9);
INSERT INTO receiver_groups_receivers VALUES (191, 158, 10);
INSERT INTO receiver_groups_receivers VALUES (192, 159, 8);
INSERT INTO receiver_groups_receivers VALUES (193, 160, 9);
INSERT INTO receiver_groups_receivers VALUES (194, 161, 3);
INSERT INTO receiver_groups_receivers VALUES (195, 162, 11);
INSERT INTO receiver_groups_receivers VALUES (196, 163, 11);
INSERT INTO receiver_groups_receivers VALUES (197, 164, 11);
INSERT INTO receiver_groups_receivers VALUES (198, 165, 8);
INSERT INTO receiver_groups_receivers VALUES (199, 166, 8);
INSERT INTO receiver_groups_receivers VALUES (200, 167, 8);
INSERT INTO receiver_groups_receivers VALUES (201, 168, 8);
INSERT INTO receiver_groups_receivers VALUES (202, 169, 10);
INSERT INTO receiver_groups_receivers VALUES (203, 170, 10);
INSERT INTO receiver_groups_receivers VALUES (204, 171, 9);
INSERT INTO receiver_groups_receivers VALUES (205, 172, 12);
INSERT INTO receiver_groups_receivers VALUES (206, 173, 12);
INSERT INTO receiver_groups_receivers VALUES (207, 174, 8);
INSERT INTO receiver_groups_receivers VALUES (208, 175, 8);
INSERT INTO receiver_groups_receivers VALUES (209, 176, 10);
INSERT INTO receiver_groups_receivers VALUES (210, 177, 10);
INSERT INTO receiver_groups_receivers VALUES (211, 178, 9);
INSERT INTO receiver_groups_receivers VALUES (212, 179, 9);
INSERT INTO receiver_groups_receivers VALUES (213, 180, 9);
INSERT INTO receiver_groups_receivers VALUES (214, 181, 11);
INSERT INTO receiver_groups_receivers VALUES (215, 182, 12);
INSERT INTO receiver_groups_receivers VALUES (216, 183, 9);
INSERT INTO receiver_groups_receivers VALUES (217, 184, 8);
INSERT INTO receiver_groups_receivers VALUES (218, 185, 10);
INSERT INTO receiver_groups_receivers VALUES (219, 186, 10);
INSERT INTO receiver_groups_receivers VALUES (220, 187, 11);
INSERT INTO receiver_groups_receivers VALUES (221, 188, 9);
INSERT INTO receiver_groups_receivers VALUES (222, 189, 6);
INSERT INTO receiver_groups_receivers VALUES (223, 190, 6);
INSERT INTO receiver_groups_receivers VALUES (224, 191, 6);
INSERT INTO receiver_groups_receivers VALUES (225, 192, 8);
INSERT INTO receiver_groups_receivers VALUES (226, 193, 3);
INSERT INTO receiver_groups_receivers VALUES (227, 194, 6);
INSERT INTO receiver_groups_receivers VALUES (228, 195, 3);
INSERT INTO receiver_groups_receivers VALUES (229, 196, 6);
INSERT INTO receiver_groups_receivers VALUES (230, 197, 3);
INSERT INTO receiver_groups_receivers VALUES (231, 198, 6);
INSERT INTO receiver_groups_receivers VALUES (232, 199, 6);
INSERT INTO receiver_groups_receivers VALUES (233, 200, 8);
INSERT INTO receiver_groups_receivers VALUES (234, 201, 6);
INSERT INTO receiver_groups_receivers VALUES (235, 202, 6);
INSERT INTO receiver_groups_receivers VALUES (236, 203, 8);
INSERT INTO receiver_groups_receivers VALUES (237, 204, 6);
INSERT INTO receiver_groups_receivers VALUES (238, 205, 6);
INSERT INTO receiver_groups_receivers VALUES (239, 206, 6);
INSERT INTO receiver_groups_receivers VALUES (240, 207, 6);
INSERT INTO receiver_groups_receivers VALUES (241, 208, 8);
INSERT INTO receiver_groups_receivers VALUES (242, 209, 8);
INSERT INTO receiver_groups_receivers VALUES (243, 210, 8);
INSERT INTO receiver_groups_receivers VALUES (244, 211, 4);
INSERT INTO receiver_groups_receivers VALUES (245, 212, 12);
INSERT INTO receiver_groups_receivers VALUES (246, 212, 11);
INSERT INTO receiver_groups_receivers VALUES (247, 213, 12);
INSERT INTO receiver_groups_receivers VALUES (248, 213, 11);
INSERT INTO receiver_groups_receivers VALUES (249, 214, 7);
INSERT INTO receiver_groups_receivers VALUES (250, 215, 11);
INSERT INTO receiver_groups_receivers VALUES (251, 215, 12);
INSERT INTO receiver_groups_receivers VALUES (252, 216, 11);
INSERT INTO receiver_groups_receivers VALUES (253, 216, 12);
INSERT INTO receiver_groups_receivers VALUES (254, 217, 12);
INSERT INTO receiver_groups_receivers VALUES (255, 218, 12);
INSERT INTO receiver_groups_receivers VALUES (256, 219, 8);
INSERT INTO receiver_groups_receivers VALUES (257, 220, 6);
INSERT INTO receiver_groups_receivers VALUES (258, 221, 8);
INSERT INTO receiver_groups_receivers VALUES (259, 222, 8);
INSERT INTO receiver_groups_receivers VALUES (260, 223, 9);
INSERT INTO receiver_groups_receivers VALUES (261, 224, 9);
INSERT INTO receiver_groups_receivers VALUES (262, 225, 9);
INSERT INTO receiver_groups_receivers VALUES (263, 226, 9);
INSERT INTO receiver_groups_receivers VALUES (264, 227, 9);
INSERT INTO receiver_groups_receivers VALUES (265, 228, 9);
INSERT INTO receiver_groups_receivers VALUES (266, 229, 9);
INSERT INTO receiver_groups_receivers VALUES (267, 230, 9);
INSERT INTO receiver_groups_receivers VALUES (268, 231, 9);
INSERT INTO receiver_groups_receivers VALUES (269, 232, 9);
INSERT INTO receiver_groups_receivers VALUES (270, 233, 9);
INSERT INTO receiver_groups_receivers VALUES (271, 234, 9);
INSERT INTO receiver_groups_receivers VALUES (272, 235, 9);
INSERT INTO receiver_groups_receivers VALUES (273, 236, 9);
INSERT INTO receiver_groups_receivers VALUES (274, 237, 9);
INSERT INTO receiver_groups_receivers VALUES (275, 238, 3);
INSERT INTO receiver_groups_receivers VALUES (276, 239, 9);
INSERT INTO receiver_groups_receivers VALUES (277, 240, 9);
INSERT INTO receiver_groups_receivers VALUES (278, 241, 9);
INSERT INTO receiver_groups_receivers VALUES (279, 242, 9);
INSERT INTO receiver_groups_receivers VALUES (280, 243, 9);
INSERT INTO receiver_groups_receivers VALUES (281, 244, 9);
INSERT INTO receiver_groups_receivers VALUES (282, 245, 9);
INSERT INTO receiver_groups_receivers VALUES (283, 246, 12);
INSERT INTO receiver_groups_receivers VALUES (284, 247, 12);
INSERT INTO receiver_groups_receivers VALUES (285, 248, 11);
INSERT INTO receiver_groups_receivers VALUES (286, 249, 11);
INSERT INTO receiver_groups_receivers VALUES (287, 250, 11);
INSERT INTO receiver_groups_receivers VALUES (288, 251, 11);
INSERT INTO receiver_groups_receivers VALUES (289, 252, 11);
INSERT INTO receiver_groups_receivers VALUES (290, 253, 11);
INSERT INTO receiver_groups_receivers VALUES (291, 254, 10);
INSERT INTO receiver_groups_receivers VALUES (292, 254, 11);


--
-- Data for Name: receiver_schedule; Type: TABLE DATA; Schema: public; Owner: dss
--



--
-- Data for Name: receivers; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO receivers VALUES (1, 'NoiseSource', 'NS', 0, 0);
INSERT INTO receivers VALUES (2, 'Rcvr_RRI', 'RRI', 0.10000000000000001, 1.6000000000000001);
INSERT INTO receivers VALUES (3, 'Rcvr_342', '342', 0.28999999999999998, 0.39500000000000002);
INSERT INTO receivers VALUES (4, 'Rcvr_450', '450', 0.38500000000000001, 0.52000000000000002);
INSERT INTO receivers VALUES (5, 'Rcvr_600', '600', 0.51000000000000001, 0.68999999999999995);
INSERT INTO receivers VALUES (6, 'Rcvr_800', '800', 0.68000000000000005, 0.92000000000000004);
INSERT INTO receivers VALUES (7, 'Rcvr_1070', '1070', 0.91000000000000003, 1.23);
INSERT INTO receivers VALUES (8, 'Rcvr1_2', 'L', 1.1499999999999999, 1.73);
INSERT INTO receivers VALUES (9, 'Rcvr2_3', 'S', 1.73, 2.6000000000000001);
INSERT INTO receivers VALUES (10, 'Rcvr4_6', 'C', 3.9500000000000002, 6.0999999999999996);
INSERT INTO receivers VALUES (11, 'Rcvr8_10', 'X', 8, 10);
INSERT INTO receivers VALUES (12, 'Rcvr12_18', 'Ku', 12, 15.4);
INSERT INTO receivers VALUES (13, 'Rcvr18_26', 'K', 18, 26.5);
INSERT INTO receivers VALUES (14, 'Rcvr26_40', 'Ka', 26, 39.5);
INSERT INTO receivers VALUES (15, 'Rcvr40_52', 'Q', 38.200000000000003, 49.799999999999997);
INSERT INTO receivers VALUES (16, 'Rcvr_PAR', 'MBA', 80, 100);
INSERT INTO receivers VALUES (17, 'Zpectrometer', 'Z', 0, 0);
INSERT INTO receivers VALUES (18, 'Holography', 'Hol', 11.699999999999999, 12.199999999999999);


--
-- Data for Name: semesters; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO semesters VALUES (1, '09A');
INSERT INTO semesters VALUES (2, '09B');
INSERT INTO semesters VALUES (3, '09C');
INSERT INTO semesters VALUES (4, '08A');
INSERT INTO semesters VALUES (5, '08B');
INSERT INTO semesters VALUES (6, '08C');
INSERT INTO semesters VALUES (7, '07A');
INSERT INTO semesters VALUES (8, '07B');
INSERT INTO semesters VALUES (9, '07C');
INSERT INTO semesters VALUES (10, '06A');
INSERT INTO semesters VALUES (11, '06B');
INSERT INTO semesters VALUES (12, '06C');
INSERT INTO semesters VALUES (13, '05A');
INSERT INTO semesters VALUES (14, '05B');
INSERT INTO semesters VALUES (15, '05C');
INSERT INTO semesters VALUES (16, '04A');


--
-- Data for Name: sesshuns_email; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO sesshuns_email VALUES (1, 1, 'fghigo@nrao.edu');
INSERT INTO sesshuns_email VALUES (2, 2, 'jbraatz@nrao.edu');
INSERT INTO sesshuns_email VALUES (3, 3, 'jharnett@nrao.edu');
INSERT INTO sesshuns_email VALUES (4, 4, 'cbignell@nrao.edu');
INSERT INTO sesshuns_email VALUES (5, 4, 'cbignell@gb.nrao.edu');
INSERT INTO sesshuns_email VALUES (6, 5, 'dbalser@nrao.edu');
INSERT INTO sesshuns_email VALUES (7, 6, 'tminter@nrao.edu');
INSERT INTO sesshuns_email VALUES (8, 7, 'rmaddale@nrao.edu');
INSERT INTO sesshuns_email VALUES (9, 8, 'sransom@nrao.edu');
INSERT INTO sesshuns_email VALUES (10, 9, 'koneil@gb.nrao.edu');
INSERT INTO sesshuns_email VALUES (11, 9, 'koneil@nrao.edu');
INSERT INTO sesshuns_email VALUES (12, 10, 'paul@paulruffle.com');
INSERT INTO sesshuns_email VALUES (13, 11, 'bmason@nrao.edu');
INSERT INTO sesshuns_email VALUES (14, 11, 'bmason@gb.nrao.edu');
INSERT INTO sesshuns_email VALUES (15, 12, 'jlockman@nrao.edu');
INSERT INTO sesshuns_email VALUES (16, 13, 'glangsto@nrao.edu');
INSERT INTO sesshuns_email VALUES (17, 14, 'rrosen@nrao.edu');
INSERT INTO sesshuns_email VALUES (18, 15, 'jmangum@nrao.edu');
INSERT INTO sesshuns_email VALUES (19, 16, 'aremijan@nrao.edu');
INSERT INTO sesshuns_email VALUES (20, 17, 'dperera@nrao.edu');
INSERT INTO sesshuns_email VALUES (21, 18, 'dpisano@nrao.edu');
INSERT INTO sesshuns_email VALUES (22, 19, 'gbower@astro.berkeley.edu');
INSERT INTO sesshuns_email VALUES (23, 19, 'gbower@astron.berkeley.edu');
INSERT INTO sesshuns_email VALUES (24, 20, 'bolatto@astro.umd.edu');
INSERT INTO sesshuns_email VALUES (25, 21, 'eford@gmail.com');
INSERT INTO sesshuns_email VALUES (26, 22, 'kalas@astro.berkeley.edu');
INSERT INTO sesshuns_email VALUES (27, 23, 'jcondon@nrao.edu');
INSERT INTO sesshuns_email VALUES (28, 24, 'greenhill@cfa.harvard.edu');
INSERT INTO sesshuns_email VALUES (29, 24, 'lincoln@play');
INSERT INTO sesshuns_email VALUES (30, 24, 'harvard.edu');
INSERT INTO sesshuns_email VALUES (31, 25, 'p220hen@mpifr-bonn.mpg.de');
INSERT INTO sesshuns_email VALUES (32, 26, 'flo@nrao.edu');
INSERT INTO sesshuns_email VALUES (33, 27, 'reid@cfa.harvard.edu');
INSERT INTO sesshuns_email VALUES (34, 27, 'mreid@cfa.harvard.edu');
INSERT INTO sesshuns_email VALUES (35, 28, 'ck2v@virginia.edu');
INSERT INTO sesshuns_email VALUES (36, 29, 'iz6@astro.physics.nyu.edu');
INSERT INTO sesshuns_email VALUES (37, 30, 'atilak@cfa.harvard.edu');
INSERT INTO sesshuns_email VALUES (38, 31, 'haol@isc.astro.cornell.edu');
INSERT INTO sesshuns_email VALUES (39, 32, 'plah@mso.anu.edu.au');
INSERT INTO sesshuns_email VALUES (40, 33, 'brunthaler@mpifr-bonn.mpg.de');
INSERT INTO sesshuns_email VALUES (41, 33, 'brunthal@mpifr-bonn.mpg.de');
INSERT INTO sesshuns_email VALUES (42, 34, 'lsjouwer@nrao.edu');
INSERT INTO sesshuns_email VALUES (43, 34, 'lsjouwer@aoc.nrao.edu');
INSERT INTO sesshuns_email VALUES (44, 34, 'lsjouwerman@aoc.nrao.edu');
INSERT INTO sesshuns_email VALUES (45, 35, 'garrett@astron.nl');
INSERT INTO sesshuns_email VALUES (46, 36, 'l.loinard@astrosmo.unam.mx');
INSERT INTO sesshuns_email VALUES (47, 37, 'jmiller@nrao.edu');
INSERT INTO sesshuns_email VALUES (48, 38, 'mrupen@nrao.edu');
INSERT INTO sesshuns_email VALUES (49, 38, 'mrupen@aoc.nrao.edu');
INSERT INTO sesshuns_email VALUES (50, 39, 'amiodusz@aoc.nrao.edu');
INSERT INTO sesshuns_email VALUES (51, 39, 'amiodusz@nrao.edu');
INSERT INTO sesshuns_email VALUES (52, 40, 'vdhawan@aoc.nrao.edu');
INSERT INTO sesshuns_email VALUES (53, 40, 'vdhawan@nrao.edu');
INSERT INTO sesshuns_email VALUES (54, 41, 'elena@physics.ucsb.edu');
INSERT INTO sesshuns_email VALUES (55, 42, 'P.Jonker@sron.nl');
INSERT INTO sesshuns_email VALUES (56, 43, 'wbrisken@nrao.edu');
INSERT INTO sesshuns_email VALUES (57, 43, 'wbrisken@aoc.nrao.edu');
INSERT INTO sesshuns_email VALUES (58, 44, 'emomjian@nrao.edu');
INSERT INTO sesshuns_email VALUES (59, 45, 'whwang@nrao.edu');
INSERT INTO sesshuns_email VALUES (60, 45, 'whwang@aoc.nrao.edu');
INSERT INTO sesshuns_email VALUES (61, 46, 'ccarilli@nrao.edu');
INSERT INTO sesshuns_email VALUES (62, 46, 'ccarilli@aoc.nrao.edu');
INSERT INTO sesshuns_email VALUES (63, 47, 'r.torres@astrosmo.unam.mx');
INSERT INTO sesshuns_email VALUES (64, 48, 'william-peterson@uiowa.edu');
INSERT INTO sesshuns_email VALUES (65, 49, 'robert-mutel@uiowa.edu');
INSERT INTO sesshuns_email VALUES (66, 50, 'mgoss@nrao.edu');
INSERT INTO sesshuns_email VALUES (67, 50, 'mgoss@aoc.nrao.edu');
INSERT INTO sesshuns_email VALUES (68, 51, 'sjc@phys.unsw.edu.au');
INSERT INTO sesshuns_email VALUES (69, 51, 'sjc@bat.phys.unsw.edu.au');
INSERT INTO sesshuns_email VALUES (70, 52, 'Matthew.Whiting@csiro.au');
INSERT INTO sesshuns_email VALUES (71, 53, 'jkw@phys.unsw.edu.au');
INSERT INTO sesshuns_email VALUES (72, 53, 'jkw@bat.phys.unsw.edu.au');
INSERT INTO sesshuns_email VALUES (73, 54, 'mmurphy@swin.edu.au');
INSERT INTO sesshuns_email VALUES (74, 55, 'ylva@unm.edu');
INSERT INTO sesshuns_email VALUES (75, 56, 'wiklind@stsci.edu');
INSERT INTO sesshuns_email VALUES (76, 57, 'pfrancis@mso.anu.edu.au');
INSERT INTO sesshuns_email VALUES (77, 58, 'awootten@nrao.edu');
INSERT INTO sesshuns_email VALUES (78, 59, 'nkanekar@nrao.edu');
INSERT INTO sesshuns_email VALUES (79, 59, 'nkanekar@aoc.nrao.edu');
INSERT INTO sesshuns_email VALUES (80, 60, 'sarae@uvic.ca');
INSERT INTO sesshuns_email VALUES (81, 61, 'xavier@ucolick.org');
INSERT INTO sesshuns_email VALUES (82, 62, 'briany@uvic.ca');
INSERT INTO sesshuns_email VALUES (83, 63, 'yshirley@as.arizona.edu');
INSERT INTO sesshuns_email VALUES (84, 64, 'jan.m.hollis@nasa.gov');
INSERT INTO sesshuns_email VALUES (85, 64, 'mhollis@milkyway.gsfc.nasa.gov');
INSERT INTO sesshuns_email VALUES (86, 64, 'jan.m.hollis@gsfc.nasa.gov');
INSERT INTO sesshuns_email VALUES (87, 65, 'pjewell@nrao.edu');
INSERT INTO sesshuns_email VALUES (88, 66, 'lovas@nist.gov');
INSERT INTO sesshuns_email VALUES (89, 66, 'francis.lovas@nist.gov');
INSERT INTO sesshuns_email VALUES (90, 67, 'jbregman@umich.edu');
INSERT INTO sesshuns_email VALUES (91, 68, 'jairwin@umich.edu');
INSERT INTO sesshuns_email VALUES (92, 69, 'pdemores@nrao.edu');
INSERT INTO sesshuns_email VALUES (93, 70, 'bryan.jacoby@gmail.com');
INSERT INTO sesshuns_email VALUES (94, 71, 'ferdman@phas.ubc.ca');
INSERT INTO sesshuns_email VALUES (95, 71, 'robertferdman@physics.ubc.ca');
INSERT INTO sesshuns_email VALUES (96, 72, 'dbacker@astro.berkeley.edu');
INSERT INTO sesshuns_email VALUES (97, 73, 'istairs@astro.ubc.ca');
INSERT INTO sesshuns_email VALUES (98, 73, 'stairs@astro.ubc.ca');
INSERT INTO sesshuns_email VALUES (99, 74, 'dnice@brynmawr.edu');
INSERT INTO sesshuns_email VALUES (100, 74, 'dnice@princeton.edu');
INSERT INTO sesshuns_email VALUES (101, 75, 'alommen@fandm.edu');
INSERT INTO sesshuns_email VALUES (102, 76, 'mbailes@astro.swin.edu.au');
INSERT INTO sesshuns_email VALUES (103, 77, 'icognard@cnrs-orleans.fr');
INSERT INTO sesshuns_email VALUES (104, 78, 'tbourke@cfa.harvard.edu');
INSERT INTO sesshuns_email VALUES (105, 79, 'p.caselli@leeds.ac.uk');
INSERT INTO sesshuns_email VALUES (106, 80, 'rfriesen@uvastro.phys.uvic.ca');
INSERT INTO sesshuns_email VALUES (107, 81, 'james.difrancesco@nrc-cnrc.gc.ca');
INSERT INTO sesshuns_email VALUES (108, 81, 'difrancesco@nrc.ca');
INSERT INTO sesshuns_email VALUES (109, 82, 'pmyers@cfa.harvard.edu');
INSERT INTO sesshuns_email VALUES (110, 83, 'jdarling@origins.colorado.edu');
INSERT INTO sesshuns_email VALUES (111, 84, 'sedel@mix.wvu.edu');
INSERT INTO sesshuns_email VALUES (112, 85, 'dludovic@mix.wvu.edu');
INSERT INTO sesshuns_email VALUES (113, 86, 'Duncan.Lorimer@mail.wvu.edu');
INSERT INTO sesshuns_email VALUES (114, 87, 'maura.mclaughlin@mail.wvu.edu');
INSERT INTO sesshuns_email VALUES (115, 88, 'vlad.kondratiev@mail.wvu.edu');
INSERT INTO sesshuns_email VALUES (116, 89, 'jridley2@mix.wvu.edu');
INSERT INTO sesshuns_email VALUES (117, 90, 'earaya@nrao.edu');
INSERT INTO sesshuns_email VALUES (118, 90, 'earaya@nmt.edu');
INSERT INTO sesshuns_email VALUES (119, 91, 'phofner@nrao.edu');
INSERT INTO sesshuns_email VALUES (120, 91, 'hofner@kestrel.nmt.edu');
INSERT INTO sesshuns_email VALUES (121, 91, 'hofner_p@yahoo.com');
INSERT INTO sesshuns_email VALUES (122, 92, 'ihoffman@sps.edu');
INSERT INTO sesshuns_email VALUES (123, 93, 'linz@mpia-hd.mpg.de');
INSERT INTO sesshuns_email VALUES (124, 93, 'linz@tls-tautenburg.de');
INSERT INTO sesshuns_email VALUES (125, 94, 's.kurtz@astrosmo.unam.mx');
INSERT INTO sesshuns_email VALUES (126, 94, 'kurtz@astroscu.unam.mx');
INSERT INTO sesshuns_email VALUES (127, 95, 'vrmarthi@ncra.tifr.res.in');
INSERT INTO sesshuns_email VALUES (128, 96, 'ymaan4@gmail.com');
INSERT INTO sesshuns_email VALUES (129, 97, 'avideshi@gmail.com');
INSERT INTO sesshuns_email VALUES (130, 98, 'campbellb@si.edu');
INSERT INTO sesshuns_email VALUES (131, 98, 'campbellb@nasm.si.edu');
INSERT INTO sesshuns_email VALUES (132, 99, 'campbell@astro.cornell.edu');
INSERT INTO sesshuns_email VALUES (133, 99, 'campbell@naic.edu');
INSERT INTO sesshuns_email VALUES (134, 99, 'campbell@astrosun.tn.cornell.edu');
INSERT INTO sesshuns_email VALUES (135, 100, 'carterl@si.edu');
INSERT INTO sesshuns_email VALUES (136, 100, 'carterl@nasm.si.edu');
INSERT INTO sesshuns_email VALUES (137, 101, 'ghentr@si.edu');
INSERT INTO sesshuns_email VALUES (138, 102, 'mnolan@naic.edu');
INSERT INTO sesshuns_email VALUES (139, 102, 'nolan@naic.edu');
INSERT INTO sesshuns_email VALUES (140, 103, 'naoto@ioa.s.u-tokyo.ac.jp');
INSERT INTO sesshuns_email VALUES (141, 104, 'Tom.Millar@qub.ac.uk');
INSERT INTO sesshuns_email VALUES (142, 105, 'Masao.Saito@nao.ac.jp');
INSERT INTO sesshuns_email VALUES (143, 106, 'ck_yasui@ioa.s.u-tokyo.ac.jp');
INSERT INTO sesshuns_email VALUES (144, 107, 'mkramer@jb.man.ac.uk');
INSERT INTO sesshuns_email VALUES (145, 107, 'Michael.Kramer@manchester.ac.uk');
INSERT INTO sesshuns_email VALUES (146, 108, 'fernando@astro.columbia.edu');
INSERT INTO sesshuns_email VALUES (147, 109, 'agl@jb.man.ac.uk');
INSERT INTO sesshuns_email VALUES (148, 110, 'dick.manchester@csiro.au');
INSERT INTO sesshuns_email VALUES (149, 110, 'rmanches@atnf.csiro.au');
INSERT INTO sesshuns_email VALUES (150, 111, 'possenti@ca.astro.it');
INSERT INTO sesshuns_email VALUES (151, 112, 'damico@ca.astro.it');
INSERT INTO sesshuns_email VALUES (152, 113, 'burgay@ca.astro.it');
INSERT INTO sesshuns_email VALUES (153, 114, 'pfreire@naic.edu');
INSERT INTO sesshuns_email VALUES (154, 115, 'dennison@unca.edu');
INSERT INTO sesshuns_email VALUES (155, 116, 'lhdicken@unca.edu');
INSERT INTO sesshuns_email VALUES (156, 117, 'bbutler@nrao.edu');
INSERT INTO sesshuns_email VALUES (157, 117, 'bbutler@aoc.nrao.edu');
INSERT INTO sesshuns_email VALUES (158, 118, 'ben.bussey@jhuapl.edu');
INSERT INTO sesshuns_email VALUES (159, 119, 'Ian.Smail@durham.ac.uk');
INSERT INTO sesshuns_email VALUES (160, 120, 'genzel@mpe.mpg.de');
INSERT INTO sesshuns_email VALUES (161, 121, 'rji@roe.ac.uk');
INSERT INTO sesshuns_email VALUES (162, 122, 'ljh@astro.umd.edu');
INSERT INTO sesshuns_email VALUES (163, 122, 'ljh@astro.caltech.edu');
INSERT INTO sesshuns_email VALUES (164, 123, 'awb@astro.caltech.edu');
INSERT INTO sesshuns_email VALUES (165, 124, 'linda@mpe.mpg.de');
INSERT INTO sesshuns_email VALUES (166, 125, 'bertoldi@astro.uni-bonn.de');
INSERT INTO sesshuns_email VALUES (167, 126, 'tgreve@submm.caltech.edu');
INSERT INTO sesshuns_email VALUES (168, 127, 'neri@iram.fr');
INSERT INTO sesshuns_email VALUES (169, 128, 'schapman@ast.cam.ac.uk');
INSERT INTO sesshuns_email VALUES (170, 129, 'harris@astro.umd.edu');
INSERT INTO sesshuns_email VALUES (171, 130, 'ajbaker@physics.rutgers.edu');
INSERT INTO sesshuns_email VALUES (172, 131, 'cox@iram.fr');
INSERT INTO sesshuns_email VALUES (173, 132, 'omont@iap.fr');
INSERT INTO sesshuns_email VALUES (174, 133, 'jules@astro.columbia.edu');
INSERT INTO sesshuns_email VALUES (175, 134, 'jreynold@atnf.csiro.au');
INSERT INTO sesshuns_email VALUES (176, 134, 'John.Reynolds@csiro.au');
INSERT INTO sesshuns_email VALUES (177, 135, 'malloryr@gmail.com');
INSERT INTO sesshuns_email VALUES (178, 136, 'zaven@milkyway.gsfc.nasa.gov');
INSERT INTO sesshuns_email VALUES (179, 137, 'rwr@astro.stanford.edu');
INSERT INTO sesshuns_email VALUES (180, 138, 'Paul.Ray@nrl.navy.mil');
INSERT INTO sesshuns_email VALUES (181, 138, 'paulr@xeus.nrl.navy.mil');
INSERT INTO sesshuns_email VALUES (182, 139, 'dwilner@cfa.harvard.edu');
INSERT INTO sesshuns_email VALUES (183, 140, 'ahales@nrao.edu');
INSERT INTO sesshuns_email VALUES (184, 141, 'rsl4v@virginia.edu');
INSERT INTO sesshuns_email VALUES (185, 142, 'Cecilia.Ceccarelli@obs.ujf-grenoble.fr');
INSERT INTO sesshuns_email VALUES (186, 143, 's.pacheco@astrosmo.unam.mx');
INSERT INTO sesshuns_email VALUES (187, 144, 'caux@cesr.fr');
INSERT INTO sesshuns_email VALUES (188, 145, 'cerni@damir.iem.csic.es');
INSERT INTO sesshuns_email VALUES (189, 145, 'cerni@astro.iem.csic.es');
INSERT INTO sesshuns_email VALUES (190, 146, 'awolfe@ucsd.edu');
INSERT INTO sesshuns_email VALUES (191, 147, 'regina.jorgenson@gmail.com');
INSERT INTO sesshuns_email VALUES (192, 147, 'raj@ast.cam.ac.uk');
INSERT INTO sesshuns_email VALUES (193, 148, 'robishaw@physics.usyd.edu.au');
INSERT INTO sesshuns_email VALUES (194, 149, 'cheiles@astron.berkeley.edu');
INSERT INTO sesshuns_email VALUES (195, 149, 'heiles@astro.berkeley.edu');
INSERT INTO sesshuns_email VALUES (196, 150, 'szonak@astro.umd.edu');
INSERT INTO sesshuns_email VALUES (197, 151, 'csharon@physics.rutgers.edu');
INSERT INTO sesshuns_email VALUES (198, 152, 'pvandenb@nrao.edu');
INSERT INTO sesshuns_email VALUES (199, 153, 'hessels@astron.nl');
INSERT INTO sesshuns_email VALUES (200, 153, 'J.W.T.Hessels@uva.nl');
INSERT INTO sesshuns_email VALUES (201, 153, 'jhessels@science.uva.nl');
INSERT INTO sesshuns_email VALUES (202, 154, 'bcotton@nrao.edu');
INSERT INTO sesshuns_email VALUES (203, 155, 'simon.dicker@gmail.com');
INSERT INTO sesshuns_email VALUES (204, 155, 'sdicker@hep.upenn.edu');
INSERT INTO sesshuns_email VALUES (205, 156, 'PhillipKorngut@gmail.com');
INSERT INTO sesshuns_email VALUES (206, 156, 'pkorngut@physics.upenn.edu');
INSERT INTO sesshuns_email VALUES (207, 157, 'devlin@physics.upenn.edu');
INSERT INTO sesshuns_email VALUES (208, 158, 'andersld@bu.edu');
INSERT INTO sesshuns_email VALUES (209, 159, 'bania@bu.edu');
INSERT INTO sesshuns_email VALUES (210, 160, 'rtr@virginia.edu');
INSERT INTO sesshuns_email VALUES (211, 161, 'Neeraj.Gupta@atnf.csiro.au');
INSERT INTO sesshuns_email VALUES (212, 162, 'anand@iucaa.ernet.in');
INSERT INTO sesshuns_email VALUES (213, 163, 'ppetitje@iap.fr');
INSERT INTO sesshuns_email VALUES (214, 163, 'petitjean@iap.fr');
INSERT INTO sesshuns_email VALUES (215, 164, 'noterdae@iap.fr');
INSERT INTO sesshuns_email VALUES (216, 165, 'bburton@nrao.edu');
INSERT INTO sesshuns_email VALUES (217, 165, 'burton@strw.leidenuniv.nl');
INSERT INTO sesshuns_email VALUES (218, 166, 'edaddi@cea.fr');
INSERT INTO sesshuns_email VALUES (219, 167, 'jwagg@nrao.edu');
INSERT INTO sesshuns_email VALUES (220, 167, 'jwagg@aoc.nrao.edu');
INSERT INTO sesshuns_email VALUES (221, 168, 'maraven@astro.uni-bonn.de');
INSERT INTO sesshuns_email VALUES (222, 169, 'walter@mpia.de');
INSERT INTO sesshuns_email VALUES (223, 169, 'walter@mpia-hd.mpg.de');
INSERT INTO sesshuns_email VALUES (224, 170, 'dr@astro.caltech.edu');
INSERT INTO sesshuns_email VALUES (225, 171, 'dannerb@mpia-hd.mpg.de');
INSERT INTO sesshuns_email VALUES (226, 172, 'med@noao.edu');
INSERT INTO sesshuns_email VALUES (227, 173, 'delbaz@cea.fr');
INSERT INTO sesshuns_email VALUES (228, 174, 'stern@zwolfkinder.jpl.nasa.gov');
INSERT INTO sesshuns_email VALUES (229, 175, 'morrison@cfht.hawaii.edu');
INSERT INTO sesshuns_email VALUES (230, 176, 'lucie.vincent@obspm.fr');
INSERT INTO sesshuns_email VALUES (231, 177, 'nicole.feautrier@obspm.fr');
INSERT INTO sesshuns_email VALUES (232, 178, 'Pierre.Valiron@obs.ujf-grenoble.fr');
INSERT INTO sesshuns_email VALUES (233, 179, 'afaure@obs.ujf-grenoble.fr');
INSERT INTO sesshuns_email VALUES (234, 179, 'Alexandre.Faure@obs.ujf-grenoble.fr');
INSERT INTO sesshuns_email VALUES (235, 180, 'annie.spielfiedel@obspm.fr');
INSERT INTO sesshuns_email VALUES (236, 181, 'senent@damir.iem.csic.es');
INSERT INTO sesshuns_email VALUES (237, 182, 'daniel@damir.iem.csic.es');
INSERT INTO sesshuns_email VALUES (238, 183, 'maca@ph1.uni-koeln.de');
INSERT INTO sesshuns_email VALUES (239, 184, 'eckart@ph1.uni-koeln.de');
INSERT INTO sesshuns_email VALUES (240, 185, 'skoenig@ph1.uni-koeln.de');
INSERT INTO sesshuns_email VALUES (241, 186, 'fischer@ph1.uni-koeln.de');
INSERT INTO sesshuns_email VALUES (242, 187, 'jzuther@mpe.mpg.de');
INSERT INTO sesshuns_email VALUES (243, 188, 'huchtmeier@mpifr-bonn.mpg.de');
INSERT INTO sesshuns_email VALUES (244, 189, 'bertram@ph1.uni-koeln.de');
INSERT INTO sesshuns_email VALUES (245, 190, 'a.m.swinbank@dur.ac.uk');
INSERT INTO sesshuns_email VALUES (246, 191, 'kristen.coppin@durham.ac.uk');
INSERT INTO sesshuns_email VALUES (247, 192, 'Alastair.Edge@durham.ac.uk');
INSERT INTO sesshuns_email VALUES (248, 193, 'rse@astro.caltech.edu');
INSERT INTO sesshuns_email VALUES (249, 194, 'dps@astro.caltech.edu');
INSERT INTO sesshuns_email VALUES (250, 195, 'tajones@astro.caltech.edu');
INSERT INTO sesshuns_email VALUES (251, 196, 'jeanpaul.kneib@gmail.com');
INSERT INTO sesshuns_email VALUES (252, 196, 'kneib@astro.caltech.edu');
INSERT INTO sesshuns_email VALUES (253, 197, 'ebeling@ifa.hawaii.edu');
INSERT INTO sesshuns_email VALUES (254, 198, 'katie.m.chynoweth@vanderbilt.edu');
INSERT INTO sesshuns_email VALUES (255, 199, 'k.holley@vanderbilt.edu');
INSERT INTO sesshuns_email VALUES (256, 200, 'stocke@colorado.edu');
INSERT INTO sesshuns_email VALUES (257, 200, 'stocke@hyades.Colorado.EDU');
INSERT INTO sesshuns_email VALUES (258, 201, 'ting.yan@colorado.edu');
INSERT INTO sesshuns_email VALUES (259, 202, 'sheather@nrao.edu');
INSERT INTO sesshuns_email VALUES (260, 203, 'eric@astro.columbia.edu');
INSERT INTO sesshuns_email VALUES (261, 203, 'evg@astro.columbia.edu');
INSERT INTO sesshuns_email VALUES (262, 204, 'vkaspi@physics.mcgill.ca');
INSERT INTO sesshuns_email VALUES (263, 205, 'cordes@astro.cornell.edu');
INSERT INTO sesshuns_email VALUES (264, 205, 'cordes@spacenet.tn.cornell.edu');
INSERT INTO sesshuns_email VALUES (265, 206, 'david.champion@csiro.au');
INSERT INTO sesshuns_email VALUES (266, 207, 'aarchiba@physics.mcgill.ca');
INSERT INTO sesshuns_email VALUES (267, 208, 'jboyles5@mix.wvu.edu');
INSERT INTO sesshuns_email VALUES (268, 209, 'mcphee@phas.ubc.ca');
INSERT INTO sesshuns_email VALUES (269, 210, 'kasian@physics.ubc.ca');
INSERT INTO sesshuns_email VALUES (270, 211, 'leeuwen@astron.nl');
INSERT INTO sesshuns_email VALUES (271, 211, 'joeri@astro.berkeley.edu');
INSERT INTO sesshuns_email VALUES (272, 212, 'deneva@astro.cornell.edu');
INSERT INTO sesshuns_email VALUES (273, 213, 'fcrawfor@fandm.edu');
INSERT INTO sesshuns_email VALUES (274, 214, 'afaulkne@jb.man.ac.uk');
INSERT INTO sesshuns_email VALUES (275, 214, 'Andrew.Faulkner@manchester.ac.uk');
INSERT INTO sesshuns_email VALUES (276, 215, 'cgilpin@fandm.edu');
INSERT INTO sesshuns_email VALUES (277, 216, 'cgwinn@physics.ucsb.edu');
INSERT INTO sesshuns_email VALUES (278, 217, 'michaeltdh@gmail.com');
INSERT INTO sesshuns_email VALUES (279, 218, 'tania@prao.ru');
INSERT INTO sesshuns_email VALUES (280, 219, 'S.Chatterjee@physics.usyd.edu.au');
INSERT INTO sesshuns_email VALUES (281, 220, 'E.A.RubioHerrera@uva.nl');
INSERT INTO sesshuns_email VALUES (282, 221, 'Ben.Stappers@manchester.ac.uk');
INSERT INTO sesshuns_email VALUES (283, 222, 'dmeier@nrao.edu');
INSERT INTO sesshuns_email VALUES (284, 223, 'zstork@parkland.edu');
INSERT INTO sesshuns_email VALUES (285, 224, 'dww7v@virginia.edu');
INSERT INTO sesshuns_email VALUES (286, 225, 'gcp8y@virginia.edu');
INSERT INTO sesshuns_email VALUES (287, 226, 'lmw7k@virginia.edu');
INSERT INTO sesshuns_email VALUES (288, 227, 'kej7a@virginia.edu');
INSERT INTO sesshuns_email VALUES (289, 228, 'kepley@astro.wisc.edu');
INSERT INTO sesshuns_email VALUES (290, 229, 'larry@astro.umn.edu');
INSERT INTO sesshuns_email VALUES (291, 230, 'farnsworth@astro.umn.edu');
INSERT INTO sesshuns_email VALUES (292, 231, 'brown@physics.umn.edu');
INSERT INTO sesshuns_email VALUES (293, 231, 'brown@astro.umn.edu');
INSERT INTO sesshuns_email VALUES (294, 232, 'kmenten@mpifr-bonn.mpg.de');
INSERT INTO sesshuns_email VALUES (295, 233, 'ehumphre@cfa.harvard.edu');
INSERT INTO sesshuns_email VALUES (296, 233, 'ehumphreys@cfa.harvard.edu');
INSERT INTO sesshuns_email VALUES (297, 234, 'armijos@damir.iem.csic.es');
INSERT INTO sesshuns_email VALUES (298, 235, 'jmartin.pintado@iem.cfmac.csic.es');
INSERT INTO sesshuns_email VALUES (299, 236, 'mrequena@mpifr-bonn.mpg.de');
INSERT INTO sesshuns_email VALUES (300, 237, 'smartin@cfa.harvard.edu');
INSERT INTO sesshuns_email VALUES (301, 238, 'arturo@damir.iem.csic.es');
INSERT INTO sesshuns_email VALUES (302, 239, 'Joseph.Lazio@nrl.navy.mil');
INSERT INTO sesshuns_email VALUES (303, 239, 'lazio@rsd.nrl.navy.mil');
INSERT INTO sesshuns_email VALUES (304, 240, 'ctibbs@jb.man.ac.uk');
INSERT INTO sesshuns_email VALUES (305, 241, 'cdickins@astro.caltech.edu');
INSERT INTO sesshuns_email VALUES (306, 242, 'rdd@jb.man.ac.uk');
INSERT INTO sesshuns_email VALUES (307, 243, 'raw@jb.man.ac.uk');
INSERT INTO sesshuns_email VALUES (308, 244, 'rjd@jb.man.ac.uk');
INSERT INTO sesshuns_email VALUES (309, 245, 'paladini@ipac.caltech.edu');
INSERT INTO sesshuns_email VALUES (310, 246, 'simon@das.uchile.cl');
INSERT INTO sesshuns_email VALUES (311, 247, 'Kieran.A.Cleary@jpl.nasa.gov');
INSERT INTO sesshuns_email VALUES (312, 248, 'kudo@a.phys.nagoya-u.ac.jp');
INSERT INTO sesshuns_email VALUES (313, 249, 'torii@a.phys.nagoya-u.ac.jp');
INSERT INTO sesshuns_email VALUES (314, 250, 'natsukok@xj.commufa.jp');
INSERT INTO sesshuns_email VALUES (315, 251, 'morris@astro.ucla.edu');
INSERT INTO sesshuns_email VALUES (316, 251, 'morris@osprey.astro.ucla.edu');
INSERT INTO sesshuns_email VALUES (317, 252, 'm.walker@mawtech.com.au');
INSERT INTO sesshuns_email VALUES (318, 253, 'willem@phys.utb.edu');
INSERT INTO sesshuns_email VALUES (319, 254, 'aris.karastergiou@gmail.com');
INSERT INTO sesshuns_email VALUES (320, 255, 'j314159@gmail.com');
INSERT INTO sesshuns_email VALUES (321, 256, 'evan.keane@gmail.com');
INSERT INTO sesshuns_email VALUES (322, 257, 'bperera@mix.wvu.edu');
INSERT INTO sesshuns_email VALUES (323, 258, 'jcannon@macalester.edu');
INSERT INTO sesshuns_email VALUES (324, 259, 'jrosenb4@gmu.edu');
INSERT INTO sesshuns_email VALUES (325, 260, 'slaz@astro.indiana.edu');
INSERT INTO sesshuns_email VALUES (326, 261, 'yugao@pmo.ac.cn');
INSERT INTO sesshuns_email VALUES (327, 262, 'Jayaram.Chengalur@atnf.csiro.au');
INSERT INTO sesshuns_email VALUES (328, 262, 'chengalu@ncra.tifr.res.in');
INSERT INTO sesshuns_email VALUES (329, 262, 'chengalu@gmrt.ernet.in');
INSERT INTO sesshuns_email VALUES (330, 263, 'benjamin.zeiger@colorado.edu');
INSERT INTO sesshuns_email VALUES (331, 264, 'gonzalez@phas.ubc.ca');
INSERT INTO sesshuns_email VALUES (332, 265, 'joncas@phy.ulaval.ca');
INSERT INTO sesshuns_email VALUES (333, 266, 'jean-francois.robitaille.1@ulaval.ca');
INSERT INTO sesshuns_email VALUES (334, 267, 'douglas.marshall.1@ulaval.ca');
INSERT INTO sesshuns_email VALUES (335, 268, 'mamd@ias.u-psud.fr');
INSERT INTO sesshuns_email VALUES (336, 269, 'pgmartin@cita.utoronto.ca');
INSERT INTO sesshuns_email VALUES (337, 270, 'megandecesar@gmail.com');
INSERT INTO sesshuns_email VALUES (338, 271, 'miller@astro.umd.edu');
INSERT INTO sesshuns_email VALUES (339, 272, 'amss@st-and.ac.uk');
INSERT INTO sesshuns_email VALUES (340, 273, 'jsg5@st-andrews.ac.uk');
INSERT INTO sesshuns_email VALUES (341, 274, 'mmj@st-andrews.ac.uk');
INSERT INTO sesshuns_email VALUES (342, 275, 'acc4@st-and.ac.uk');
INSERT INTO sesshuns_email VALUES (343, 276, 'violette@nrao.edu');
INSERT INTO sesshuns_email VALUES (344, 277, 'aroy@mpifr-bonn.mpg.de');
INSERT INTO sesshuns_email VALUES (345, 278, 'sleurini@eso.org');
INSERT INTO sesshuns_email VALUES (346, 278, 'sleurini@mpifr-bonn.mpg.de');
INSERT INTO sesshuns_email VALUES (347, 279, 'jlm@ess.ucla.edu');
INSERT INTO sesshuns_email VALUES (348, 280, 'marty@shannon.jpl.nasa.gov');
INSERT INTO sesshuns_email VALUES (349, 280, 'martin.a.slade@jpl.nasa.gov');
INSERT INTO sesshuns_email VALUES (350, 281, 'jtomsick@ssl.berkeley.edu');
INSERT INTO sesshuns_email VALUES (351, 282, 'corbel@discovery.saclay.cea.fr');
INSERT INTO sesshuns_email VALUES (352, 283, 'migliari@ucsd.edu');
INSERT INTO sesshuns_email VALUES (353, 283, 'smigliari@ucsd.edu');
INSERT INTO sesshuns_email VALUES (354, 284, '');
INSERT INTO sesshuns_email VALUES (355, 287, 'guy@mrao.cam.ac.uk');
INSERT INTO sesshuns_email VALUES (356, 287, 'GGP1@mrao.cam.uk');


--
-- Data for Name: session_types; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO session_types VALUES (1, 'open');
INSERT INTO session_types VALUES (2, 'fixed');
INSERT INTO session_types VALUES (3, 'windowed');
INSERT INTO session_types VALUES (4, 'vlbi');
INSERT INTO session_types VALUES (5, 'maintenance');
INSERT INTO session_types VALUES (6, 'commissioning');


--
-- Data for Name: sessions; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO sessions VALUES (5, 2, 3, 2, 110, 5, 4217, 'BB240-05', 9, 8, 8, NULL, false);
INSERT INTO sessions VALUES (6, 2, 3, 2, 111, 6, 4218, 'BB240-06', 9, 8, 8, NULL, false);
INSERT INTO sessions VALUES (7, 2, 3, 2, 112, 7, 4219, 'BB240-07', 9, 8, 8, NULL, false);
INSERT INTO sessions VALUES (8, 2, 3, 2, 113, 8, 4220, 'BB240-08', 9, 8, 8, NULL, false);
INSERT INTO sessions VALUES (9, 2, 3, 2, 114, 9, 4221, 'BB240-09', 9, 8, 8, NULL, false);
INSERT INTO sessions VALUES (10, 2, 3, 2, 115, 10, 4222, 'BB240-10', 9, 8, 8, NULL, false);
INSERT INTO sessions VALUES (11, 2, 3, 2, 116, 11, 4223, 'BB240-11', 9, 8, 8, NULL, false);
INSERT INTO sessions VALUES (12, 2, 3, 2, 117, 12, 4224, 'BB240-12', 9, 8, 8, NULL, false);
INSERT INTO sessions VALUES (13, 2, 3, 2, 118, 13, 4225, 'BB240-13', 9, 8, 8, NULL, false);
INSERT INTO sessions VALUES (14, 2, 3, 2, 119, 14, 4226, 'BB240-14', 9, 8, 8, NULL, false);
INSERT INTO sessions VALUES (15, 2, 3, 2, 120, 15, 4227, 'BB240-15', 9, 8, 8, NULL, false);
INSERT INTO sessions VALUES (16, 2, 3, 2, 121, 16, 4229, 'BB240-16', 9, 8, 8, NULL, false);
INSERT INTO sessions VALUES (17, 3, 2, 2, 122, 17, 3742, 'BB261-01', 22.199999999999999, 12, 12, NULL, false);
INSERT INTO sessions VALUES (18, 4, 2, 2, 123, 18, 4246, 'BB268-01', 0, 16, 16, NULL, false);
INSERT INTO sessions VALUES (19, 5, 3, 2, 124, 19, 3712, 'BM290-01', 9, 5, 5, NULL, false);
INSERT INTO sessions VALUES (22, 8, 2, 2, 127, 22, 4249, 'BP157-01', 13.699999999999999, 10, 10, NULL, false);
INSERT INTO sessions VALUES (23, 8, 2, 2, 128, 23, 4291, 'BP157-02', 13.699999999999999, 10, 10, NULL, false);
INSERT INTO sessions VALUES (24, 8, 2, 2, 129, 24, 4292, 'BP157-03', 13.699999999999999, 10, 10, NULL, false);
INSERT INTO sessions VALUES (25, 8, 2, 2, 130, 25, 4293, 'BP157-04', 13.699999999999999, 10, 10, NULL, false);
INSERT INTO sessions VALUES (26, 9, 1, 5, 131, 26, 4187, 'GBT04A-003-01', 0.80000000000000004, 2.75, 2.75, NULL, false);
INSERT INTO sessions VALUES (27, 9, 1, 5, 132, 27, 4188, 'GBT04A-003-02', 1.0700000000000001, 2.75, 2.75, NULL, false);
INSERT INTO sessions VALUES (28, 10, 1, 5, 133, 28, 2342, 'GBT05C-027-01', 32.75, 5, 3, NULL, false);
INSERT INTO sessions VALUES (29, 11, 1, 5, 134, 29, 3136, 'GBT06C-048-01', 0.59999999999999998, 1.5, 1.5, NULL, false);
INSERT INTO sessions VALUES (30, 12, 1, 5, 135, 30, 1985, 'GBT07A-035-01', 44, 5, 3, NULL, false);
INSERT INTO sessions VALUES (31, 13, 1, 5, 136, 31, 2314, 'GBT07A-051-01', 44, 6, 3, NULL, false);
INSERT INTO sessions VALUES (32, 13, 1, 5, 137, 32, 2322, 'GBT07A-051-02', 44, 6, 3, NULL, false);
INSERT INTO sessions VALUES (33, 13, 1, 5, 138, 33, 4034, 'GBT07A-051-03', 0.59999999999999998, 6, 3, NULL, false);
INSERT INTO sessions VALUES (34, 14, 1, 5, 139, 34, 2102, 'GBT07A-086-01', 32.75, 2.8999999999999999, 2.8999999999999999, NULL, false);
INSERT INTO sessions VALUES (35, 14, 1, 5, 140, 35, 2103, 'GBT07A-086-02', 32.75, 2.8999999999999999, 2.8999999999999999, NULL, false);
INSERT INTO sessions VALUES (38, 16, 1, 5, 143, 38, 2515, 'GBT07C-032-01', 22.199999999999999, 5, 3, NULL, false);
INSERT INTO sessions VALUES (39, 17, 1, 5, 144, 39, 2811, 'GBT08A-004-01', 0.45000000000000001, 6, 3, NULL, false);
INSERT INTO sessions VALUES (40, 18, 3, 3, 145, 40, 4044, 'GBT08A-037-01', 2.1699999999999999, 4.5, 4.5, NULL, false);
INSERT INTO sessions VALUES (41, 19, 3, 5, 146, 41, 2928, 'GBT08A-048-01', 22.199999999999999, 1.5, 1.5, NULL, false);
INSERT INTO sessions VALUES (42, 20, 1, 5, 147, 42, 2977, 'GBT08A-073-01', 0.59999999999999998, 2.3999999999999999, 2.3999999999999999, NULL, false);
INSERT INTO sessions VALUES (43, 20, 1, 5, 148, 43, 3708, 'GBT08A-073-02', 0.45000000000000001, 2, 2, NULL, false);
INSERT INTO sessions VALUES (44, 21, 1, 3, 149, 44, 3019, 'GBT08A-085-01', 0, 7, 3, NULL, false);
INSERT INTO sessions VALUES (45, 21, 1, 3, 150, 45, 3020, 'GBT08A-085-02', 0, 7, 3, NULL, false);
INSERT INTO sessions VALUES (46, 21, 1, 3, 151, 46, 3021, 'GBT08A-085-03', 0, 6, 3, NULL, false);
INSERT INTO sessions VALUES (47, 21, 1, 3, 152, 47, 3022, 'GBT08A-085-04', 0, 7, 3, NULL, false);
INSERT INTO sessions VALUES (206, 86, 3, 3, 311, 206, 4195, 'GBT09B-031-03', 0.80000000000000004, 2.25, 2.25, NULL, true);
INSERT INTO sessions VALUES (52, 23, 1, 5, 157, 52, 3279, 'GBT08B-010-01', 13.699999999999999, 6, 3, NULL, false);
INSERT INTO sessions VALUES (53, 24, 3, 3, 158, 53, 3305, 'GBT08B-025-01', 0.80000000000000004, 5.5, 5.5, NULL, false);
INSERT INTO sessions VALUES (54, 24, 3, 3, 159, 54, 3306, 'GBT08B-025-02', 1.4399999999999999, 5.5, 5.5, NULL, false);
INSERT INTO sessions VALUES (55, 25, 1, 5, 160, 55, 4263, 'GBT08B-026-01', 9, 4, 3, NULL, false);
INSERT INTO sessions VALUES (56, 26, 1, 1, 161, 56, 3778, 'GBT08B-049-01', 2.1699999999999999, 10, 3, NULL, false);
INSERT INTO sessions VALUES (57, 27, 1, 5, 162, 57, 3514, 'GBT08C-009-01', 32.75, 8, 3, NULL, false);
INSERT INTO sessions VALUES (58, 27, 1, 5, 163, 58, 3515, 'GBT08C-009-02', 32.75, 8, 3, NULL, false);
INSERT INTO sessions VALUES (59, 28, 3, 3, 164, 59, 3527, 'GBT08C-014-01', 2.1699999999999999, 0.75, 0.75, NULL, false);
INSERT INTO sessions VALUES (62, 30, 1, 4, 167, 62, 3553, 'GBT08C-026-01', 90, 8, 3, NULL, false);
INSERT INTO sessions VALUES (63, 31, 3, 5, 168, 63, 3569, 'GBT08C-035-01', 22.199999999999999, 8, 8, NULL, false);
INSERT INTO sessions VALUES (64, 31, 1, 5, 169, 64, 3570, 'GBT08C-035-02', 22.199999999999999, 10, 3, NULL, false);
INSERT INTO sessions VALUES (65, 31, 1, 5, 170, 65, 3746, 'GBT08C-035-03', 22.199999999999999, 10, 3, NULL, false);
INSERT INTO sessions VALUES (66, 31, 3, 5, 171, 66, 4043, 'GBT08C-035-04', 22.199999999999999, 18, 18, NULL, false);
INSERT INTO sessions VALUES (67, 32, 3, 3, 172, 67, 4041, 'GBT08C-049-01', 2.1699999999999999, 6, 6, NULL, false);
INSERT INTO sessions VALUES (68, 32, 1, 3, 173, 68, 4042, 'GBT08C-049-02', 2.1699999999999999, 6, 3, NULL, false);
INSERT INTO sessions VALUES (69, 33, 1, 5, 174, 69, 3619, 'GBT08C-061-01', 44, 3, 3, NULL, false);
INSERT INTO sessions VALUES (70, 34, 1, 5, 175, 70, 3624, 'GBT08C-065-01', 0.45000000000000001, 7.3300000000000001, 3, NULL, false);
INSERT INTO sessions VALUES (71, 34, 1, 5, 176, 71, 3625, 'GBT08C-065-02', 0.45000000000000001, 4, 3, NULL, false);
INSERT INTO sessions VALUES (72, 35, 1, 5, 177, 72, 3631, 'GBT08C-070-01', 32.75, 7, 3, NULL, false);
INSERT INTO sessions VALUES (73, 36, 1, 5, 178, 73, 3643, 'GBT08C-073-01', 32.75, 7.5999999999999996, 3, NULL, false);
INSERT INTO sessions VALUES (74, 36, 1, 5, 179, 74, 3644, 'GBT08C-073-02', 32.75, 9, 3, NULL, false);
INSERT INTO sessions VALUES (75, 36, 1, 5, 180, 75, 3646, 'GBT08C-073-03', 32.75, 9.9000000000000004, 3, NULL, false);
INSERT INTO sessions VALUES (76, 37, 3, 3, 181, 76, 3651, 'GBT08C-076-01', 2.1699999999999999, 8, 8, NULL, false);
INSERT INTO sessions VALUES (77, 37, 3, 3, 182, 77, 3652, 'GBT08C-076-02', 2.1699999999999999, 9, 9, NULL, false);
INSERT INTO sessions VALUES (78, 38, 1, 4, 183, 78, 3655, 'GBT08C-078-01', 90, 8.5, 3, NULL, false);
INSERT INTO sessions VALUES (79, 39, 1, 4, 184, 79, 3781, 'GBT09A-002-01', 9, 5, 3, NULL, false);
INSERT INTO sessions VALUES (80, 40, 3, 3, 185, 80, 3998, 'GBT09A-003-01', 2.1699999999999999, 3, 3, NULL, false);
INSERT INTO sessions VALUES (81, 41, 1, 5, 186, 81, 3786, 'GBT09A-004-01', 0.34000000000000002, 5, 3, NULL, false);
INSERT INTO sessions VALUES (82, 41, 1, 5, 187, 82, 3787, 'GBT09A-004-02', 0.34000000000000002, 5, 3, NULL, false);
INSERT INTO sessions VALUES (83, 41, 1, 5, 188, 83, 3788, 'GBT09A-004-03', 0.34000000000000002, 5, 3, NULL, false);
INSERT INTO sessions VALUES (84, 42, 1, 5, 189, 84, 3797, 'GBT09A-007-01', 1.4399999999999999, 8.75, 3, NULL, false);
INSERT INTO sessions VALUES (85, 42, 1, 5, 190, 85, 3798, 'GBT09A-007-02', 1.4399999999999999, 6.25, 3, NULL, false);
INSERT INTO sessions VALUES (86, 43, 1, 5, 191, 86, 3810, 'GBT09A-012-01', 44, 7.1500000000000004, 3, NULL, false);
INSERT INTO sessions VALUES (87, 43, 1, 5, 192, 87, 3811, 'GBT09A-012-02', 44, 5.2000000000000002, 3, NULL, false);
INSERT INTO sessions VALUES (88, 43, 1, 5, 193, 88, 3812, 'GBT09A-012-03', 44, 5.2000000000000002, 3, NULL, false);
INSERT INTO sessions VALUES (89, 43, 1, 5, 194, 89, 3814, 'GBT09A-012-04', 44, 6.5, 3, NULL, false);
INSERT INTO sessions VALUES (90, 44, 1, 5, 195, 90, 3843, 'GBT09A-021-01', 13.699999999999999, 5, 3, NULL, false);
INSERT INTO sessions VALUES (91, 45, 1, 5, 196, 91, 3999, 'GBT09A-025-01', 0.45000000000000001, 1.3999999999999999, 1.3999999999999999, NULL, false);
INSERT INTO sessions VALUES (92, 45, 1, 5, 197, 92, 4000, 'GBT09A-025-02', 0.45000000000000001, 3.3999999999999999, 3, NULL, false);
INSERT INTO sessions VALUES (93, 45, 1, 5, 198, 93, 4001, 'GBT09A-025-03', 0.45000000000000001, 1.3999999999999999, 1.3999999999999999, NULL, false);
INSERT INTO sessions VALUES (94, 45, 1, 5, 199, 94, 4002, 'GBT09A-025-04', 0.45000000000000001, 4.4199999999999999, 3, NULL, false);
INSERT INTO sessions VALUES (95, 45, 1, 5, 200, 95, 4003, 'GBT09A-025-05', 0.45000000000000001, 6.4000000000000004, 3, NULL, false);
INSERT INTO sessions VALUES (96, 45, 1, 5, 201, 96, 4004, 'GBT09A-025-06', 0.45000000000000001, 1.3999999999999999, 1.3999999999999999, NULL, false);
INSERT INTO sessions VALUES (97, 45, 1, 5, 202, 97, 4005, 'GBT09A-025-07', 0.45000000000000001, 1.3999999999999999, 1.3999999999999999, NULL, false);
INSERT INTO sessions VALUES (98, 45, 1, 5, 203, 98, 4006, 'GBT09A-025-08', 0.45000000000000001, 1.3999999999999999, 1.3999999999999999, NULL, false);
INSERT INTO sessions VALUES (99, 45, 1, 5, 204, 99, 4007, 'GBT09A-025-09', 0.45000000000000001, 1.3999999999999999, 1.3999999999999999, NULL, false);
INSERT INTO sessions VALUES (100, 45, 1, 5, 205, 100, 4008, 'GBT09A-025-10', 0.45000000000000001, 2.3999999999999999, 2.3999999999999999, NULL, false);
INSERT INTO sessions VALUES (101, 46, 1, 5, 206, 101, 3867, 'GBT09A-034-01', 1.0700000000000001, 2.2000000000000002, 2.2000000000000002, NULL, false);
INSERT INTO sessions VALUES (102, 46, 1, 5, 207, 102, 3868, 'GBT09A-034-02', 1.0700000000000001, 2.2000000000000002, 2.2000000000000002, NULL, false);
INSERT INTO sessions VALUES (103, 46, 1, 5, 208, 103, 3869, 'GBT09A-034-03', 1.0700000000000001, 2.2000000000000002, 2.2000000000000002, NULL, false);
INSERT INTO sessions VALUES (104, 46, 1, 5, 209, 104, 3870, 'GBT09A-034-04', 1.0700000000000001, 2.2000000000000002, 2.2000000000000002, NULL, false);
INSERT INTO sessions VALUES (105, 46, 1, 5, 210, 105, 3871, 'GBT09A-034-05', 1.0700000000000001, 2.2000000000000002, 2.2000000000000002, NULL, false);
INSERT INTO sessions VALUES (106, 46, 1, 5, 211, 106, 3872, 'GBT09A-034-06', 1.0700000000000001, 2.2000000000000002, 2.2000000000000002, NULL, false);
INSERT INTO sessions VALUES (107, 46, 1, 5, 212, 107, 3873, 'GBT09A-034-07', 1.0700000000000001, 2.2000000000000002, 2.2000000000000002, NULL, false);
INSERT INTO sessions VALUES (108, 46, 1, 5, 213, 108, 3874, 'GBT09A-034-08', 1.0700000000000001, 2.2000000000000002, 2.2000000000000002, NULL, false);
INSERT INTO sessions VALUES (109, 47, 3, 3, 214, 109, 3880, 'GBT09A-038-01', 2.1699999999999999, 0.5, 0.5, NULL, false);
INSERT INTO sessions VALUES (110, 48, 1, 5, 215, 110, 3882, 'GBT09A-040-01', 32.75, 10, 3, NULL, false);
INSERT INTO sessions VALUES (111, 48, 1, 5, 216, 111, 3883, 'GBT09A-040-02', 32.75, 10, 3, NULL, false);
INSERT INTO sessions VALUES (112, 49, 1, 5, 217, 112, 3894, 'GBT09A-046-01', 1.4399999999999999, 5.25, 3, NULL, false);
INSERT INTO sessions VALUES (113, 49, 1, 5, 218, 113, 3895, 'GBT09A-046-02', 1.4399999999999999, 5.5, 3, NULL, false);
INSERT INTO sessions VALUES (114, 49, 1, 5, 219, 114, 3896, 'GBT09A-046-03', 1.4399999999999999, 5.1299999999999999, 3, NULL, false);
INSERT INTO sessions VALUES (115, 49, 1, 5, 220, 115, 3897, 'GBT09A-046-04', 1.4399999999999999, 5, 3, NULL, false);
INSERT INTO sessions VALUES (116, 50, 1, 5, 221, 116, 3908, 'GBT09A-055-01', 0.59999999999999998, 1.73, 1.73, NULL, false);
INSERT INTO sessions VALUES (117, 50, 1, 5, 222, 117, 3909, 'GBT09A-055-02', 0.80000000000000004, 4.7699999999999996, 3, NULL, false);
INSERT INTO sessions VALUES (118, 50, 1, 5, 223, 118, 3910, 'GBT09A-055-03', 1.0700000000000001, 1.3, 1.3, NULL, false);
INSERT INTO sessions VALUES (119, 50, 1, 5, 224, 119, 3911, 'GBT09A-055-04', 1.0700000000000001, 2.6000000000000001, 2.6000000000000001, NULL, false);
INSERT INTO sessions VALUES (120, 51, 1, 3, 225, 120, 3917, 'GBT09A-058-01', 0.34000000000000002, 2, 2, NULL, false);
INSERT INTO sessions VALUES (121, 51, 1, 3, 226, 121, 4023, 'GBT09A-058-02', 0.80000000000000004, 2, 2, NULL, false);
INSERT INTO sessions VALUES (122, 52, 1, 3, 227, 122, 3927, 'GBT09A-062-01', 2.1699999999999999, 10.550000000000001, 3, NULL, false);
INSERT INTO sessions VALUES (123, 53, 1, 1, 228, 123, 3935, 'GBT09A-070-01', 2.1699999999999999, 2, 2, NULL, false);
INSERT INTO sessions VALUES (124, 54, 1, 3, 229, 124, 3967, 'GBT09A-081-01', 0.34000000000000002, 3.5, 3, NULL, false);
INSERT INTO sessions VALUES (125, 54, 1, 3, 230, 125, 3969, 'GBT09A-081-02', 0.34000000000000002, 3.5, 3, NULL, false);
INSERT INTO sessions VALUES (126, 55, 1, 3, 231, 126, 4200, 'GBT09A-092-01', 0.34000000000000002, 8, 3, NULL, false);
INSERT INTO sessions VALUES (127, 55, 1, 3, 232, 127, 4210, 'GBT09A-092-02', 0.80000000000000004, 8, 3, NULL, false);
INSERT INTO sessions VALUES (128, 55, 1, 3, 233, 128, 4211, 'GBT09A-092-03', 1.4399999999999999, 8, 3, NULL, false);
INSERT INTO sessions VALUES (129, 56, 1, 3, 234, 129, 4201, 'GBT09A-093-01', 9, 12, 3, NULL, false);
INSERT INTO sessions VALUES (130, 56, 1, 3, 235, 130, 4202, 'GBT09A-093-02', 0.80000000000000004, 10, 3, NULL, false);
INSERT INTO sessions VALUES (131, 56, 1, 3, 236, 131, 4203, 'GBT09A-093-03', 9, 12, 3, NULL, false);
INSERT INTO sessions VALUES (132, 57, 1, 5, 237, 132, 4204, 'GBT09A-094-01', 13.699999999999999, 4, 3, NULL, false);
INSERT INTO sessions VALUES (133, 57, 1, 5, 238, 133, 4205, 'GBT09A-094-02', 13.699999999999999, 6, 3, NULL, false);
INSERT INTO sessions VALUES (134, 57, 1, 5, 239, 134, 4206, 'GBT09A-094-03', 13.699999999999999, 3, 3, NULL, false);
INSERT INTO sessions VALUES (135, 57, 1, 5, 240, 135, 4207, 'GBT09A-094-04', 13.699999999999999, 5, 3, NULL, false);
INSERT INTO sessions VALUES (136, 57, 1, 5, 241, 136, 4208, 'GBT09A-094-05', 13.699999999999999, 2, 2, NULL, false);
INSERT INTO sessions VALUES (137, 58, 1, 3, 242, 137, 4212, 'GBT09A-095-01', 2.1699999999999999, 6, 3, NULL, false);
INSERT INTO sessions VALUES (138, 59, 1, 3, 243, 138, 4273, 'GBT09A-096-01', 9, 4, 3, NULL, false);
INSERT INTO sessions VALUES (139, 59, 1, 3, 244, 139, 4274, 'GBT09A-096-02', 1.4399999999999999, 3.5, 3, NULL, false);
INSERT INTO sessions VALUES (140, 59, 1, 3, 245, 140, 4275, 'GBT09A-096-03', 2.1699999999999999, 3, 3, NULL, false);
INSERT INTO sessions VALUES (141, 59, 1, 3, 246, 141, 4276, 'GBT09A-096-04', 1.4399999999999999, 2, 2, NULL, false);
INSERT INTO sessions VALUES (142, 59, 1, 3, 247, 142, 4277, 'GBT09A-096-05', 1.4399999999999999, 3, 3, NULL, false);
INSERT INTO sessions VALUES (143, 59, 1, 3, 248, 143, 4278, 'GBT09A-096-06', 1.4399999999999999, 3, 3, NULL, false);
INSERT INTO sessions VALUES (144, 60, 1, 4, 249, 144, 4055, 'GBT09B-001-01', 9, 5, 3, NULL, false);
INSERT INTO sessions VALUES (145, 61, 1, 4, 250, 145, 4056, 'GBT09B-002-01', 9, 5, 3, NULL, false);
INSERT INTO sessions VALUES (146, 62, 1, 3, 251, 146, 4057, 'GBT09B-003-01', 0.80000000000000004, 3.5, 3, NULL, false);
INSERT INTO sessions VALUES (147, 62, 1, 3, 252, 147, 4058, 'GBT09B-003-02', 0.34000000000000002, 3.5, 3, NULL, false);
INSERT INTO sessions VALUES (148, 62, 1, 3, 253, 148, 4059, 'GBT09B-003-03', 2.1699999999999999, 4.5, 3, NULL, false);
INSERT INTO sessions VALUES (149, 63, 1, 3, 254, 149, 4060, 'GBT09B-004-01', 0.34000000000000002, 5.5, 3, NULL, false);
INSERT INTO sessions VALUES (150, 63, 1, 3, 255, 150, 4197, 'GBT09B-004-02', 0.34000000000000002, 5.5, 3, NULL, false);
INSERT INTO sessions VALUES (151, 64, 1, 5, 256, 151, 4061, 'GBT09B-005-01', 0.59999999999999998, 1.73, 1.73, NULL, false);
INSERT INTO sessions VALUES (152, 64, 1, 5, 257, 152, 4062, 'GBT09B-005-02', 0.80000000000000004, 6.3600000000000003, 3, NULL, false);
INSERT INTO sessions VALUES (153, 64, 1, 5, 258, 153, 4063, 'GBT09B-005-03', 1.0700000000000001, 1.3, 1.3, NULL, false);
INSERT INTO sessions VALUES (154, 64, 1, 5, 259, 154, 4064, 'GBT09B-005-04', 0.80000000000000004, 4.7699999999999996, 3, NULL, false);
INSERT INTO sessions VALUES (155, 64, 1, 5, 260, 155, 4065, 'GBT09B-005-05', 1.0700000000000001, 3.8999999999999999, 3, NULL, false);
INSERT INTO sessions VALUES (156, 64, 1, 5, 261, 156, 4066, 'GBT09B-005-06', 1.0700000000000001, 1.3, 1.3, NULL, false);
INSERT INTO sessions VALUES (157, 65, 3, 3, 262, 157, 4067, 'GBT09B-006-01', 2.1699999999999999, 1.25, 1.25, NULL, false);
INSERT INTO sessions VALUES (158, 65, 1, 3, 263, 158, 4068, 'GBT09B-006-02', 0, 2, 2, NULL, false);
INSERT INTO sessions VALUES (159, 65, 1, 3, 264, 159, 4069, 'GBT09B-006-03', 1.4399999999999999, 1, 1, NULL, false);
INSERT INTO sessions VALUES (160, 65, 3, 3, 265, 160, 4070, 'GBT09B-006-04', 2.1699999999999999, 0.75, 0.75, NULL, false);
INSERT INTO sessions VALUES (161, 66, 3, 3, 266, 161, 4071, 'GBT09B-008-01', 0.34000000000000002, 9, 9, NULL, false);
INSERT INTO sessions VALUES (162, 67, 1, 5, 267, 162, 4080, 'GBT09B-010-01', 9, 4, 3, NULL, false);
INSERT INTO sessions VALUES (163, 67, 1, 5, 268, 163, 4191, 'GBT09B-010-02', 9, 4, 3, NULL, false);
INSERT INTO sessions VALUES (164, 67, 1, 5, 269, 164, 4192, 'GBT09B-010-03', 9, 7, 3, NULL, false);
INSERT INTO sessions VALUES (165, 68, 1, 5, 270, 165, 4083, 'GBT09B-011-01', 1.4399999999999999, 5.5, 3, NULL, false);
INSERT INTO sessions VALUES (166, 69, 1, 4, 271, 166, 4086, 'GBT09B-012-01', 1.4399999999999999, 11.199999999999999, 3, NULL, false);
INSERT INTO sessions VALUES (167, 69, 1, 4, 272, 167, 4087, 'GBT09B-012-02', 1.4399999999999999, 12, 3, NULL, false);
INSERT INTO sessions VALUES (168, 69, 1, 4, 273, 168, 4088, 'GBT09B-012-03', 1.4399999999999999, 0.01, 0.01, NULL, false);
INSERT INTO sessions VALUES (169, 70, 1, 5, 274, 169, 4089, 'GBT09B-013-01', 0, 5, 3, NULL, false);
INSERT INTO sessions VALUES (170, 70, 1, 5, 275, 170, 4090, 'GBT09B-013-02', 0, 5, 3, NULL, false);
INSERT INTO sessions VALUES (171, 71, 1, 3, 276, 171, 4091, 'GBT09B-014-01', 2.1699999999999999, 4.5, 3, NULL, false);
INSERT INTO sessions VALUES (172, 72, 1, 5, 277, 172, 4092, 'GBT09B-015-01', 13.699999999999999, 5, 3, NULL, false);
INSERT INTO sessions VALUES (173, 72, 1, 5, 278, 173, 4282, 'GBT09B-015-02', 13.699999999999999, 5, 3, NULL, false);
INSERT INTO sessions VALUES (174, 73, 1, 5, 279, 174, 4093, 'GBT09B-016-01', 1.4399999999999999, 10, 3, NULL, false);
INSERT INTO sessions VALUES (175, 73, 1, 5, 280, 175, 4094, 'GBT09B-016-02', 1.4399999999999999, 10, 3, NULL, false);
INSERT INTO sessions VALUES (176, 74, 1, 3, 281, 176, 4095, 'GBT09B-017-01', 0, 3.5, 3, NULL, false);
INSERT INTO sessions VALUES (177, 74, 1, 3, 282, 177, 4096, 'GBT09B-017-02', 0, 3.5, 3, NULL, false);
INSERT INTO sessions VALUES (178, 74, 1, 3, 283, 178, 4097, 'GBT09B-017-03', 2.1699999999999999, 3, 3, NULL, false);
INSERT INTO sessions VALUES (179, 74, 1, 3, 284, 179, 4098, 'GBT09B-017-04', 2.1699999999999999, 3, 3, NULL, false);
INSERT INTO sessions VALUES (180, 75, 3, 3, 285, 180, 4177, 'GBT09B-018-01', 2.1699999999999999, 1.75, 1.75, NULL, false);
INSERT INTO sessions VALUES (181, 75, 1, 3, 286, 181, 4178, 'GBT09B-018-02', 9, 2, 2, NULL, false);
INSERT INTO sessions VALUES (182, 75, 1, 3, 287, 182, 4179, 'GBT09B-018-03', 13.699999999999999, 2, 2, NULL, false);
INSERT INTO sessions VALUES (183, 75, 3, 3, 288, 183, 4194, 'GBT09B-018-04', 2.1699999999999999, 1.75, 1.75, NULL, false);
INSERT INTO sessions VALUES (184, 76, 1, 4, 289, 184, 4099, 'GBT09B-019-01', 1.4399999999999999, 3.5, 3, NULL, false);
INSERT INTO sessions VALUES (185, 76, 1, 4, 290, 185, 4100, 'GBT09B-019-02', 0, 5.75, 3, NULL, false);
INSERT INTO sessions VALUES (186, 77, 1, 3, 291, 186, 4103, 'GBT09B-021-01', 0, 4.75, 3, NULL, false);
INSERT INTO sessions VALUES (187, 78, 1, 4, 292, 187, 4104, 'GBT09B-022-01', 9, 7, 3, NULL, false);
INSERT INTO sessions VALUES (188, 79, 1, 3, 293, 188, 4105, 'GBT09B-023-01', 2.1699999999999999, 4.5, 3, NULL, false);
INSERT INTO sessions VALUES (189, 79, 1, 3, 294, 189, 4106, 'GBT09B-023-02', 0.80000000000000004, 6.5, 3, NULL, false);
INSERT INTO sessions VALUES (190, 80, 1, 3, 295, 190, 4107, 'GBT09B-024-01', 0.80000000000000004, 9.5, 3, NULL, false);
INSERT INTO sessions VALUES (191, 80, 1, 3, 296, 191, 4108, 'GBT09B-024-02', 0.80000000000000004, 6.25, 3, NULL, false);
INSERT INTO sessions VALUES (192, 81, 1, 5, 297, 192, 4109, 'GBT09B-025-01', 1.4399999999999999, 4.5, 3, NULL, false);
INSERT INTO sessions VALUES (193, 82, 1, 3, 298, 193, 4110, 'GBT09B-026-01', 0.34000000000000002, 4, 3, NULL, false);
INSERT INTO sessions VALUES (194, 83, 1, 3, 299, 194, 4113, 'GBT09B-028-01', 0.80000000000000004, 5.5, 3, NULL, false);
INSERT INTO sessions VALUES (195, 83, 3, 3, 300, 195, 4114, 'GBT09B-028-02', 0.34000000000000002, 5.5, 5.5, NULL, false);
INSERT INTO sessions VALUES (196, 83, 1, 3, 301, 196, 4115, 'GBT09B-028-03', 0.80000000000000004, 5.5, 3, NULL, false);
INSERT INTO sessions VALUES (197, 83, 1, 3, 302, 197, 4116, 'GBT09B-028-04', 0.34000000000000002, 5.5, 3, NULL, false);
INSERT INTO sessions VALUES (198, 84, 3, 3, 303, 198, 4117, 'GBT09B-029-01', 0.80000000000000004, 4.25, 4.25, NULL, false);
INSERT INTO sessions VALUES (199, 84, 3, 3, 304, 199, 4118, 'GBT09B-029-02', 0.80000000000000004, 5.5, 5.5, NULL, false);
INSERT INTO sessions VALUES (200, 84, 3, 3, 305, 200, 4119, 'GBT09B-029-03', 1.4399999999999999, 5.5, 5.5, NULL, false);
INSERT INTO sessions VALUES (201, 84, 1, 3, 306, 201, 4120, 'GBT09B-029-04', 0.80000000000000004, 7.5, 3, NULL, false);
INSERT INTO sessions VALUES (202, 84, 1, 3, 307, 202, 4198, 'GBT09B-029-05', 0.80000000000000004, 7.5, 3, NULL, false);
INSERT INTO sessions VALUES (203, 85, 1, 5, 308, 203, 4121, 'GBT09B-030-01', 1.4399999999999999, 6, 3, NULL, false);
INSERT INTO sessions VALUES (204, 86, 3, 3, 309, 204, 4122, 'GBT09B-031-01', 0.80000000000000004, 2.3199999999999998, 2.3199999999999998, NULL, false);
INSERT INTO sessions VALUES (205, 86, 3, 3, 310, 205, 4123, 'GBT09B-031-02', 0.80000000000000004, 2.3300000000000001, 2.3300000000000001, NULL, false);
INSERT INTO sessions VALUES (207, 86, 3, 3, 312, 207, 4196, 'GBT09B-031-04', 0.80000000000000004, 2.25, 2.25, NULL, false);
INSERT INTO sessions VALUES (208, 87, 1, 3, 313, 208, 4124, 'GBT09B-032-01', 1.4399999999999999, 10.5, 3, NULL, false);
INSERT INTO sessions VALUES (209, 88, 1, 5, 314, 209, 4128, 'GBT09B-034-01', 1.4399999999999999, 7.75, 3, NULL, false);
INSERT INTO sessions VALUES (210, 88, 1, 5, 315, 210, 4129, 'GBT09B-034-02', 1.4399999999999999, 10, 3, NULL, false);
INSERT INTO sessions VALUES (211, 89, 1, 5, 316, 211, 4285, 'GBT09B-035-01', 0.45000000000000001, 4, 3, NULL, false);
INSERT INTO sessions VALUES (212, 90, 1, 5, 317, 212, 4131, 'GBT09B-036-01', 13.699999999999999, 12, 3, NULL, false);
INSERT INTO sessions VALUES (213, 90, 1, 5, 318, 213, 4132, 'GBT09B-036-02', 13.699999999999999, 10.800000000000001, 3, NULL, false);
INSERT INTO sessions VALUES (214, 91, 1, 5, 319, 214, 4133, 'GBT09B-037-01', 1.0700000000000001, 2, 2, NULL, false);
INSERT INTO sessions VALUES (215, 92, 1, 5, 320, 215, 4135, 'GBT09B-039-01', 13.699999999999999, 2, 2, NULL, false);
INSERT INTO sessions VALUES (216, 92, 1, 5, 321, 216, 4136, 'GBT09B-039-02', 13.699999999999999, 1.5, 1.5, NULL, false);
INSERT INTO sessions VALUES (217, 93, 1, 5, 322, 217, 4137, 'GBT09B-040-01', 13.699999999999999, 9, 3, NULL, false);
INSERT INTO sessions VALUES (218, 93, 1, 5, 323, 218, 4138, 'GBT09B-040-02', 13.699999999999999, 10, 3, NULL, false);
INSERT INTO sessions VALUES (219, 94, 3, 3, 324, 219, 4139, 'GBT09B-041-01', 1.4399999999999999, 8.5, 8.5, NULL, false);
INSERT INTO sessions VALUES (220, 94, 3, 3, 325, 220, 4140, 'GBT09B-041-02', 0.80000000000000004, 8.5, 8.5, NULL, false);
INSERT INTO sessions VALUES (221, 94, 3, 3, 326, 221, 4141, 'GBT09B-041-03', 1.4399999999999999, 3, 3, NULL, false);
INSERT INTO sessions VALUES (222, 95, 1, 5, 327, 222, 4142, 'GBT09B-042-01', 1.4399999999999999, 8, 3, NULL, false);
INSERT INTO sessions VALUES (223, 96, 1, 3, 328, 223, 4143, 'GBT09B-043-01', 2.1699999999999999, 1, 1, NULL, false);
INSERT INTO sessions VALUES (224, 96, 1, 3, 329, 224, 4144, 'GBT09B-043-02', 2.1699999999999999, 1, 1, NULL, false);
INSERT INTO sessions VALUES (225, 96, 1, 3, 330, 225, 4145, 'GBT09B-043-03', 2.1699999999999999, 1, 1, NULL, false);
INSERT INTO sessions VALUES (226, 96, 1, 3, 331, 226, 4146, 'GBT09B-043-04', 2.1699999999999999, 1, 1, NULL, false);
INSERT INTO sessions VALUES (227, 96, 1, 3, 332, 227, 4147, 'GBT09B-043-05', 2.1699999999999999, 1, 1, NULL, false);
INSERT INTO sessions VALUES (228, 96, 1, 3, 333, 228, 4148, 'GBT09B-043-06', 2.1699999999999999, 1, 1, NULL, false);
INSERT INTO sessions VALUES (229, 96, 1, 3, 334, 229, 4149, 'GBT09B-043-07', 2.1699999999999999, 1, 1, NULL, false);
INSERT INTO sessions VALUES (230, 96, 1, 3, 335, 230, 4150, 'GBT09B-043-08', 2.1699999999999999, 1, 1, NULL, false);
INSERT INTO sessions VALUES (231, 96, 1, 3, 336, 231, 4151, 'GBT09B-043-09', 2.1699999999999999, 1, 1, NULL, false);
INSERT INTO sessions VALUES (232, 96, 1, 3, 337, 232, 4152, 'GBT09B-043-10', 2.1699999999999999, 1, 1, NULL, false);
INSERT INTO sessions VALUES (233, 96, 1, 3, 338, 233, 4153, 'GBT09B-043-11', 2.1699999999999999, 1, 1, NULL, false);
INSERT INTO sessions VALUES (234, 96, 1, 3, 339, 234, 4154, 'GBT09B-043-12', 2.1699999999999999, 1, 1, NULL, false);
INSERT INTO sessions VALUES (235, 96, 1, 3, 340, 235, 4155, 'GBT09B-043-13', 2.1699999999999999, 1, 1, NULL, false);
INSERT INTO sessions VALUES (236, 96, 1, 3, 341, 236, 4156, 'GBT09B-043-14', 2.1699999999999999, 1, 1, NULL, false);
INSERT INTO sessions VALUES (237, 96, 1, 3, 342, 237, 4157, 'GBT09B-043-15', 2.1699999999999999, 1, 1, NULL, false);
INSERT INTO sessions VALUES (238, 97, 3, 4, 343, 238, 4158, 'GBT09B-044-01', 0.34000000000000002, 6, 6, NULL, false);
INSERT INTO sessions VALUES (239, 98, 1, 3, 344, 239, 4159, 'GBT09B-045-01', 2.1699999999999999, 3.5, 3, NULL, false);
INSERT INTO sessions VALUES (240, 98, 1, 3, 345, 240, 4160, 'GBT09B-045-02', 2.1699999999999999, 3.5, 3, NULL, false);
INSERT INTO sessions VALUES (241, 98, 1, 3, 346, 241, 4161, 'GBT09B-045-03', 2.1699999999999999, 3.5, 3, NULL, false);
INSERT INTO sessions VALUES (242, 98, 1, 3, 347, 242, 4162, 'GBT09B-045-04', 2.1699999999999999, 3.5, 3, NULL, false);
INSERT INTO sessions VALUES (243, 98, 1, 3, 348, 243, 4163, 'GBT09B-045-05', 2.1699999999999999, 3.5, 3, NULL, false);
INSERT INTO sessions VALUES (244, 98, 1, 3, 349, 244, 4164, 'GBT09B-045-06', 2.1699999999999999, 3.5, 3, NULL, false);
INSERT INTO sessions VALUES (245, 98, 1, 3, 350, 245, 4165, 'GBT09B-045-07', 2.1699999999999999, 3.5, 3, NULL, false);
INSERT INTO sessions VALUES (246, 99, 1, 5, 351, 246, 4166, 'GBT09B-046-01', 13.699999999999999, 6, 3, NULL, false);
INSERT INTO sessions VALUES (247, 99, 1, 5, 352, 247, 4167, 'GBT09B-046-02', 13.699999999999999, 4, 3, NULL, false);
INSERT INTO sessions VALUES (254, 101, 3, 4, 359, 254, 4045, 'GLST011217-01', 9, 2, 2, NULL, false);
INSERT INTO sessions VALUES (2, 2, 3, 2, 107, 2, 4214, 'BB240-02', 9, 8, 8, NULL, false);
INSERT INTO sessions VALUES (3, 2, 3, 2, 108, 3, 4215, 'BB240-03', 9, 8, 8, NULL, false);
INSERT INTO sessions VALUES (248, 100, 2, 1, 353, 248, 4171, 'GBT09B-048-01', 9, 1.5, 1.5, NULL, true);
INSERT INTO sessions VALUES (249, 100, 2, 1, 354, 249, 4286, 'GBT09B-048-02', 9, 1.5, 1.5, NULL, true);
INSERT INTO sessions VALUES (250, 100, 2, 1, 355, 250, 4287, 'GBT09B-048-03', 9, 1.5, 1.5, NULL, true);
INSERT INTO sessions VALUES (251, 100, 2, 1, 356, 251, 4288, 'GBT09B-048-04', 9, 1.5, 1.5, NULL, true);
INSERT INTO sessions VALUES (252, 100, 2, 1, 357, 252, 4289, 'GBT09B-048-05', 9, 1.5, 1.5, NULL, true);
INSERT INTO sessions VALUES (253, 100, 2, 1, 358, 253, 4290, 'GBT09B-048-06', 9, 1.5, 1.5, NULL, true);
INSERT INTO sessions VALUES (4, 2, 3, 2, 109, 4, 4216, 'BB240-04', 9, 8, 8, NULL, true);
INSERT INTO sessions VALUES (20, 6, 2, 2, 125, 20, 4247, 'BM305-01', 1.4399999999999999, 8, 8, NULL, false);
INSERT INTO sessions VALUES (1, 2, 3, 2, 106, 1, 4213, 'BB240-01', 9, 8, 8, NULL, false);
INSERT INTO sessions VALUES (48, 22, 2, 1, 153, 48, 3992, 'GBT08B-005-01', 2.1699999999999999, 4, 4, NULL, true);
INSERT INTO sessions VALUES (49, 22, 2, 1, 154, 49, 4182, 'GBT08B-005-02', 2.1699999999999999, 3.75, 3.75, NULL, true);
INSERT INTO sessions VALUES (36, 15, 3, 3, 141, 36, 2106, 'GBT07A-087-01', 0.80000000000000004, 7.5, 7.5, NULL, true);
INSERT INTO sessions VALUES (21, 7, 2, 2, 126, 21, 4248, 'BM306-01', 9, 6, 6, NULL, true);
INSERT INTO sessions VALUES (61, 29, 3, 3, 166, 61, 3548, 'GBT08C-023-02', 0.80000000000000004, 1, 1, NULL, true);
INSERT INTO sessions VALUES (37, 15, 3, 3, 142, 37, 2108, 'GBT07A-087-02', 1.4399999999999999, 7.5, 7.5, NULL, true);
INSERT INTO sessions VALUES (60, 29, 3, 3, 165, 60, 3547, 'GBT08C-023-01', 2.1699999999999999, 3.75, 3.75, NULL, true);
INSERT INTO sessions VALUES (50, 22, 2, 1, 155, 50, 4183, 'GBT08B-005-03', 2.1699999999999999, 3.5, 3.5, NULL, true);
INSERT INTO sessions VALUES (51, 22, 2, 1, 156, 51, 4184, 'GBT08B-005-04', 2.1699999999999999, 3.5, 3.5, NULL, true);


--
-- Data for Name: status; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO status VALUES (5, false, true, false, false);
INSERT INTO status VALUES (6, false, true, false, false);
INSERT INTO status VALUES (7, false, true, false, false);
INSERT INTO status VALUES (8, false, true, false, false);
INSERT INTO status VALUES (9, false, true, false, false);
INSERT INTO status VALUES (10, false, true, false, false);
INSERT INTO status VALUES (11, false, true, false, false);
INSERT INTO status VALUES (12, false, true, false, false);
INSERT INTO status VALUES (13, false, true, false, false);
INSERT INTO status VALUES (14, false, true, false, false);
INSERT INTO status VALUES (15, false, true, false, false);
INSERT INTO status VALUES (16, false, true, false, false);
INSERT INTO status VALUES (17, false, true, false, false);
INSERT INTO status VALUES (18, false, true, false, false);
INSERT INTO status VALUES (19, false, true, false, false);
INSERT INTO status VALUES (22, false, true, false, false);
INSERT INTO status VALUES (23, false, true, false, false);
INSERT INTO status VALUES (24, false, true, false, false);
INSERT INTO status VALUES (25, false, true, false, false);
INSERT INTO status VALUES (26, false, true, false, false);
INSERT INTO status VALUES (27, false, true, false, false);
INSERT INTO status VALUES (28, false, true, false, false);
INSERT INTO status VALUES (29, false, true, false, false);
INSERT INTO status VALUES (30, false, true, false, false);
INSERT INTO status VALUES (31, false, true, false, false);
INSERT INTO status VALUES (32, false, true, false, false);
INSERT INTO status VALUES (33, false, true, false, false);
INSERT INTO status VALUES (34, false, true, false, false);
INSERT INTO status VALUES (35, false, true, false, false);
INSERT INTO status VALUES (38, false, true, false, false);
INSERT INTO status VALUES (39, false, true, false, false);
INSERT INTO status VALUES (40, false, true, false, false);
INSERT INTO status VALUES (41, false, true, false, false);
INSERT INTO status VALUES (42, false, true, false, false);
INSERT INTO status VALUES (43, false, true, false, false);
INSERT INTO status VALUES (44, false, true, false, false);
INSERT INTO status VALUES (45, false, true, false, false);
INSERT INTO status VALUES (46, false, true, false, false);
INSERT INTO status VALUES (47, false, true, false, false);
INSERT INTO status VALUES (52, false, true, false, false);
INSERT INTO status VALUES (53, false, true, false, false);
INSERT INTO status VALUES (54, false, true, false, false);
INSERT INTO status VALUES (55, false, true, false, false);
INSERT INTO status VALUES (56, false, true, false, false);
INSERT INTO status VALUES (57, false, true, false, false);
INSERT INTO status VALUES (58, false, true, false, false);
INSERT INTO status VALUES (59, false, true, false, false);
INSERT INTO status VALUES (62, false, true, false, false);
INSERT INTO status VALUES (63, false, true, false, false);
INSERT INTO status VALUES (64, false, true, false, false);
INSERT INTO status VALUES (65, false, true, false, false);
INSERT INTO status VALUES (66, false, true, false, false);
INSERT INTO status VALUES (67, false, true, false, false);
INSERT INTO status VALUES (68, false, true, false, false);
INSERT INTO status VALUES (69, false, true, false, false);
INSERT INTO status VALUES (70, false, true, false, false);
INSERT INTO status VALUES (71, false, true, false, false);
INSERT INTO status VALUES (72, false, true, false, false);
INSERT INTO status VALUES (73, false, true, false, false);
INSERT INTO status VALUES (74, false, true, false, false);
INSERT INTO status VALUES (75, false, true, false, false);
INSERT INTO status VALUES (76, false, true, false, false);
INSERT INTO status VALUES (77, false, true, false, false);
INSERT INTO status VALUES (78, false, true, false, false);
INSERT INTO status VALUES (79, false, true, false, false);
INSERT INTO status VALUES (80, false, true, false, false);
INSERT INTO status VALUES (81, false, true, false, false);
INSERT INTO status VALUES (82, false, true, false, false);
INSERT INTO status VALUES (83, false, true, false, false);
INSERT INTO status VALUES (84, false, true, false, false);
INSERT INTO status VALUES (85, false, true, false, false);
INSERT INTO status VALUES (86, false, true, false, false);
INSERT INTO status VALUES (87, false, true, false, false);
INSERT INTO status VALUES (88, false, true, false, false);
INSERT INTO status VALUES (89, false, true, false, false);
INSERT INTO status VALUES (90, false, true, false, false);
INSERT INTO status VALUES (91, false, true, false, false);
INSERT INTO status VALUES (92, false, true, false, false);
INSERT INTO status VALUES (93, false, true, false, false);
INSERT INTO status VALUES (94, false, true, false, false);
INSERT INTO status VALUES (95, false, true, false, false);
INSERT INTO status VALUES (96, false, true, false, false);
INSERT INTO status VALUES (97, false, true, false, false);
INSERT INTO status VALUES (98, false, true, false, false);
INSERT INTO status VALUES (99, false, true, false, false);
INSERT INTO status VALUES (100, false, true, false, false);
INSERT INTO status VALUES (101, false, true, false, false);
INSERT INTO status VALUES (102, false, true, false, false);
INSERT INTO status VALUES (103, false, true, false, false);
INSERT INTO status VALUES (104, false, true, false, false);
INSERT INTO status VALUES (105, false, true, false, false);
INSERT INTO status VALUES (106, false, true, false, false);
INSERT INTO status VALUES (107, false, true, false, false);
INSERT INTO status VALUES (108, false, true, false, false);
INSERT INTO status VALUES (109, false, true, false, false);
INSERT INTO status VALUES (110, false, true, false, false);
INSERT INTO status VALUES (111, false, true, false, false);
INSERT INTO status VALUES (112, false, true, false, false);
INSERT INTO status VALUES (113, false, true, false, false);
INSERT INTO status VALUES (114, false, true, false, false);
INSERT INTO status VALUES (115, false, true, false, false);
INSERT INTO status VALUES (116, false, true, false, false);
INSERT INTO status VALUES (117, false, true, false, false);
INSERT INTO status VALUES (118, false, true, false, false);
INSERT INTO status VALUES (119, false, true, false, false);
INSERT INTO status VALUES (120, false, true, false, false);
INSERT INTO status VALUES (121, false, true, false, false);
INSERT INTO status VALUES (122, false, true, false, false);
INSERT INTO status VALUES (123, false, true, false, false);
INSERT INTO status VALUES (124, false, true, false, false);
INSERT INTO status VALUES (125, false, true, false, false);
INSERT INTO status VALUES (126, false, true, false, false);
INSERT INTO status VALUES (127, false, true, false, false);
INSERT INTO status VALUES (128, false, true, false, false);
INSERT INTO status VALUES (129, false, true, false, false);
INSERT INTO status VALUES (130, false, true, false, false);
INSERT INTO status VALUES (131, false, true, false, false);
INSERT INTO status VALUES (132, false, true, false, false);
INSERT INTO status VALUES (133, false, true, false, false);
INSERT INTO status VALUES (134, false, true, false, false);
INSERT INTO status VALUES (135, false, true, false, false);
INSERT INTO status VALUES (136, false, true, false, false);
INSERT INTO status VALUES (137, false, true, false, false);
INSERT INTO status VALUES (138, false, true, false, false);
INSERT INTO status VALUES (139, false, true, false, false);
INSERT INTO status VALUES (140, false, true, false, false);
INSERT INTO status VALUES (141, false, true, false, false);
INSERT INTO status VALUES (142, false, true, false, false);
INSERT INTO status VALUES (143, false, true, false, false);
INSERT INTO status VALUES (144, false, true, false, false);
INSERT INTO status VALUES (145, false, true, false, false);
INSERT INTO status VALUES (146, false, true, false, false);
INSERT INTO status VALUES (147, false, true, false, false);
INSERT INTO status VALUES (148, false, true, false, false);
INSERT INTO status VALUES (149, false, true, false, false);
INSERT INTO status VALUES (150, false, true, false, false);
INSERT INTO status VALUES (151, false, true, false, false);
INSERT INTO status VALUES (152, false, true, false, false);
INSERT INTO status VALUES (153, false, true, false, false);
INSERT INTO status VALUES (154, false, true, false, false);
INSERT INTO status VALUES (155, false, true, false, false);
INSERT INTO status VALUES (156, false, true, false, false);
INSERT INTO status VALUES (157, false, true, false, false);
INSERT INTO status VALUES (158, false, true, false, false);
INSERT INTO status VALUES (159, false, true, false, false);
INSERT INTO status VALUES (160, false, true, false, false);
INSERT INTO status VALUES (161, false, true, false, false);
INSERT INTO status VALUES (162, false, true, false, false);
INSERT INTO status VALUES (163, false, true, false, false);
INSERT INTO status VALUES (164, false, true, false, false);
INSERT INTO status VALUES (165, false, true, false, false);
INSERT INTO status VALUES (166, false, true, false, false);
INSERT INTO status VALUES (167, false, true, false, false);
INSERT INTO status VALUES (168, false, true, false, false);
INSERT INTO status VALUES (169, false, true, false, false);
INSERT INTO status VALUES (170, false, true, false, false);
INSERT INTO status VALUES (171, false, true, false, false);
INSERT INTO status VALUES (172, false, true, false, false);
INSERT INTO status VALUES (173, false, true, false, false);
INSERT INTO status VALUES (174, false, true, false, false);
INSERT INTO status VALUES (175, false, true, false, false);
INSERT INTO status VALUES (176, false, true, false, false);
INSERT INTO status VALUES (177, false, true, false, false);
INSERT INTO status VALUES (178, false, true, false, false);
INSERT INTO status VALUES (179, false, true, false, false);
INSERT INTO status VALUES (180, false, true, false, false);
INSERT INTO status VALUES (181, false, true, false, false);
INSERT INTO status VALUES (182, false, true, false, false);
INSERT INTO status VALUES (183, false, true, false, false);
INSERT INTO status VALUES (184, false, true, false, false);
INSERT INTO status VALUES (185, false, true, false, false);
INSERT INTO status VALUES (186, false, true, false, false);
INSERT INTO status VALUES (187, false, true, false, false);
INSERT INTO status VALUES (188, false, true, false, false);
INSERT INTO status VALUES (189, false, true, false, false);
INSERT INTO status VALUES (190, false, true, false, false);
INSERT INTO status VALUES (191, false, true, false, false);
INSERT INTO status VALUES (192, false, true, false, false);
INSERT INTO status VALUES (193, false, true, false, false);
INSERT INTO status VALUES (194, false, true, false, false);
INSERT INTO status VALUES (195, false, true, false, false);
INSERT INTO status VALUES (196, false, true, false, false);
INSERT INTO status VALUES (197, false, true, false, false);
INSERT INTO status VALUES (198, false, true, false, false);
INSERT INTO status VALUES (199, false, true, false, false);
INSERT INTO status VALUES (200, false, true, false, false);
INSERT INTO status VALUES (201, false, true, false, false);
INSERT INTO status VALUES (202, false, true, false, false);
INSERT INTO status VALUES (203, false, true, false, false);
INSERT INTO status VALUES (204, false, true, false, false);
INSERT INTO status VALUES (205, false, true, false, false);
INSERT INTO status VALUES (207, false, true, false, false);
INSERT INTO status VALUES (208, false, true, false, false);
INSERT INTO status VALUES (209, false, true, false, false);
INSERT INTO status VALUES (210, false, true, false, false);
INSERT INTO status VALUES (211, false, true, false, false);
INSERT INTO status VALUES (212, false, true, false, false);
INSERT INTO status VALUES (213, false, true, false, false);
INSERT INTO status VALUES (214, false, true, false, false);
INSERT INTO status VALUES (215, false, true, false, false);
INSERT INTO status VALUES (216, false, true, false, false);
INSERT INTO status VALUES (217, false, true, false, false);
INSERT INTO status VALUES (218, false, true, false, false);
INSERT INTO status VALUES (219, false, true, false, false);
INSERT INTO status VALUES (220, false, true, false, false);
INSERT INTO status VALUES (221, false, true, false, false);
INSERT INTO status VALUES (222, false, true, false, false);
INSERT INTO status VALUES (223, false, true, false, false);
INSERT INTO status VALUES (224, false, true, false, false);
INSERT INTO status VALUES (225, false, true, false, false);
INSERT INTO status VALUES (226, false, true, false, false);
INSERT INTO status VALUES (206, true, true, true, true);
INSERT INTO status VALUES (227, false, true, false, false);
INSERT INTO status VALUES (228, false, true, false, false);
INSERT INTO status VALUES (229, false, true, false, false);
INSERT INTO status VALUES (230, false, true, false, false);
INSERT INTO status VALUES (231, false, true, false, false);
INSERT INTO status VALUES (232, false, true, false, false);
INSERT INTO status VALUES (233, false, true, false, false);
INSERT INTO status VALUES (234, false, true, false, false);
INSERT INTO status VALUES (235, false, true, false, false);
INSERT INTO status VALUES (236, false, true, false, false);
INSERT INTO status VALUES (237, false, true, false, false);
INSERT INTO status VALUES (238, false, true, false, false);
INSERT INTO status VALUES (239, false, true, false, false);
INSERT INTO status VALUES (240, false, true, false, false);
INSERT INTO status VALUES (241, false, true, false, false);
INSERT INTO status VALUES (242, false, true, false, false);
INSERT INTO status VALUES (243, false, true, false, false);
INSERT INTO status VALUES (244, false, true, false, false);
INSERT INTO status VALUES (245, false, true, false, false);
INSERT INTO status VALUES (246, false, true, false, false);
INSERT INTO status VALUES (247, false, true, false, false);
INSERT INTO status VALUES (248, false, true, false, false);
INSERT INTO status VALUES (249, false, true, false, false);
INSERT INTO status VALUES (250, false, true, false, false);
INSERT INTO status VALUES (251, false, true, false, false);
INSERT INTO status VALUES (252, false, true, false, false);
INSERT INTO status VALUES (253, false, true, false, false);
INSERT INTO status VALUES (254, false, true, false, false);
INSERT INTO status VALUES (2, true, true, true, true);
INSERT INTO status VALUES (3, true, true, true, true);
INSERT INTO status VALUES (4, true, true, true, true);
INSERT INTO status VALUES (61, true, true, true, true);
INSERT INTO status VALUES (60, true, true, true, true);
INSERT INTO status VALUES (37, true, true, true, true);
INSERT INTO status VALUES (36, true, true, true, true);
INSERT INTO status VALUES (20, true, true, true, true);
INSERT INTO status VALUES (49, true, true, true, true);
INSERT INTO status VALUES (1, true, true, true, true);
INSERT INTO status VALUES (21, true, true, true, true);
INSERT INTO status VALUES (50, true, true, true, true);
INSERT INTO status VALUES (51, true, true, true, true);
INSERT INTO status VALUES (48, true, true, true, true);


--
-- Data for Name: systems; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO systems VALUES (1, 'J2000', 'ra', 'dec');
INSERT INTO systems VALUES (2, 'B1950', 'ra', 'dec');
INSERT INTO systems VALUES (3, 'Galactic', 'lat', 'long');
INSERT INTO systems VALUES (4, 'RaDecOfDate', 'ra', 'dec');
INSERT INTO systems VALUES (5, 'AzEl', 'az', 'el');
INSERT INTO systems VALUES (6, 'HaDec', 'ra', 'dec');
INSERT INTO systems VALUES (7, 'ApparentRaDec', 'ra', 'dec');
INSERT INTO systems VALUES (8, 'CableWrap', 'az', 'el');
INSERT INTO systems VALUES (9, 'Encoder', 'az', 'el');


--
-- Data for Name: targets; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO targets VALUES (5, 5, 1, '729,867B', -0.38798669271800001, 5.4977871437800001);
INSERT INTO targets VALUES (6, 6, 1, '1230A/B,866', 0.082903139469700002, 5.4977871437800001);
INSERT INTO targets VALUES (7, 7, 1, '4063,LSRJ1835+3259', 0.63809237452900003, 4.9741883681800001);
INSERT INTO targets VALUES (8, 8, 1, '1005A,84', -0.29443704481100003, 0.39269908169899997);
INSERT INTO targets VALUES (9, 9, 1, '873,53B', 0.86620690776499998, 0.1308996939);
INSERT INTO targets VALUES (10, 10, 1, '686,1224', 0.022863813201100001, 4.9741883681800001);
INSERT INTO targets VALUES (11, 11, 1, '412B,3789', 0.63529984772600001, 3.4033920413900001);
INSERT INTO targets VALUES (12, 12, 1, '4360,65A/B', -0.29775317038999999, 0.26179938779900003);
INSERT INTO targets VALUES (13, 13, 1, '278C,1116A/B', 0.450644012865, 2.35619449019);
INSERT INTO targets VALUES (14, 14, 1, '102,109', 0.44017203735299998, 0.78539816339699997);
INSERT INTO targets VALUES (15, 15, 1, '234A/B,285', 0.0064577182323800001, 1.96349540849);
INSERT INTO targets VALUES (16, 16, 1, '896A,3146', 0.29251718263400001, 0.39269908169899997);
INSERT INTO targets VALUES (17, 18, 1, '* (5)', 0.72134457984900002, 0.26179938779900003);
INSERT INTO targets VALUES (18, 19, 1, 'V404Cyg', 0.59114301764999999, 5.8904862254800001);
INSERT INTO targets VALUES (21, 22, 1, 'UXArietis * (4)', 0.56932640200100004, 1.83259571459);
INSERT INTO targets VALUES (22, 23, 1, 'UXArietis * (4)', 0.56932640200100004, 1.83259571459);
INSERT INTO targets VALUES (23, 24, 1, 'UXArietis * (4)', 0.56932640200100004, 1.83259571459);
INSERT INTO targets VALUES (24, 25, 1, 'UXArietis * (4)', 0.56932640200100004, 1.83259571459);
INSERT INTO targets VALUES (25, 26, 1, '2252-090', -0.15236724369900001, 6.0004419683599997);
INSERT INTO targets VALUES (26, 27, 1, '2252-090', -0.15236724369900001, 6.0004419683599997);
INSERT INTO targets VALUES (27, 28, 1, 'G34.3,S68N,DR21OH', 0.0223402144255, 4.8432886742800001);
INSERT INTO targets VALUES (28, 29, 1, 'PKS B0237-233/confirm', -0.40404372183699999, 0.69900436542400002);
INSERT INTO targets VALUES (29, 30, 1, 'PKS1830-21', -0.36756634046999997, 4.8589966375499998);
INSERT INTO targets VALUES (30, 31, 1, '', -0.49514990879100002, 4.6574111089499999);
INSERT INTO targets VALUES (31, 32, 1, '', -0.49514990879100002, 4.6574111089499999);
INSERT INTO targets VALUES (32, 33, 1, '', -0.49514990879100002, 4.6574111089499999);
INSERT INTO targets VALUES (33, 34, 1, '3C273', 0.035779249665900001, 3.2698743536100001);
INSERT INTO targets VALUES (34, 35, 1, '3C279', -0.10105456369, 3.3876840781199999);
INSERT INTO targets VALUES (37, 38, 1, 'Oph A', -0.42586033748699997, 4.3039819354200004);
INSERT INTO targets VALUES (38, 39, 1, 'J0414+0534-host', 0.097389372261299997, 1.1100294042700001);
INSERT INTO targets VALUES (39, 40, 1, '* (9)', 0.057770398240999998, 4.21235214969);
INSERT INTO targets VALUES (40, 41, 1, 'NGC7538 IRS1', 1.0728538912000001, 6.0815997785700002);
INSERT INTO targets VALUES (41, 42, 1, 'TXS0213-026 * (4)', 0.319395253115, 2.1336650105600001);
INSERT INTO targets VALUES (42, 43, 1, '', 0.61383229792600003, 0.21467549799499999);
INSERT INTO targets VALUES (43, 44, 1, 'B0031-07 * (4)', 0.35063664672599998, 0.61261056744999998);
INSERT INTO targets VALUES (44, 45, 1, 'B0809+74 * (4)', 0.334579617607, 2.2881266493600001);
INSERT INTO targets VALUES (45, 46, 1, 'B1237+25,B1702-19,B1919+21', 0.16091935703400001, 4.2856559782700003);
INSERT INTO targets VALUES (46, 47, 1, 'B1929+10 * (4)', 0.28937558998099999, 5.47946118664);
INSERT INTO targets VALUES (51, 52, 1, 'EC2-SouthPeak', 1.0192722831600001, 0.73565627971600001);
INSERT INTO targets VALUES (52, 53, 1, 'PSR J0737-3039', -0.53511794866100004, 1.99752932891);
INSERT INTO targets VALUES (53, 54, 1, 'PSR J0737-3039', -0.53511794866100004, 1.99752932891);
INSERT INTO targets VALUES (54, 55, 1, '', 0.66130525358100001, 5.3852134070300002);
INSERT INTO targets VALUES (55, 56, 1, 'C-1', 0, 0);
INSERT INTO targets VALUES (56, 57, 1, 'SMMJ123707.21D,SMMJ123600.10B', 1.08454759719, 3.3012902801499999);
INSERT INTO targets VALUES (57, 58, 1, 'SMMJ123622.65O,SMMJ123712.05B', 1.0862929264400001, 3.3012902801499999);
INSERT INTO targets VALUES (58, 59, 1, 'XTE J1810-197', -0.344353461418, 4.7542768824300001);
INSERT INTO targets VALUES (61, 62, 1, 'vega', 0.67683868392299995, 4.8747046008200003);
INSERT INTO targets VALUES (62, 63, 1, 'Monitor 180dy', 0.17453292519899999, 3.1415926535900001);
INSERT INTO targets VALUES (63, 64, 1, 'SDSS galaxies', 0.17453292519899999, 3.4033920413900001);
INSERT INTO targets VALUES (64, 65, 1, 'SDSS galaxies', 0.17453292519899999, 3.4033920413900001);
INSERT INTO targets VALUES (65, 66, 1, 'Monitor galaxies', 0.17453292519899999, 3.1415926535900001);
INSERT INTO targets VALUES (66, 67, 1, 'NGC6517,M22', -0.156381500979, 4.7202429620200004);
INSERT INTO targets VALUES (67, 68, 1, 'NGC6517,M22', -0.156381500979, 4.7202429620200004);
INSERT INTO targets VALUES (68, 69, 1, 'IR16293', -0.42725660088799999, 4.2961279537800001);
INSERT INTO targets VALUES (69, 70, 1, 'PKS0458-02', 0.24888395133399999, 2.4268803248999999);
INSERT INTO targets VALUES (70, 71, 1, '3C286', 0.24888395133399999, 2.4268803248999999);
INSERT INTO targets VALUES (71, 72, 1, 'Cloverleaf,CRSSJ1415.1+1140', 0.20071286397900001, 3.73325927002);
INSERT INTO targets VALUES (72, 73, 1, 'SMMJ12360+6210 * (2)', 1.08542026182, 3.3012902801499999);
INSERT INTO targets VALUES (73, 74, 1, 'MMJ154127+6615,MMJ154127+6616', 1.1564551623699999, 4.1076323945700004);
INSERT INTO targets VALUES (74, 75, 1, 'SMMJ16363+4055 * (3)', 0.71541046039199996, 4.3484878313399999);
INSERT INTO targets VALUES (75, 76, 1, 'Ter5', -0.43249258864399998, 4.6600291028200003);
INSERT INTO targets VALUES (76, 77, 1, 'NGC6440,NGC6441,M28', -0.47874381382199999, 4.71762496814);
INSERT INTO targets VALUES (77, 78, 1, 'Cynus A', 0.71087260433699995, 5.2333697620999997);
INSERT INTO targets VALUES (78, 79, 1, '* (10)', 0.061610122595400003, 4.9715703743099997);
INSERT INTO targets VALUES (79, 80, 1, '* (8)', -0.482059939401, 4.6888270354800001);
INSERT INTO targets VALUES (80, 81, 1, 'J0839+2002', 0.34976398209999998, 2.2645647044600001);
INSERT INTO targets VALUES (81, 82, 1, 'J0852+2431', 0.42795473258900002, 2.3247785636599998);
INSERT INTO targets VALUES (82, 83, 1, 'J1223+5037', 0.88366020028500003, 3.2463124087100002);
INSERT INTO targets VALUES (83, 84, 1, '* (5)', 0.13962634016, 5.0789081232999997);
INSERT INTO targets VALUES (84, 85, 1, '* (6)', 0.29094638630699998, 4.2332961007099996);
INSERT INTO targets VALUES (85, 86, 1, '* (5)', 1.0866419922899999, 3.3039082740299999);
INSERT INTO targets VALUES (86, 87, 1, '* (5)', 1.0866419922899999, 3.3039082740299999);
INSERT INTO targets VALUES (87, 88, 1, '* (5)', 1.0866419922899999, 3.3039082740299999);
INSERT INTO targets VALUES (88, 89, 1, '* (5)', 1.0866419922899999, 3.3039082740299999);
INSERT INTO targets VALUES (89, 90, 1, '* (6)', 0.37524578917899998, 1.2068951777500001);
INSERT INTO targets VALUES (90, 91, 1, 'PKS1055-301', -0.53092915845699995, 2.8719392841600002);
INSERT INTO targets VALUES (91, 92, 1, 'CTQ247 0405-443', -0.77091193060600005, 1.07861347773);
INSERT INTO targets VALUES (92, 93, 1, 'PKS1230-101', -0.18186330805799999, 3.2855823168799998);
INSERT INTO targets VALUES (93, 94, 1, 'TXS1157+014', 0.020943951023899999, 3.1415926535900001);
INSERT INTO targets VALUES (94, 95, 1, 'PKSB0347-211', -0.367391807545, 1.00269165527);
INSERT INTO targets VALUES (95, 96, 1, 'TXS1452+502', 0.87371182354800003, 3.9008108782100002);
INSERT INTO targets VALUES (96, 97, 1, 'TXS1755+578', 1.0089748405800001, 4.69406302324);
INSERT INTO targets VALUES (97, 98, 1, 'TXS1850+402', 0.70371675440399994, 4.9427724416499998);
INSERT INTO targets VALUES (98, 99, 1, 'QSO1215+333', 0.57752944948499996, 3.2175144760499998);
INSERT INTO targets VALUES (99, 100, 1, 'TXS0620+389', 0.67980574365199997, 1.6781340757900001);
INSERT INTO targets VALUES (100, 101, 1, 'RS30', 0.013962634016, 0.28797932657899999);
INSERT INTO targets VALUES (101, 102, 1, 'RS38', 0.0083775804095700002, 0.39531707557700002);
INSERT INTO targets VALUES (102, 103, 1, 'RS56', -0.0078539816339699992, 0.604756585816);
INSERT INTO targets VALUES (103, 104, 1, 'RS59', -0.012217304764, 0.72256631032600005);
INSERT INTO targets VALUES (104, 105, 1, 'RS62', 0.018849555921499998, 0.80372412054300002);
INSERT INTO targets VALUES (105, 106, 1, 'RS63', -0.015707963267899999, 0.80634211442100001);
INSERT INTO targets VALUES (106, 107, 1, 'RS65', 0.0202458193231, 0.83775804095700002);
INSERT INTO targets VALUES (107, 108, 1, 'RS67', 0.0069813170079800002, 0.908443875663);
INSERT INTO targets VALUES (108, 109, 1, 'M22/added to 8C49', -0.417133691227, 4.87208660694);
INSERT INTO targets VALUES (109, 110, 1, 'A2218arc z=2.52 * (3)', 1.0194468160900001, 3.2620203719799998);
INSERT INTO targets VALUES (110, 111, 1, 'A2218arc z=2.52 * (3)', 1.0194468160900001, 3.2620203719799998);
INSERT INTO targets VALUES (111, 112, 1, 'CanesIa,CanesIb', 0.66863563643900004, 3.29605429239);
INSERT INTO targets VALUES (112, 113, 1, 'N45', -0.40578905108899999, 0.054977871437800002);
INSERT INTO targets VALUES (113, 114, 1, 'N672a,N672b', 0.52656583532699996, 0.48432886742800002);
INSERT INTO targets VALUES (114, 115, 1, 'M81', 1.2054989143499999, 2.59966792085);
INSERT INTO targets VALUES (115, 116, 1, 'B2 1030+39', 0.69115038379000004, 2.7646015351600002);
INSERT INTO targets VALUES (116, 117, 1, '4C+24.19 * (3)', 0.77492618788500001, 2.8509953331300002);
INSERT INTO targets VALUES (117, 118, 1, 'PKS 0001-11 * (3)', 0.049043751981, 1.5550883635299999);
INSERT INTO targets VALUES (118, 119, 1, 'PKS 0001-11 * (3)', 0.049043751981, 1.5550883635299999);
INSERT INTO targets VALUES (119, 120, 1, 'New Pulsars - unknown', -0.26179938779900003, 2.09439510239);
INSERT INTO targets VALUES (120, 121, 1, 'New Pulsars - unknown', -0.26179938779900003, 2.09439510239);
INSERT INTO targets VALUES (121, 122, 1, 'J1837-069', -0.12007865253699999, 4.8747046008200003);
INSERT INTO targets VALUES (122, 123, 1, 'LRO', 0, 0);
INSERT INTO targets VALUES (123, 124, 1, 'PSRJ1012+5307', 0.92711889865899999, 2.6729717494299998);
INSERT INTO targets VALUES (124, 125, 1, 'PSRJ2124-3358,PSRJ2322+2057', -0.113620934305, 5.8616882928200003);
INSERT INTO targets VALUES (125, 126, 1, 'All Sky Drift Scans', 0, 3.1415926535900001);
INSERT INTO targets VALUES (126, 127, 1, 'All Sky Drift Scans', 0, 3.1415926535900001);
INSERT INTO targets VALUES (127, 128, 1, 'All Sky Drift Scans', 0, 3.1415926535900001);
INSERT INTO targets VALUES (128, 129, 1, 'Galactic Plane,Orion', 0.039968039870700002, 0.71994831644799995);
INSERT INTO targets VALUES (129, 130, 1, 'followup', 0, 0);
INSERT INTO targets VALUES (130, 131, 1, 'Galactic Plane,Orion', 0.039968039870700002, 0.71994831644799995);
INSERT INTO targets VALUES (131, 132, 1, 'C2007W1Boattini', -0.061261056745, 1.03672557568);
INSERT INTO targets VALUES (132, 133, 1, '* (15)', 0.19390607989700001, 3.3955380597499998);
INSERT INTO targets VALUES (133, 134, 1, 'DR21,L1157,L1228', 1.0937978422200001, 5.4323372968300001);
INSERT INTO targets VALUES (134, 135, 1, 'NGC7027,DR21', 0.73792520774299997, 5.4663712172499999);
INSERT INTO targets VALUES (135, 136, 1, 'B335,L1689S', -0.15201817784900001, 4.7333329314099997);
INSERT INTO targets VALUES (136, 137, 1, 'J0348+04', 0.0794124809657, 0.99745566751500003);
INSERT INTO targets VALUES (137, 138, 1, 'NGC 7027,DR 21', 0.73792520774299997, 5.4663712172499999);
INSERT INTO targets VALUES (138, 139, 1, '3C147', 0.87004663211900002, 1.49487450433);
INSERT INTO targets VALUES (139, 140, 1, 'Pulsar', 0, 0.1308996939);
INSERT INTO targets VALUES (140, 141, 1, 'Galaxies', 0, 0.1308996939);
INSERT INTO targets VALUES (141, 142, 1, 'Continuum Source', 0, 0.1308996939);
INSERT INTO targets VALUES (142, 143, 1, 'Milky Way (non-GC)', 0, 0.1308996939);
INSERT INTO targets VALUES (143, 144, 1, '* (10)', -0.49305551368799999, 4.6547931150700004);
INSERT INTO targets VALUES (144, 145, 1, 'HII 01,HII 02,HII 03,HII 04', -0.118856922061, 4.87208660694);
INSERT INTO targets VALUES (145, 146, 1, 'PSR J1723-28', -0.50021136362200003, 4.5526913538300002);
INSERT INTO targets VALUES (146, 147, 1, 'PSR J1723-28', -0.50021136362200003, 4.5526913538300002);
INSERT INTO targets VALUES (147, 148, 1, 'PSR J1723-28', -0.50021136362200003, 4.5526913538300002);
INSERT INTO targets VALUES (148, 149, 1, 'PSR B0834+06', 0.107686814848, 2.2567107228299998);
INSERT INTO targets VALUES (149, 150, 1, 'PSR B1133+16', 0.27663468644099998, 3.03425490459);
INSERT INTO targets VALUES (150, 151, 1, 'B2 1030+39', 0.69115038379000004, 2.7646015351600002);
INSERT INTO targets VALUES (151, 152, 1, '* (7)', 0.31363566658300002, 2.6651177678);
INSERT INTO targets VALUES (152, 153, 1, 'PKS 0001-11 * (3)', 0.049043751981, 1.5550883635299999);
INSERT INTO targets VALUES (153, 154, 1, '* (7)', 0.31363566658300002, 2.6651177678);
INSERT INTO targets VALUES (154, 155, 1, '* (5)', 0.0303687289847, 2.1572269554600001);
INSERT INTO targets VALUES (155, 156, 1, '* (5)', 0.0303687289847, 2.1572269554600001);
INSERT INTO targets VALUES (156, 157, 1, '* (7)', 0.069289571304200007, 4.9898963314499998);
INSERT INTO targets VALUES (157, 158, 1, 'PSR J1841-0457,PSR J1841-0457', -0.086568330898899995, 4.8930305579700004);
INSERT INTO targets VALUES (158, 159, 1, '* (5)', 0.131772358526, 5.0265482457399999);
INSERT INTO targets VALUES (159, 160, 1, 'PSR J1818-1502 * (3)', -0.2624975195, 4.7935467905999998);
INSERT INTO targets VALUES (160, 161, 1, 'M31R001 * (4)', 0.71855205304600001, 0.19111355309299999);
INSERT INTO targets VALUES (161, 162, 1, 'grB2(M),SgrB2(S),G34.3+0.2,W51', -0.178896248329, 4.8354346926499998);
INSERT INTO targets VALUES (162, 163, 1, 'IRS16293-2422', -0.42725660088799999, 4.3301618741999999);
INSERT INTO targets VALUES (163, 164, 1, 'OrionKL,Bar,TMC-1CP,NH3,L1448C', 0.24940755010999999, 1.25663706144);
INSERT INTO targets VALUES (164, 165, 1, '* (6)', 0.42010075095499999, 3.3274702189299998);
INSERT INTO targets VALUES (165, 166, 1, '* (6)', 0.19931660057799999, 2.2148228207799998);
INSERT INTO targets VALUES (166, 167, 1, 'A1367,N45,NGC6251,HB13', 0.68294733630500004, 3.2489304025900001);
INSERT INTO targets VALUES (167, 168, 1, '* (6)', 0.19931660057799999, 2.2148228207799998);
INSERT INTO targets VALUES (168, 169, 1, 'PSSJ2322', 0.344527994344, 6.1182516928700004);
INSERT INTO targets VALUES (169, 170, 1, 'APM08279', 0.92066118042699996, 2.2331487779299999);
INSERT INTO targets VALUES (170, 171, 1, '* (9)', 0.237888377047, 3.8772489333100002);
INSERT INTO targets VALUES (171, 172, 1, 'MC-0.02,MC-0.11,MC+0.693', -0.50823987818100003, 4.65217512119);
INSERT INTO targets VALUES (172, 173, 1, 'MC-0.02,MC-0.11,MC+0.693', -0.50823987818100003, 4.65217512119);
INSERT INTO targets VALUES (173, 174, 1, 'NGC2997', -0.54436819369699996, 2.55516202492);
INSERT INTO targets VALUES (174, 175, 1, 'NGC 6946', 1.04981554507, 5.3878314009099997);
INSERT INTO targets VALUES (175, 176, 1, 'Arches cluster', -0.50300389042500004, 4.6495571273099996);
INSERT INTO targets VALUES (176, 177, 1, 'Quintuplet cluster', -0.50317842334999996, 4.65217512119);
INSERT INTO targets VALUES (177, 178, 1, 'Arches cluster', -0.50300389042500004, 4.6495571273099996);
INSERT INTO targets VALUES (178, 179, 1, 'Quintuplet cluster', -0.50317842334999996, 4.65217512119);
INSERT INTO targets VALUES (179, 180, 1, 'J1746-2850I * (3)', -0.50492375260199995, 4.6495571273099996);
INSERT INTO targets VALUES (180, 181, 1, 'J1746-2850I,J1746-2850I', -0.50352748920000001, 4.65217512119);
INSERT INTO targets VALUES (181, 182, 1, 'J1746-2850I,J1746-2850I', -0.50352748920000001, 4.65217512119);
INSERT INTO targets VALUES (182, 183, 1, 'J1746-2850I * (3)', -0.50352748920000001, 4.65217512119);
INSERT INTO targets VALUES (183, 184, 1, 'Strip 1,Strip 2,Strip 3', 0.55606189968499997, 0.97127572873500001);
INSERT INTO targets VALUES (184, 185, 1, 'Strip 1,Strip 2,Strip 3', 0.55606189968499997, 0.97127572873500001);
INSERT INTO targets VALUES (185, 186, 1, 'G1.9+0.3', 0.47420595776699997, 4.6626470966999998);
INSERT INTO targets VALUES (186, 187, 1, 'S209,W3', 0.98837995540400003, 0.86655597361500003);
INSERT INTO targets VALUES (187, 188, 1, 'LEO0056,AUG0103', -0.38728856101800002, 4.6835910477300002);
INSERT INTO targets VALUES (188, 189, 1, 'AUG0140,AUG0096,AUG0028', 0.40753438034099998, 3.86677695779);
INSERT INTO targets VALUES (189, 190, 1, '* (27)', 0.040491638646300003, 4.8301987048899999);
INSERT INTO targets VALUES (190, 191, 1, '* (27)', 0.040491638646300003, 4.8301987048899999);
INSERT INTO targets VALUES (191, 192, 1, '* (6)', -0.547335253425, 4.5945792558800003);
INSERT INTO targets VALUES (192, 193, 1, 'B1642-03 * (4)', 0.36582101121799998, 3.8929568965699999);
INSERT INTO targets VALUES (193, 194, 1, '* (5)', -0.18535396656200001, 4.7673668518200003);
INSERT INTO targets VALUES (194, 195, 1, '* (5)', -0.18535396656200001, 4.7673668518200003);
INSERT INTO targets VALUES (195, 196, 1, '* (5)', -0.39479347680100002, 4.6731190722099996);
INSERT INTO targets VALUES (196, 197, 1, '* (5)', -0.39479347680100002, 4.6731190722099996);
INSERT INTO targets VALUES (197, 198, 1, 'PSR B1929+10', 0.19181168479399999, 5.1155600375999999);
INSERT INTO targets VALUES (198, 199, 1, 'PSR J0737-3039', -0.53511794866100004, 1.99752932891);
INSERT INTO targets VALUES (199, 200, 1, 'PSR J0737-3039', -0.53511794866100004, 1.99752932891);
INSERT INTO targets VALUES (200, 201, 1, 'PSR J0737-3039', -0.53511794866100004, 1.99752932891);
INSERT INTO targets VALUES (201, 202, 1, 'PSR J0737-3039', -0.53511794866100004, 1.99752932891);
INSERT INTO targets VALUES (202, 203, 1, '* (8)', 0.70738194583299996, 3.7254052883800002);
INSERT INTO targets VALUES (203, 204, 1, '* (11)', -0.034732052114699999, 4.5605453354599996);
INSERT INTO targets VALUES (204, 205, 1, '* (11)', -0.034732052114699999, 4.5605453354599996);
INSERT INTO targets VALUES (206, 207, 1, '* (10)', -0.071383966406599997, 4.0578905108900001);
INSERT INTO targets VALUES (207, 208, 1, 'FIRST J102347.67+003841', 0.0111701072128, 2.7227136331100001);
INSERT INTO targets VALUES (208, 209, 1, 'NGC2403,NGC2366', 1.17652644877, 1.97658537788);
INSERT INTO targets VALUES (209, 210, 1, 'UGC4305,UGC4483,K52,DDO53', 1.2117820996599999, 2.2200588085400002);
INSERT INTO targets VALUES (210, 211, 1, 'PKS B1228-113', -0.203330857857, 3.27772833525);
INSERT INTO targets VALUES (211, 212, 1, '* (6)', 0.50230575872399996, 3.1703905862499999);
INSERT INTO targets VALUES (212, 213, 1, '* (6)', 0.50230575872399996, 3.1703905862499999);
INSERT INTO targets VALUES (213, 214, 1, '* (7)', -0.18832102629, 4.3353978619499998);
INSERT INTO targets VALUES (214, 215, 1, 'B0218+357', 0.62727133316700001, 0.61522856132799997);
INSERT INTO targets VALUES (215, 216, 1, 'B0218+357', 0.62727133316700001, 0.61522856132799997);
INSERT INTO targets VALUES (216, 217, 1, 'HB1413+115', 0.20071286397900001, 3.73325927002);
INSERT INTO targets VALUES (217, 218, 1, 'F10214+4724', 0.82292274231499996, 2.7253316269900001);
INSERT INTO targets VALUES (218, 219, 1, '* (15)', -0.070860367630999996, 3.9819686884299998);
INSERT INTO targets VALUES (219, 220, 1, '* (15)', -0.070860367630999996, 3.9819686884299998);
INSERT INTO targets VALUES (220, 221, 1, '* (11)', 0.020943951023899999, 3.93222680474);
INSERT INTO targets VALUES (221, 222, 1, '* (11)', 1.0679669693, 2.6101398963600002);
INSERT INTO targets VALUES (222, 223, 1, 'HETE J1900.1-2455', -0.434936049597, 4.9741883681800001);
INSERT INTO targets VALUES (223, 224, 1, 'V822 Cen', -0.55274577410699999, 3.9191368353499998);
INSERT INTO targets VALUES (224, 225, 1, 'IK Peg', 0.33824480903699999, 5.6129788744100004);
INSERT INTO targets VALUES (225, 226, 1, 'HD 49798', -0.77352992448400004, 1.78023583703);
INSERT INTO targets VALUES (226, 227, 1, 'SAX J1808.4-3658', -0.64542275738800003, 4.7490408946800002);
INSERT INTO targets VALUES (227, 228, 1, 'IGR J00291+5934', 1.03969263541, 0.12566370614399999);
INSERT INTO targets VALUES (228, 229, 1, 'SAX J1748.9-2021', -0.35534903570600002, 4.6626470966999998);
INSERT INTO targets VALUES (229, 230, 1, 'XTE J1814-338', -0.589397688398, 4.7726028395800002);
INSERT INTO targets VALUES (230, 231, 1, 'XTE J0929-314', -0.54785885220099995, 2.4844761902100001);
INSERT INTO targets VALUES (231, 232, 1, 'XTE J1807-294', -0.51330133301199998, 4.7438049069200003);
INSERT INTO targets VALUES (232, 233, 1, 'SWIFT J1756.9-2508', -0.43825217517600001, 4.6992990109899999);
INSERT INTO targets VALUES (233, 234, 1, 'XTE J1751-305', -0.53441981696100005, 4.6731190722099996);
INSERT INTO targets VALUES (234, 235, 1, 'IGR J17191-2821', -0.49480084293999999, 4.5343653966800002);
INSERT INTO targets VALUES (235, 236, 1, 'V1341 Cyg', 0.66881016936399995, 5.6915186907499997);
INSERT INTO targets VALUES (236, 237, 1, 'V651 Mon', -0.0141371669412, 1.8744836166400001);
INSERT INTO targets VALUES (237, 238, 1, 'HD 189733', 0.39636427312799999, 5.2386057498599996);
INSERT INTO targets VALUES (238, 239, 1, 'NGC5897', -0.36669367584399998, 4.0029126394499999);
INSERT INTO targets VALUES (239, 240, 1, 'NGC 5986', -0.65955992432900001, 4.12857634559);
INSERT INTO targets VALUES (240, 241, 1, 'M 92', 0.75293503931000005, 4.5265114150499999);
INSERT INTO targets VALUES (241, 242, 1, 'HP 1', -0.523249709748, 4.58672527424);
INSERT INTO targets VALUES (242, 243, 1, 'Djorg 1', -0.57718038363500002, 4.6574111089499999);
INSERT INTO targets VALUES (243, 244, 1, 'Terzan 9', -0.46844637123499999, 4.7202429620200004);
INSERT INTO targets VALUES (244, 245, 1, 'Pal 6', -0.45762532987299998, 4.6417031456800002);
INSERT INTO targets VALUES (245, 246, 1, 'NGC 3079,Mrk 348', 0.76480327822399996, 1.41895268187);
INSERT INTO targets VALUES (246, 247, 1, 'NGC 3079,Mrk 348', 0.76480327822399996, 1.41895268187);
INSERT INTO targets VALUES (247, 248, 1, 'Mercury', 0, 0);
INSERT INTO targets VALUES (248, 249, 1, 'Mercury', 0, 0);
INSERT INTO targets VALUES (249, 250, 1, 'Venus', 0, 0);
INSERT INTO targets VALUES (250, 251, 1, 'Venus', 0, 0);
INSERT INTO targets VALUES (251, 252, 1, 'Venus', 0, 0);
INSERT INTO targets VALUES (252, 253, 1, 'Venus', 0, 0);
INSERT INTO targets VALUES (253, 254, 1, 'Cyg X-1,GRS1915+105,Cyg X-3', 0.40264745843499999, 5.13388599474);
INSERT INTO targets VALUES (2, 2, 1, '2066,3522', 0.085346600422500002, 2.35619449019);
INSERT INTO targets VALUES (3, 3, 1, '803,4247', -0.026529004630300002, 5.3668874498800001);
INSERT INTO targets VALUES (4, 4, 1, '661A/B,1224', 0.25918139392099998, 4.7123889803800001);
INSERT INTO targets VALUES (60, 61, 1, 'PSR J1833-1034', -0.18448130193599999, 4.8589966375499998);
INSERT INTO targets VALUES (59, 60, 1, '* (5)', 0.79325214503100006, 4.2175881374399999);
INSERT INTO targets VALUES (36, 37, 1, '* (12)', -0.030194196059500002, 4.0735984741499998);
INSERT INTO targets VALUES (35, 36, 1, '* (12)', -0.030194196059500002, 4.0735984741499998);
INSERT INTO targets VALUES (19, 20, 1, 'GOODS850-16', 1.0847221301100001, 3.8615409700400001);
INSERT INTO targets VALUES (48, 49, 1, 'Moon', 0, 0);
INSERT INTO targets VALUES (1, 1, 1, '644C,1207', -0.111177473352, 4.5814892864900001);
INSERT INTO targets VALUES (20, 21, 1, 'V773TauA on6/17or8/7or9/27', 0.49218284906199999, 0.52359877559800005);
INSERT INTO targets VALUES (49, 50, 1, 'Moon', 0, 0);
INSERT INTO targets VALUES (50, 51, 1, 'Moon', 0, 0);
INSERT INTO targets VALUES (205, 206, 1, '* (10)', -0.071383966406599997, 4.0578905108900001);
INSERT INTO targets VALUES (47, 48, 1, 'Moon', 0, 0);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO users VALUES (1, 227, NULL, NULL, false, 'Frank', 'Ghigo');
INSERT INTO users VALUES (2, 3292, NULL, NULL, false, 'Jim', 'Braatz');
INSERT INTO users VALUES (3, 1373, NULL, NULL, false, 'Jules', 'Harnett');
INSERT INTO users VALUES (4, 4810, NULL, NULL, false, 'Carl', 'Bignell');
INSERT INTO users VALUES (5, 2669, NULL, NULL, false, 'Dana', 'Balser');
INSERT INTO users VALUES (6, 2927, NULL, NULL, false, 'Toney', 'Minter');
INSERT INTO users VALUES (7, 1339, NULL, NULL, false, 'Ron', 'Maddalena');
INSERT INTO users VALUES (8, 4789, NULL, NULL, false, 'Scott', 'Ransom');
INSERT INTO users VALUES (9, 4305, NULL, NULL, false, 'Karen', 'O''Neil');
INSERT INTO users VALUES (10, 6150, NULL, NULL, false, 'Paul', 'Ruffle');
INSERT INTO users VALUES (11, 4644, NULL, NULL, false, 'Brian', 'Mason');
INSERT INTO users VALUES (12, 846, NULL, NULL, false, 'Jay', 'Lockman');
INSERT INTO users VALUES (13, 915, NULL, NULL, false, 'Glen', 'Langston');
INSERT INTO users VALUES (14, 5605, NULL, NULL, false, 'Rachel', 'Rosen');
INSERT INTO users VALUES (15, 1744, NULL, NULL, false, 'Jeff', 'Mangum');
INSERT INTO users VALUES (16, 5293, NULL, NULL, false, 'Tony', 'Remijan');
INSERT INTO users VALUES (17, 6526, NULL, NULL, false, 'Daniel', 'Perera');
INSERT INTO users VALUES (18, 3919, NULL, NULL, false, 'D.J.', 'Pisano');
INSERT INTO users VALUES (19, 3628, NULL, NULL, false, 'Geoff', 'Bower');
INSERT INTO users VALUES (20, 4871, NULL, NULL, false, 'Alberto', 'Bolatto');
INSERT INTO users VALUES (21, 3403, NULL, NULL, false, 'Eric', 'Ford');
INSERT INTO users VALUES (22, 5714, NULL, NULL, false, 'Paul', 'Kalas');
INSERT INTO users VALUES (23, 832, NULL, NULL, false, 'Jim', 'Condon');
INSERT INTO users VALUES (24, 1503, NULL, NULL, false, 'Lincoln', 'Greenhill');
INSERT INTO users VALUES (25, 278, NULL, NULL, false, 'Chris', 'Henkel');
INSERT INTO users VALUES (26, 4852, NULL, NULL, false, 'Fred', 'Lo');
INSERT INTO users VALUES (27, 516, NULL, NULL, false, 'Mark', 'Reid');
INSERT INTO users VALUES (28, 5379, NULL, NULL, false, 'Cheng-Yu', 'Kuo');
INSERT INTO users VALUES (29, 6240, NULL, NULL, false, 'Ingyin', 'Zaw');
INSERT INTO users VALUES (30, 5064, NULL, NULL, false, 'Avanti', 'Tilak');
INSERT INTO users VALUES (31, 5902, NULL, NULL, false, 'Lei', 'Hao');
INSERT INTO users VALUES (32, 6406, NULL, NULL, false, 'Philip', 'Lah');
INSERT INTO users VALUES (33, 4516, NULL, NULL, false, 'Andreas', 'Brunthaler');
INSERT INTO users VALUES (34, 2563, NULL, NULL, false, 'Lorant', 'Sjouwerman');
INSERT INTO users VALUES (35, 2069, NULL, NULL, false, 'Mike', 'Garrett');
INSERT INTO users VALUES (36, 4963, NULL, NULL, false, 'Laurent', 'Loinard');
INSERT INTO users VALUES (37, 5403, NULL, NULL, false, 'James', 'Miller-Jones');
INSERT INTO users VALUES (38, 1522, NULL, NULL, false, 'Michael', 'Rupen');
INSERT INTO users VALUES (39, 3662, NULL, NULL, false, 'Amy', 'Mioduszewski');
INSERT INTO users VALUES (40, 903, NULL, NULL, false, 'Vivek', 'Dhawan');
INSERT INTO users VALUES (41, 5295, NULL, NULL, false, 'Elena', 'Gallo');
INSERT INTO users VALUES (42, 5081, NULL, NULL, false, 'Peter', 'Jonker');
INSERT INTO users VALUES (43, 4056, NULL, NULL, false, 'Walter', 'Brisken');
INSERT INTO users VALUES (44, 4596, NULL, NULL, false, 'Emmanuel', 'Momjian');
INSERT INTO users VALUES (45, 5920, NULL, NULL, false, 'Wei-Hao', 'Wang');
INSERT INTO users VALUES (46, 1226, NULL, NULL, false, 'Chris', 'Carilli');
INSERT INTO users VALUES (47, 5460, NULL, NULL, false, 'Rosa', 'Torres');
INSERT INTO users VALUES (48, 6189, NULL, NULL, false, 'William', 'Peterson');
INSERT INTO users VALUES (49, 451, NULL, NULL, false, 'Bob', 'Mutel');
INSERT INTO users VALUES (50, 838, NULL, NULL, false, 'Miller', 'Goss');
INSERT INTO users VALUES (51, 4847, NULL, NULL, false, 'Steve', 'Curran');
INSERT INTO users VALUES (52, 4974, NULL, NULL, false, 'Matthew', 'Whiting');
INSERT INTO users VALUES (53, 2839, NULL, NULL, false, 'John', 'Webb');
INSERT INTO users VALUES (54, 4849, NULL, NULL, false, 'Michael', 'Murphy');
INSERT INTO users VALUES (55, 4905, NULL, NULL, false, 'Ylva', 'Pihlstrom');
INSERT INTO users VALUES (56, 1392, NULL, NULL, false, 'Tommy', 'Wiklind');
INSERT INTO users VALUES (57, 4975, NULL, NULL, false, 'Paul', 'Francis');
INSERT INTO users VALUES (58, 862, NULL, NULL, false, 'Al', 'Wootten');
INSERT INTO users VALUES (59, 4801, NULL, NULL, false, 'Nissim', 'Kanekar');
INSERT INTO users VALUES (60, 4824, NULL, NULL, false, 'Sara', 'Ellison');
INSERT INTO users VALUES (61, 4338, NULL, NULL, false, 'Jason', 'Prochaska');
INSERT INTO users VALUES (62, 5633, NULL, NULL, false, 'Brian', 'York');
INSERT INTO users VALUES (63, 4884, NULL, NULL, false, 'Yancy', 'Shirley');
INSERT INTO users VALUES (64, 298, NULL, NULL, false, 'Mike', 'Hollis');
INSERT INTO users VALUES (65, 953, NULL, NULL, false, 'Phil', 'Jewell');
INSERT INTO users VALUES (66, 398, NULL, NULL, false, 'Frank', 'Lovas');
INSERT INTO users VALUES (67, 1620, NULL, NULL, false, 'Joel', 'Bregman');
INSERT INTO users VALUES (68, 4558, NULL, NULL, false, 'Jimmy', 'Irwin');
INSERT INTO users VALUES (69, 5002, NULL, NULL, false, 'Paul', 'Demorest');
INSERT INTO users VALUES (70, 4799, NULL, NULL, false, 'Bryan', 'Jacoby');
INSERT INTO users VALUES (71, 4996, NULL, NULL, false, 'Robert', 'Ferdman');
INSERT INTO users VALUES (72, 23, NULL, NULL, false, 'Don', 'Backer');
INSERT INTO users VALUES (73, 4796, NULL, NULL, false, 'Ingrid', 'Stairs');
INSERT INTO users VALUES (74, 2314, NULL, NULL, false, 'David', 'Nice');
INSERT INTO users VALUES (75, 4800, NULL, NULL, false, 'Andrea', 'Lommen');
INSERT INTO users VALUES (76, 3616, NULL, NULL, false, 'Matthew', 'Bailes');
INSERT INTO users VALUES (77, 4833, NULL, NULL, false, 'Ismael', 'Cognard');
INSERT INTO users VALUES (78, 3782, NULL, NULL, false, 'Tyler', 'Bourke');
INSERT INTO users VALUES (79, 5072, NULL, NULL, false, 'Paola', 'Caselli');
INSERT INTO users VALUES (80, 5630, NULL, NULL, false, 'Rachel', 'Friesen');
INSERT INTO users VALUES (81, 3701, NULL, NULL, false, 'James', 'Di Francesco');
INSERT INTO users VALUES (82, 452, NULL, NULL, false, 'Phil', 'Myers');
INSERT INTO users VALUES (83, 4772, NULL, NULL, false, 'Jeremy', 'Darling');
INSERT INTO users VALUES (84, 6212, NULL, NULL, false, 'Stanislav', 'Edel');
INSERT INTO users VALUES (85, 6213, NULL, NULL, false, 'Dominic', 'Ludovici');
INSERT INTO users VALUES (86, 4226, NULL, NULL, false, 'Dunc', 'Lorimer');
INSERT INTO users VALUES (87, 4142, NULL, NULL, false, 'Maura', 'McLaughlin');
INSERT INTO users VALUES (88, 5561, NULL, NULL, false, 'Vlad', 'Kondratiev');
INSERT INTO users VALUES (89, 6214, NULL, NULL, false, 'Joshua', 'Ridley');
INSERT INTO users VALUES (90, 4820, NULL, NULL, false, 'Esteban', 'Araya');
INSERT INTO users VALUES (91, 2360, NULL, NULL, false, 'Peter', 'Hofner');
INSERT INTO users VALUES (92, 5061, NULL, NULL, false, 'Ian', 'Hoffman');
INSERT INTO users VALUES (93, 5117, NULL, NULL, false, 'Hendrik', 'Linz');
INSERT INTO users VALUES (94, 2309, NULL, NULL, false, 'Stan', 'Kurtz');
INSERT INTO users VALUES (95, 6225, NULL, NULL, false, 'Viswesh', 'Marthi');
INSERT INTO users VALUES (96, 6229, NULL, NULL, false, 'Yogesh', 'Maan');
INSERT INTO users VALUES (97, 4197, NULL, NULL, false, 'Avinash', 'Deshpande');
INSERT INTO users VALUES (98, 3542, NULL, NULL, false, 'Bruce', 'Campbell');
INSERT INTO users VALUES (99, 91, NULL, NULL, false, 'Don', 'Campbell');
INSERT INTO users VALUES (100, 4790, NULL, NULL, false, 'Lynn', 'Carter');
INSERT INTO users VALUES (101, 5618, NULL, NULL, false, 'Rebecca', 'Ghent');
INSERT INTO users VALUES (102, 4816, NULL, NULL, false, 'Mike', 'Nolan');
INSERT INTO users VALUES (103, 6242, NULL, NULL, false, 'Naoto', 'Kobayashi');
INSERT INTO users VALUES (104, 4032, NULL, NULL, false, 'Tom', 'Millar');
INSERT INTO users VALUES (105, 3344, NULL, NULL, false, 'Masao', 'Saito');
INSERT INTO users VALUES (106, 6243, NULL, NULL, false, 'Chikako', 'Yasui');
INSERT INTO users VALUES (107, 4227, NULL, NULL, false, 'Michael', 'Kramer');
INSERT INTO users VALUES (108, 2923, NULL, NULL, false, 'Fernando', 'Camilo');
INSERT INTO users VALUES (109, 403, NULL, NULL, false, 'Andrew', 'Lyne');
INSERT INTO users VALUES (110, 411, NULL, NULL, false, 'Dick', 'Manchester');
INSERT INTO users VALUES (111, 4999, NULL, NULL, false, 'Andrea', 'Possenti');
INSERT INTO users VALUES (112, 129, NULL, NULL, false, 'Nichi', 'D''Amico');
INSERT INTO users VALUES (113, 5286, NULL, NULL, false, 'Marta', 'Burgay');
INSERT INTO users VALUES (114, 5282, NULL, NULL, false, 'Paulo', 'Freire');
INSERT INTO users VALUES (115, 1534, NULL, NULL, false, 'Brian', 'Dennison');
INSERT INTO users VALUES (116, 6248, NULL, NULL, false, 'Leigha', 'Dickens');
INSERT INTO users VALUES (117, 2072, NULL, NULL, false, 'Bryan', 'Butler');
INSERT INTO users VALUES (118, 6434, NULL, NULL, false, 'Ben', 'Bussey');
INSERT INTO users VALUES (119, 4137, NULL, NULL, false, 'Ian', 'Smail');
INSERT INTO users VALUES (120, 226, NULL, NULL, false, 'Reinhardt', 'Genzel');
INSERT INTO users VALUES (121, 2749, NULL, NULL, false, 'Rob', 'Ivison');
INSERT INTO users VALUES (122, 5387, NULL, NULL, false, 'Laura', 'Hainline');
INSERT INTO users VALUES (123, 4893, NULL, NULL, false, 'Andrew', 'Blain');
INSERT INTO users VALUES (124, 995, NULL, NULL, false, 'Linda', 'Tacconi');
INSERT INTO users VALUES (125, 1940, NULL, NULL, false, 'Frank', 'Bertoldi');
INSERT INTO users VALUES (126, 4873, NULL, NULL, false, 'Thomas', 'Greve');
INSERT INTO users VALUES (127, 5430, NULL, NULL, false, 'Roberto', 'Neri');
INSERT INTO users VALUES (128, 4894, NULL, NULL, false, 'Scott', 'Chapman');
INSERT INTO users VALUES (129, 4342, NULL, NULL, false, 'Andy', 'Harris');
INSERT INTO users VALUES (130, 3887, NULL, NULL, false, 'Andrew', 'Baker');
INSERT INTO users VALUES (131, 4828, NULL, NULL, false, 'Pierre', 'Cox');
INSERT INTO users VALUES (132, 1696, NULL, NULL, false, 'Alain', 'Omont');
INSERT INTO users VALUES (133, 1007, NULL, NULL, false, 'Jules', 'Halpern');
INSERT INTO users VALUES (134, 2434, NULL, NULL, false, 'John', 'Reynolds');
INSERT INTO users VALUES (135, 4570, NULL, NULL, false, 'Mallory', 'Roberts');
INSERT INTO users VALUES (136, 2939, NULL, NULL, false, 'Zaven', 'Arzoumanian');
INSERT INTO users VALUES (137, 1875, NULL, NULL, false, 'Roger', 'Romani');
INSERT INTO users VALUES (138, 3756, NULL, NULL, false, 'Paul', 'Ray');
INSERT INTO users VALUES (139, 2036, NULL, NULL, false, 'David', 'Wilner');
INSERT INTO users VALUES (140, 6182, NULL, NULL, false, 'Antonio', 'Hales');
INSERT INTO users VALUES (141, 5971, NULL, NULL, false, 'Ryan', 'Lynch');
INSERT INTO users VALUES (142, 1684, NULL, NULL, false, 'Cecilia', 'Ceccarelli');
INSERT INTO users VALUES (143, 6366, NULL, NULL, false, 'Susana', 'Pacheco');
INSERT INTO users VALUES (144, 6420, NULL, NULL, false, 'Emmanuel', 'Caux');
INSERT INTO users VALUES (145, 2720, NULL, NULL, false, 'Jose', 'Cernicharo');
INSERT INTO users VALUES (146, 710, NULL, NULL, false, 'Art', 'Wolfe');
INSERT INTO users VALUES (147, 5599, NULL, NULL, false, 'Regina', 'Jorgenson');
INSERT INTO users VALUES (148, 4805, NULL, NULL, false, 'Tim', 'Robishaw');
INSERT INTO users VALUES (149, 274, NULL, NULL, false, 'Carl', 'Heiles');
INSERT INTO users VALUES (150, 5900, NULL, NULL, false, 'Stephanie', 'Zonak');
INSERT INTO users VALUES (151, 6424, NULL, NULL, false, 'Chelsea', 'Sharon');
INSERT INTO users VALUES (152, 655, NULL, NULL, false, 'Paul', 'VandenBout');
INSERT INTO users VALUES (153, 4856, NULL, NULL, false, 'Jason', 'Hessels');
INSERT INTO users VALUES (154, 834, NULL, NULL, false, 'Bill', 'Cotton');
INSERT INTO users VALUES (155, 4827, NULL, NULL, false, 'Simon', 'Dicker');
INSERT INTO users VALUES (156, 6217, NULL, NULL, false, 'Phil', 'Korngut');
INSERT INTO users VALUES (157, 4842, NULL, NULL, false, 'Mark', 'Devlin');
INSERT INTO users VALUES (158, 6169, NULL, NULL, false, 'Loren', 'Anderson');
INSERT INTO users VALUES (159, 33, NULL, NULL, false, 'Tom', 'Bania');
INSERT INTO users VALUES (160, 962, NULL, NULL, false, 'Bob', 'Rood');
INSERT INTO users VALUES (161, 5875, NULL, NULL, false, 'Neeraj', 'Gupta');
INSERT INTO users VALUES (162, 4189, NULL, NULL, false, 'Raghunathan', 'Srianand');
INSERT INTO users VALUES (163, 3918, NULL, NULL, false, 'Patrick', 'Petitjean');
INSERT INTO users VALUES (164, 5967, NULL, NULL, false, 'Pasquier', 'Noterdaeme');
INSERT INTO users VALUES (165, 83, NULL, NULL, false, 'Butler', 'Burton');
INSERT INTO users VALUES (166, 6013, NULL, NULL, false, 'Emanuele', 'Daddi');
INSERT INTO users VALUES (167, 4925, NULL, NULL, false, 'Jeff', 'Wagg');
INSERT INTO users VALUES (168, 6429, NULL, NULL, false, 'Manuel', 'Aravena');
INSERT INTO users VALUES (169, 3079, NULL, NULL, false, 'Fabian', 'Walter');
INSERT INTO users VALUES (170, 5559, NULL, NULL, false, 'Dominik', 'Riechers');
INSERT INTO users VALUES (171, 6438, NULL, NULL, false, 'Helmut', 'Dannerbauer');
INSERT INTO users VALUES (172, 2512, NULL, NULL, false, 'Mark', 'Dickinson');
INSERT INTO users VALUES (173, 6439, NULL, NULL, false, 'David', 'Elbaz');
INSERT INTO users VALUES (174, 4418, NULL, NULL, false, 'Daniel', 'Stern');
INSERT INTO users VALUES (175, 3282, NULL, NULL, false, 'Glenn', 'Morrison');
INSERT INTO users VALUES (176, 6441, NULL, NULL, false, 'Lucie', 'Vincent');
INSERT INTO users VALUES (177, 6442, NULL, NULL, false, 'Nicole', 'Feautrier');
INSERT INTO users VALUES (178, 5397, NULL, NULL, false, 'Pierre', 'Valiron');
INSERT INTO users VALUES (179, 5396, NULL, NULL, false, 'Alexandre', 'Faure');
INSERT INTO users VALUES (180, 6443, NULL, NULL, false, 'Annie', 'Spielfiedel');
INSERT INTO users VALUES (181, 6444, NULL, NULL, false, 'Maria Luisa', 'Senent');
INSERT INTO users VALUES (182, 6445, NULL, NULL, false, 'Fabien', 'Daniel');
INSERT INTO users VALUES (183, 6447, NULL, NULL, false, 'Macarena', 'Garcia-Marin');
INSERT INTO users VALUES (184, 1304, NULL, NULL, false, 'Andreas', 'Eckart');
INSERT INTO users VALUES (185, 6199, NULL, NULL, false, 'Sabine', 'Koenig');
INSERT INTO users VALUES (186, 6201, NULL, NULL, false, 'Sebastian', 'Fischer');
INSERT INTO users VALUES (187, 6448, NULL, NULL, false, 'Jens', 'Zuther');
INSERT INTO users VALUES (188, 1036, NULL, NULL, false, 'Walter', 'Huchtmeier');
INSERT INTO users VALUES (189, 6200, NULL, NULL, false, 'Thomas', 'Bertram');
INSERT INTO users VALUES (190, 5928, NULL, NULL, false, 'Mark', 'Swinbank');
INSERT INTO users VALUES (191, 6151, NULL, NULL, false, 'Kristen', 'Coppin');
INSERT INTO users VALUES (192, 3129, NULL, NULL, false, 'Alastair', 'Edge');
INSERT INTO users VALUES (193, 4538, NULL, NULL, false, 'Richard', 'Ellis');
INSERT INTO users VALUES (194, 6118, NULL, NULL, false, 'Dan', 'Stark');
INSERT INTO users VALUES (195, 6411, NULL, NULL, false, 'Tucker', 'Jones');
INSERT INTO users VALUES (196, 4139, NULL, NULL, false, 'Jean-Paul', 'Kneib');
INSERT INTO users VALUES (197, 4565, NULL, NULL, false, 'Harold', 'Ebeling');
INSERT INTO users VALUES (198, 6251, NULL, NULL, false, 'Katie', 'Chynoweth');
INSERT INTO users VALUES (199, 6252, NULL, NULL, false, 'Kelly', 'Holley-Bockelmann');
INSERT INTO users VALUES (200, 612, NULL, NULL, false, 'John', 'Stocke');
INSERT INTO users VALUES (201, 6465, NULL, NULL, false, 'Ting', 'Yan');
INSERT INTO users VALUES (202, 5572, NULL, NULL, false, 'Sue Ann', 'Heatherly');
INSERT INTO users VALUES (203, 3903, NULL, NULL, false, 'Eric', 'Gotthelf');
INSERT INTO users VALUES (204, 3936, NULL, NULL, false, 'Vicky', 'Kaspi');
INSERT INTO users VALUES (205, 1533, NULL, NULL, false, 'Jim', 'Cordes');
INSERT INTO users VALUES (206, 5283, NULL, NULL, false, 'David', 'Champion');
INSERT INTO users VALUES (207, 6236, NULL, NULL, false, 'Anne', 'Archibald');
INSERT INTO users VALUES (208, 5936, NULL, NULL, false, 'Jason', 'Boyles');
INSERT INTO users VALUES (209, 6253, NULL, NULL, false, 'Christie', 'McPhee');
INSERT INTO users VALUES (210, 5593, NULL, NULL, false, 'Laura', 'Kasian');
INSERT INTO users VALUES (211, 5350, NULL, NULL, false, 'Joeri', 'van Leeuwen');
INSERT INTO users VALUES (212, 5348, NULL, NULL, false, 'Julia', 'Deneva');
INSERT INTO users VALUES (213, 3663, NULL, NULL, false, 'Fronefield', 'Crawford');
INSERT INTO users VALUES (214, 4998, NULL, NULL, false, 'Andrew', 'Faulkner');
INSERT INTO users VALUES (215, 6488, NULL, NULL, false, 'Claire', 'Gilpin');
INSERT INTO users VALUES (216, 1568, NULL, NULL, false, 'Carl', 'Gwinn');
INSERT INTO users VALUES (217, 6490, NULL, NULL, false, 'Michael', 'Johnson');
INSERT INTO users VALUES (218, 6489, NULL, NULL, false, 'Tatiana', 'Smirnova');
INSERT INTO users VALUES (219, 4147, NULL, NULL, false, 'Shami', 'Chatterjee');
INSERT INTO users VALUES (220, 6491, NULL, NULL, false, 'Eduardo', 'Rubio-Herrera');
INSERT INTO users VALUES (221, 3802, NULL, NULL, false, 'Ben', 'Stappers');
INSERT INTO users VALUES (222, 432, NULL, NULL, false, 'David', 'Meier');
INSERT INTO users VALUES (223, 5576, NULL, NULL, false, 'Wilmer', 'Stork');
INSERT INTO users VALUES (224, 6492, NULL, NULL, false, 'David', 'Whelan');
INSERT INTO users VALUES (225, 6459, NULL, NULL, false, 'George', 'Privon');
INSERT INTO users VALUES (226, 6493, NULL, NULL, false, 'Lisa', 'Walker');
INSERT INTO users VALUES (227, 4665, NULL, NULL, false, 'Kelsey', 'Johnson');
INSERT INTO users VALUES (228, 4936, NULL, NULL, false, 'Amanda', 'Kepley');
INSERT INTO users VALUES (229, 536, NULL, NULL, false, 'Larry', 'Rudnick');
INSERT INTO users VALUES (230, 6436, NULL, NULL, false, 'Damon', 'Farnsworth');
INSERT INTO users VALUES (231, 5933, NULL, NULL, false, 'Shea', 'Brown');
INSERT INTO users VALUES (232, 3946, NULL, NULL, false, 'Karl', 'Menten');
INSERT INTO users VALUES (233, 5003, NULL, NULL, false, 'Liz', 'Humphreys');
INSERT INTO users VALUES (234, 6454, NULL, NULL, false, 'Jairo', 'Armijos');
INSERT INTO users VALUES (235, 1958, NULL, NULL, false, 'Jesus', 'Martin-Pintado');
INSERT INTO users VALUES (236, 5614, NULL, NULL, false, 'Miguel Angel', 'Requena-Torres');
INSERT INTO users VALUES (237, 6453, NULL, NULL, false, 'Sergio', 'exception');
INSERT INTO users VALUES (238, 5054, NULL, NULL, false, 'Arturo', 'Rodriguez-Franco');
INSERT INTO users VALUES (239, 1426, NULL, NULL, false, 'Joe', 'Lazio');
INSERT INTO users VALUES (240, 6494, NULL, NULL, false, 'Christopher', 'Tibbs');
INSERT INTO users VALUES (241, 5893, NULL, NULL, false, 'Clive', 'Dickinson');
INSERT INTO users VALUES (242, 132, NULL, NULL, false, 'Rod', 'Davies');
INSERT INTO users VALUES (243, 6495, NULL, NULL, false, 'Robert', 'Watson');
INSERT INTO users VALUES (244, 3161, NULL, NULL, false, 'Richard', 'Davis');
INSERT INTO users VALUES (245, 5895, NULL, NULL, false, 'Roberta', 'Paladini');
INSERT INTO users VALUES (246, 5894, NULL, NULL, false, 'Simon', 'Casassus');
INSERT INTO users VALUES (247, 5897, NULL, NULL, false, 'Kieran', 'Cleary');
INSERT INTO users VALUES (248, 6425, NULL, NULL, false, 'Natsuko', 'Kudo');
INSERT INTO users VALUES (249, 6427, NULL, NULL, false, 'Kazufumi', 'Torii');
INSERT INTO users VALUES (250, 211, NULL, NULL, false, 'Yasuo', 'Fukui');
INSERT INTO users VALUES (251, 446, NULL, NULL, false, 'Mark', 'Morris');
INSERT INTO users VALUES (252, 3931, NULL, NULL, false, 'M.A.', 'Walker');
INSERT INTO users VALUES (253, 5284, NULL, NULL, false, 'Willem', 'van Straten');
INSERT INTO users VALUES (254, 5399, NULL, NULL, false, 'Aris', 'Karasteregiou');
INSERT INTO users VALUES (255, 6249, NULL, NULL, false, 'Joshua', 'Miller');
INSERT INTO users VALUES (256, 6516, NULL, NULL, false, 'Evan', 'Keane');
INSERT INTO users VALUES (257, 6499, NULL, NULL, false, 'Benetge', 'Perera');
INSERT INTO users VALUES (258, 5180, NULL, NULL, false, 'John', 'Cannon');
INSERT INTO users VALUES (259, 4052, NULL, NULL, false, 'Jessica', 'Rosenberg');
INSERT INTO users VALUES (260, 3148, NULL, NULL, false, 'John', 'Salzer');
INSERT INTO users VALUES (261, 3941, NULL, NULL, false, 'Yu', 'Gao');
INSERT INTO users VALUES (262, 2196, NULL, NULL, false, 'Jayaram', 'Chengalur');
INSERT INTO users VALUES (263, 5981, NULL, NULL, false, 'Ben', 'Zeiger');
INSERT INTO users VALUES (264, 6501, NULL, NULL, false, 'Marjorie', 'Gonzalez');
INSERT INTO users VALUES (265, 1227, NULL, NULL, false, 'Gilles', 'Joncas');
INSERT INTO users VALUES (266, 6502, NULL, NULL, false, 'Jean-Francois', 'Robitaille');
INSERT INTO users VALUES (267, 6503, NULL, NULL, false, 'Douglas', 'Marshall');
INSERT INTO users VALUES (268, 5001, NULL, NULL, false, 'Marc-Antoine', 'Miville-Deschenes');
INSERT INTO users VALUES (269, 4647, NULL, NULL, false, 'Peter', 'Martin');
INSERT INTO users VALUES (270, 6504, NULL, NULL, false, 'Megan', 'DeCesar');
INSERT INTO users VALUES (271, 6519, NULL, NULL, false, 'Cole', 'Miller');
INSERT INTO users VALUES (272, 6460, NULL, NULL, false, 'Alexis', 'Smith');
INSERT INTO users VALUES (273, 5608, NULL, NULL, false, 'Jane', 'Greaves');
INSERT INTO users VALUES (274, 5530, NULL, NULL, false, 'Moira', 'Jardine');
INSERT INTO users VALUES (275, 5937, NULL, NULL, false, 'Andrew', 'Cameron');
INSERT INTO users VALUES (276, 5258, NULL, NULL, false, 'Violette', 'Impellizzeri');
INSERT INTO users VALUES (277, 1963, NULL, NULL, false, 'Alan', 'Roy');
INSERT INTO users VALUES (278, 5184, NULL, NULL, false, 'Silvia', 'Leurini');
INSERT INTO users VALUES (279, 3541, NULL, NULL, false, 'Jean-Luc', 'Margot');
INSERT INTO users VALUES (280, 589, NULL, NULL, false, 'Martin', 'Slade');
INSERT INTO users VALUES (281, 5225, NULL, NULL, false, 'John', 'Tomsick');
INSERT INTO users VALUES (282, 5167, NULL, NULL, false, 'Stephane', 'Corbel');
INSERT INTO users VALUES (283, 5163, NULL, NULL, false, 'Simone', 'Migliari');
INSERT INTO users VALUES (284, 6238, NULL, NULL, false, 'Katja', 'Pottschmidt');
INSERT INTO users VALUES (285, 6239, NULL, NULL, false, 'Joern', 'Wilms');
INSERT INTO users VALUES (286, 5249, NULL, NULL, false, 'Jerome', 'Rodriguez');
INSERT INTO users VALUES (287, 494, NULL, NULL, false, 'Guy', 'Pooley');


--
-- Data for Name: windows; Type: TABLE DATA; Schema: public; Owner: dss
--

INSERT INTO windows VALUES (1, 17, true);
INSERT INTO windows VALUES (2, 18, true);
INSERT INTO windows VALUES (3, 20, true);
INSERT INTO windows VALUES (5, 22, true);
INSERT INTO windows VALUES (6, 23, true);
INSERT INTO windows VALUES (7, 24, true);
INSERT INTO windows VALUES (8, 25, true);
INSERT INTO windows VALUES (9, 48, true);
INSERT INTO windows VALUES (10, 49, true);
INSERT INTO windows VALUES (11, 50, true);
INSERT INTO windows VALUES (12, 51, true);
INSERT INTO windows VALUES (13, 248, true);
INSERT INTO windows VALUES (14, 249, true);
INSERT INTO windows VALUES (16, 251, true);
INSERT INTO windows VALUES (17, 252, true);
INSERT INTO windows VALUES (18, 253, true);
INSERT INTO windows VALUES (29, 36, true);
INSERT INTO windows VALUES (30, 36, true);
INSERT INTO windows VALUES (32, 61, true);
INSERT INTO windows VALUES (33, 61, true);
INSERT INTO windows VALUES (34, 61, true);
INSERT INTO windows VALUES (38, 60, true);
INSERT INTO windows VALUES (39, 60, true);
INSERT INTO windows VALUES (40, 60, true);
INSERT INTO windows VALUES (41, 60, true);
INSERT INTO windows VALUES (42, 60, true);
INSERT INTO windows VALUES (43, 60, true);
INSERT INTO windows VALUES (51, 4, true);
INSERT INTO windows VALUES (52, 4, true);
INSERT INTO windows VALUES (53, 4, true);
INSERT INTO windows VALUES (54, 4, true);
INSERT INTO windows VALUES (55, 4, true);
INSERT INTO windows VALUES (56, 4, true);
INSERT INTO windows VALUES (57, 4, true);
INSERT INTO windows VALUES (58, 21, true);
INSERT INTO windows VALUES (31, 61, false);
INSERT INTO windows VALUES (61, 37, false);
INSERT INTO windows VALUES (59, 37, false);
INSERT INTO windows VALUES (60, 37, false);
INSERT INTO windows VALUES (35, 60, false);
INSERT INTO windows VALUES (37, 60, false);
INSERT INTO windows VALUES (76, 206, true);
INSERT INTO windows VALUES (77, 206, true);
INSERT INTO windows VALUES (78, 206, true);
INSERT INTO windows VALUES (79, 206, true);
INSERT INTO windows VALUES (80, 206, true);
INSERT INTO windows VALUES (81, 206, true);
INSERT INTO windows VALUES (82, 206, true);
INSERT INTO windows VALUES (15, 250, false);
INSERT INTO windows VALUES (28, 36, false);
INSERT INTO windows VALUES (36, 60, false);
INSERT INTO windows VALUES (83, 49, false);


--
-- Name: allotment_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY allotment
    ADD CONSTRAINT allotment_pkey PRIMARY KEY (id);


--
-- Name: auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions_group_id_key; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_key UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_message_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY auth_message
    ADD CONSTRAINT auth_message_pkey PRIMARY KEY (id);


--
-- Name: auth_permission_content_type_id_key; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_key UNIQUE (content_type_id, codename);


--
-- Name: auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups_user_id_key; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_key UNIQUE (user_id, group_id);


--
-- Name: auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions_user_id_key; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_key UNIQUE (user_id, permission_id);


--
-- Name: auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- Name: cadences_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY cadences
    ADD CONSTRAINT cadences_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type_app_label_key; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_app_label_key UNIQUE (app_label, model);


--
-- Name: django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: django_site_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY django_site
    ADD CONSTRAINT django_site_pkey PRIMARY KEY (id);


--
-- Name: investigators_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY investigators
    ADD CONSTRAINT investigators_pkey PRIMARY KEY (id);


--
-- Name: observing_parameters_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY observing_parameters
    ADD CONSTRAINT observing_parameters_pkey PRIMARY KEY (id);


--
-- Name: observing_parameters_session_id_key; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY observing_parameters
    ADD CONSTRAINT observing_parameters_session_id_key UNIQUE (session_id, parameter_id);


--
-- Name: observing_types_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY observing_types
    ADD CONSTRAINT observing_types_pkey PRIMARY KEY (id);


--
-- Name: opportunities_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY opportunities
    ADD CONSTRAINT opportunities_pkey PRIMARY KEY (id);


--
-- Name: parameters_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY parameters
    ADD CONSTRAINT parameters_pkey PRIMARY KEY (id);


--
-- Name: project_types_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY project_types
    ADD CONSTRAINT project_types_pkey PRIMARY KEY (id);


--
-- Name: projects_allotments_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY projects_allotments
    ADD CONSTRAINT projects_allotments_pkey PRIMARY KEY (id);


--
-- Name: projects_allotments_project_id_key; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY projects_allotments
    ADD CONSTRAINT projects_allotments_project_id_key UNIQUE (project_id, allotment_id);


--
-- Name: projects_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: receiver_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY receiver_groups
    ADD CONSTRAINT receiver_groups_pkey PRIMARY KEY (id);


--
-- Name: receiver_groups_receivers_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY receiver_groups_receivers
    ADD CONSTRAINT receiver_groups_receivers_pkey PRIMARY KEY (id);


--
-- Name: receiver_groups_receivers_receiver_group_id_key; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY receiver_groups_receivers
    ADD CONSTRAINT receiver_groups_receivers_receiver_group_id_key UNIQUE (receiver_group_id, receiver_id);


--
-- Name: receiver_schedule_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY receiver_schedule
    ADD CONSTRAINT receiver_schedule_pkey PRIMARY KEY (id);


--
-- Name: receivers_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY receivers
    ADD CONSTRAINT receivers_pkey PRIMARY KEY (id);


--
-- Name: semesters_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY semesters
    ADD CONSTRAINT semesters_pkey PRIMARY KEY (id);


--
-- Name: sesshuns_email_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY sesshuns_email
    ADD CONSTRAINT sesshuns_email_pkey PRIMARY KEY (id);


--
-- Name: session_types_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY session_types
    ADD CONSTRAINT session_types_pkey PRIMARY KEY (id);


--
-- Name: sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);


--
-- Name: status_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY status
    ADD CONSTRAINT status_pkey PRIMARY KEY (id);


--
-- Name: systems_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY systems
    ADD CONSTRAINT systems_pkey PRIMARY KEY (id);


--
-- Name: targets_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY targets
    ADD CONSTRAINT targets_pkey PRIMARY KEY (id);


--
-- Name: users_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: windows_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY windows
    ADD CONSTRAINT windows_pkey PRIMARY KEY (id);


--
-- Name: auth_message_user_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX auth_message_user_id ON auth_message USING btree (user_id);


--
-- Name: auth_permission_content_type_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX auth_permission_content_type_id ON auth_permission USING btree (content_type_id);


--
-- Name: cadences_session_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX cadences_session_id ON cadences USING btree (session_id);


--
-- Name: django_admin_log_content_type_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX django_admin_log_content_type_id ON django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX django_admin_log_user_id ON django_admin_log USING btree (user_id);


--
-- Name: investigators_project_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX investigators_project_id ON investigators USING btree (project_id);


--
-- Name: investigators_user_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX investigators_user_id ON investigators USING btree (user_id);


--
-- Name: observing_parameters_parameter_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX observing_parameters_parameter_id ON observing_parameters USING btree (parameter_id);


--
-- Name: observing_parameters_session_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX observing_parameters_session_id ON observing_parameters USING btree (session_id);


--
-- Name: opportunities_window_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX opportunities_window_id ON opportunities USING btree (window_id);


--
-- Name: projects_project_type_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX projects_project_type_id ON projects USING btree (project_type_id);


--
-- Name: projects_semester_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX projects_semester_id ON projects USING btree (semester_id);


--
-- Name: receiver_groups_session_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX receiver_groups_session_id ON receiver_groups USING btree (session_id);


--
-- Name: receiver_schedule_receiver_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX receiver_schedule_receiver_id ON receiver_schedule USING btree (receiver_id);


--
-- Name: sesshuns_email_user_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX sesshuns_email_user_id ON sesshuns_email USING btree (user_id);


--
-- Name: sessions_allotment_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX sessions_allotment_id ON sessions USING btree (allotment_id);


--
-- Name: sessions_observing_type_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX sessions_observing_type_id ON sessions USING btree (observing_type_id);


--
-- Name: sessions_project_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX sessions_project_id ON sessions USING btree (project_id);


--
-- Name: sessions_session_type_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX sessions_session_type_id ON sessions USING btree (session_type_id);


--
-- Name: sessions_status_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX sessions_status_id ON sessions USING btree (status_id);


--
-- Name: targets_session_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX targets_session_id ON targets USING btree (session_id);


--
-- Name: targets_system_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX targets_system_id ON targets USING btree (system_id);


--
-- Name: windows_session_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX windows_session_id ON windows USING btree (session_id);


--
-- Name: auth_group_permissions_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_message_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY auth_message
    ADD CONSTRAINT auth_message_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: cadences_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY cadences
    ADD CONSTRAINT cadences_session_id_fkey FOREIGN KEY (session_id) REFERENCES sessions(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: content_type_id_refs_id_288599e6; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT content_type_id_refs_id_288599e6 FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: content_type_id_refs_id_728de91f; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT content_type_id_refs_id_728de91f FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: investigators_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY investigators
    ADD CONSTRAINT investigators_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: investigators_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY investigators
    ADD CONSTRAINT investigators_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: observing_parameters_parameter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY observing_parameters
    ADD CONSTRAINT observing_parameters_parameter_id_fkey FOREIGN KEY (parameter_id) REFERENCES parameters(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: observing_parameters_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY observing_parameters
    ADD CONSTRAINT observing_parameters_session_id_fkey FOREIGN KEY (session_id) REFERENCES sessions(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: opportunities_window_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY opportunities
    ADD CONSTRAINT opportunities_window_id_fkey FOREIGN KEY (window_id) REFERENCES windows(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: projects_allotments_allotment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY projects_allotments
    ADD CONSTRAINT projects_allotments_allotment_id_fkey FOREIGN KEY (allotment_id) REFERENCES allotment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: projects_allotments_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY projects_allotments
    ADD CONSTRAINT projects_allotments_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: projects_project_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_project_type_id_fkey FOREIGN KEY (project_type_id) REFERENCES project_types(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: projects_semester_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_semester_id_fkey FOREIGN KEY (semester_id) REFERENCES semesters(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: receiver_groups_receivers_receiver_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY receiver_groups_receivers
    ADD CONSTRAINT receiver_groups_receivers_receiver_group_id_fkey FOREIGN KEY (receiver_group_id) REFERENCES receiver_groups(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: receiver_groups_receivers_receiver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY receiver_groups_receivers
    ADD CONSTRAINT receiver_groups_receivers_receiver_id_fkey FOREIGN KEY (receiver_id) REFERENCES receivers(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: receiver_groups_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY receiver_groups
    ADD CONSTRAINT receiver_groups_session_id_fkey FOREIGN KEY (session_id) REFERENCES sessions(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: receiver_schedule_receiver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY receiver_schedule
    ADD CONSTRAINT receiver_schedule_receiver_id_fkey FOREIGN KEY (receiver_id) REFERENCES receivers(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: sesshuns_email_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY sesshuns_email
    ADD CONSTRAINT sesshuns_email_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: sessions_allotment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY sessions
    ADD CONSTRAINT sessions_allotment_id_fkey FOREIGN KEY (allotment_id) REFERENCES allotment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: sessions_observing_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY sessions
    ADD CONSTRAINT sessions_observing_type_id_fkey FOREIGN KEY (observing_type_id) REFERENCES observing_types(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: sessions_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY sessions
    ADD CONSTRAINT sessions_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: sessions_session_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY sessions
    ADD CONSTRAINT sessions_session_type_id_fkey FOREIGN KEY (session_type_id) REFERENCES session_types(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: sessions_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY sessions
    ADD CONSTRAINT sessions_status_id_fkey FOREIGN KEY (status_id) REFERENCES status(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: targets_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY targets
    ADD CONSTRAINT targets_session_id_fkey FOREIGN KEY (session_id) REFERENCES sessions(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: targets_system_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY targets
    ADD CONSTRAINT targets_system_id_fkey FOREIGN KEY (system_id) REFERENCES systems(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: user_id_refs_id_c8665aa; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT user_id_refs_id_c8665aa FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: windows_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY windows
    ADD CONSTRAINT windows_session_id_fkey FOREIGN KEY (session_id) REFERENCES sessions(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: public; Type: ACL; Schema: -; Owner: dss
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM dss;
GRANT ALL ON SCHEMA public TO dss;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

