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
    grade double precision NOT NULL,
    ignore_grade boolean NOT NULL
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
-- Name: blackouts; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE blackouts (
    id integer NOT NULL,
    user_id integer NOT NULL,
    start timestamp with time zone,
    "end" timestamp with time zone,
    tz_id integer NOT NULL,
    repeat_id integer NOT NULL,
    until timestamp with time zone,
    description character varying(512)
);


ALTER TABLE public.blackouts OWNER TO dss;

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
    principal_investigator boolean NOT NULL,
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
    datetime_value timestamp without time zone
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
    start_time timestamp without time zone NOT NULL,
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
-- Name: periods; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE periods (
    id integer NOT NULL,
    session_id integer NOT NULL,
    start timestamp without time zone NOT NULL,
    duration double precision NOT NULL,
    score double precision,
    forecast timestamp without time zone,
    backup boolean NOT NULL
);


ALTER TABLE public.periods OWNER TO dss;

--
-- Name: project_blackouts_09b; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE project_blackouts_09b (
    id integer NOT NULL,
    project_id integer NOT NULL,
    requester_id integer NOT NULL,
    start_date timestamp without time zone,
    end_date timestamp without time zone,
    description character varying(512)
);


ALTER TABLE public.project_blackouts_09b OWNER TO dss;

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
    start_date timestamp without time zone,
    end_date timestamp without time zone
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
    start_date timestamp without time zone
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
-- Name: repeats; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE repeats (
    id integer NOT NULL,
    repeat character varying(32) NOT NULL
);


ALTER TABLE public.repeats OWNER TO dss;

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
    time_between double precision
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
    vertical double precision,
    horizontal double precision
);


ALTER TABLE public.targets OWNER TO dss;

--
-- Name: timezones; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE timezones (
    id integer NOT NULL,
    "timeZone" character varying(128) NOT NULL
);


ALTER TABLE public.timezones OWNER TO dss;

--
-- Name: users; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE users (
    id integer NOT NULL,
    original_id integer,
    pst_id integer,
    username character varying(32),
    sanctioned boolean NOT NULL,
    first_name character varying(32) NOT NULL,
    last_name character varying(150) NOT NULL,
    contact_instructions text
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

SELECT pg_catalog.setval('allotment_id_seq', 346, true);


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
    START WITH 1
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

SELECT pg_catalog.setval('auth_message_id_seq', 1, false);


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

SELECT pg_catalog.setval('auth_permission_id_seq', 102, true);


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
-- Name: blackouts_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE blackouts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.blackouts_id_seq OWNER TO dss;

--
-- Name: blackouts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE blackouts_id_seq OWNED BY blackouts.id;


--
-- Name: blackouts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('blackouts_id_seq', 1, false);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE django_admin_log_id_seq
    START WITH 1
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

SELECT pg_catalog.setval('django_admin_log_id_seq', 1, false);


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

SELECT pg_catalog.setval('django_content_type_id_seq', 34, true);


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

SELECT pg_catalog.setval('investigators_id_seq', 636, true);


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

SELECT pg_catalog.setval('observing_parameters_id_seq', 99, true);


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
    START WITH 1
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

SELECT pg_catalog.setval('opportunities_id_seq', 1, false);


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
-- Name: periods_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE periods_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.periods_id_seq OWNER TO dss;

--
-- Name: periods_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE periods_id_seq OWNED BY periods.id;


--
-- Name: periods_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('periods_id_seq', 1, false);


--
-- Name: project_blackouts_09b_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE project_blackouts_09b_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.project_blackouts_09b_id_seq OWNER TO dss;

--
-- Name: project_blackouts_09b_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE project_blackouts_09b_id_seq OWNED BY project_blackouts_09b.id;


--
-- Name: project_blackouts_09b_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('project_blackouts_09b_id_seq', 1, false);


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

SELECT pg_catalog.setval('projects_allotments_id_seq', 103, true);


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

SELECT pg_catalog.setval('projects_id_seq', 107, true);


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

SELECT pg_catalog.setval('receiver_groups_id_seq', 242, true);


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

SELECT pg_catalog.setval('receiver_groups_receivers_id_seq', 253, true);


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
-- Name: repeats_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE repeats_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.repeats_id_seq OWNER TO dss;

--
-- Name: repeats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE repeats_id_seq OWNED BY repeats.id;


--
-- Name: repeats_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('repeats_id_seq', 3, true);


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

SELECT pg_catalog.setval('sesshuns_email_id_seq', 379, true);


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

SELECT pg_catalog.setval('sessions_id_seq', 242, true);


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

SELECT pg_catalog.setval('status_id_seq', 242, true);


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

SELECT pg_catalog.setval('targets_id_seq', 240, true);


--
-- Name: timezones_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE timezones_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.timezones_id_seq OWNER TO dss;

--
-- Name: timezones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE timezones_id_seq OWNED BY timezones.id;


--
-- Name: timezones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--

SELECT pg_catalog.setval('timezones_id_seq', 24, true);


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

SELECT pg_catalog.setval('users_id_seq', 305, true);


--
-- Name: windows_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE windows_id_seq
    START WITH 1
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

SELECT pg_catalog.setval('windows_id_seq', 1, false);


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

ALTER TABLE blackouts ALTER COLUMN id SET DEFAULT nextval('blackouts_id_seq'::regclass);


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

ALTER TABLE periods ALTER COLUMN id SET DEFAULT nextval('periods_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: dss
--

ALTER TABLE project_blackouts_09b ALTER COLUMN id SET DEFAULT nextval('project_blackouts_09b_id_seq'::regclass);


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

ALTER TABLE repeats ALTER COLUMN id SET DEFAULT nextval('repeats_id_seq'::regclass);


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

ALTER TABLE timezones ALTER COLUMN id SET DEFAULT nextval('timezones_id_seq'::regclass);


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

COPY allotment (id, psc_time, total_time, max_semester_time, grade) FROM stdin;
1	100.5	100.5	100.5	4
2	768	768	768	4
3	118	118	118	4
4	16	16	16	4
5	10	10	10	4
6	6	6	6	4
7	40	40	40	4
8	16	16	16	4
9	5.5	5.5	5.5	4
10	5.4199999999999999	5.4199999999999999	5.4199999999999999	4
11	5	5	5	4
12	1.5	1.5	1.5	4
13	15	15	15	4
14	378	378	378	4
15	8.6999999999999993	8.6999999999999993	8.6999999999999993	4
16	45	45	45	4
17	6	6	6	4
18	5	5	5	4
19	12	12	12	4
20	4.5	4.5	4.5	3
21	3	3	3	4
22	6.2000000000000002	6.2000000000000002	6.2000000000000002	4
23	27	27	27	4
24	3	3	3	4
25	16	16	16	4
26	6	6	6	4
27	12	12	12	4
28	4	4	4	4
29	5	5	5	4
30	32	32	32	4
31	6	6	6	4
32	37.75	37.75	37.75	4
33	24	24	24	4
34	125	125	125	4
35	18.670000000000002	18.670000000000002	18.670000000000002	4
36	7	7	7	4
37	54.399999999999999	54.399999999999999	54.399999999999999	4
38	17	17	17	4
39	8.5	8.5	8.5	4
40	10	10	10	3
41	12	12	12	4
42	30	30	30	3
43	20	20	20	3
44	31.199999999999999	31.199999999999999	31.199999999999999	4
45	10	10	10	3
46	25.02	25.02	25.02	4
47	17.600000000000001	17.600000000000001	17.600000000000001	3
48	4	4	4	4
49	60	60	60	4
50	33	33	33	3
51	12	12	12	3
52	3.0299999999999998	3.0299999999999998	3.0299999999999998	3
53	8	8	8	4
54	21	21	21	3
55	40	40	40	4
56	8.5	8.5	8.5	4
57	7	7	7	3
58	12	12	12	4
59	6	6	6	4
60	2.5	2.5	2.5	4
61	15	15	15	4
62	20	20	20	4
63	8	8	8	3
64	5.5	5.5	5.5	3
65	6.9299999999999997	6.9299999999999997	6.9299999999999997	4
66	10.75	10.75	10.75	4
67	9	9	9	4
68	58.200000000000003	58.200000000000003	58.200000000000003	4
69	10	10	10	4
70	4.5	4.5	4.5	3
71	20	20	20	4
72	20	20	20	3
73	17	17	17	3
74	8.75	8.75	8.75	3
75	11	11	11	4
76	22	22	22	4
77	18	18	18	4
78	4	4	4	4
79	11	11	11	3
80	104.5	104.5	104.5	4
81	50.380000000000003	50.380000000000003	50.380000000000003	4
82	114.25	114.25	114.25	3
83	4	4	4	3
84	67	67	67	3
85	2	2	2	4
86	19	19	19	4
87	672	672	672	4
88	56	56	56	3
89	7	7	7	3
90	24	24	24	3
91	3.5	3.5	3.5	4
92	10.5	10.5	10.5	3
93	12	12	12	4
94	1	1	1	4
95	4	4	4	4
96	6	6	6	3
97	1.5	1.5	1.5	4
98	9	9	9	4
99	16	16	16	4
100	8	8	8	4
101	130	130	130	4
102	30	30	30	4
103	30	30	30	4
104	14	14	14	4
105	40	40	40	4
106	40	40	40	4
107	48	48	48	4
108	56	56	56	4
109	56	56	56	4
110	48	48	48	4
111	48	48	48	4
112	56	56	56	4
113	40	40	40	4
114	40	40	40	4
115	40	40	40	4
116	48	48	48	4
117	56	56	56	4
118	48	48	48	4
119	56	56	56	4
120	48	48	48	4
121	10	10	10	4
122	108	108	108	4
123	16	16	16	4
124	10	10	10	4
125	6	6	6	4
126	10	10	10	4
127	10	10	10	4
128	10	10	10	4
129	10	10	10	4
130	16	16	16	4
131	2.75	2.75	2.75	4
132	2.75	2.75	2.75	4
133	5.4199999999999999	5.4199999999999999	5.4199999999999999	4
134	5	5	5	4
135	1.5	1.5	1.5	4
136	15	15	15	4
137	84	84	84	4
138	60	60	60	4
139	42	42	42	4
140	6	6	6	4
141	12	12	12	4
142	60	60	60	4
143	78	78	78	4
144	36	36	36	4
145	8.6999999999999993	8.6999999999999993	8.6999999999999993	4
146	22.5	22.5	22.5	4
147	22.5	22.5	22.5	4
148	6	6	6	4
149	5	5	5	4
150	12	12	12	4
151	4.5	4.5	4.5	3
152	3	3	3	4
153	0.59999999999999998	0.59999999999999998	0.59999999999999998	4
154	2.3999999999999999	2.3999999999999999	2.3999999999999999	4
155	0.59999999999999998	0.59999999999999998	0.59999999999999998	4
156	0.59999999999999998	0.59999999999999998	0.59999999999999998	4
157	2	2	2	4
158	7	7	7	4
159	7	7	7	4
160	6	6	6	4
161	7	7	7	4
162	3	3	3	4
163	5	5	5	4
164	0	0	0	4
165	0	0	0	4
166	0	0	0	4
167	3.5	3.5	3.5	4
168	3.5	3.5	3.5	4
169	4	4	4	4
170	6	6	6	4
171	0	0	0	4
172	3	3	3	4
173	9	9	9	4
174	4	4	4	4
175	1	1	1	4
176	4	4	4	4
177	8	8	8	4
178	8	8	8	4
179	16	16	16	4
180	6	6	6	4
181	0	0	0	4
182	33.75	33.75	33.75	4
183	4	4	4	4
184	24	24	24	4
185	25	25	25	4
186	8	8	8	4
187	10	10	10	4
188	10	10	10	4
189	72	72	72	4
190	0	0	0	4
191	14.67	14.67	14.67	4
192	4	4	4	4
193	7	7	7	4
194	15.199999999999999	15.199999999999999	15.199999999999999	4
195	9	9	9	4
196	10.4	10.4	10.4	4
197	19.800000000000001	19.800000000000001	19.800000000000001	4
198	8	8	8	4
199	9	9	9	4
200	8.5	8.5	8.5	4
201	10	10	10	3
202	12	12	12	4
203	10	10	10	3
204	10	10	10	3
205	10	10	10	3
206	20	20	20	3
207	7.1500000000000004	7.1500000000000004	7.1500000000000004	4
208	5.2000000000000002	5.2000000000000002	5.2000000000000002	4
209	5.8499999999999996	5.8499999999999996	5.8499999999999996	4
210	13	13	13	4
211	0	0	0	4
212	5	5	5	3
213	5	5	5	3
214	1.3999999999999999	1.3999999999999999	1.3999999999999999	4
215	3.3999999999999999	3.3999999999999999	3.3999999999999999	4
216	1.3999999999999999	1.3999999999999999	1.3999999999999999	4
217	4.4199999999999999	4.4199999999999999	4.4199999999999999	4
218	6.4000000000000004	6.4000000000000004	6.4000000000000004	4
219	1.3999999999999999	1.3999999999999999	1.3999999999999999	4
220	1.3999999999999999	1.3999999999999999	1.3999999999999999	4
221	1.3999999999999999	1.3999999999999999	1.3999999999999999	4
222	1.3999999999999999	1.3999999999999999	1.3999999999999999	4
223	2.3999999999999999	2.3999999999999999	2.3999999999999999	4
224	2.2000000000000002	2.2000000000000002	2.2000000000000002	3
225	2.2000000000000002	2.2000000000000002	2.2000000000000002	3
226	2.2000000000000002	2.2000000000000002	2.2000000000000002	3
227	2.2000000000000002	2.2000000000000002	2.2000000000000002	3
228	2.2000000000000002	2.2000000000000002	2.2000000000000002	3
229	2.2000000000000002	2.2000000000000002	2.2000000000000002	3
230	2.2000000000000002	2.2000000000000002	2.2000000000000002	3
231	2.2000000000000002	2.2000000000000002	2.2000000000000002	3
232	4	4	4	4
233	40	40	40	4
234	20	20	20	4
235	0	0	0	3
236	33	33	33	3
237	0	0	0	3
238	0	0	0	3
239	12	12	12	3
240	1.73	1.73	1.73	3
241	0	0	0	3
242	1.3	1.3	1.3	3
243	0	0	0	4
244	8	8	8	4
245	10.449999999999999	10.449999999999999	10.449999999999999	3
246	10.550000000000001	10.550000000000001	10.550000000000001	3
247	10	10	10	4
248	20	20	20	4
249	10	10	10	4
250	6.5	6.5	6.5	4
251	2	2	2	4
252	3.5	3.5	3.5	3
253	3.5	3.5	3.5	3
254	0	0	0	3
255	-24	-24	-24	3
256	0	0	0	3
257	12	12	12	4
258	6	6	6	4
259	2.5	2.5	2.5	4
260	15	15	15	4
261	20	20	20	4
262	3.5	3.5	3.5	3
263	4.5	4.5	4.5	3
264	5.5	5.5	5.5	3
265	1.73	1.73	1.73	4
266	1.3	1.3	1.3	4
267	3.8999999999999999	3.8999999999999999	3.8999999999999999	4
268	8.75	8.75	8.75	4
269	2	2	2	4
270	9	9	9	4
271	0	0	0	3
272	44.799999999999997	44.799999999999997	44.799999999999997	4
273	13.4	13.4	13.4	4
274	0	0	0	3
275	10	10	10	4
276	4.5	4.5	4.5	3
277	20	20	20	4
278	20	20	20	3
279	7	7	7	3
280	7	7	7	3
281	3	3	3	3
282	0	0	0	3
283	3.5	3.5	3.5	3
284	0	0	0	3
285	5.25	5.25	5.25	3
286	4.5	4.5	4.5	4
287	6.5	6.5	6.5	4
288	9.5	9.5	9.5	4
289	12.5	12.5	12.5	4
290	18	18	18	4
291	4	4	4	4
292	5.5	5.5	5.5	3
293	5.5	5.5	5.5	3
294	8.5	8.5	8.5	4
295	33	33	33	4
296	33	33	33	4
297	15	15	15	4
298	15	15	15	4
299	25.629999999999999	25.629999999999999	25.629999999999999	4
300	24.75	24.75	24.75	4
301	54.25	54.25	54.25	3
302	60	60	60	3
303	4	4	4	3
304	13	13	13	3
305	54	54	54	3
306	2	2	2	4
307	9	9	9	4
308	10	10	10	4
309	306	306	306	4
310	306	306	306	4
311	60	60	60	4
312	56	56	56	3
313	1	1	1	3
314	1	1	1	3
315	1	1	1	3
316	1	1	1	3
317	1	1	1	3
318	1	1	1	3
319	0	0	0	3
320	0	0	0	3
321	1	1	1	3
322	0	0	0	3
323	6	6	6	3
324	6	6	6	3
325	6	6	6	3
326	6	6	6	3
327	3.5	3.5	3.5	3
328	3.5	3.5	3.5	3
329	3.5	3.5	3.5	3
330	3.5	3.5	3.5	4
331	12	12	12	4
332	1	1	1	4
333	6	6	6	3
334	4	4	4	4
335	1.5	1.5	1.5	4
336	9	9	9	4
337	2	2	2	4
338	2	2	2	4
339	4	4	4	4
340	8	8	8	4
341	8	8	8	4
342	104	104	104	4
343	26	26	26	4
344	30	30	30	4
345	30	30	30	4
346	14	14	14	4
\.


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_message; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY auth_message (id, user_id, message) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add permission	1	add_permission
2	Can change permission	1	change_permission
3	Can delete permission	1	delete_permission
4	Can add group	2	add_group
5	Can change group	2	change_group
6	Can delete group	2	delete_group
7	Can add user	3	add_user
8	Can change user	3	change_user
9	Can delete user	3	delete_user
10	Can add message	4	add_message
11	Can change message	4	change_message
12	Can delete message	4	delete_message
13	Can add content type	5	add_contenttype
14	Can change content type	5	change_contenttype
15	Can delete content type	5	delete_contenttype
16	Can add session	6	add_session
17	Can change session	6	change_session
18	Can delete session	6	delete_session
19	Can add site	7	add_site
20	Can change site	7	change_site
21	Can delete site	7	delete_site
22	Can add user	8	add_user
23	Can change user	8	change_user
24	Can delete user	8	delete_user
25	Can add email	9	add_email
26	Can change email	9	change_email
27	Can delete email	9	delete_email
28	Can add semester	10	add_semester
29	Can change semester	10	change_semester
30	Can delete semester	10	delete_semester
31	Can add project_ type	11	add_project_type
32	Can change project_ type	11	change_project_type
33	Can delete project_ type	11	delete_project_type
34	Can add allotment	12	add_allotment
35	Can change allotment	12	change_allotment
36	Can delete allotment	12	delete_allotment
37	Can add project	13	add_project
38	Can change project	13	change_project
39	Can delete project	13	delete_project
40	Can add project_ allotment	14	add_project_allotment
41	Can change project_ allotment	14	change_project_allotment
42	Can delete project_ allotment	14	delete_project_allotment
43	Can add repeat	15	add_repeat
44	Can change repeat	15	change_repeat
45	Can delete repeat	15	delete_repeat
46	Can add time zone	16	add_timezone
47	Can change time zone	16	change_timezone
48	Can delete time zone	16	delete_timezone
49	Can add blackout	17	add_blackout
50	Can change blackout	17	change_blackout
51	Can delete blackout	17	delete_blackout
52	Can add project_ blackout_09b	18	add_project_blackout_09b
53	Can change project_ blackout_09b	18	change_project_blackout_09b
54	Can delete project_ blackout_09b	18	delete_project_blackout_09b
55	Can add investigators	19	add_investigators
56	Can change investigators	19	change_investigators
57	Can delete investigators	19	delete_investigators
58	Can add session_ type	20	add_session_type
59	Can change session_ type	20	change_session_type
60	Can delete session_ type	20	delete_session_type
61	Can add observing_ type	21	add_observing_type
62	Can change observing_ type	21	change_observing_type
63	Can delete observing_ type	21	delete_observing_type
64	Can add receiver	22	add_receiver
65	Can change receiver	22	change_receiver
66	Can delete receiver	22	delete_receiver
67	Can add receiver_ schedule	23	add_receiver_schedule
68	Can change receiver_ schedule	23	change_receiver_schedule
69	Can delete receiver_ schedule	23	delete_receiver_schedule
70	Can add parameter	24	add_parameter
71	Can change parameter	24	change_parameter
72	Can delete parameter	24	delete_parameter
73	Can add status	25	add_status
74	Can change status	25	change_status
75	Can delete status	25	delete_status
76	Can add sesshun	26	add_sesshun
77	Can change sesshun	26	change_sesshun
78	Can delete sesshun	26	delete_sesshun
79	Can add receiver_ group	27	add_receiver_group
80	Can change receiver_ group	27	change_receiver_group
81	Can delete receiver_ group	27	delete_receiver_group
82	Can add observing_ parameter	28	add_observing_parameter
83	Can change observing_ parameter	28	change_observing_parameter
84	Can delete observing_ parameter	28	delete_observing_parameter
85	Can add window	29	add_window
86	Can change window	29	change_window
87	Can delete window	29	delete_window
88	Can add opportunity	30	add_opportunity
89	Can change opportunity	30	change_opportunity
90	Can delete opportunity	30	delete_opportunity
91	Can add system	31	add_system
92	Can change system	31	change_system
93	Can delete system	31	delete_system
94	Can add target	32	add_target
95	Can change target	32	change_target
96	Can delete target	32	delete_target
97	Can add period	33	add_period
98	Can change period	33	change_period
99	Can delete period	33	delete_period
100	Can add log entry	34	add_logentry
101	Can change log entry	34	change_logentry
102	Can delete log entry	34	delete_logentry
\.


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY auth_user (id, username, first_name, last_name, email, password, is_staff, is_active, is_superuser, last_login, date_joined) FROM stdin;
1	dss			dss@nrao.edu	sha1$98295$71a569bf3152a80768596321964697e1d569b326	t	t	t	2009-07-31 17:24:01.902164-04	2009-07-31 17:24:01.902164-04
\.


--
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY auth_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: blackouts; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY blackouts (id, user_id, start, "end", tz_id, repeat_id, until, description) FROM stdin;
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY django_admin_log (id, action_time, user_id, content_type_id, object_id, object_repr, action_flag, change_message) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY django_content_type (id, name, app_label, model) FROM stdin;
1	permission	auth	permission
2	group	auth	group
3	user	auth	user
4	message	auth	message
5	content type	contenttypes	contenttype
6	session	sessions	session
7	site	sites	site
8	user	sesshuns	user
9	email	sesshuns	email
10	semester	sesshuns	semester
11	project_ type	sesshuns	project_type
12	allotment	sesshuns	allotment
13	project	sesshuns	project
14	project_ allotment	sesshuns	project_allotment
15	repeat	sesshuns	repeat
16	time zone	sesshuns	timezone
17	blackout	sesshuns	blackout
18	project_ blackout_09b	sesshuns	project_blackout_09b
19	investigators	sesshuns	investigators
20	session_ type	sesshuns	session_type
21	observing_ type	sesshuns	observing_type
22	receiver	sesshuns	receiver
23	receiver_ schedule	sesshuns	receiver_schedule
24	parameter	sesshuns	parameter
25	status	sesshuns	status
26	sesshun	sesshuns	sesshun
27	receiver_ group	sesshuns	receiver_group
28	observing_ parameter	sesshuns	observing_parameter
29	window	sesshuns	window
30	opportunity	sesshuns	opportunity
31	system	sesshuns	system
32	target	sesshuns	target
33	period	sesshuns	period
34	log entry	admin	logentry
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY django_session (session_key, session_data, expire_date) FROM stdin;
\.


--
-- Data for Name: django_site; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY django_site (id, domain, name) FROM stdin;
1	example.com	example.com
\.


--
-- Data for Name: investigators; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY investigators (id, project_id, user_id, friend, observer, principal_contact, principal_investigator, priority) FROM stdin;
1	2	1	t	f	f	f	1
2	3	2	t	f	f	f	1
3	4	3	t	f	f	f	1
4	5	1	t	f	f	f	1
5	6	1	t	f	f	f	1
6	7	3	t	f	f	f	1
7	9	4	t	f	f	f	1
8	10	5	t	f	f	f	1
9	11	5	t	f	f	f	1
10	12	6	t	f	f	f	1
11	13	6	t	f	f	f	1
12	14	7	t	f	f	f	1
13	15	2	t	f	f	f	1
14	16	8	t	f	f	f	1
15	17	1	t	f	f	f	1
16	18	1	t	f	f	f	1
17	19	4	t	f	f	f	1
18	20	8	t	f	f	f	1
19	21	2	t	f	f	f	1
20	22	3	t	f	f	f	1
21	23	9	t	f	f	f	1
22	24	10	t	f	f	f	1
23	25	1	t	f	f	f	1
24	26	11	t	f	f	f	1
25	27	6	t	f	f	f	1
26	28	6	t	f	f	f	1
27	29	1	t	f	f	f	1
28	30	6	t	f	f	f	1
29	31	1	t	f	f	f	1
30	32	8	t	f	f	f	1
31	33	8	t	f	f	f	1
32	34	10	t	f	f	f	1
33	35	2	t	f	f	f	1
34	36	8	t	f	f	f	1
35	37	6	t	f	f	f	1
36	38	7	t	f	f	f	1
37	39	6	t	f	f	f	1
38	40	8	t	f	f	f	1
39	41	10	t	f	f	f	1
40	42	5	t	f	f	f	1
41	43	8	t	f	f	f	1
42	44	3	t	f	f	f	1
43	45	2	t	f	f	f	1
44	46	6	t	f	f	f	1
45	47	12	t	f	f	f	1
46	48	2	t	f	f	f	1
47	49	3	t	f	f	f	1
48	50	3	t	f	f	f	1
49	51	8	t	f	f	f	1
50	52	9	t	f	f	f	1
51	53	13	t	f	f	f	1
52	54	8	t	f	f	f	1
53	55	10	t	f	f	f	1
54	56	3	t	f	f	f	1
55	57	8	t	f	f	f	1
56	58	8	t	f	f	f	1
57	59	1	t	f	f	f	1
58	60	2	t	f	f	f	1
59	61	8	t	f	f	f	1
60	62	14	t	f	f	f	1
61	63	14	t	f	f	f	1
62	64	8	t	f	f	f	1
63	65	6	t	f	f	f	1
64	66	5	t	f	f	f	1
65	67	5	t	f	f	f	1
66	68	8	t	f	f	f	1
67	69	6	t	f	f	f	1
68	70	3	t	f	f	f	1
69	71	8	t	f	f	f	1
70	72	8	t	f	f	f	1
71	73	15	t	f	f	f	1
72	74	3	t	f	f	f	1
73	75	6	t	f	f	f	1
74	76	8	t	f	f	f	1
75	77	2	t	f	f	f	1
76	78	8	t	f	f	f	1
77	79	8	t	f	f	f	1
78	80	8	t	f	f	f	1
79	81	8	t	f	f	f	1
80	82	2	t	f	f	f	1
81	83	8	t	f	f	f	1
82	84	8	t	f	f	f	1
83	85	8	t	f	f	f	1
84	86	8	t	f	f	f	1
85	87	13	t	f	f	f	1
86	88	6	t	f	f	f	1
87	89	7	t	f	f	f	1
88	90	7	t	f	f	f	1
89	91	7	t	f	f	f	1
90	92	8	t	f	f	f	1
91	93	12	t	f	f	f	1
92	94	8	t	f	f	f	1
93	95	13	t	f	f	f	1
94	96	8	t	f	f	f	1
95	97	2	t	f	f	f	1
96	98	1	t	f	f	f	1
97	2	16	f	f	t	t	1
98	2	17	f	f	f	f	1
99	2	18	f	f	f	f	1
100	2	19	f	f	f	f	1
101	3	2	f	f	t	t	1
102	3	20	f	f	f	f	1
103	3	21	f	f	f	f	1
104	3	22	f	f	f	f	1
105	3	23	f	f	f	f	1
106	3	24	f	f	f	f	1
107	3	25	f	f	f	f	1
108	3	26	f	f	f	f	1
109	3	27	f	f	f	f	1
110	3	28	f	f	f	f	1
111	3	29	f	f	f	f	1
112	4	30	f	f	t	t	1
113	4	31	f	f	f	f	1
114	4	32	f	f	f	f	1
115	4	33	f	f	f	f	1
116	5	34	f	f	t	t	1
117	5	35	f	f	f	f	1
118	5	36	f	f	f	f	1
119	5	37	f	f	f	f	1
120	5	38	f	f	f	f	1
121	5	39	f	f	f	f	1
122	5	40	f	f	f	f	1
123	6	36	f	f	t	t	1
124	6	41	f	f	f	f	1
125	6	33	f	f	f	f	1
126	7	42	f	f	t	t	1
127	7	43	f	f	f	f	1
128	7	44	f	f	f	f	1
129	8	45	f	f	t	t	1
130	8	46	f	f	f	f	1
131	8	47	f	f	f	f	1
132	8	48	f	f	f	f	1
133	8	49	f	f	f	f	1
134	8	50	f	f	f	f	1
135	9	51	f	f	t	t	1
136	9	52	f	f	f	f	1
137	9	53	f	f	f	f	1
138	9	54	f	f	f	f	1
139	9	55	f	f	f	f	1
140	9	56	f	f	f	f	1
141	9	57	f	f	f	f	1
142	10	58	f	f	t	t	1
143	10	59	f	f	f	f	1
144	10	60	f	f	f	f	1
145	11	61	f	f	t	t	1
146	11	62	f	f	f	f	1
147	12	63	f	f	t	t	1
148	12	64	f	f	f	f	1
149	12	65	f	f	f	f	1
150	12	66	f	f	f	f	1
151	13	63	f	f	t	t	1
152	13	67	f	f	f	f	1
153	14	68	f	f	f	t	1
154	14	15	f	f	t	f	1
155	14	69	f	f	f	f	1
156	14	70	f	f	f	f	1
157	15	71	f	f	t	t	1
158	15	72	f	f	f	f	1
159	16	73	f	f	t	t	1
160	16	74	f	f	f	f	1
161	16	75	f	f	f	f	1
162	16	76	f	f	f	f	1
163	16	77	f	f	f	f	1
164	16	78	f	f	f	f	1
165	16	79	f	f	f	f	1
166	16	8	f	f	f	f	1
167	16	80	f	f	f	f	1
168	16	81	f	f	f	f	1
169	17	63	f	f	t	t	1
170	17	82	f	f	f	f	1
171	18	83	f	f	t	t	1
172	18	84	f	f	f	f	1
173	18	85	f	f	f	f	1
174	18	86	f	f	f	f	1
175	18	87	f	f	f	f	1
176	19	51	f	f	t	t	1
177	19	88	f	f	f	f	1
178	19	52	f	f	f	f	1
179	19	17	f	f	f	f	1
180	19	53	f	f	f	f	1
181	19	4	f	f	f	f	1
182	20	89	f	f	f	t	1
183	20	90	f	f	f	f	1
184	20	91	f	f	t	f	1
185	20	92	f	f	f	f	1
186	20	93	f	f	f	f	1
187	20	94	f	f	f	f	1
188	21	95	f	f	t	t	1
189	21	96	f	f	f	f	1
190	21	97	f	f	f	f	1
191	21	44	f	f	f	f	1
192	21	98	f	f	f	f	1
193	21	99	f	f	f	f	1
194	22	63	f	f	t	f	1
195	22	100	f	f	f	t	1
196	23	101	f	f	t	t	1
197	23	102	f	f	f	f	1
198	24	103	f	f	t	t	1
199	24	104	f	f	f	f	1
200	24	105	f	f	f	f	1
201	25	106	f	f	t	t	1
202	25	107	f	f	f	f	1
203	25	108	f	f	f	f	1
204	25	109	f	f	f	f	1
205	25	110	f	f	f	f	1
206	26	11	f	f	t	t	1
207	26	111	f	f	f	f	1
208	26	112	f	f	f	f	1
209	26	113	f	f	f	f	1
210	26	114	f	f	f	f	1
211	27	6	f	f	t	t	1
212	27	115	f	f	f	f	1
213	27	116	f	f	f	f	1
214	28	6	f	f	t	t	1
215	28	12	f	f	f	f	1
216	28	117	f	f	f	f	1
217	29	118	f	f	t	t	1
218	29	119	f	f	f	f	1
219	30	120	f	f	t	t	1
220	30	6	f	f	f	f	1
221	31	121	f	f	t	t	1
222	31	60	f	f	f	f	1
223	31	122	f	f	f	f	1
224	31	123	f	f	f	f	1
225	31	124	f	f	f	f	1
226	31	125	f	f	f	f	1
227	31	126	f	f	f	f	1
228	31	127	f	f	f	f	1
229	31	128	f	f	f	f	1
230	31	129	f	f	f	f	1
231	31	59	f	f	f	f	1
232	31	58	f	f	f	f	1
233	31	130	f	f	f	f	1
234	31	131	f	f	f	f	1
235	32	132	f	f	t	t	1
236	32	8	f	f	f	f	1
237	32	133	f	f	f	f	1
238	32	134	f	f	f	f	1
239	33	132	f	f	t	t	1
240	33	8	f	f	f	f	1
241	33	135	f	f	f	f	1
242	33	92	f	f	f	f	1
243	33	136	f	f	f	f	1
244	33	137	f	f	f	f	1
245	33	138	f	f	f	f	1
246	33	133	f	f	f	f	1
247	33	139	f	f	f	f	1
248	34	140	f	f	f	t	1
249	34	104	f	f	t	f	1
250	34	10	f	f	f	f	1
251	35	2	f	f	t	t	1
252	35	20	f	f	f	f	1
253	35	21	f	f	f	f	1
254	35	22	f	f	f	f	1
255	35	23	f	f	f	f	1
256	35	24	f	f	f	f	1
257	35	25	f	f	f	f	1
258	35	26	f	f	f	f	1
259	35	27	f	f	f	f	1
260	35	28	f	f	f	f	1
261	35	29	f	f	f	f	1
262	36	141	f	f	t	t	1
263	36	8	f	f	f	f	1
264	36	137	f	f	f	f	1
265	36	77	f	f	f	f	1
266	37	142	f	f	t	t	1
267	37	143	f	f	f	f	1
268	37	144	f	f	f	f	1
269	37	145	f	f	f	f	1
270	37	65	f	f	f	f	1
271	38	146	f	f	f	t	1
272	38	59	f	f	t	f	1
273	38	58	f	f	f	f	1
274	38	147	f	f	f	f	1
275	38	148	f	f	f	f	1
276	38	7	f	f	f	f	1
277	39	59	f	f	t	t	1
278	39	58	f	f	f	f	1
279	39	146	f	f	f	f	1
280	39	147	f	f	f	f	1
281	40	8	f	f	t	t	1
282	40	137	f	f	f	f	1
283	40	77	f	f	f	f	1
284	40	149	f	f	f	f	1
285	40	141	f	f	f	f	1
286	41	150	f	f	f	t	1
287	41	10	f	f	t	f	1
288	41	151	f	f	f	f	1
289	41	152	f	f	f	f	1
290	41	153	f	f	f	f	1
291	42	154	f	f	t	t	1
292	42	155	f	f	f	f	1
293	42	5	f	f	f	f	1
294	42	156	f	f	f	f	1
295	43	137	f	f	t	t	1
296	43	8	f	f	f	f	1
297	43	141	f	f	f	f	1
298	44	157	f	f	t	t	1
299	44	158	f	f	f	f	1
300	44	159	f	f	f	f	1
301	44	160	f	f	f	f	1
302	45	161	f	f	t	t	1
303	45	162	f	f	f	f	1
304	45	163	f	f	f	f	1
305	45	164	f	f	f	f	1
306	45	165	f	f	f	f	1
307	45	166	f	f	f	f	1
308	46	167	f	f	t	t	1
309	46	168	f	f	f	f	1
310	46	169	f	f	f	f	1
311	46	170	f	f	f	f	1
312	46	171	f	f	f	f	1
313	46	172	f	f	f	f	1
314	46	173	f	f	f	f	1
315	46	174	f	f	f	f	1
316	46	175	f	f	f	f	1
317	46	176	f	f	f	f	1
318	46	177	f	f	f	f	1
319	47	12	f	f	t	t	1
320	47	178	f	f	f	f	1
321	47	13	f	f	f	f	1
322	48	179	f	f	t	t	1
323	48	180	f	f	f	f	1
324	48	181	f	f	f	f	1
325	48	182	f	f	f	f	1
326	48	183	f	f	f	f	1
327	48	184	f	f	f	f	1
328	48	185	f	f	f	f	1
329	48	186	f	f	f	f	1
330	49	63	f	f	t	t	1
331	50	187	f	f	t	t	1
332	50	188	f	f	f	f	1
333	50	189	f	f	f	f	1
334	50	190	f	f	f	f	1
335	50	191	f	f	f	f	1
336	50	192	f	f	f	f	1
337	50	193	f	f	f	f	1
338	51	141	f	f	t	t	1
339	51	8	f	f	f	f	1
340	51	77	f	f	f	f	1
341	51	137	f	f	f	f	1
342	52	194	f	f	t	t	1
343	52	121	f	f	f	f	1
344	52	195	f	f	f	f	1
345	52	196	f	f	f	f	1
346	52	197	f	f	f	f	1
347	52	58	f	f	f	f	1
348	52	59	f	f	f	f	1
349	52	198	f	f	f	f	1
350	52	199	f	f	f	f	1
351	52	200	f	f	f	f	1
352	52	201	f	f	f	f	1
353	53	178	f	f	t	t	1
354	53	13	f	f	f	f	1
355	53	202	f	f	f	f	1
356	54	14	f	f	t	t	1
357	54	73	f	f	f	f	1
358	54	203	f	f	f	f	1
359	55	10	f	f	t	t	1
360	55	151	f	f	f	f	1
361	55	204	f	f	f	f	1
362	55	205	f	f	f	f	1
363	55	152	f	f	f	f	1
364	55	150	f	f	f	f	1
365	55	206	f	f	f	f	1
366	55	153	f	f	f	f	1
367	56	207	f	f	f	t	1
368	56	88	f	f	t	f	1
369	56	208	f	f	f	f	1
370	57	14	f	f	t	t	1
371	57	92	f	f	f	f	1
372	57	91	f	f	f	f	1
373	57	209	f	f	f	f	1
374	58	132	f	f	t	t	1
375	58	133	f	f	f	f	1
376	58	8	f	f	f	f	1
377	58	210	f	f	f	f	1
378	59	118	f	f	t	t	1
379	59	119	f	f	f	f	1
380	59	108	f	f	f	f	1
381	60	211	f	f	t	t	1
382	60	212	f	f	f	f	1
383	60	213	f	f	f	f	1
384	60	214	f	f	f	f	1
385	60	215	f	f	f	f	1
386	60	206	f	f	f	f	1
387	60	216	f	f	f	f	1
388	60	217	f	f	f	f	1
389	60	218	f	f	f	f	1
390	60	219	f	f	f	f	1
391	60	220	f	f	f	f	1
392	61	93	f	f	t	t	1
393	61	91	f	f	f	f	1
394	61	92	f	f	f	f	1
395	62	209	f	f	t	t	1
396	62	14	f	f	f	f	1
397	63	209	f	f	t	t	1
398	63	14	f	f	f	f	1
399	64	141	f	f	t	t	1
400	64	8	f	f	f	f	1
401	64	91	f	f	f	f	1
402	64	92	f	f	f	f	1
403	64	77	f	f	f	f	1
404	64	221	f	f	f	f	1
405	64	222	f	f	f	f	1
406	64	223	f	f	f	f	1
407	64	224	f	f	f	f	1
408	64	93	f	f	f	f	1
409	64	225	f	f	f	f	1
410	64	149	f	f	f	f	1
411	64	226	f	f	f	f	1
412	64	135	f	f	f	f	1
413	64	227	f	f	f	f	1
414	64	228	f	f	f	f	1
415	64	229	f	f	f	f	1
416	65	63	f	f	t	t	1
417	66	155	f	f	t	t	1
418	66	5	f	f	f	f	1
419	66	154	f	f	f	f	1
420	66	156	f	f	f	f	1
421	67	154	f	f	t	t	1
422	67	155	f	f	f	f	1
423	67	5	f	f	f	f	1
424	67	156	f	f	f	f	1
425	68	230	f	f	t	t	1
426	68	91	f	f	f	f	1
427	68	92	f	f	f	f	1
428	68	231	f	f	f	f	1
429	68	232	f	f	f	f	1
430	68	233	f	f	f	f	1
431	68	77	f	f	f	f	1
432	68	132	f	f	f	f	1
433	68	234	f	f	f	f	1
434	68	235	f	f	f	f	1
435	68	236	f	f	f	f	1
436	68	237	f	f	f	f	1
437	69	238	f	f	t	t	1
438	69	239	f	f	f	f	1
439	69	6	f	f	f	f	1
440	69	73	f	f	f	f	1
441	69	93	f	f	f	f	1
442	69	240	f	f	f	f	1
443	70	207	f	f	f	t	1
444	70	88	f	f	t	f	1
445	70	208	f	f	f	f	1
446	71	132	f	f	t	t	1
447	71	8	f	f	f	f	1
448	71	241	f	f	f	f	1
449	71	139	f	f	f	f	1
450	71	91	f	f	f	f	1
451	72	242	f	f	t	t	1
452	72	243	f	f	f	f	1
453	72	149	f	f	f	f	1
454	73	15	f	f	t	t	1
455	73	244	f	f	f	f	1
456	73	245	f	f	f	f	1
457	74	246	f	f	t	t	1
458	74	247	f	f	f	f	1
459	74	248	f	f	f	f	1
460	75	170	f	f	t	t	1
461	75	169	f	f	f	f	1
462	75	140	f	f	f	f	1
463	75	249	f	f	f	f	1
464	75	167	f	f	f	f	1
465	75	250	f	f	f	f	1
466	76	89	f	f	t	t	1
467	76	90	f	f	f	f	1
468	76	91	f	f	f	f	1
469	76	92	f	f	f	f	1
470	76	93	f	f	f	f	1
471	76	225	f	f	f	f	1
472	76	94	f	f	f	f	1
473	77	251	f	f	t	t	1
474	77	252	f	f	f	f	1
475	77	253	f	f	f	f	1
476	77	254	f	f	f	f	1
477	77	255	f	f	f	f	1
478	78	229	f	f	t	t	1
479	78	222	f	f	f	f	1
480	78	256	f	f	f	f	1
481	79	229	f	f	t	t	1
482	79	222	f	f	f	f	1
483	79	256	f	f	f	f	1
484	80	139	f	f	t	t	1
485	80	132	f	f	f	f	1
486	80	8	f	f	f	f	1
487	80	135	f	f	f	f	1
488	81	8	f	f	t	t	1
489	81	132	f	f	f	f	1
490	81	139	f	f	f	f	1
491	81	135	f	f	f	f	1
492	82	257	f	f	t	t	1
493	82	258	f	f	f	f	1
494	82	259	f	f	f	f	1
495	82	260	f	f	f	f	1
496	83	73	f	f	t	t	1
497	83	261	f	f	f	f	1
498	83	262	f	f	f	f	1
499	83	263	f	f	f	f	1
500	84	92	f	f	t	t	1
501	84	233	f	f	f	f	1
502	84	232	f	f	f	f	1
503	84	264	f	f	f	f	1
504	84	91	f	f	f	f	1
505	84	265	f	f	f	f	1
506	85	232	f	f	t	t	1
507	85	77	f	f	f	f	1
508	85	92	f	f	f	f	1
509	85	75	f	f	f	f	1
510	85	132	f	f	f	f	1
511	85	233	f	f	f	f	1
512	85	266	f	f	f	f	1
513	85	235	f	f	f	f	1
514	85	236	f	f	f	f	1
515	85	234	f	f	f	f	1
516	85	137	f	f	f	f	1
517	85	267	f	f	f	f	1
518	86	141	f	f	t	t	1
519	86	8	f	f	f	f	1
520	86	91	f	f	f	f	1
521	86	92	f	f	f	f	1
522	86	77	f	f	f	f	1
523	86	221	f	f	f	f	1
524	86	222	f	f	f	f	1
525	86	223	f	f	f	f	1
526	86	224	f	f	f	f	1
527	86	93	f	f	f	f	1
528	86	225	f	f	f	f	1
529	86	149	f	f	f	f	1
530	86	226	f	f	f	f	1
531	86	135	f	f	f	f	1
532	86	227	f	f	f	f	1
533	86	228	f	f	f	f	1
534	86	229	f	f	f	f	1
535	87	178	f	f	t	t	1
536	87	13	f	f	f	f	1
537	87	202	f	f	f	f	1
538	88	63	f	f	t	t	1
539	88	64	f	f	f	f	1
540	89	268	f	f	t	t	1
541	89	172	f	f	f	f	1
542	89	167	f	f	f	f	1
543	89	169	f	f	f	f	1
544	90	269	f	f	t	t	1
545	90	88	f	f	f	f	1
546	91	63	f	f	t	t	1
547	91	169	f	f	f	f	1
548	91	167	f	f	f	f	1
549	92	73	f	f	t	t	1
550	92	78	f	f	f	f	1
551	92	77	f	f	f	f	1
552	92	8	f	f	f	f	1
553	92	75	f	f	f	f	1
554	92	79	f	f	f	f	1
555	92	76	f	f	f	f	1
556	92	270	f	f	f	f	1
557	93	271	f	f	t	t	1
558	93	272	f	f	f	f	1
559	93	12	f	f	f	f	1
560	93	273	f	f	f	f	1
561	93	274	f	f	f	f	1
562	93	275	f	f	f	f	1
563	94	276	f	f	t	t	1
564	94	8	f	f	f	f	1
565	94	77	f	f	f	f	1
566	94	91	f	f	f	f	1
567	94	92	f	f	f	f	1
568	94	221	f	f	f	f	1
569	94	224	f	f	f	f	1
570	94	228	f	f	f	f	1
571	94	277	f	f	f	f	1
572	95	278	f	f	t	t	1
573	95	103	f	f	f	f	1
574	95	279	f	f	f	f	1
575	95	280	f	f	f	f	1
576	95	13	f	f	f	f	1
577	95	76	f	f	f	f	1
578	96	141	f	f	t	t	1
579	96	8	f	f	f	f	1
580	97	281	f	f	t	t	1
581	97	22	f	f	f	f	1
582	97	282	f	f	f	f	1
583	97	2	f	f	f	f	1
584	97	283	f	f	f	f	1
585	97	249	f	f	f	f	1
586	98	284	f	f	t	t	1
587	98	107	f	f	f	f	1
588	98	285	f	f	f	f	1
589	98	284	f	f	t	t	1
590	99	221	f	f	t	t	1
591	99	224	f	f	f	f	1
592	99	286	f	f	f	f	1
593	100	13	f	f	t	t	1
594	101	287	f	f	t	t	1
595	101	288	f	f	f	f	1
596	101	289	f	f	f	f	1
597	101	290	f	f	f	f	1
598	101	291	f	f	f	f	1
599	101	292	f	f	f	f	1
600	102	139	f	f	t	t	1
601	102	132	f	f	f	f	1
602	102	8	f	f	f	f	1
603	102	135	f	f	f	f	1
604	103	210	f	f	t	t	1
605	103	293	f	f	f	f	1
606	103	221	f	f	f	f	1
607	103	135	f	f	f	f	1
608	103	294	f	f	f	f	1
609	103	8	f	f	f	f	1
610	103	295	f	f	f	f	1
611	104	132	f	f	t	t	1
612	104	8	f	f	f	f	1
613	104	135	f	f	f	f	1
614	104	92	f	f	f	f	1
615	105	135	f	f	t	t	1
616	105	92	f	f	f	f	1
617	105	149	f	f	f	f	1
618	105	8	f	f	f	f	1
619	105	139	f	f	f	f	1
620	105	296	f	f	f	f	1
621	106	92	f	f	t	t	1
622	106	297	f	f	f	f	1
623	106	8	f	f	f	f	1
624	106	93	f	f	f	f	1
625	106	298	f	f	f	f	1
626	106	13	f	f	f	f	1
627	106	243	f	f	f	f	1
628	106	91	f	f	f	f	1
629	106	299	f	f	f	f	1
630	107	300	f	f	t	t	1
631	107	301	f	f	f	f	1
632	107	32	f	f	f	f	1
633	107	302	f	f	f	f	1
634	107	303	f	f	f	f	1
635	107	304	f	f	f	f	1
636	107	305	f	f	f	f	1
\.


--
-- Data for Name: observing_parameters; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY observing_parameters (id, session_id, parameter_id, string_value, integer_value, float_value, boolean_value, datetime_value) FROM stdin;
1	1	1	Gb,VLBA	\N	\N	\N	\N
2	2	1	Gb,VLBA	\N	\N	\N	\N
3	3	1	Gb,VLBA	\N	\N	\N	\N
4	4	1	Gb,VLBA	\N	\N	\N	\N
5	5	1	Gb,VLBA	\N	\N	\N	\N
6	6	1	Gb,VLBA	\N	\N	\N	\N
7	7	1	Gb,VLBA	\N	\N	\N	\N
8	8	1	Gb,VLBA	\N	\N	\N	\N
9	9	1	Gb,VLBA	\N	\N	\N	\N
10	10	1	Gb,VLBA	\N	\N	\N	\N
11	11	1	Gb,VLBA	\N	\N	\N	\N
12	12	1	Gb,VLBA	\N	\N	\N	\N
13	13	1	Gb,VLBA	\N	\N	\N	\N
14	14	1	Gb,VLBA	\N	\N	\N	\N
15	15	1	Gb,VLBA	\N	\N	\N	\N
16	16	1	Gb,VLBA	\N	\N	\N	\N
17	17	1	Eb,Gb,Y27,VLBA	\N	\N	\N	\N
18	18	1	Eb,Gb,Y27,VLBA	\N	\N	\N	\N
19	19	1	Eb,Gb,Y27,VLBA	\N	\N	\N	\N
20	20	1	Gb,VLBA	\N	\N	\N	\N
21	21	1	Eb,Gb,Y27,VLBA	\N	\N	\N	\N
22	22	1	Eb,Gb,VLBA	\N	\N	\N	\N
23	22	6	\N	\N	\N	t	\N
24	23	1	Eb,Gb,VLBA	\N	\N	\N	\N
25	23	6	\N	\N	\N	t	\N
26	24	1	Eb,Gb,VLBA	\N	\N	\N	\N
27	24	6	\N	\N	\N	t	\N
28	25	1	Eb,Gb,VLBA	\N	\N	\N	\N
29	25	6	\N	\N	\N	t	\N
30	26	1	EVN,Gb,VLA,VLBA	\N	\N	\N	\N
31	27	7	\N	\N	\N	t	\N
32	28	7	\N	\N	\N	t	\N
33	31	7	\N	\N	\N	t	\N
34	39	7	\N	\N	\N	t	\N
35	40	7	\N	\N	\N	t	\N
36	44	7	\N	\N	\N	t	\N
37	46	7	\N	\N	\N	t	\N
38	49	7	\N	\N	\N	t	\N
39	50	7	\N	\N	\N	t	\N
40	51	7	\N	\N	\N	t	\N
41	52	7	\N	\N	\N	t	\N
42	53	7	\N	\N	\N	t	\N
43	60	6	\N	\N	\N	t	\N
44	61	6	\N	\N	\N	t	\N
45	62	6	\N	\N	\N	t	\N
46	63	6	\N	\N	\N	t	\N
47	63	7	\N	\N	\N	t	\N
48	64	6	\N	\N	\N	t	\N
49	64	7	\N	\N	\N	t	\N
50	65	6	\N	\N	\N	t	\N
51	69	7	\N	\N	\N	t	\N
52	70	7	\N	\N	\N	t	\N
53	99	7	\N	\N	\N	t	\N
54	100	7	\N	\N	\N	t	\N
55	101	7	\N	\N	\N	t	\N
56	110	7	\N	\N	\N	t	\N
57	111	7	\N	\N	\N	t	\N
58	112	7	\N	\N	\N	t	\N
59	113	7	\N	\N	\N	t	\N
60	114	7	\N	\N	\N	t	\N
61	115	7	\N	\N	\N	t	\N
62	116	7	\N	\N	\N	t	\N
63	117	7	\N	\N	\N	t	\N
64	118	7	\N	\N	\N	t	\N
65	119	7	\N	\N	\N	t	\N
66	120	7	\N	\N	\N	t	\N
67	121	7	\N	\N	\N	t	\N
68	122	7	\N	\N	\N	t	\N
69	123	7	\N	\N	\N	t	\N
70	124	7	\N	\N	\N	t	\N
71	125	7	\N	\N	\N	t	\N
72	126	7	\N	\N	\N	t	\N
73	127	7	\N	\N	\N	t	\N
74	131	4	\N	\N	15	\N	\N
75	131	5	\N	\N	21	\N	\N
76	134	4	\N	\N	15	\N	\N
77	134	5	\N	\N	21	\N	\N
78	135	7	\N	\N	\N	t	\N
79	136	7	\N	\N	\N	t	\N
80	137	7	\N	\N	\N	t	\N
81	138	7	\N	\N	\N	t	\N
82	146	4	\N	\N	15	\N	\N
83	146	5	\N	\N	21	\N	\N
84	147	4	\N	\N	15	\N	\N
85	147	5	\N	\N	21	\N	\N
86	148	4	\N	\N	15	\N	\N
87	148	5	\N	\N	21	\N	\N
88	149	4	\N	\N	15	\N	\N
89	149	5	\N	\N	21	\N	\N
90	161	7	\N	\N	\N	t	\N
91	162	7	\N	\N	\N	t	\N
92	163	7	\N	\N	\N	t	\N
93	218	6	\N	\N	\N	t	\N
94	219	6	\N	\N	\N	t	\N
95	220	6	\N	\N	\N	t	\N
96	221	6	\N	\N	\N	t	\N
97	222	6	\N	\N	\N	t	\N
98	228	6	\N	\N	\N	t	\N
99	242	1	Eb,Gb	\N	\N	\N	\N
\.


--
-- Data for Name: observing_types; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY observing_types (id, type) FROM stdin;
1	radar
2	vlbi
3	pulsar
4	continuum
5	spectral line
6	maintenance
7	calibration
8	testing
\.


--
-- Data for Name: opportunities; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY opportunities (id, window_id, start_time, duration) FROM stdin;
\.


--
-- Data for Name: parameters; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY parameters (id, name, type) FROM stdin;
1	Instruments	string
2	LST Include Low	float
3	LST Include Hi	float
4	LST Exclude Low	float
5	LST Exclude Hi	float
6	UTC Flag	boolean
7	Night-time Flag	boolean
8	Obs Eff Limit	float
9	Atmos St Limit	float
10	Tr Err Limit	float
11	Min Eff TSys	float
12	HA Limit	float
13	ZA Limit	float
14	Solar Avoid	float
15	Precip	float
16	Wind	float
17	Time Day	datetime
18	Transit	boolean
19	Transit Before	float
20	Transit After	float
\.


--
-- Data for Name: periods; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY periods (id, session_id, start, duration, score, forecast, backup) FROM stdin;
\.


--
-- Data for Name: project_blackouts_09b; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY project_blackouts_09b (id, project_id, requester_id, start_date, end_date, description) FROM stdin;
\.


--
-- Data for Name: project_types; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY project_types (id, type) FROM stdin;
1	science
2	non-science
\.


--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY projects (id, semester_id, project_type_id, pcode, name, thesis, complete, start_date, end_date) FROM stdin;
1	1	1	GBT09A-001		f	f	f	\N	\N
2	7	1	BB240	RIPL: Radio Interferometric PLanet Search	f	f	f	\N	\N
3	6	1	BB261	The Megamaser Cosmology Project: Year 2	f	f	f	\N	\N
4	2	1	BB268	Detecting the nucleus of M31	f	f	f	\N	\N
5	6	1	BM290	A direct geometric distance to a quiescent black hole Xray binary	f	f	f	\N	\N
6	2	1	BM306	Imaging the interacting young binary V773 Tau A/B	f	f	f	\N	\N
7	2	1	BP157	Confirmation of Large Coronal Loops on an RS CVN Binary	f	f	f	\N	\N
8	1	1	GB065	Resolving the jets in Cygnus A	f	f	f	\N	\N
9	16	1	GBT04A-003	Highly Redshifted HI and OH Absorption in Red Quasars	f	f	f	\N	\N
10	13	1	GBT05A-040	CO(1-0) Observations of Four Submillimeter Galaxies	f	f	f	\N	\N
11	15	1	GBT05C-027	An Exact Identification of High Densities in Molecular Clouds	f	f	f	\N	\N
12	12	1	GBT06C-048	HI 21cm absorption in strong MgII and CI absorbers in the redshift desert	f	f	f	\N	\N
13	7	1	GBT07A-035	Using CCH lines to measure changes in fundamental constants	f	f	f	\N	\N
14	7	1	GBT07A-051	A GBT Legacy Survey of Prebiotic Molecules Toward SgrB2(N-LMH) and TMC-1	f	f	f	\N	\N
15	7	1	GBT07A-086	The Detection of  the Missing Baryons with the NVII Line	f	f	f	\N	\N
16	7	1	GBT07A-087	Detecting nHz Gravitational Radiation using a Pulsar Timing Array	t	f	f	\N	\N
17	9	1	GBT07C-013	Conjugate OH lines in the z ~ 0.886 gravitational lens towards 1830-21	f	f	f	\N	\N
18	9	1	GBT07C-032	What is the gas temperature in the nearest cluster-forming region?	f	f	f	\N	\N
19	4	1	GBT08A-004	OH Absorption In the Lensing and Host Galaxies of J0414+0534	f	f	f	\N	\N
20	4	1	GBT08A-037	Radio monitoring of magnetars	f	f	f	\N	\N
21	4	1	GBT08A-048	Correlated Variability of Astrophysical Masers I: monitoring of NGC7538 IRS1	f	f	f	\N	\N
22	4	1	GBT08A-073	A deep search for associated HI 21cm absorption in red quasars	t	f	f	\N	\N
23	4	1	GBT08A-085	"Tomography" of Pulsar Polar Emission Region	t	f	f	\N	\N
24	4	1	GBT08A-092	Super-sized dust and exo-Earth formation	f	f	f	\N	\N
25	5	1	GBT08B-005	High-Resolution 12.6-cm Radar Mapping of the Nearside of the Moon	f	f	f	\N	\N
26	5	1	GBT08B-010	Molecular Line Survey of Edge Cloud 2 Southern Core	f	f	f	\N	\N
27	5	1	GBT08B-026	The H 2p-2s fine-structure line toward HII Regions and Planetary Nebulae	f	f	f	\N	\N
28	5	1	GBT08B-034	The Magnetic Field in the HVC Smith's Cloud and the Galactic Halo	f	f	f	\N	\N
29	5	1	GBT08B-049	Observations of the Chandrayaan-1 and Lunar Reconnaissance Orbiter Spacecraft	f	f	f	\N	\N
30	6	1	GBT08C-005	SiO Maser Observations of VY CMa	f	f	f	\N	\N
31	6	1	GBT08C-009	A Combined GBT/PdBI CO Survey of Submm Galaxies	f	f	f	\N	\N
32	6	1	GBT08C-014	Studying the magnetar XTE J1810-197	f	f	f	\N	\N
33	6	1	GBT08C-023	GLAST timing at GBT: six key radio-faint pulsars	f	f	f	\N	\N
34	6	1	GBT08C-026	3.3 mm MUSTANG Imaging of the Vega Debris Disk	f	f	f	\N	\N
35	6	1	GBT08C-035	The Megamaser Cosmology Project: Year 2	t	f	f	\N	\N
36	6	1	GBT08C-049	Timing of Newly Discovered MSPs in the Globular Cluster NGC6517	t	f	f	\N	\N
37	6	1	GBT08C-065	Search for Zeeman Splitting at High Redshift	f	f	f	\N	\N
38	6	1	GBT08C-070	Deep Zpectrometer integration toward the Cloverleaf galaxy	t	f	f	\N	\N
39	6	1	GBT08C-073	A CO(1-0) Survey of Dusty Galaxies at High Redshift	f	f	f	\N	\N
40	6	1	GBT08C-076	Long Term Timing of 55 Recycled Pulsars in Bulge Globular Clusters	t	f	f	\N	\N
41	6	1	GBT08C-078	MUSTANG Observations of Cygnus A	f	f	f	\N	\N
42	1	1	GBT09A-002	Discovering Milky Way HII Regions	t	f	f	\N	\N
43	1	1	GBT09A-003	Timing the pulsars in M62, NGC 6544 and NGC 6624	t	f	f	\N	\N
44	1	1	GBT09A-004	Search for HI 21cm absorption in a complete sample of DLAs at z>2.	f	f	f	\N	\N
45	1	1	GBT09A-010	Imaging infalling clumps around high-mass young stellar objects	t	f	f	\N	\N
46	1	1	GBT09A-012	Study of the ISM conditions in normal star forming galaxies at $z \\sim 1.5$	f	f	f	\N	\N
47	1	1	GBT09A-017	GBT HI Observations of "Wright's Cloud"	t	f	f	\N	\N
48	1	1	GBT09A-021	SO2: A molecule with maser emission and line absorption line in cold dark clouds	t	f	f	\N	\N
49	1	1	GBT09A-025	The spin temperature of high redshift damped Lyman-alpha systems	f	f	f	\N	\N
50	1	1	GBT09A-034	21 cm HI Observations of intermediate-z Clusters of Galaxies	f	f	f	\N	\N
51	1	1	GBT09A-038	Continued Timing of Pulsars in M22	t	f	f	\N	\N
52	1	1	GBT09A-040	Probing the Gas Properties of Star-Forming Galaxies at High-z via Strong Lensing	f	f	f	\N	\N
53	1	1	GBT09A-046	A Search for Faint Extended HI in Nearby Galaxy Groups - copy	t	f	f	\N	\N
54	1	1	GBT09A-049	Observational Tests for Non-radial Oscillations in Radio Pulsars	f	f	f	\N	\N
55	1	1	GBT09A-052	A High-Resolution Image of the SZE in RXJ1347-1149 With MUSTANG	f	f	f	\N	\N
56	1	1	GBT09A-055	A New Approach to Discovering Highly Obscured Radio-Loud Quasars	f	f	f	\N	\N
57	1	1	GBT09A-058	Confirmation Observations of New Pulsars Discovered by the PSC	f	f	f	\N	\N
58	1	1	GBT09A-062	New pulsar identifications of TeV gamma-ray sources	f	f	f	\N	\N
59	1	1	GBT09A-070	Calibrating the Transmitted Radar Signal from the LRO Spacecraft	f	f	f	\N	\N
60	1	1	GBT09A-080	NH3 in Dense Cloud Cores Selected from the 1.1 mm Continuum BGPS	t	f	f	\N	\N
61	1	1	GBT09A-081	A search for giant pulses in interpulse pulsars	f	f	f	\N	\N
62	1	1	GBT09A-092	Maintenance Observing with the GBT	f	f	f	\N	\N
63	1	1	GBT09A-093	Educational Projects on the GBT	f	f	f	\N	\N
64	1	1	GBT09A-095	Searching for Variability in PSR J0348+04	f	f	f	\N	\N
65	1	1	GBT09A-099	Probing changes in the proton-electron mass ratio with radio molecular lines.	f	f	f	\N	\N
66	2	1	GBT09B-001	Searching for Star Formation in the 3 kpc Arm	f	f	f	\N	\N
67	2	1	GBT09B-002	Discovering Milky Way HII Regions	t	f	f	\N	\N
68	2	1	GBT09B-003	On the Trail of the Enigmatic Millisecond Binary Pulsar PSR J1723-28	f	f	f	\N	\N
69	2	1	GBT09B-004	Noise and Signal in Pulsar Scintillation	f	f	f	\N	\N
70	2	1	GBT09B-005	A Search for HI Absorption Toward Red AGN in Non-Elliptical Host Galaxies	f	f	f	\N	\N
71	2	1	GBT09B-006	Three newly discovered pulsars	f	f	f	\N	\N
72	2	1	GBT09B-008	Confirmation of Radio Pulsar Candidates in M31	t	f	f	\N	\N
73	2	1	GBT09B-010	Surveying Cyanoformaldehyde (CNCHO) in Galactic Environments	f	f	f	\N	\N
74	2	1	GBT09B-012	Relativistic Probes of the WHIM  (redux)	t	f	f	\N	\N
75	2	1	GBT09B-013	A search for luminous H2O maser emission in lensed, FIR luminous QSOs at z~4	f	f	f	\N	\N
76	2	1	GBT09B-014	GBT radio monitoring of magnetars	f	f	f	\N	\N
77	2	1	GBT09B-015	Chemical complexity in the nuclei of galaxies. The nucleus of the Milky way	t	f	f	\N	\N
78	2	1	GBT09B-017	Are the Arches and Quintuplet Clusters Pulsar Nurseries?	t	f	f	\N	\N
79	2	1	GBT09B-018	Two Very Dispersed Pulsars Near SgrA*: Continued Timing and Spectrum Estimation	t	f	f	\N	\N
80	2	1	GBT09B-023	Search for Radio Pulsations from Gamma-Ray Pulsars Discovered with Fermi	f	f	f	\N	\N
81	2	1	GBT09B-024	Searching for Radio Pulsars in Fermi Bright Unidentified Sources	f	f	f	\N	\N
82	2	1	GBT09B-025	An OH Absorption Line Survey of the Galactic Scale Molecular Loops	t	f	f	\N	\N
83	2	1	GBT09B-026	Cyclic Spectroscopy of Three Pulsars	f	f	f	\N	\N
84	2	1	GBT09B-028	Timing of New and Old Rotating Radio Transient Sources	t	f	f	\N	\N
85	2	1	GBT09B-029	Timing and General Relativity in the Double Pulsar System	t	f	f	\N	\N
86	2	1	GBT09B-031	Timing the New GBT 350 MHz Drift Scan Pulsars	t	f	f	\N	\N
87	2	1	GBT09B-034	Deep Observations of Possible HVC Analogs in the NGC 2403 Group	t	f	f	\N	\N
88	2	1	GBT09B-035	Confirming a tentative detection of HI 21cm absorption at z ~ 2.193	f	f	f	\N	\N
89	2	1	GBT09B-036	CS(1-0) survey of dense gas at high-redshift	f	f	f	\N	\N
90	2	1	GBT09B-039	C3H2 in the Gravitational Lens B0218+357: Chemical Evolution and Densitometry	f	f	f	\N	\N
91	2	1	GBT09B-040	A search for CS 1-0 emission at high redshifts	f	f	f	\N	\N
92	2	1	GBT09B-041	Detecting nHz Gravitational Radiation using a Pulsar Timing Array	f	f	f	\N	\N
93	2	1	GBT09B-042	Establishing a scenario of molecule formation from high Galactic latitude sites	f	f	f	\N	\N
94	2	1	GBT09B-043	A Search for Radio Pulsations from Low-Mass X-ray Binaries	f	f	f	\N	\N
95	2	1	GBT09B-044	Cyclotron emission from the exo-planet HD 189733b - copy	f	f	f	\N	\N
96	2	1	GBT09B-045	Searching For New Pulsars in Eight Low Metallicity Globular Clusters	t	f	f	\N	\N
97	2	1	GBT09B-046	Tracing the Physical Conditions in NGC 3079 and Mrk 348 with Methanol	f	f	f	\N	\N
98	2	1	GBT09B-048	Venus spin dynamics	f	f	f	\N	\N
99	2	1	GBT09B-055	Target-of-Opportunity Observations of an unusual Periodic Gamma-Ray Burst	f	f	f	\N	\N
100	2	1	GBT09B-056	HC_9N  Temperature TMC in Cynanopolyyne Peak	f	f	f	\N	\N
101	2	1	GBT09B-057	Water on Main-Belt Asteroids	f	f	f	\N	\N
102	2	1	GLST021097	SEARCH FOR RADIO PULSATIONS FROM GAMMA-RAY PULSARS DISCOVERED WITH FERMI	f	f	f	\N	\N
103	2	1	GLST021177	X-RAY AND GAMMA-RAY TIMING AND SPECTRAL STUDIES OF FIVE RADIO QUIET PULSARS	f	f	f	\N	\N
104	2	1	GLST021284	GREEN BANK TELESCOPE TIMING OF KEY FERMI PULSARS	f	f	f	\N	\N
105	2	1	GLST021296	A PULSAR SURVEY OF FERMI SOURCES NOT IN THE BRIGHT SOURCE LIST	f	f	f	\N	\N
106	2	1	GLST021302	CONSTRAINING PULSAR EMISSION PHYSICS THROUGH RADIO/GAMMA-RAY CORRELATION OF CRAB	f	f	f	\N	\N
107	8	1	GP044	A Misaligned Relativistic Jet in SN 2007gr?	f	f	f	\N	\N
\.


--
-- Data for Name: projects_allotments; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY projects_allotments (id, project_id, allotment_id) FROM stdin;
1	2	2
2	3	3
3	4	4
4	5	5
5	6	6
6	7	7
7	8	8
8	9	9
9	10	10
10	11	11
11	12	12
12	13	13
13	14	14
14	15	15
15	16	16
16	17	17
17	18	18
18	19	19
19	20	20
20	21	21
21	22	22
22	23	23
23	24	24
24	25	25
25	26	26
26	28	27
27	29	28
28	30	29
29	31	30
30	32	31
31	33	32
32	34	33
33	35	34
34	37	35
35	38	36
36	39	37
37	40	38
38	41	39
39	42	40
40	43	41
41	44	42
42	45	43
43	46	44
44	48	45
45	49	46
46	50	47
47	51	48
48	52	49
49	53	50
50	55	51
51	56	52
52	57	53
53	58	54
54	59	55
55	60	56
56	61	57
57	63	58
58	64	59
59	65	60
60	66	61
61	67	62
62	68	63
63	69	64
64	70	65
65	71	66
66	72	67
67	74	68
68	75	69
69	76	70
70	77	71
71	77	72
72	78	73
73	79	74
74	80	75
75	81	76
76	82	77
77	83	78
78	84	79
79	85	80
80	86	81
81	87	82
82	88	83
83	89	84
84	90	85
85	91	86
86	92	87
87	93	88
88	94	89
89	95	90
90	96	91
91	96	92
92	97	93
93	98	94
94	99	95
95	99	96
96	100	97
97	101	98
98	102	99
99	103	100
100	104	101
101	105	102
102	106	103
103	107	104
\.


--
-- Data for Name: receiver_groups; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY receiver_groups (id, session_id) FROM stdin;
1	1
2	2
3	3
4	4
5	5
6	6
7	7
8	8
9	9
10	10
11	11
12	12
13	13
14	14
15	15
16	16
17	17
18	18
19	19
20	20
21	21
22	22
23	23
24	24
25	25
26	26
27	27
28	28
29	29
30	30
31	31
32	32
33	33
34	34
35	35
36	36
37	37
38	38
39	39
40	40
41	41
42	42
43	43
44	44
45	45
46	46
47	47
48	48
49	49
50	50
51	51
52	52
53	53
54	54
55	55
56	56
57	57
58	58
59	59
60	60
61	61
62	62
63	63
64	64
65	65
66	66
67	67
68	68
69	69
70	70
71	71
72	72
73	73
74	74
75	75
76	76
77	77
78	78
79	79
80	80
81	81
82	82
83	83
84	84
85	85
86	86
87	87
88	88
89	89
90	90
91	91
92	92
93	93
94	94
95	95
96	96
97	97
98	98
99	99
100	100
101	101
102	102
103	103
104	104
105	105
106	106
107	107
108	108
109	109
110	110
111	111
112	112
113	113
114	114
115	115
116	116
117	117
118	118
119	119
120	120
121	121
122	122
123	123
124	124
125	125
126	126
127	127
128	128
129	129
130	130
131	131
132	132
133	133
134	134
135	135
136	136
137	137
138	138
139	139
140	140
141	141
142	142
143	143
144	144
145	145
146	146
147	147
148	148
149	149
150	150
151	151
152	152
153	153
154	154
155	155
156	156
157	157
158	158
159	159
160	160
161	161
162	162
163	163
164	164
165	165
166	166
167	167
168	168
169	169
170	170
171	171
172	172
173	173
174	174
175	175
176	176
177	177
178	178
179	179
180	180
181	181
182	182
183	183
184	184
185	185
186	186
187	187
188	188
189	189
190	190
191	191
192	192
193	193
194	194
195	195
196	196
197	197
198	198
199	199
200	200
201	201
202	202
203	203
204	204
205	205
206	206
207	207
208	208
209	209
210	210
211	211
212	212
213	213
214	214
215	215
216	216
217	217
218	218
219	219
220	220
221	221
222	222
223	223
224	224
225	225
226	226
227	227
228	228
229	229
230	230
231	231
232	232
233	233
234	234
235	235
236	236
237	237
238	238
239	239
240	240
241	241
242	242
\.


--
-- Data for Name: receiver_groups_receivers; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY receiver_groups_receivers (id, receiver_group_id, receiver_id) FROM stdin;
1	1	11
2	2	11
3	3	11
4	4	11
5	5	11
6	6	11
7	7	11
8	8	11
9	9	11
10	10	11
11	11	11
12	12	11
13	13	11
14	14	11
15	15	11
16	16	11
17	17	13
18	18	13
19	19	10
20	20	11
21	21	11
22	22	12
23	23	12
24	24	12
25	25	12
26	26	15
27	27	5
28	28	6
29	29	14
30	30	12
31	30	14
32	31	5
33	32	15
34	33	14
35	34	15
36	35	13
37	36	10
38	37	8
39	38	15
40	39	14
41	40	13
42	41	14
43	42	6
44	43	8
45	44	6
46	45	13
47	46	4
48	47	9
49	48	10
50	48	12
51	48	13
52	49	7
53	50	5
54	51	7
55	52	7
56	53	4
57	54	2
58	55	2
59	56	2
60	57	2
61	58	14
62	59	9
63	60	9
64	61	9
65	62	9
66	63	9
67	64	9
68	65	9
69	66	12
70	67	11
71	68	8
72	69	8
73	70	9
74	71	15
75	72	15
76	73	14
77	74	14
78	75	14
79	76	9
80	76	8
81	77	11
82	77	10
83	77	9
84	78	9
85	79	6
86	80	16
87	81	13
88	82	13
89	83	13
90	84	13
91	85	13
92	86	9
93	87	4
94	88	4
95	89	14
96	90	14
97	91	14
98	92	14
99	93	14
100	94	9
101	95	9
102	96	16
103	97	11
104	98	9
105	99	3
106	100	3
107	101	3
108	102	13
109	103	15
110	104	15
111	105	15
112	106	15
113	107	8
114	108	14
115	109	12
116	110	4
117	111	4
118	112	4
119	113	4
120	114	4
121	115	4
122	116	4
123	117	4
124	118	4
125	119	4
126	120	7
127	121	7
128	122	7
129	123	7
130	124	7
131	125	7
132	126	7
133	127	7
134	128	9
135	129	14
136	130	14
137	131	8
138	132	8
139	133	8
140	134	6
141	135	16
142	136	5
143	137	6
144	138	7
145	139	3
146	140	6
147	141	9
148	142	9
149	143	9
150	144	9
151	145	9
152	146	13
153	147	13
154	148	3
155	149	3
156	150	3
157	151	6
158	152	8
159	153	8
160	153	10
161	153	11
162	154	9
163	155	11
164	156	11
165	157	11
166	158	3
167	159	9
168	160	3
169	161	5
170	162	7
171	163	7
172	164	9
173	165	10
174	166	3
175	167	11
176	168	8
177	169	8
178	170	10
179	171	10
180	172	9
181	173	12
182	174	12
183	175	10
184	176	10
185	177	9
186	178	9
187	179	9
188	180	12
189	181	9
190	182	9
191	183	6
192	184	6
193	185	6
194	186	8
195	187	3
196	188	3
197	189	3
198	190	6
199	191	6
200	192	8
201	193	6
202	194	6
203	195	6
204	196	6
205	197	8
206	198	8
207	199	4
208	200	12
209	200	11
210	201	12
211	201	11
212	202	12
213	203	12
214	204	12
215	205	8
216	206	6
217	207	8
218	208	8
219	209	9
220	210	9
221	211	9
222	212	9
223	213	9
224	214	9
225	215	9
226	216	9
227	217	9
228	218	3
229	219	3
230	220	3
231	221	3
232	222	3
233	223	9
234	224	9
235	225	9
236	226	9
237	227	12
238	228	11
239	229	3
240	230	6
241	231	11
242	232	8
243	233	9
244	234	6
245	235	6
246	236	6
247	236	9
248	237	9
249	238	9
250	239	6
251	240	3
252	241	10
253	242	10
\.


--
-- Data for Name: receiver_schedule; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY receiver_schedule (id, receiver_id, start_date) FROM stdin;
\.


--
-- Data for Name: receivers; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY receivers (id, name, abbreviation, freq_low, freq_hi) FROM stdin;
1	NoiseSource	NS	0	0
2	Rcvr_RRI	RRI	0.10000000000000001	1.6000000000000001
3	Rcvr_342	342	0.28999999999999998	0.39500000000000002
4	Rcvr_450	450	0.38500000000000001	0.52000000000000002
5	Rcvr_600	600	0.51000000000000001	0.68999999999999995
6	Rcvr_800	800	0.68000000000000005	0.92000000000000004
7	Rcvr_1070	1070	0.91000000000000003	1.23
8	Rcvr1_2	L	1.1499999999999999	1.73
9	Rcvr2_3	S	1.73	2.6000000000000001
10	Rcvr4_6	C	3.9500000000000002	6.0999999999999996
11	Rcvr8_10	X	8	10
12	Rcvr12_18	Ku	12	15.4
13	Rcvr18_26	K	18	26.5
14	Rcvr26_40	Ka	26	39.5
15	Rcvr40_52	Q	38.200000000000003	49.799999999999997
16	Rcvr_PAR	MBA	80	100
17	Zpectrometer	Z	0	0
18	Holography	Hol	11.699999999999999	12.199999999999999
\.


--
-- Data for Name: repeats; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY repeats (id, repeat) FROM stdin;
1	Once
2	Weekly
3	Monthly
\.


--
-- Data for Name: semesters; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY semesters (id, semester) FROM stdin;
1	09A
2	09B
3	09C
4	08A
5	08B
6	08C
7	07A
8	07B
9	07C
10	06A
11	06B
12	06C
13	05A
14	05B
15	05C
16	04A
\.


--
-- Data for Name: sesshuns_email; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY sesshuns_email (id, user_id, email) FROM stdin;
1	1	fghigo@nrao.edu
2	2	jbraatz@nrao.edu
3	3	jharnett@nrao.edu
4	4	cbignell@nrao.edu
5	4	cbignell@gb.nrao.edu
6	5	dbalser@nrao.edu
7	6	tminter@nrao.edu
8	7	rmaddale@nrao.edu
9	8	sransom@nrao.edu
10	9	koneil@gb.nrao.edu
11	9	koneil@nrao.edu
12	10	bmason@nrao.edu
13	10	bmason@gb.nrao.edu
14	11	paul@paulruffle.com
15	12	jlockman@nrao.edu
16	13	glangsto@nrao.edu
17	14	rrosen@nrao.edu
18	15	aremijan@nrao.edu
19	16	gbower@astro.berkeley.edu
20	16	gbower@astron.berkeley.edu
21	17	bolatto@astro.umd.edu
22	18	eford@gmail.com
23	19	kalas@astro.berkeley.edu
24	20	jcondon@nrao.edu
25	21	greenhill@cfa.harvard.edu
26	21	lincoln@play
27	21	harvard.edu
28	22	p220hen@mpifr-bonn.mpg.de
29	23	flo@nrao.edu
30	24	reid@cfa.harvard.edu
31	24	mreid@cfa.harvard.edu
32	25	ck2v@virginia.edu
33	26	iz6@astro.physics.nyu.edu
34	27	atilak@cfa.harvard.edu
35	28	haol@astro.as.utexas.edu
36	29	plah@mso.anu.edu.au
37	30	brunthaler@mpifr-bonn.mpg.de
38	30	brunthal@mpifr-bonn.mpg.de
39	31	lsjouwer@nrao.edu
40	31	lsjouwer@aoc.nrao.edu
41	31	lsjouwerman@aoc.nrao.edu
42	32	garrett@astron.nl
43	33	l.loinard@astrosmo.unam.mx
44	34	jmiller@nrao.edu
45	35	mrupen@nrao.edu
46	35	mrupen@aoc.nrao.edu
47	36	amiodusz@aoc.nrao.edu
48	36	amiodusz@nrao.edu
49	37	vdhawan@aoc.nrao.edu
50	37	vdhawan@nrao.edu
51	38	elena@physics.ucsb.edu
52	39	P.Jonker@sron.nl
53	40	wbrisken@nrao.edu
54	40	wbrisken@aoc.nrao.edu
55	41	r.torres@astrosmo.unam.mx
56	42	william-peterson@uiowa.edu
57	43	robert-mutel@uiowa.edu
58	44	mgoss@nrao.edu
59	44	mgoss@aoc.nrao.edu
60	45	ubach@mpifr.de
61	45	ubach@mpifr-bonn.mpg.de
62	46	p459kri@mpifr-bonn.de
63	46	tkrichbaum@mpifrbonn.mpg.de
64	47	middelberg@astro.rub.de
65	47	enno.middelberg@csiro.au
66	48	walef@mpifr-bonn.mpg.de
67	49	awitzel@mpifr-bonn.mpg.de
68	50	azensus@mpifr-bonn.mpg.de
69	51	sjc@phys.unsw.edu.au
70	51	sjc@bat.phys.unsw.edu.au
71	52	Matthew.Whiting@csiro.au
72	53	jkw@phys.unsw.edu.au
73	53	jkw@bat.phys.unsw.edu.au
74	54	mmurphy@swin.edu.au
75	55	ylva@unm.edu
76	56	wiklind@stsci.edu
77	57	pfrancis@mso.anu.edu.au
78	58	ajbaker@physics.rutgers.edu
79	59	harris@astro.umd.edu
80	60	genzel@mpe.mpg.de
81	61	jmangum@nrao.edu
82	62	awootten@nrao.edu
83	63	nkanekar@nrao.edu
84	63	nkanekar@aoc.nrao.edu
85	64	sarae@uvic.ca
86	65	xavier@ucolick.org
87	66	briany@uvic.ca
88	67	yshirley@as.arizona.edu
89	68	jan.m.hollis@nasa.gov
90	68	mhollis@milkyway.gsfc.nasa.gov
91	68	jan.m.hollis@gsfc.nasa.gov
92	69	pjewell@nrao.edu
93	70	lovas@nist.gov
94	70	francis.lovas@nist.gov
95	71	jbregman@umich.edu
96	72	jairwin@umich.edu
97	73	pdemores@nrao.edu
98	74	bryan.jacoby@gmail.com
99	75	robert.ferdman@cnrs-orleans.fr
100	76	dbacker@astro.berkeley.edu
101	77	istairs@astro.ubc.ca
102	77	stairs@astro.ubc.ca
103	78	dnice@brynmawr.edu
104	78	dnice@princeton.edu
105	79	alommen@fandm.edu
106	80	mbailes@astro.swin.edu.au
107	81	icognard@cnrs-orleans.fr
108	82	Jayaram.Chengalur@atnf.csiro.au
109	82	chengalu@ncra.tifr.res.in
110	82	chengalu@gmrt.ernet.in
111	83	tbourke@cfa.harvard.edu
112	84	p.caselli@leeds.ac.uk
113	85	rfriesen@uvastro.phys.uvic.ca
114	86	james.difrancesco@nrc-cnrc.gc.ca
115	86	difrancesco@nrc.ca
116	87	pmyers@cfa.harvard.edu
117	88	jdarling@origins.colorado.edu
118	89	sedel@mix.wvu.edu
119	90	dludovic@mix.wvu.edu
120	91	Duncan.Lorimer@mail.wvu.edu
121	92	maura.mclaughlin@mail.wvu.edu
122	93	vlad.kondratiev@mail.wvu.edu
123	94	jridley2@mix.wvu.edu
124	95	earaya@nrao.edu
125	95	earaya@nmt.edu
126	96	phofner@nrao.edu
127	96	hofner@kestrel.nmt.edu
128	96	hofner_p@yahoo.com
129	97	ihoffman@sps.edu
130	98	linz@mpia-hd.mpg.de
131	98	linz@tls-tautenburg.de
132	99	s.kurtz@astrosmo.unam.mx
133	99	kurtz@astroscu.unam.mx
134	100	vrmarthi@ncra.tifr.res.in
135	101	ymaan4@gmail.com
136	102	avideshi@gmail.com
137	103	jsg5@st-andrews.ac.uk
138	104	ahales@nrao.edu
139	105	brenda.matthews@nrc-cnrc.gc.ca
140	106	campbellb@si.edu
141	106	campbellb@nasm.si.edu
142	107	campbell@astro.cornell.edu
143	107	campbell@naic.edu
144	107	campbell@astrosun.tn.cornell.edu
145	108	carterl@si.edu
146	108	carterl@nasm.si.edu
147	109	ghentr@si.edu
148	110	mnolan@naic.edu
149	110	nolan@naic.edu
150	111	naoto@ioa.s.u-tokyo.ac.jp
151	112	Tom.Millar@qub.ac.uk
152	113	Masao.Saito@nao.ac.jp
153	114	ck_yasui@ioa.s.u-tokyo.ac.jp
154	115	dennison@unca.edu
155	116	lhdicken@unca.edu
156	117	benjamir@uww.edu
157	118	bbutler@nrao.edu
158	118	bbutler@aoc.nrao.edu
159	119	ben.bussey@jhuapl.edu
160	120	mcintogc@morris.umn.edu
161	121	Ian.Smail@durham.ac.uk
162	122	rji@roe.ac.uk
163	123	ljh@astro.umd.edu
164	123	ljh@astro.caltech.edu
165	124	awb@astro.caltech.edu
166	125	linda@mpe.mpg.de
167	126	bertoldi@astro.uni-bonn.de
168	127	tgreve@submm.caltech.edu
169	128	neri@iram.fr
170	129	schapman@ast.cam.ac.uk
171	130	cox@iram.fr
172	131	omont@iap.fr
173	132	fernando@astro.columbia.edu
174	133	jules@astro.columbia.edu
175	134	jreynold@atnf.csiro.au
176	134	John.Reynolds@csiro.au
177	135	malloryr@gmail.com
178	136	zaven.arzoumanian@nasa.gov
179	136	zaven@milkyway.gsfc.nasa.gov
180	137	pfreire@naic.edu
181	138	rwr@astro.stanford.edu
182	139	Paul.Ray@nrl.navy.mil
183	139	paulr@xeus.nrl.navy.mil
184	140	dwilner@cfa.harvard.edu
185	141	rsl4v@virginia.edu
186	142	awolfe@kingpin.ucsd.edu
187	143	regina.jorgenson@physics.ucsd.edu
188	144	robishaw@physics.usyd.edu.au
189	145	cheiles@astron.berkeley.edu
190	145	heiles@astro.berkeley.edu
191	146	szonak@astro.umd.edu
192	147	csharon@physics.rutgers.edu
193	148	pvandenb@nrao.edu
194	149	hessels@astron.nl
195	149	J.W.T.Hessels@uva.nl
196	149	jhessels@science.uva.nl
197	150	bcotton@nrao.edu
198	151	simon.dicker@gmail.com
199	151	sdicker@hep.upenn.edu
200	152	PhillipKorngut@gmail.com
201	152	pkorngut@physics.upenn.edu
202	153	devlin@physics.upenn.edu
203	154	andersld@bu.edu
204	155	bania@bu.edu
205	156	rtr@virginia.edu
206	157	Neeraj.Gupta@atnf.csiro.au
207	158	anand@iucaa.ernet.in
208	159	ppetitje@iap.fr
209	159	petitjean@iap.fr
210	160	noterdae@iap.fr
211	161	sepulcre@arcetri.astro.it
212	162	cesa@arcetri.astro.it
213	163	brand@ira.inaf.it
214	163	brand@ira.bo.cnr.it
215	164	Francesco.Fontani@unige.ch
216	165	walmsley@arcetri.astro.it
217	166	wyrowski@mpifr-bonn.mpg.de
218	167	ccarilli@nrao.edu
219	167	ccarilli@aoc.nrao.edu
220	168	edaddi@cea.fr
221	169	jwagg@nrao.edu
222	169	jwagg@aoc.nrao.edu
223	170	maraven@astro.uni-bonn.de
224	171	walter@mpia.de
225	171	walter@mpia-hd.mpg.de
226	172	dr@astro.caltech.edu
227	173	dannerb@mpia-hd.mpg.de
228	174	med@noao.edu
229	175	delbaz@cea.fr
230	176	stern@zwolfkinder.jpl.nasa.gov
231	177	morrison@cfht.hawaii.edu
232	178	katie.m.chynoweth@vanderbilt.edu
233	179	cerni@damir.iem.csic.es
234	179	cerni@astro.iem.csic.es
235	180	lucie.vincent@obspm.fr
236	181	nicole.feautrier@obspm.fr
237	182	Pierre.Valiron@obs.ujf-grenoble.fr
238	183	afaure@obs.ujf-grenoble.fr
239	183	Alexandre.Faure@obs.ujf-grenoble.fr
240	184	annie.spielfiedel@obspm.fr
241	185	senent@damir.iem.csic.es
242	186	daniel@damir.iem.csic.es
243	187	maca@ph1.uni-koeln.de
244	188	eckart@ph1.uni-koeln.de
245	189	skoenig@ph1.uni-koeln.de
246	190	fischer@ph1.uni-koeln.de
247	191	jzuther@mpe.mpg.de
248	192	huchtmeier@mpifr-bonn.mpg.de
249	193	bertram@ph1.uni-koeln.de
250	194	a.m.swinbank@dur.ac.uk
251	195	kristen.coppin@durham.ac.uk
252	196	Alastair.Edge@durham.ac.uk
253	197	rse@astro.caltech.edu
254	198	dps@astro.caltech.edu
255	199	tajones@astro.caltech.edu
256	200	jeanpaul.kneib@gmail.com
257	200	kneib@astro.caltech.edu
258	201	ebeling@ifa.hawaii.edu
259	202	k.holley@vanderbilt.edu
260	203	clemens@physics.unc.edu
261	204	sandor@asiaa.sinica.edu.tw
262	205	pmkoch@asiaa.sinica.edu.tw
263	206	jaguirre@nrao.edu
264	207	stocke@colorado.edu
265	207	stocke@hyades.Colorado.EDU
266	208	ting.yan@colorado.edu
267	209	sheather@nrao.edu
268	210	eric@astro.columbia.edu
269	210	evg@astro.columbia.edu
270	211	nordhaus@astro.as.utexas.edu
271	212	nje@bubba.as.utexas.edu
272	212	nje@astro.as.utexas.edu
273	213	erik.rosolowsky@ubc.ca
274	214	ccyganow@astro.wisc.edu
275	215	John.Bally@colorado.edu
276	215	bally@janos.colorado.edu
277	216	Meredith.Drosback@casa.colorado.edu
278	217	jglenn@casa.colorado.edu
279	217	Jason.Glenn@colorado.edu
280	218	jpw@ifa.hawaii.edu
281	219	bradleet@colorado.edu
282	220	adam.ginsburg@colorado.edu
283	220	keflavich@gmail.com
284	221	vkaspi@physics.mcgill.ca
285	222	cordes@astro.cornell.edu
286	222	cordes@spacenet.tn.cornell.edu
287	223	david.champion@csiro.au
288	224	aarchiba@physics.mcgill.ca
289	225	jboyles5@mix.wvu.edu
290	226	mcphee@phas.ubc.ca
291	227	kasian@physics.ubc.ca
292	228	leeuwen@astron.nl
293	228	joeri@astro.berkeley.edu
294	229	deneva@astro.cornell.edu
295	230	fcrawfor@fandm.edu
296	231	afaulkne@jb.man.ac.uk
297	231	Andrew.Faulkner@manchester.ac.uk
298	232	mkramer@jb.man.ac.uk
299	232	Michael.Kramer@manchester.ac.uk
300	233	agl@jb.man.ac.uk
301	234	burgay@ca.astro.it
302	235	possenti@ca.astro.it
303	236	damico@ca.astro.it
304	237	cgilpin@fandm.edu
305	238	cgwinn@physics.ucsb.edu
306	239	michaeltdh@gmail.com
307	240	tania@prao.ru
308	241	S.Chatterjee@physics.usyd.edu.au
309	242	E.A.RubioHerrera@uva.nl
310	243	Ben.Stappers@manchester.ac.uk
311	244	dmeier@nrao.edu
312	245	zstork@parkland.edu
313	246	larry@umn.edu
314	247	farnsworth@astro.umn.edu
315	248	brown@physics.umn.edu
316	248	brown@astro.umn.edu
317	249	kmenten@mpifr-bonn.mpg.de
318	250	ehumphre@cfa.harvard.edu
319	250	ehumphreys@cfa.harvard.edu
320	251	jairo.armijos@estudiante.uam.es
321	252	jmartin.pintado@iem.cfmac.csic.es
322	253	requena@damir.iem.csic.es
323	254	smartin@cfa.harvard.edu
324	255	arturo@damir.iem.csic.es
325	256	Joseph.Lazio@nrl.navy.mil
326	256	lazio@rsd.nrl.navy.mil
327	257	kudo@a.phys.nagoya-u.ac.jp
328	258	torii@a.phys.nagoya-u.ac.jp
329	259	natsukok@xj.commufa.jp
330	260	morris@astro.ucla.edu
331	260	morris@osprey.astro.ucla.edu
332	261	m.walker@mawtech.com.au
333	262	willem@phys.utb.edu
334	263	aris.karastergiou@gmail.com
335	264	j314159@gmail.com
336	265	evan.keane@gmail.com
337	266	dick.manchester@csiro.au
338	266	rmanches@atnf.csiro.au
339	267	bperera@mix.wvu.edu
340	268	yugao@pmo.ac.cn
341	269	benjamin.zeiger@colorado.edu
342	270	gonzalez@phas.ubc.ca
343	271	joncas@phy.ulaval.ca
344	272	jean-francois.robitaille.1@ulaval.ca
345	273	douglas.marshall.1@ulaval.ca
346	274	mamd@ias.u-psud.fr
347	275	pgmartin@cita.utoronto.ca
348	276	megandecesar@gmail.com
349	277	miller@astro.umd.edu
350	278	amss@st-and.ac.uk
351	279	mmj@st-andrews.ac.uk
352	280	acc4@st-and.ac.uk
353	281	violette@nrao.edu
354	282	aroy@mpifr-bonn.mpg.de
355	283	sleurini@eso.org
356	283	sleurini@mpifr-bonn.mpg.de
357	284	jlm@ess.ucla.edu
358	285	marty@shannon.jpl.nasa.gov
359	285	martin.a.slade@jpl.nasa.gov
360	286	julianhaw@gmail.com
361	287	yan@physics.ucf.edu
362	288	alovell@agnesscott.edu
363	289	campins@physics.ucf.edu
364	290	mikek@ece.cornell.edu
365	291	jlicandr@iac.es
366	292	a.zijlstra@manchester.ac.uk
367	292	a.zijlstra@umist.ac.uk
368	293	maggie@hep.physics.mcgill.ca
369	293	maggie@physics.mcgill.ca
370	294	frank.marshall.gsfc.nasa.gov
371	295	
372	300	zparagi@jive.nl
373	301	chryssa.kouveliotou@nasa.gov
374	301	chryssa.kouveliotou@msfc.nasa.gov
375	302	enrico@ias.edu
376	303	langevelde@jive.nl
377	303	huib@jive.nfra.nl
378	304	szomoru@jive.nl
379	305	mkargo@jb.man.ac.uk
\.


--
-- Data for Name: session_types; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY session_types (id, type) FROM stdin;
1	open
2	fixed
3	windowed
4	vlbi
5	maintenance
6	commissioning
\.


--
-- Data for Name: sessions; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY sessions (id, project_id, session_type_id, observing_type_id, allotment_id, status_id, original_id, name, frequency, max_duration, min_duration, time_between) FROM stdin;
1	2	3	2	105	1	4213	BB240-01	9	8	8	\N
2	2	3	2	106	2	4214	BB240-02	9	8	8	\N
3	2	3	2	107	3	4215	BB240-03	9	8	8	\N
4	2	3	2	108	4	4216	BB240-04	9	8	8	\N
5	2	3	2	109	5	4217	BB240-05	9	8	8	\N
6	2	3	2	110	6	4218	BB240-06	9	8	8	\N
7	2	3	2	111	7	4219	BB240-07	9	8	8	\N
8	2	3	2	112	8	4220	BB240-08	9	8	8	\N
9	2	3	2	113	9	4221	BB240-09	9	8	8	\N
10	2	3	2	114	10	4222	BB240-10	9	8	8	\N
11	2	3	2	115	11	4223	BB240-11	9	8	8	\N
12	2	3	2	116	12	4224	BB240-12	9	8	8	\N
13	2	3	2	117	13	4225	BB240-13	9	8	8	\N
14	2	3	2	118	14	4226	BB240-14	9	8	8	\N
15	2	3	2	119	15	4227	BB240-15	9	8	8	\N
16	2	3	2	120	16	4229	BB240-16	9	8	8	\N
17	3	2	2	121	17	3713	BB261-01	22.199999999999999	10	10	\N
18	3	2	2	122	18	3742	BB261-02	22.199999999999999	12	12	\N
19	4	2	2	123	19	4246	BB268-01	0	16	16	\N
20	5	3	2	124	20	3712	BM290-01	9	5	5	\N
21	6	2	2	125	21	4248	BM306-01	9	6	6	\N
22	7	2	2	126	22	4249	BP157-01	13.699999999999999	10	10	\N
23	7	2	2	127	23	4291	BP157-02	13.699999999999999	10	10	\N
24	7	2	2	128	24	4292	BP157-03	13.699999999999999	10	10	\N
25	7	2	2	129	25	4293	BP157-04	13.699999999999999	10	10	\N
26	8	3	2	130	26	4046	GB065-01	44	16	16	\N
27	9	1	5	131	27	4539	GBT04A-003-01	0.59999999999999998	2.75	2.75	\N
28	9	1	5	132	28	4540	GBT04A-003-02	0.80000000000000004	2.75	2.75	\N
29	10	1	5	133	29	685	GBT05A-040-01	32.75	5.4199999999999999	3	\N
30	11	1	5	134	30	2342	GBT05C-027-01	32.75	5	3	\N
31	12	1	5	135	31	3136	GBT06C-048-01	0.59999999999999998	1.5	1.5	\N
32	13	1	5	136	32	1985	GBT07A-035-01	44	5	3	\N
33	14	1	5	137	33	2314	GBT07A-051-01	32.75	6	3	\N
34	14	1	5	138	34	2322	GBT07A-051-02	44	6	3	\N
35	14	1	5	139	35	4535	GBT07A-051-03	22.199999999999999	6	3	\N
36	14	1	5	140	36	4536	GBT07A-051-04	0	6	3	\N
37	14	1	5	141	37	4537	GBT07A-051-05	1.4399999999999999	6	3	\N
38	14	1	5	142	38	4544	GBT07A-051-06	44	6	3	\N
39	14	1	5	143	39	4545	GBT07A-051-07	32.75	6	3	\N
40	14	1	5	144	40	4546	GBT07A-051-08	22.199999999999999	6	3	\N
41	15	1	5	145	41	2103	GBT07A-086-01	32.75	2.8999999999999999	2.8999999999999999	\N
42	16	3	3	146	42	2106	GBT07A-087-01	0.80000000000000004	7.5	7.5	\N
43	16	3	3	147	43	2108	GBT07A-087-02	1.4399999999999999	7.5	7.5	\N
44	17	2	5	148	44	2351	GBT07C-013-01	0.80000000000000004	6	6	\N
45	18	1	5	149	45	2515	GBT07C-032-01	22.199999999999999	5	3	\N
46	19	1	5	150	46	2811	GBT08A-004-01	0.45000000000000001	6	3	\N
47	20	3	3	151	47	4044	GBT08A-037-01	2.1699999999999999	4.5	4.5	\N
48	21	3	5	152	48	2928	GBT08A-048-01	22.199999999999999	1.5	1.5	\N
49	22	1	5	153	49	2975	GBT08A-073-01	1.0700000000000001	0.59999999999999998	0.59999999999999998	\N
50	22	1	5	154	50	2977	GBT08A-073-02	0.59999999999999998	2.3999999999999999	2.3999999999999999	\N
51	22	1	5	155	51	2979	GBT08A-073-03	1.0700000000000001	0.59999999999999998	0.59999999999999998	\N
52	22	1	5	156	52	2985	GBT08A-073-04	1.0700000000000001	0.59999999999999998	0.59999999999999998	\N
53	22	1	5	157	53	3708	GBT08A-073-05	0.45000000000000001	2	2	\N
54	23	1	3	158	54	3019	GBT08A-085-01	0	7	3	\N
55	23	1	3	159	55	3020	GBT08A-085-02	0	7	3	\N
56	23	1	3	160	56	3021	GBT08A-085-03	0	6	3	\N
57	23	1	3	161	57	3022	GBT08A-085-04	0	7	3	\N
58	24	1	4	162	58	3489	GBT08A-092-01	32.75	3	3	\N
59	25	2	1	163	59	3992	GBT08B-005-01	2.1699999999999999	5	5	\N
60	25	2	1	164	60	4182	GBT08B-005-02	2.1699999999999999	3.75	3.75	\N
61	25	2	1	165	61	4183	GBT08B-005-03	2.1699999999999999	3.5	3.5	\N
62	25	2	1	166	62	4184	GBT08B-005-04	2.1699999999999999	3.5	3.5	\N
63	25	2	1	167	63	4494	GBT08B-005-05	2.1699999999999999	3.5	3.5	\N
64	25	2	1	168	64	4495	GBT08B-005-06	2.1699999999999999	3.5	3.5	\N
65	25	1	1	169	65	4497	GBT08B-005-07	2.1699999999999999	4	3	\N
66	26	1	5	170	66	3279	GBT08B-010-01	13.699999999999999	6	3	\N
67	27	1	5	171	67	4263	GBT08B-026-01	9	4	3	\N
68	28	1	5	172	68	3327	GBT08B-034-01	1.4399999999999999	3	3	\N
69	28	1	5	173	69	4542	GBT08B-034-02	1.4399999999999999	4.5	3	\N
70	29	1	1	174	70	4500	GBT08B-049-01	2.1699999999999999	4	3	\N
71	30	1	5	175	71	3501	GBT08C-005-01	44	1	1	\N
72	30	1	5	176	72	3502	GBT08C-005-02	44	4	3	\N
73	31	1	5	177	73	3512	GBT08C-009-01	32.75	8	3	\N
74	31	1	5	178	74	3514	GBT08C-009-02	32.75	8	3	\N
75	31	1	5	179	75	3515	GBT08C-009-03	32.75	8	3	\N
76	32	3	3	180	76	3527	GBT08C-014-01	2.1699999999999999	0.75	0.75	\N
77	32	3	3	181	77	3528	GBT08C-014-02	9	3	3	\N
78	33	3	3	182	78	3547	GBT08C-023-01	2.1699999999999999	3.75	3.75	\N
79	33	3	3	183	79	3548	GBT08C-023-02	0.80000000000000004	1	1	\N
80	34	1	4	184	80	3553	GBT08C-026-01	90	8	3	\N
81	35	1	5	185	81	3567	GBT08C-035-01	22.199999999999999	8.3300000000000001	3	\N
82	35	3	5	186	82	3569	GBT08C-035-02	22.199999999999999	8	8	\N
83	35	1	5	187	83	3570	GBT08C-035-03	22.199999999999999	10	3	\N
84	35	1	5	188	84	3746	GBT08C-035-04	22.199999999999999	10	3	\N
85	35	3	5	189	85	4043	GBT08C-035-05	22.199999999999999	18	18	\N
86	36	1	3	190	86	4042	GBT08C-049-01	2.1699999999999999	6	3	\N
87	37	1	5	191	87	3624	GBT08C-065-01	0.45000000000000001	7.3300000000000001	3	\N
88	37	1	5	192	88	3625	GBT08C-065-02	0.45000000000000001	4	3	\N
89	38	1	5	193	89	3631	GBT08C-070-01	32.75	7	3	\N
90	39	1	5	194	90	3643	GBT08C-073-01	32.75	7.5999999999999996	3	\N
91	39	1	5	195	91	3644	GBT08C-073-02	32.75	9	3	\N
92	39	1	5	196	92	3645	GBT08C-073-03	32.75	10.4	3	\N
93	39	1	5	197	93	3646	GBT08C-073-04	32.75	9.9000000000000004	3	\N
94	40	3	3	198	94	3651	GBT08C-076-01	2.1699999999999999	8	8	\N
95	40	3	3	199	95	3652	GBT08C-076-02	2.1699999999999999	9	9	\N
96	41	1	4	200	96	3655	GBT08C-078-01	90	8.5	3	\N
97	42	1	4	201	97	3781	GBT09A-002-01	9	5	3	\N
98	43	3	3	202	98	3998	GBT09A-003-01	2.1699999999999999	3	3	\N
99	44	1	5	203	99	3786	GBT09A-004-01	0.34000000000000002	5	3	\N
100	44	1	5	204	100	3787	GBT09A-004-02	0.34000000000000002	5	3	\N
101	44	1	5	205	101	3788	GBT09A-004-03	0.34000000000000002	5	3	\N
102	45	1	5	206	102	3802	GBT09A-010-01	22.199999999999999	5	3	\N
103	46	1	5	207	103	3810	GBT09A-012-01	44	7.1500000000000004	3	\N
104	46	1	5	208	104	3812	GBT09A-012-02	44	5.2000000000000002	3	\N
105	46	1	5	209	105	3813	GBT09A-012-03	44	5.8499999999999996	3	\N
106	46	1	5	210	106	3814	GBT09A-012-04	44	6.5	3	\N
107	47	1	5	211	107	3836	GBT09A-017-01	1.4399999999999999	12	3	\N
108	48	1	5	212	108	3842	GBT09A-021-01	32.75	5	3	\N
109	48	1	5	213	109	3843	GBT09A-021-02	13.699999999999999	5	3	\N
110	49	1	5	214	110	3999	GBT09A-025-01	0.45000000000000001	1.3999999999999999	1.3999999999999999	\N
111	49	1	5	215	111	4000	GBT09A-025-02	0.45000000000000001	3.3999999999999999	3	\N
112	49	1	5	216	112	4001	GBT09A-025-03	0.45000000000000001	1.3999999999999999	1.3999999999999999	\N
113	49	1	5	217	113	4002	GBT09A-025-04	0.45000000000000001	4.4199999999999999	3	\N
114	49	1	5	218	114	4003	GBT09A-025-05	0.45000000000000001	6.4000000000000004	3	\N
115	49	1	5	219	115	4004	GBT09A-025-06	0.45000000000000001	1.3999999999999999	1.3999999999999999	\N
116	49	1	5	220	116	4005	GBT09A-025-07	0.45000000000000001	1.3999999999999999	1.3999999999999999	\N
117	49	1	5	221	117	4006	GBT09A-025-08	0.45000000000000001	1.3999999999999999	1.3999999999999999	\N
118	49	1	5	222	118	4007	GBT09A-025-09	0.45000000000000001	1.3999999999999999	1.3999999999999999	\N
119	49	1	5	223	119	4008	GBT09A-025-10	0.45000000000000001	2.3999999999999999	2.3999999999999999	\N
120	50	1	5	224	120	3867	GBT09A-034-01	1.0700000000000001	2.2000000000000002	2.2000000000000002	\N
121	50	1	5	225	121	3868	GBT09A-034-02	1.0700000000000001	2.2000000000000002	2.2000000000000002	\N
122	50	1	5	226	122	3869	GBT09A-034-03	1.0700000000000001	2.2000000000000002	2.2000000000000002	\N
123	50	1	5	227	123	3870	GBT09A-034-04	1.0700000000000001	2.2000000000000002	2.2000000000000002	\N
124	50	1	5	228	124	3871	GBT09A-034-05	1.0700000000000001	2.2000000000000002	2.2000000000000002	\N
125	50	1	5	229	125	3872	GBT09A-034-06	1.0700000000000001	2.2000000000000002	2.2000000000000002	\N
126	50	1	5	230	126	3873	GBT09A-034-07	1.0700000000000001	2.2000000000000002	2.2000000000000002	\N
127	50	1	5	231	127	3874	GBT09A-034-08	1.0700000000000001	2.2000000000000002	2.2000000000000002	\N
128	51	3	3	232	128	3880	GBT09A-038-01	2.1699999999999999	0.5	0.5	\N
129	52	1	5	233	129	3882	GBT09A-040-01	32.75	10	3	\N
130	52	1	5	234	130	3883	GBT09A-040-02	32.75	10	3	\N
131	53	1	5	235	131	3894	GBT09A-046-01	1.4399999999999999	5.25	3	\N
132	53	1	5	236	132	3895	GBT09A-046-02	1.4399999999999999	5.5	3	\N
133	53	1	5	237	133	3896	GBT09A-046-03	1.4399999999999999	5.1299999999999999	3	\N
134	54	1	3	238	134	3901	GBT09A-049-01	0.80000000000000004	3	3	\N
135	55	1	4	239	135	4039	GBT09A-052-01	90	3	3	\N
136	56	1	5	240	136	3908	GBT09A-055-01	0.59999999999999998	1.73	1.73	\N
137	56	1	5	241	137	3909	GBT09A-055-02	0.80000000000000004	4.7699999999999996	3	\N
138	56	1	5	242	138	3910	GBT09A-055-03	1.0700000000000001	1.3	1.3	\N
139	57	1	3	243	139	3917	GBT09A-058-01	0.34000000000000002	2	2	\N
140	57	1	3	244	140	4023	GBT09A-058-02	0.80000000000000004	2	2	\N
141	58	1	3	245	141	3926	GBT09A-062-01	2.1699999999999999	10.449999999999999	3	\N
142	58	1	3	246	142	3927	GBT09A-062-02	2.1699999999999999	10.550000000000001	3	\N
143	59	3	1	247	143	3935	GBT09A-070-01	2.1699999999999999	2	2	\N
144	59	3	1	248	144	4498	GBT09A-070-02	2.1699999999999999	4	4	\N
145	59	3	1	249	145	4499	GBT09A-070-03	2.1699999999999999	2	2	\N
146	60	1	5	250	146	3965	GBT09A-080-01	22.199999999999999	6.5	3	\N
147	60	1	5	251	147	3966	GBT09A-080-02	22.199999999999999	2	2	\N
148	61	1	3	252	148	3967	GBT09A-081-01	0.34000000000000002	3.5	3	\N
149	61	1	3	253	149	3969	GBT09A-081-02	0.34000000000000002	3.5	3	\N
150	62	1	3	254	150	4200	GBT09A-092-01	0.34000000000000002	8	3	\N
151	62	1	3	255	151	4210	GBT09A-092-02	0.80000000000000004	8	3	\N
152	62	1	3	256	152	4211	GBT09A-092-03	1.4399999999999999	8	3	\N
153	63	1	3	257	153	4203	GBT09A-093-01	9	12	3	\N
154	64	1	3	258	154	4212	GBT09A-095-01	2.1699999999999999	6	3	\N
155	65	1	5	259	155	4304	GBT09A-099-01	9	2.5	2.5	\N
156	66	1	4	260	156	4055	GBT09B-001-01	9	5	3	\N
157	67	1	4	261	157	4056	GBT09B-002-01	9	5	3	\N
158	68	1	3	262	158	4058	GBT09B-003-01	0.34000000000000002	3.5	3	\N
159	68	1	3	263	159	4059	GBT09B-003-02	2.1699999999999999	4.5	3	\N
160	69	1	3	264	160	4060	GBT09B-004-01	0.34000000000000002	5.5	3	\N
161	70	1	5	265	161	4061	GBT09B-005-01	0.59999999999999998	1.73	1.73	\N
162	70	1	5	266	162	4063	GBT09B-005-02	1.0700000000000001	1.3	1.3	\N
163	70	1	5	267	163	4065	GBT09B-005-03	1.0700000000000001	3.8999999999999999	3	\N
164	71	3	3	268	164	4067	GBT09B-006-01	2.1699999999999999	1.25	1.25	\N
165	71	1	3	269	165	4068	GBT09B-006-02	0	2	2	\N
166	72	3	3	270	166	4071	GBT09B-008-01	0.34000000000000002	9	9	\N
167	73	1	5	271	167	4191	GBT09B-010-01	9	4	3	\N
168	74	1	4	272	168	4086	GBT09B-012-01	1.4399999999999999	11.199999999999999	3	\N
169	74	1	4	273	169	4087	GBT09B-012-02	1.4399999999999999	12	3	\N
170	75	1	5	274	170	4089	GBT09B-013-01	0	5	3	\N
171	75	1	5	275	171	4090	GBT09B-013-02	0	5	3	\N
172	76	1	3	276	172	4091	GBT09B-014-01	2.1699999999999999	4.5	3	\N
173	77	1	5	277	173	4092	GBT09B-015-01	13.699999999999999	5	3	\N
174	77	1	5	278	174	4282	GBT09B-015-02	13.699999999999999	5	3	\N
175	78	1	3	279	175	4095	GBT09B-017-01	0	3.5	3	\N
176	78	1	3	280	176	4096	GBT09B-017-02	0	3.5	3	\N
177	78	1	3	281	177	4097	GBT09B-017-03	2.1699999999999999	3	3	\N
178	78	1	3	282	178	4098	GBT09B-017-04	2.1699999999999999	3	3	\N
179	79	3	3	283	179	4177	GBT09B-018-01	2.1699999999999999	1.75	1.75	\N
180	79	1	3	284	180	4179	GBT09B-018-02	13.699999999999999	2	2	\N
181	79	3	3	285	181	4194	GBT09B-018-03	2.1699999999999999	1.75	1.75	\N
182	80	1	3	286	182	4105	GBT09B-023-01	2.1699999999999999	4.5	3	\N
183	80	1	3	287	183	4106	GBT09B-023-02	0.80000000000000004	6.5	3	\N
184	81	1	3	288	184	4107	GBT09B-024-01	0.80000000000000004	9.5	3	\N
185	81	1	3	289	185	4108	GBT09B-024-02	0.80000000000000004	6.25	3	\N
186	82	1	5	290	186	4109	GBT09B-025-01	1.4399999999999999	4.5	3	\N
187	83	1	3	291	187	4110	GBT09B-026-01	0.34000000000000002	4	3	\N
188	84	3	3	292	188	4114	GBT09B-028-01	0.34000000000000002	5.5	5.5	\N
189	84	1	3	293	189	4116	GBT09B-028-02	0.34000000000000002	5.5	3	\N
190	85	3	3	294	190	4117	GBT09B-029-01	0.80000000000000004	4.25	4.25	\N
191	85	3	3	295	191	4118	GBT09B-029-02	0.80000000000000004	5.5	5.5	\N
192	85	3	3	296	192	4119	GBT09B-029-03	1.4399999999999999	5.5	5.5	\N
193	85	1	3	297	193	4120	GBT09B-029-04	0.80000000000000004	7.5	3	\N
194	85	1	3	298	194	4198	GBT09B-029-05	0.80000000000000004	7.5	3	\N
195	86	3	3	299	195	4123	GBT09B-031-01	0.80000000000000004	2.3300000000000001	2.3300000000000001	\N
196	86	3	3	300	196	4196	GBT09B-031-02	0.80000000000000004	2.25	2.25	\N
197	87	1	5	301	197	4128	GBT09B-034-01	1.4399999999999999	7.75	3	\N
198	87	1	5	302	198	4129	GBT09B-034-02	1.4399999999999999	10	3	\N
199	88	1	5	303	199	4285	GBT09B-035-01	0.45000000000000001	4	3	\N
200	89	1	5	304	200	4131	GBT09B-036-01	13.699999999999999	12	3	\N
201	89	1	5	305	201	4132	GBT09B-036-02	13.699999999999999	10.800000000000001	3	\N
202	90	1	5	306	202	4135	GBT09B-039-01	13.699999999999999	2	2	\N
203	91	1	5	307	203	4137	GBT09B-040-01	13.699999999999999	9	3	\N
204	91	1	5	308	204	4138	GBT09B-040-02	13.699999999999999	10	3	\N
205	92	3	3	309	205	4139	GBT09B-041-01	1.4399999999999999	8.5	8.5	\N
206	92	3	3	310	206	4140	GBT09B-041-02	0.80000000000000004	8.5	8.5	\N
207	92	3	3	311	207	4141	GBT09B-041-03	1.4399999999999999	3	3	\N
208	93	1	5	312	208	4142	GBT09B-042-01	1.4399999999999999	8	3	\N
209	94	1	3	313	209	4143	GBT09B-043-01	2.1699999999999999	1	1	\N
210	94	1	3	314	210	4146	GBT09B-043-02	2.1699999999999999	1	1	\N
211	94	1	3	315	211	4147	GBT09B-043-03	2.1699999999999999	1	1	\N
212	94	1	3	316	212	4150	GBT09B-043-04	2.1699999999999999	1	1	\N
213	94	1	3	317	213	4152	GBT09B-043-05	2.1699999999999999	1	1	\N
214	94	1	3	318	214	4153	GBT09B-043-06	2.1699999999999999	1	1	\N
215	94	1	3	319	215	4154	GBT09B-043-07	2.1699999999999999	1	1	\N
216	94	1	3	320	216	4156	GBT09B-043-08	2.1699999999999999	1	1	\N
217	94	1	3	321	217	4157	GBT09B-043-09	2.1699999999999999	1	1	\N
218	95	2	4	322	218	4158	GBT09B-044-01	0.34000000000000002	6	6	\N
219	95	2	4	323	219	4298	GBT09B-044-02	0.34000000000000002	6	6	\N
220	95	2	4	324	220	4299	GBT09B-044-03	0.34000000000000002	6	6	\N
221	95	2	4	325	221	4300	GBT09B-044-04	0.34000000000000002	6	6	\N
222	95	2	4	326	222	4301	GBT09B-044-05	0.34000000000000002	6	6	\N
223	96	1	3	327	223	4160	GBT09B-045-01	2.1699999999999999	3.5	3	\N
224	96	1	3	328	224	4161	GBT09B-045-02	2.1699999999999999	3.5	3	\N
225	96	1	3	329	225	4162	GBT09B-045-03	2.1699999999999999	3.5	3	\N
226	96	1	3	330	226	4163	GBT09B-045-04	2.1699999999999999	3.5	3	\N
227	97	1	5	331	227	4166	GBT09B-046-01	13.699999999999999	6	3	\N
228	98	2	1	332	228	4286	GBT09B-048-01	9	1	1	\N
229	99	1	3	333	229	4532	GBT09B-055-01	0.34000000000000002	2	2	\N
230	99	1	3	334	230	4533	GBT09B-055-02	0.80000000000000004	2	2	\N
231	100	1	5	335	231	4534	GBT09B-056-01	9	1.5	1.5	\N
232	101	1	5	336	232	4538	GBT09B-057-01	1.4399999999999999	9	3	\N
233	102	1	3	337	233	4264	GLST021097-01	2.1699999999999999	2	2	\N
234	102	1	3	338	234	4265	GLST021097-02	0.80000000000000004	2	2	\N
235	102	1	3	339	235	4266	GLST021097-03	0.80000000000000004	4	3	\N
236	102	1	3	340	236	4267	GLST021097-04	2.1699999999999999	8	3	\N
237	103	1	3	341	237	4256	GLST021177-01	2.1699999999999999	8	3	\N
238	104	3	3	342	238	4250	GLST021284-01	2.1699999999999999	4	4	\N
239	104	3	3	343	239	4251	GLST021284-02	0.80000000000000004	1	1	\N
240	105	1	3	344	240	4261	GLST021296-01	0.34000000000000002	10	3	\N
241	106	1	3	345	241	4262	GLST021302-01	0	3	3	\N
242	107	3	2	346	242	2784	GP044-01	0	7	7	\N
\.


--
-- Data for Name: status; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY status (id, enabled, authorized, complete, backup) FROM stdin;
1	f	t	f	f
2	f	t	f	f
3	f	t	f	f
4	f	t	f	f
5	f	t	f	f
6	f	t	f	f
7	f	t	f	f
8	f	t	f	f
9	f	t	f	f
10	f	t	f	f
11	f	t	f	f
12	f	t	f	f
13	f	t	f	f
14	f	t	f	f
15	f	t	f	f
16	f	t	f	f
17	f	t	f	f
18	f	t	f	f
19	f	t	f	f
20	f	t	f	f
21	f	t	f	f
22	f	t	f	f
23	f	t	f	f
24	f	t	f	f
25	f	t	f	f
26	f	t	f	f
27	f	t	f	f
28	f	t	f	f
29	f	t	f	f
30	f	t	f	f
31	f	t	f	f
32	f	t	f	f
33	f	t	f	f
34	f	t	f	f
35	f	t	f	f
36	f	t	f	f
37	f	t	f	f
38	f	t	f	f
39	f	t	f	f
40	f	t	f	f
41	f	t	f	f
42	f	t	f	f
43	f	t	f	f
44	f	t	f	f
45	f	t	f	f
46	f	t	f	f
47	f	t	f	f
48	f	t	f	f
49	f	t	f	f
50	f	t	f	f
51	f	t	f	f
52	f	t	f	f
53	f	t	f	f
54	f	t	f	f
55	f	t	f	f
56	f	t	f	f
57	f	t	f	f
58	f	t	f	f
59	f	t	f	f
60	f	t	f	f
61	f	t	f	f
62	f	t	f	f
63	f	t	f	f
64	f	t	f	f
65	f	t	f	f
66	f	t	f	f
67	f	t	f	f
68	f	t	f	f
69	f	t	f	f
70	f	t	f	f
71	f	t	f	f
72	f	t	f	f
73	f	t	f	f
74	f	t	f	f
75	f	t	f	f
76	f	t	f	f
77	f	t	f	f
78	f	t	f	f
79	f	t	f	f
80	f	t	f	f
81	f	t	f	f
82	f	t	f	f
83	f	t	f	f
84	f	t	f	f
85	f	t	f	f
86	f	t	f	f
87	f	t	f	f
88	f	t	f	f
89	f	t	f	f
90	f	t	f	f
91	f	t	f	f
92	f	t	f	f
93	f	t	f	f
94	f	t	f	f
95	f	t	f	f
96	f	t	f	f
97	f	t	f	f
98	f	t	f	f
99	f	t	f	f
100	f	t	f	f
101	f	t	f	f
102	f	t	f	f
103	f	t	f	f
104	f	t	f	f
105	f	t	f	f
106	f	t	f	f
107	f	t	f	f
108	f	t	f	f
109	f	t	f	f
110	f	t	f	f
111	f	t	f	f
112	f	t	f	f
113	f	t	f	f
114	f	t	f	f
115	f	t	f	f
116	f	t	f	f
117	f	t	f	f
118	f	t	f	f
119	f	t	f	f
120	f	t	f	f
121	f	t	f	f
122	f	t	f	f
123	f	t	f	f
124	f	t	f	f
125	f	t	f	f
126	f	t	f	f
127	f	t	f	f
128	f	t	f	f
129	f	t	f	f
130	f	t	f	f
131	f	t	f	f
132	f	t	f	f
133	f	t	f	f
134	f	t	f	f
135	f	t	f	f
136	f	t	f	f
137	f	t	f	f
138	f	t	f	f
139	f	t	f	f
140	f	t	f	f
141	f	t	f	f
142	f	t	f	f
143	f	t	f	f
144	f	t	f	f
145	f	t	f	f
146	f	t	f	f
147	f	t	f	f
148	f	t	f	f
149	f	t	f	f
150	f	t	f	f
151	f	t	f	f
152	f	t	f	f
153	f	t	f	f
154	f	t	f	f
155	f	t	f	f
156	f	t	f	f
157	f	t	f	f
158	f	t	f	f
159	f	t	f	f
160	f	t	f	f
161	f	t	f	f
162	f	t	f	f
163	f	t	f	f
164	f	t	f	f
165	f	t	f	f
166	f	t	f	f
167	f	t	f	f
168	f	t	f	f
169	f	t	f	f
170	f	t	f	f
171	f	t	f	f
172	f	t	f	f
173	f	t	f	f
174	f	t	f	f
175	f	t	f	f
176	f	t	f	f
177	f	t	f	f
178	f	t	f	f
179	f	t	f	f
180	f	t	f	f
181	f	t	f	f
182	f	t	f	f
183	f	t	f	f
184	f	t	f	f
185	f	t	f	f
186	f	t	f	f
187	f	t	f	f
188	f	t	f	f
189	f	t	f	f
190	f	t	f	f
191	f	t	f	f
192	f	t	f	f
193	f	t	f	f
194	f	t	f	f
195	f	t	f	f
196	f	t	f	f
197	f	t	f	f
198	f	t	f	f
199	f	t	f	f
200	f	t	f	f
201	f	t	f	f
202	f	t	f	f
203	f	t	f	f
204	f	t	f	f
205	f	t	f	f
206	f	t	f	f
207	f	t	f	f
208	f	t	f	f
209	f	t	f	f
210	f	t	f	f
211	f	t	f	f
212	f	t	f	f
213	f	t	f	f
214	f	t	f	f
215	f	t	f	f
216	f	t	f	f
217	f	t	f	f
218	f	t	f	f
219	f	t	f	f
220	f	t	f	f
221	f	t	f	f
222	f	t	f	f
223	f	t	f	f
224	f	t	f	f
225	f	t	f	f
226	f	t	f	f
227	f	t	f	f
228	f	t	f	f
229	f	t	f	f
230	f	t	f	f
231	f	t	f	f
232	f	t	f	f
233	f	t	f	f
234	f	t	f	f
235	f	t	f	f
236	f	t	f	f
237	f	t	f	f
238	f	t	f	f
239	f	t	f	f
240	f	t	f	f
241	f	t	f	f
242	f	t	f	f
\.


--
-- Data for Name: systems; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY systems (id, name, v_unit, h_unit) FROM stdin;
1	J2000	ra	dec
2	B1950	ra	dec
3	Galactic	lat	long
4	RaDecOfDate	ra	dec
5	AzEl	az	el
6	HaDec	ra	dec
7	ApparentRaDec	ra	dec
8	CableWrap	az	el
9	Encoder	az	el
\.


--
-- Data for Name: targets; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY targets (id, session_id, system_id, source, vertical, horizontal) FROM stdin;
1	1	1	644C,1207	-0.111177473352	4.5814892864900001
2	2	1	2066,3522	0.085346600422500002	2.35619449019
3	3	1	803,4247	-0.026529004630300002	5.3668874498800001
4	4	1	661A/B,1224	0.25918139392099998	4.7123889803800001
5	5	1	729,867B	-0.38798669271800001	5.4977871437800001
6	6	1	1230A/B,866	0.082903139469700002	5.4977871437800001
7	7	1	4063,LSRJ1835+3259	0.63809237452900003	4.9741883681800001
8	8	1	1005A,84	-0.29443704481100003	0.39269908169899997
9	9	1	873,53B	0.86620690776499998	0.1308996939
10	10	1	686,1224	0.022863813201100001	4.9741883681800001
11	11	1	412B,3789	0.63529984772600001	3.4033920413900001
12	12	1	4360,65A/B	-0.29775317038999999	0.26179938779900003
13	13	1	278C,1116A/B	0.450644012865	2.35619449019
14	14	1	102,109	0.44017203735299998	0.78539816339699997
15	15	1	234A/B,285	0.0064577182323800001	1.96349540849
16	16	1	896A,3146	0.29251718263400001	0.39269908169899997
17	17	1	Mrk1419	1.06203284984	2.6179938779900001
18	19	1	* (5)	0.72134457984900002	0.26179938779900003
19	20	1	V404Cyg	0.59114301764999999	5.8904862254800001
20	21	1	V773TauA on6/17or8/7or9/27	0.49218284906199999	0.52359877559800005
21	22	1	UXArietis * (4)	0.56932640200100004	0.908443875663
22	23	1	UXArietis * (4)	0.56932640200100004	0.908443875663
23	24	1	UXArietis * (4)	0.56932640200100004	0.908443875663
24	25	1	UXArietis * (4)	0.56932640200100004	0.908443875663
25	26	1	CygA	0.71087260433699995	5.6286868376800001
26	27	1	0213-026	-0.041538836197499998	0.59166661642600005
27	28	1	0213-026	-0.041538836197499998	0.59166661642600005
28	29	1	SMMJ02399-0136	-0.0279252680319	0.69638637154600003
29	30	1	G34.3,S68N,DR21OH	0.0223402144255	4.8432886742800001
30	31	1	PKS B0237-233/confirm	-0.40404372183699999	0.69900436542400002
31	32	1	PKS1830-21	-0.36756634046999997	4.8589966375499998
32	33	1		-0.49514990879100002	4.6574111089499999
33	34	1		-0.49514990879100002	4.6574111089499999
34	35	1		-0.49514990879100002	4.6574111089499999
35	36	1		-0.49514990879100002	4.6574111089499999
36	37	1		-0.49514990879100002	4.6574111089499999
37	38	1		-0.49514990879100002	4.6574111089499999
38	39	1		-0.49514990879100002	4.6574111089499999
39	40	1		-0.49514990879100002	4.6574111089499999
40	41	1	3C279	-0.10105456369	3.3876840781199999
41	42	1	* (12)	-0.030194196059500002	4.0735984741499998
42	43	1	* (12)	-0.030194196059500002	4.0735984741499998
43	44	1	PKS 1830-21	-0.36756634046999997	4.8589966375499998
44	45	1	Oph A	-0.42586033748699997	4.3039819354200004
45	46	1	J0414+0534-host	0.097389372261299997	1.1100294042700001
46	47	1	* (9)	0.057770398240999998	4.21235214969
47	48	1	NGC7538 IRS1	1.0728538912000001	6.0815997785700002
48	49	1	* (5)	0.50527281845200001	2.7462755780100001
49	50	1	TXS0213-026 * (4)	0.319395253115	2.1336650105600001
50	51	1	* (5)	0.50527281845200001	2.7462755780100001
51	52	1	* (5)	0.50527281845200001	2.7462755780100001
52	53	1		0.61383229792600003	0.21467549799499999
53	54	1	B0031-07 * (4)	0.35063664672599998	0.61261056744999998
54	55	1	B0809+74 * (4)	0.334579617607	2.2881266493600001
55	56	1	B1237+25,B1702-19,B1919+21	0.16091935703400001	4.2856559782700003
56	57	1	B1929+10 * (4)	0.28937558998099999	5.47946118664
57	58	1	HD104860	0.63669611112799995	1.5995942594499999
58	59	1	Moon	0	0
59	60	1	Moon	0	0
60	61	1	Moon	0	0
61	62	1	Moon	0	0
62	63	1	Moon	0	0
63	64	1	Moon	0	0
64	65	1	Moon	0	0
65	66	1	EC2-SouthPeak	1.0192722831600001	0.73565627971600001
66	67	1		0.66130525358100001	5.3852134070300002
67	68	1	3C286	0.53249995478300005	3.53952772304
68	69	1	SC 38.73-13.44 * (4)	-0.0153588974176	5.1940998539400001
69	70	1	LRO	0	0
70	71	1	VY CMa	-0.449771348239	1.93207948196
71	72	1	3C286	0.53249995478300005	3.53952772304
72	73	1	SMMJ105158.02O,SMMJ105207.56O	1.0002481943199999	2.8457593453799999
73	74	1	SMMJ123707.21D,SMMJ123600.10B	1.08454759719	3.3012902801499999
74	75	1	SMMJ123622.65O,SMMJ123712.05B	1.0862929264400001	3.3012902801499999
75	76	1	XTE J1810-197	-0.344353461418	4.7542768824300001
76	77	1	XTE J1810-197	-0.344353461418	4.7542768824300001
77	78	1	* (5)	0.79325214503100006	4.2175881374399999
78	79	1	PSR J1833-1034	-0.18448130193599999	4.8589966375499998
79	80	1	vega	0.67683868392299995	4.8747046008200003
80	81	1	6dF galaxies	-0.26179938779900003	3.1415926535900001
81	82	1	Monitor 180dy	0.17453292519899999	3.1415926535900001
82	83	1	SDSS galaxies	0.17453292519899999	3.4033920413900001
83	84	1	SDSS galaxies	0.17453292519899999	3.4033920413900001
84	85	1	Monitor galaxies	0.17453292519899999	3.1415926535900001
85	86	1	NGC6517,M22	-0.156381500979	4.7202429620200004
86	87	1	PKS0458-02	0.24888395133399999	2.4268803248999999
87	88	1	3C286	0.24888395133399999	2.4268803248999999
88	89	1	Cloverleaf,CRSSJ1415.1+1140	0.20071286397900001	3.73325927002
89	90	1	SMMJ12360+6210 * (2)	1.08542026182	3.3012902801499999
90	91	1	MMJ154127+6615,MMJ154127+6616	1.1564551623699999	4.1076323945700004
91	92	1	FLSIRSY10,FLSIRSW4	1.0313150550000001	4.5474553660700003
92	93	1	SMMJ16363+4055 * (3)	0.71541046039199996	4.3484878313399999
93	94	1	Ter5	-0.43249258864399998	4.6600291028200003
94	95	1	NGC6440,NGC6441,M28	-0.47874381382199999	4.71762496814
95	96	1	Cynus A	0.71087260433699995	5.2333697620999997
96	97	1	* (10)	0.061610122595400003	4.9715703743099997
97	98	1	* (8)	-0.482059939401	4.6888270354800001
98	99	1	J0839+2002	0.34976398209999998	2.2645647044600001
99	100	1	J0852+2431	0.42795473258900002	2.3247785636599998
100	101	1	J1223+5037	0.88366020028500003	3.2463124087100002
101	102	1	G10.47+0.03,G24.78+0.08_A1	-0.23614304779500001	4.8092547538700003
102	103	1	* (5)	1.0866419922899999	3.3039082740299999
103	104	1	* (5)	1.0866419922899999	3.3039082740299999
104	105	1	* (5)	1.0866419922899999	3.3039082740299999
105	106	1	* (5)	1.0866419922899999	3.3039082740299999
106	107	1	Wright Main,Wright-M33	0.506145483078	0.35866516128499998
107	108	1	* (6)	0.37524578917899998	1.2068951777500001
108	109	1	* (6)	0.37524578917899998	1.2068951777500001
109	110	1	PKS1055-301	-0.53092915845699995	2.8719392841600002
110	111	1	CTQ247 0405-443	-0.77091193060600005	1.07861347773
111	112	1	PKS1230-101	-0.18186330805799999	3.2855823168799998
112	113	1	TXS1157+014	0.020943951023899999	3.1415926535900001
113	114	1	PKSB0347-211	-0.367391807545	1.00269165527
114	115	1	TXS1452+502	0.87371182354800003	3.9008108782100002
115	116	1	TXS1755+578	1.0089748405800001	4.69406302324
116	117	1	TXS1850+402	0.70371675440399994	4.9427724416499998
117	118	1	QSO1215+333	0.57752944948499996	3.2175144760499998
118	119	1	TXS0620+389	0.67980574365199997	1.6781340757900001
119	120	1	RS30	0.013962634016	0.28797932657899999
120	121	1	RS38	0.0083775804095700002	0.39531707557700002
121	122	1	RS56	-0.0078539816339699992	0.604756585816
122	123	1	RS59	-0.012217304764	0.72256631032600005
123	124	1	RS62	0.018849555921499998	0.80372412054300002
124	125	1	RS63	-0.015707963267899999	0.80634211442100001
125	126	1	RS65	0.0202458193231	0.83775804095700002
126	127	1	RS67	0.0069813170079800002	0.908443875663
127	128	1	M22/added to 8C49	-0.417133691227	4.87208660694
128	129	1	A2218arc z=2.52 * (3)	1.0194468160900001	3.2620203719799998
129	130	1	A2218arc z=2.52 * (3)	1.0194468160900001	3.2620203719799998
130	131	1	CanesIa,CanesIb	0.66863563643900004	3.29605429239
131	132	1	N45	-0.40578905108899999	0.054977871437800002
132	133	1	N672a,N672b	0.52656583532699996	0.48432886742800002
133	134	1	* (6)	0.189717289692	2.42164433714
134	135	1	RX J1347-1149/A1835	-0.205076187109	3.6102135577499999
135	136	1	B2 1030+39	0.69115038379000004	2.7646015351600002
136	137	1	4C+24.19 * (3)	0.77492618788500001	2.8509953331300002
137	138	1	PKS 0001-11 * (3)	0.049043751981	1.5550883635299999
138	139	1	New Pulsars - unknown	-0.26179938779900003	2.09439510239
139	140	1	New Pulsars - unknown	-0.26179938779900003	2.09439510239
140	141	1	J1834-087	0.15271630955000001	4.8642326253099997
141	142	1	J1837-069	-0.12007865253699999	4.8747046008200003
142	143	1	LRO	0	0
143	144	1	3C286: 13:31:08 +30 30 32.9	0	0
144	145	1		0	0
145	146	1	* (143) 1033_1	0.0101229096616	4.9427724416499998
146	147	1	* (31) 1033_2	0.042236967898299997	4.9610983987899999
147	148	1	PSRJ1012+5307	0.92711889865899999	2.6729717494299998
148	149	1	PSRJ2124-3358,PSRJ2322+2057	-0.113620934305	5.8616882928200003
149	150	1	All Sky Drift Scans	0	3.1415926535900001
150	151	1	All Sky Drift Scans	0	3.1415926535900001
151	152	1	All Sky Drift Scans	0	3.1415926535900001
152	153	1	Galactic Plane,Orion	0.039968039870700002	0.71994831644799995
153	154	1	J0348+04	0.0794124809657	0.99745566751500003
154	155	1	0218+357	0.62727133316700001	0.61522856132799997
155	156	1	* (10)	-0.49305551368799999	4.6547931150700004
156	157	1	HII 01,HII 02,HII 03,HII 04	-0.118856922061	4.87208660694
157	158	1	PSR J1723-28	-0.50021136362200003	4.5526913538300002
158	159	1	PSR J1723-28	-0.50021136362200003	4.5526913538300002
159	160	1	PSR B0834+06	0.107686814848	2.2567107228299998
160	161	1	B2 1030+39	0.69115038379000004	2.7646015351600002
161	162	1	PKS 0001-11 * (3)	0.049043751981	1.5550883635299999
162	163	1	* (5)	0.0303687289847	2.1572269554600001
163	164	1	* (7)	0.069289571304200007	4.9898963314499998
164	165	1	PSR J1841-0457,PSR J1841-0457	-0.086568330898899995	4.8930305579700004
165	166	1	M31R001 * (4)	0.71855205304600001	0.19111355309299999
166	167	1	IRS16293-2422	-0.42725660088799999	4.3301618741999999
167	168	1	* (6)	0.19931660057799999	2.2148228207799998
168	169	1	A1367,N45,NGC6251,HB13	0.68294733630500004	3.2489304025900001
169	170	1	PSSJ2322	0.344527994344	6.1182516928700004
170	171	1	APM08279	0.92066118042699996	2.2331487779299999
171	172	1	* (9)	0.237888377047	3.8772489333100002
172	173	1	MC-0.02,MC-0.11,MC+0.693	-0.50823987818100003	4.65217512119
173	174	1	MC-0.02,MC-0.11,MC+0.693	-0.50823987818100003	4.65217512119
174	175	1	Arches cluster	-0.50300389042500004	4.6495571273099996
175	176	1	Quintuplet cluster	-0.50317842334999996	4.65217512119
176	177	1	Arches cluster	-0.50300389042500004	4.6495571273099996
177	178	1	Quintuplet cluster	-0.50317842334999996	4.65217512119
178	179	1	J1746-2850I * (3)	-0.50492375260199995	4.6495571273099996
179	180	1	J1746-2850I,J1746-2850I	-0.50352748920000001	4.65217512119
180	181	1	J1746-2850I * (3)	-0.50352748920000001	4.65217512119
181	182	1	LEO0056,AUG0103	-0.38728856101800002	4.6835910477300002
182	183	1	AUG0140,AUG0096,AUG0028	0.40753438034099998	3.86677695779
183	184	1	* (27)	0.040491638646300003	4.8301987048899999
184	185	1	* (27)	0.040491638646300003	4.8301987048899999
185	186	1	* (6)	-0.547335253425	4.5945792558800003
186	187	1	B1642-03 * (4)	0.36582101121799998	3.8929568965699999
187	188	1	* (5)	-0.18535396656200001	4.7673668518200003
188	189	1	* (5)	-0.39479347680100002	4.6731190722099996
189	190	1	PSR B1929+10	0.19181168479399999	5.1155600375999999
190	191	1	PSR J0737-3039	-0.53511794866100004	1.99752932891
191	192	1	PSR J0737-3039	-0.53511794866100004	1.99752932891
192	193	1	PSR J0737-3039	-0.53511794866100004	1.99752932891
193	194	1	PSR J0737-3039	-0.53511794866100004	1.99752932891
194	195	1	* (11)	-0.034732052114699999	4.5605453354599996
195	196	1	* (10)	-0.071383966406599997	4.0578905108900001
196	197	1	NGC2403,NGC2366	1.17652644877	1.97658537788
197	198	1	UGC4305,UGC4483,K52,DDO53	1.2117820996599999	2.2200588085400002
198	199	1	PKS B1228-113	-0.203330857857	3.27772833525
199	200	1	* (6)	0.50230575872399996	3.1703905862499999
200	201	1	* (6)	0.50230575872399996	3.1703905862499999
201	202	1	B0218+357	0.62727133316700001	0.61522856132799997
202	203	1	HB1413+115	0.20071286397900001	3.73325927002
203	204	1	F10214+4724	0.82292274231499996	2.7253316269900001
204	205	1	* (15)	-0.070860367630999996	3.9819686884299998
205	206	1	* (15)	-0.070860367630999996	3.9819686884299998
206	207	1	* (11)	0.020943951023899999	3.93222680474
207	208	1	* (11)	1.0679669693	2.6101398963600002
208	209	1	HETE J1900.1-2455	-0.434936049597	4.9741883681800001
209	210	1	HD 49798	-0.77352992448400004	1.78023583703
210	211	1	SAX J1808.4-3658	-0.64542275738800003	4.7490408946800002
211	212	1	XTE J1814-338	-0.589397688398	4.7726028395800002
212	213	1	XTE J1807-294	-0.51330133301199998	4.7438049069200003
213	214	1	SWIFT J1756.9-2508	-0.43825217517600001	4.6992990109899999
214	215	1	XTE J1751-305	-0.53441981696100005	4.6731190722099996
215	216	1	V1341 Cyg	0.66881016936399995	5.6915186907499997
216	217	1	V651 Mon	-0.0141371669412	1.8744836166400001
217	218	1	HD 189733	0.39636427312799999	5.2386057498599996
218	219	1	HD189733b	0.39636427312799999	5.2386057498599996
219	220	1	HD189733b	0.39636427312799999	5.2386057498599996
220	221	1	HD189733b	0.39636427312799999	5.2386057498599996
221	222	1	HD189733b	0.39636427312799999	5.2386057498599996
222	223	1	NGC 5986	-0.65955992432900001	4.12857634559
223	224	1	M 92	0.75293503931000005	4.5265114150499999
224	225	1	HP 1	-0.523249709748	4.58672527424
225	226	1	Djorg 1	-0.57718038363500002	4.6574111089499999
226	227	1	NGC 3079,Mrk 348	0.76480327822399996	1.41895268187
227	228	1	Mercury	0	0
228	229	1	GRB090709a	1.0599384547399999	5.0605821661599997
229	230	1	GRB090709a	1.0599384547399999	5.0605821661599997
230	231	1	TMCCP	0.448375084837	1.2304571226600001
231	232	1	Themis1Aug	-0.28204520712199999	3.8510689945299998
232	233	1	PSRJ1732-31	-0.55134951070500005	4.5945792558800003
233	234	1	PSRJ0357+32	0.55990162403999999	1.03672557568
234	235	1	PSRJ1742-20,PSRJ2238+59	0.32358404332000001	5.2804936519099996
235	236	1		0	0
236	237	1	PSRJ1811-1925	-0.33894294073699999	4.7621308640700004
237	238	1	* (5)	0.53005649383099995	4.3065999292999999
238	239	1	PSRJ1833-1034	-0.18448130193599999	4.8589966375499998
239	241	1	B0531+21	0.38414696836399997	1.46084058392
240	242	1	SN2007GR * (4)	0	0.1308996939
\.


--
-- Data for Name: timezones; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY timezones (id, "timeZone") FROM stdin;
1	UTC-11
2	UTC-10
3	UTC-9
4	UTC-8
5	UTC-7
6	UTC-6
7	UTC-5
8	UTC-4
9	UTC-3
10	UTC-2
11	UTC-1
12	UTC
13	UTC+1
14	UTC+2
15	UTC+3
16	UTC+4
17	UTC+5
18	UTC+6
19	UTC+7
20	UTC+8
21	UTC+9
22	UTC+10
23	UTC+11
24	UTC+12
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY users (id, original_id, pst_id, username, sanctioned, first_name, last_name, contact_instructions) FROM stdin;
1	227	\N	\N	f	Frank	Ghigo	\N
2	3292	\N	\N	f	Jim	Braatz	\N
3	1373	\N	\N	f	Jules	Harnett	\N
4	4810	\N	\N	f	Carl	Bignell	\N
5	2669	\N	\N	f	Dana	Balser	\N
6	2927	\N	\N	f	Toney	Minter	\N
7	1339	\N	\N	f	Ron	Maddalena	\N
8	4789	\N	\N	f	Scott	Ransom	\N
9	4305	\N	\N	f	Karen	O'Neil	\N
10	4644	\N	\N	f	Brian	Mason	\N
11	6150	\N	\N	f	Paul	Ruffle	\N
12	846	\N	\N	f	Jay	Lockman	\N
13	915	\N	\N	f	Glen	Langston	\N
14	5605	\N	\N	f	Rachel	Rosen	\N
15	5293	\N	\N	f	Tony	Remijan	\N
16	3628	\N	\N	f	Geoff	Bower	\N
17	4871	\N	\N	f	Alberto	Bolatto	\N
18	3403	\N	\N	f	Eric	Ford	\N
19	5714	\N	\N	f	Paul	Kalas	\N
20	832	\N	\N	f	Jim	Condon	\N
21	1503	\N	\N	f	Lincoln	Greenhill	\N
22	278	\N	\N	f	Chris	Henkel	\N
23	4852	\N	\N	f	Fred	Lo	\N
24	516	\N	\N	f	Mark	Reid	\N
25	5379	\N	\N	f	Cheng-Yu	Kuo	\N
26	6240	\N	\N	f	Ingyin	Zaw	\N
27	5064	\N	\N	f	Avanti	Tilak	\N
28	5902	\N	\N	f	Lei	Hao	\N
29	6406	\N	\N	f	Philip	Lah	\N
30	4516	\N	\N	f	Andreas	Brunthaler	\N
31	2563	\N	\N	f	Lorant	Sjouwerman	\N
32	2069	\N	\N	f	Mike	Garrett	\N
33	4963	\N	\N	f	Laurent	Loinard	\N
34	5403	\N	\N	f	James	Miller-Jones	\N
35	1522	\N	\N	f	Michael	Rupen	\N
36	3662	\N	\N	f	Amy	Mioduszewski	\N
37	903	\N	\N	f	Vivek	Dhawan	\N
38	5295	\N	\N	f	Elena	Gallo	\N
39	5081	\N	\N	f	Peter	Jonker	\N
40	4056	\N	\N	f	Walter	Brisken	\N
41	5460	\N	\N	f	Rosa	Torres	\N
42	6189	\N	\N	f	William	Peterson	\N
43	451	\N	\N	f	Bob	Mutel	\N
44	838	\N	\N	f	Miller	Goss	\N
45	5045	\N	\N	f	Uwe	Bach	\N
46	5528	\N	\N	f	Thomas	Kirchbaum	\N
47	4776	\N	\N	f	Enno	Middelberg	\N
48	3	\N	\N	f	Walter	Alef	\N
49	709	\N	\N	f	Arno	Witzel	\N
50	1137	\N	\N	f	Tony	Zensus	\N
51	4847	\N	\N	f	Steve	Curran	\N
52	4974	\N	\N	f	Matthew	Whiting	\N
53	2839	\N	\N	f	John	Webb	\N
54	4849	\N	\N	f	Michael	Murphy	\N
55	4905	\N	\N	f	Ylva	Pihlstrom	\N
56	1392	\N	\N	f	Tommy	Wiklind	\N
57	4975	\N	\N	f	Paul	Francis	\N
58	3887	\N	\N	f	Andrew	Baker	\N
59	4342	\N	\N	f	Andy	Harris	\N
60	226	\N	\N	f	Reinhardt	Genzel	\N
61	1744	\N	\N	f	Jeff	Mangum	\N
62	862	\N	\N	f	Al	Wootten	\N
63	4801	\N	\N	f	Nissim	Kanekar	\N
64	4824	\N	\N	f	Sara	Ellison	\N
65	4338	\N	\N	f	Jason	Prochaska	\N
66	5633	\N	\N	f	Brian	York	\N
67	4884	\N	\N	f	Yancy	Shirley	\N
68	298	\N	\N	f	Mike	Hollis	\N
69	953	\N	\N	f	Phil	Jewell	\N
70	398	\N	\N	f	Frank	Lovas	\N
71	1620	\N	\N	f	Joel	Bregman	\N
72	4558	\N	\N	f	Jimmy	Irwin	\N
73	5002	\N	\N	f	Paul	Demorest	\N
74	4799	\N	\N	f	Bryan	Jacoby	\N
75	4996	\N	\N	f	Robert	Ferdman	\N
76	23	\N	\N	f	Don	Backer	\N
77	4796	\N	\N	f	Ingrid	Stairs	\N
78	2314	\N	\N	f	David	Nice	\N
79	4800	\N	\N	f	Andrea	Lommen	\N
80	3616	\N	\N	f	Matthew	Bailes	\N
81	4833	\N	\N	f	Ismael	Cognard	\N
82	2196	\N	\N	f	Jayaram	Chengalur	\N
83	3782	\N	\N	f	Tyler	Bourke	\N
84	5072	\N	\N	f	Paola	Caselli	\N
85	5630	\N	\N	f	Rachel	Friesen	\N
86	3701	\N	\N	f	James	Di Francesco	\N
87	452	\N	\N	f	Phil	Myers	\N
88	4772	\N	\N	f	Jeremy	Darling	\N
89	6212	\N	\N	f	Stanislav	Edel	\N
90	6213	\N	\N	f	Dominic	Ludovici	\N
91	4226	\N	\N	f	Dunc	Lorimer	\N
92	4142	\N	\N	f	Maura	McLaughlin	\N
93	5561	\N	\N	f	Vlad	Kondratiev	\N
94	6214	\N	\N	f	Joshua	Ridley	\N
95	4820	\N	\N	f	Esteban	Araya	\N
96	2360	\N	\N	f	Peter	Hofner	\N
97	5061	\N	\N	f	Ian	Hoffman	\N
98	5117	\N	\N	f	Hendrik	Linz	\N
99	2309	\N	\N	f	Stan	Kurtz	\N
100	6225	\N	\N	f	Viswesh	Marthi	\N
101	6229	\N	\N	f	Yogesh	Maan	\N
102	4197	\N	\N	f	Avinash	Deshpande	\N
103	5608	\N	\N	f	Jane	Greaves	\N
104	6182	\N	\N	f	Antonio	Hales	\N
105	5104	\N	\N	f	Brenda	Matthews	\N
106	3542	\N	\N	f	Bruce	Campbell	\N
107	91	\N	\N	f	Don	Campbell	\N
108	4790	\N	\N	f	Lynn	Carter	\N
109	5618	\N	\N	f	Rebecca	Ghent	\N
110	4816	\N	\N	f	Mike	Nolan	\N
111	6242	\N	\N	f	Naoto	Kobayashi	\N
112	4032	\N	\N	f	Tom	Millar	\N
113	3344	\N	\N	f	Masao	Saito	\N
114	6243	\N	\N	f	Chikako	Yasui	\N
115	1534	\N	\N	f	Brian	Dennison	\N
116	6248	\N	\N	f	Leigha	Dickens	\N
117	4879	\N	\N	f	Robert	Benjamin	\N
118	2072	\N	\N	f	Bryan	Butler	\N
119	6434	\N	\N	f	Ben	Bussey	\N
120	3543	\N	\N	f	Gordon	McIntosh	\N
121	4137	\N	\N	f	Ian	Smail	\N
122	2749	\N	\N	f	Rob	Ivison	\N
123	5387	\N	\N	f	Laura	Hainline	\N
124	4893	\N	\N	f	Andrew	Blain	\N
125	995	\N	\N	f	Linda	Tacconi	\N
126	1940	\N	\N	f	Frank	Bertoldi	\N
127	4873	\N	\N	f	Thomas	Greve	\N
128	5430	\N	\N	f	Roberto	Neri	\N
129	4894	\N	\N	f	Scott	Chapman	\N
130	4828	\N	\N	f	Pierre	Cox	\N
131	1696	\N	\N	f	Alain	Omont	\N
132	2923	\N	\N	f	Fernando	Camilo	\N
133	1007	\N	\N	f	Jules	Halpern	\N
134	2434	\N	\N	f	John	Reynolds	\N
135	4570	\N	\N	f	Mallory	Roberts	\N
136	2939	\N	\N	f	Zaven	Arzoumanian	\N
137	5282	\N	\N	f	Paulo	Freire	\N
138	1875	\N	\N	f	Roger	Romani	\N
139	3756	\N	\N	f	Paul	Ray	\N
140	2036	\N	\N	f	David	Wilner	\N
141	5971	\N	\N	f	Ryan	Lynch	\N
142	710	\N	\N	f	Art	Wolfe	\N
143	5599	\N	\N	f	Regina	Jorgenson	\N
144	4805	\N	\N	f	Tim	Robishaw	\N
145	274	\N	\N	f	Carl	Heiles	\N
146	5900	\N	\N	f	Stephanie	Zonak	\N
147	6424	\N	\N	f	Chelsea	Sharon	\N
148	655	\N	\N	f	Paul	VandenBout	\N
149	4856	\N	\N	f	Jason	Hessels	\N
150	834	\N	\N	f	Bill	Cotton	\N
151	4827	\N	\N	f	Simon	Dicker	\N
152	6217	\N	\N	f	Phil	Korngut	\N
153	4842	\N	\N	f	Mark	Devlin	\N
154	6169	\N	\N	f	Loren	Anderson	\N
155	33	\N	\N	f	Tom	Bania	\N
156	962	\N	\N	f	Bob	Rood	\N
157	5875	\N	\N	f	Neeraj	Gupta	\N
158	4189	\N	\N	f	Raghunathan	Srianand	\N
159	3918	\N	\N	f	Patrick	Petitjean	\N
160	5967	\N	\N	f	Pasquier	Noterdaeme	\N
161	6400	\N	\N	f	Ana	Lopez-Sepulcre	\N
162	2073	\N	\N	f	Riccardo	Cesaroni	\N
163	1143	\N	\N	f	Jan	Brand	\N
164	5181	\N	\N	f	Francesco	Fontani	\N
165	671	\N	\N	f	Malcolm	Walmsley	\N
166	3813	\N	\N	f	Friedrich	Wyrowski	\N
167	1226	\N	\N	f	Chris	Carilli	\N
168	6013	\N	\N	f	Emanuele	Daddi	\N
169	4925	\N	\N	f	Jeff	Wagg	\N
170	6429	\N	\N	f	Manuel	Aravena	\N
171	3079	\N	\N	f	Fabian	Walter	\N
172	5559	\N	\N	f	Dominik	Riechers	\N
173	6438	\N	\N	f	Helmut	Dannerbauer	\N
174	2512	\N	\N	f	Mark	Dickinson	\N
175	6439	\N	\N	f	David	Elbaz	\N
176	4418	\N	\N	f	Daniel	Stern	\N
177	3282	\N	\N	f	Glenn	Morrison	\N
178	6251	\N	\N	f	Katie	Chynoweth	\N
179	2720	\N	\N	f	Jose	Cernicharo	\N
180	6441	\N	\N	f	Lucie	Vincent	\N
181	6442	\N	\N	f	Nicole	Feautrier	\N
182	5397	\N	\N	f	Pierre	Valiron	\N
183	5396	\N	\N	f	Alexandre	Faure	\N
184	6443	\N	\N	f	Annie	Spielfiedel	\N
185	6444	\N	\N	f	Maria Luisa	Senent	\N
186	6445	\N	\N	f	Fabien	Daniel	\N
187	6447	\N	\N	f	Macarena	Garcia-Marin	\N
188	1304	\N	\N	f	Andreas	Eckart	\N
189	6199	\N	\N	f	Sabine	Koenig	\N
190	6201	\N	\N	f	Sebastian	Fischer	\N
191	6448	\N	\N	f	Jens	Zuther	\N
192	1036	\N	\N	f	Walter	Huchtmeier	\N
193	6200	\N	\N	f	Thomas	Bertram	\N
194	5928	\N	\N	f	Mark	Swinbank	\N
195	6151	\N	\N	f	Kristen	Coppin	\N
196	3129	\N	\N	f	Alastair	Edge	\N
197	4538	\N	\N	f	Richard	Ellis	\N
198	6118	\N	\N	f	Dan	Stark	\N
199	6411	\N	\N	f	Tucker	Jones	\N
200	4139	\N	\N	f	Jean-Paul	Kneib	\N
201	4565	\N	\N	f	Harold	Ebeling	\N
202	6252	\N	\N	f	Kelly	Holley-Bockelmann	\N
203	5604	\N	\N	f	Chris	Clemens	\N
204	6462	\N	\N	f	Sandor	Molnar	\N
205	6463	\N	\N	f	Patrick	Koch	\N
206	5866	\N	\N	f	James	Aguirre	\N
207	612	\N	\N	f	John	Stocke	\N
208	6465	\N	\N	f	Ting	Yan	\N
209	5572	\N	\N	f	Sue Ann	Heatherly	\N
210	3903	\N	\N	f	Eric	Gotthelf	\N
211	6222	\N	\N	f	Miranda	Nordhaus	\N
212	4885	\N	\N	f	Neal	Evans II	\N
213	5307	\N	\N	f	Erik	Rosolowsky	\N
214	5903	\N	\N	f	Claudia	Cyganowski	\N
215	30	\N	\N	f	John	Bally	\N
216	6178	\N	\N	f	Meredith	Drosback	\N
217	6177	\N	\N	f	Jason	Glenn	\N
218	2914	\N	\N	f	Jonathan	Williams	\N
219	6179	\N	\N	f	Eric	Bradley	\N
220	6180	\N	\N	f	Adam	Ginsburg	\N
221	3936	\N	\N	f	Vicky	Kaspi	\N
222	1533	\N	\N	f	Jim	Cordes	\N
223	5283	\N	\N	f	David	Champion	\N
224	6236	\N	\N	f	Anne	Archibald	\N
225	5936	\N	\N	f	Jason	Boyles	\N
226	6253	\N	\N	f	Christie	McPhee	\N
227	5593	\N	\N	f	Laura	Kasian	\N
228	5350	\N	\N	f	Joeri	van Leeuwen	\N
229	5348	\N	\N	f	Julia	Deneva	\N
230	3663	\N	\N	f	Fronefield	Crawford	\N
231	4998	\N	\N	f	Andrew	Faulkner	\N
232	4227	\N	\N	f	Michael	Kramer	\N
233	403	\N	\N	f	Andrew	Lyne	\N
234	5286	\N	\N	f	Marta	Burgay	\N
235	4999	\N	\N	f	Andrea	Possenti	\N
236	129	\N	\N	f	Nichi	D'Amico	\N
237	6488	\N	\N	f	Claire	Gilpin	\N
238	1568	\N	\N	f	Carl	Gwinn	\N
239	6490	\N	\N	f	Michael	Johnson	\N
240	6489	\N	\N	f	Tatiana	Smirnova	\N
241	4147	\N	\N	f	Shami	Chatterjee	\N
242	6491	\N	\N	f	Eduardo	Rubio-Herrera	\N
243	3802	\N	\N	f	Ben	Stappers	\N
244	432	\N	\N	f	David	Meier	\N
245	5576	\N	\N	f	Wilmer	Stork	\N
246	536	\N	\N	f	Larry	Rudnick	\N
247	6436	\N	\N	f	Damon	Farnsworth	\N
248	5933	\N	\N	f	Shea	Brown	\N
249	3946	\N	\N	f	Karl	Menten	\N
250	5003	\N	\N	f	Liz	Humphreys	\N
251	6454	\N	\N	f	Jairo	Armijos	\N
252	1958	\N	\N	f	Jesus	Martin-Pintado	\N
253	5614	\N	\N	f	Miguel Angel	Requena-Torres	\N
254	6453	\N	\N	f	Sergio	exception	\N
255	5054	\N	\N	f	Arturo	Rodriguez-Franco	\N
256	1426	\N	\N	f	Joe	Lazio	\N
257	6425	\N	\N	f	Natsuko	Kudo	\N
258	6427	\N	\N	f	Kazufumi	Torii	\N
259	211	\N	\N	f	Yasuo	Fukui	\N
260	446	\N	\N	f	Mark	Morris	\N
261	3931	\N	\N	f	M.A.	Walker	\N
262	5284	\N	\N	f	Willem	van Straten	\N
263	5399	\N	\N	f	Aris	Karasteregiou	\N
264	6249	\N	\N	f	Joshua	Miller	\N
265	6516	\N	\N	f	Evan	Keane	\N
266	411	\N	\N	f	Dick	Manchester	\N
267	6499	\N	\N	f	Benetge	Perera	\N
268	3941	\N	\N	f	Yu	Gao	\N
269	5981	\N	\N	f	Ben	Zeiger	\N
270	6501	\N	\N	f	Marjorie	Gonzalez	\N
271	1227	\N	\N	f	Gilles	Joncas	\N
272	6502	\N	\N	f	Jean-Francois	Robitaille	\N
273	6503	\N	\N	f	Douglas	Marshall	\N
274	5001	\N	\N	f	Marc-Antoine	Miville-Deschenes	\N
275	4647	\N	\N	f	Peter	Martin	\N
276	6504	\N	\N	f	Megan	DeCesar	\N
277	6519	\N	\N	f	Cole	Miller	\N
278	6460	\N	\N	f	Alexis	Smith	\N
279	5530	\N	\N	f	Moira	Jardine	\N
280	5937	\N	\N	f	Andrew	Cameron	\N
281	5258	\N	\N	f	Violette	Impellizzeri	\N
282	1963	\N	\N	f	Alan	Roy	\N
283	5184	\N	\N	f	Silvia	Leurini	\N
284	3541	\N	\N	f	Jean-Luc	Margot	\N
285	589	\N	\N	f	Martin	Slade	\N
286	6742	\N	\N	f	Julian	Haw Far Chin	\N
287	3794	\N	\N	f	Yanga	Fernandez	\N
288	4960	\N	\N	f	Amy	Lovell	\N
289	3117	\N	\N	f	L.	Campusano	\N
290	6273	\N	\N	f	Mike	Kelley	\N
291	2226	\N	\N	f	Susana	Licazano	\N
292	3152	\N	\N	f	Albert	Zijlstra	\N
293	4939	\N	\N	f	Maggie	Livingstone	\N
294	4089	\N	\N	f	Frank	Marshall	\N
295	1478	\N	\N	f	John	Middleditch	\N
296	6671	\N	\N	f	Matthew	Kerr	\N
297	6672	\N	\N	f	Maxim	Lyutikob	\N
298	6673	\N	\N	f	Anya	Bilous	\N
299	6674	\N	\N	f	Mitchell	Mickaliger	\N
300	3986	\N	\N	f	Zolt	Paragi	\N
301	2956	\N	\N	f	Chryssa	Kouveliotou	\N
302	5511	\N	\N	f	Enrico	Ramirez-Ruiz	\N
303	1704	\N	\N	f	Huib	van Langevelde	\N
304	1967	\N	\N	f	Arpad	Szomoru	\N
305	5438	\N	\N	f	Megan	Argo	\N
\.


--
-- Data for Name: windows; Type: TABLE DATA; Schema: public; Owner: dss
--

COPY windows (id, session_id, required) FROM stdin;
\.


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
-- Name: blackouts_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY blackouts
    ADD CONSTRAINT blackouts_pkey PRIMARY KEY (id);


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
-- Name: periods_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY periods
    ADD CONSTRAINT periods_pkey PRIMARY KEY (id);


--
-- Name: project_blackouts_09b_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY project_blackouts_09b
    ADD CONSTRAINT project_blackouts_09b_pkey PRIMARY KEY (id);


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
-- Name: repeats_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY repeats
    ADD CONSTRAINT repeats_pkey PRIMARY KEY (id);


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
-- Name: timezones_pkey; Type: CONSTRAINT; Schema: public; Owner: dss; Tablespace: 
--

ALTER TABLE ONLY timezones
    ADD CONSTRAINT timezones_pkey PRIMARY KEY (id);


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
-- Name: blackouts_repeat_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX blackouts_repeat_id ON blackouts USING btree (repeat_id);


--
-- Name: blackouts_tz_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX blackouts_tz_id ON blackouts USING btree (tz_id);


--
-- Name: blackouts_user_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX blackouts_user_id ON blackouts USING btree (user_id);


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
-- Name: periods_session_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX periods_session_id ON periods USING btree (session_id);


--
-- Name: project_blackouts_09b_project_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX project_blackouts_09b_project_id ON project_blackouts_09b USING btree (project_id);


--
-- Name: project_blackouts_09b_requester_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX project_blackouts_09b_requester_id ON project_blackouts_09b USING btree (requester_id);


--
-- Name: projects_allotments_allotment_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX projects_allotments_allotment_id ON projects_allotments USING btree (allotment_id);


--
-- Name: projects_allotments_project_id; Type: INDEX; Schema: public; Owner: dss; Tablespace: 
--

CREATE INDEX projects_allotments_project_id ON projects_allotments USING btree (project_id);


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
-- Name: blackouts_repeat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY blackouts
    ADD CONSTRAINT blackouts_repeat_id_fkey FOREIGN KEY (repeat_id) REFERENCES repeats(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: blackouts_tz_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY blackouts
    ADD CONSTRAINT blackouts_tz_id_fkey FOREIGN KEY (tz_id) REFERENCES timezones(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: blackouts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY blackouts
    ADD CONSTRAINT blackouts_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: content_type_id_refs_id_728de91f; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT content_type_id_refs_id_728de91f FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log_content_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


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
-- Name: periods_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY periods
    ADD CONSTRAINT periods_session_id_fkey FOREIGN KEY (session_id) REFERENCES sessions(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_blackouts_09b_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY project_blackouts_09b
    ADD CONSTRAINT project_blackouts_09b_project_id_fkey FOREIGN KEY (project_id) REFERENCES projects(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_blackouts_09b_requester_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dss
--

ALTER TABLE ONLY project_blackouts_09b
    ADD CONSTRAINT project_blackouts_09b_requester_id_fkey FOREIGN KEY (requester_id) REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED;


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

