--
-- Name: sponsors; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE sponsors (
    id integer NOT NULL,
    name character varying(150) NOT NULL,
    abbreviation character varying(64) NOT NULL
);


ALTER TABLE public.sponsors OWNER TO dss;

--
-- Name: sponsors_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE sponsors_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sponsors_id_seq OWNER TO dss;


ALTER TABLE pht_proposals ADD COLUMN sponsor_id integer;

CREATE INDEX pht_proposals_sponsor_id ON pht_proposals USING btree (sponsor_id);

ALTER TABLE ONLY pht_proposals
    ADD CONSTRAINT pht_proposals_sponsor_id_fkey FOREIGN KEY (sponsor_id) REFERENCES sponsors(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE projects ADD COLUMN sponsor_id integer;

CREATE INDEX projects_sponsor_id ON projects USING btree (sponsor_id);

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_sponsor_id_fkey FOREIGN KEY (sponsor_id) REFERENCES sponsors(id) DEFERRABLE INITIALLY DEFERRED;



