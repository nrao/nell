CREATE SEQUENCE test_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;

ALTER TABLE public.test_id_seq OWNER TO dss;

CREATE TABLE test (
    id integer DEFAULT nextval('test_id_seq'::regclass) NOT NULL,
    kase               character varying(255)               NOT NULL,
    name               character varying(255)               NOT NULL,
    start_time         timestamp without time zone          NOT NULL,
    elapsed_time       float                                NOT NULL,
    username           character varying(255)               NOT NULL,
    hostname           character varying(255)               NOT NULL,
    process_info_start text                                 NOT NULL,
    process_info_end   text                                 NOT NULL
);

ALTER TABLE public.test OWNER TO dss;
