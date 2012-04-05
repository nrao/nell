--
-- Name: pht_proposal_comments; Type: TABLE; Schema: public; Owner: dss; Tablespace: 
--

CREATE TABLE pht_proposal_comments (
    id integer NOT NULL,
    nrao_comment text,
    srp_to_pi text,
    srp_to_tac text,
    tech_review_to_pi text,
    tech_review_to_tac text
);


ALTER TABLE public.pht_proposal_comments OWNER TO dss;

--
-- Name: pht_proposal_comments_id_seq; Type: SEQUENCE; Schema: public; Owner: dss
--

CREATE SEQUENCE pht_proposal_comments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.pht_proposal_comments_id_seq OWNER TO dss;

--
-- Name: pht_proposal_comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dss
--

ALTER SEQUENCE pht_proposal_comments_id_seq OWNED BY pht_proposal_comments.id;


--
-- Name: pht_proposal_comments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dss
--
SELECT pg_catalog.setval('pht_proposal_comments_id_seq', 1, false);

ALTER TABLE pht_proposals ADD COLUMN comments_id integer;

ALTER TABLE pht_proposal_comments ALTER COLUMN id SET DEFAULT nextval('pht_proposal_comments_id_seq'::regclass);

ALTER TABLE ONLY pht_proposal_comments
    ADD CONSTRAINT pht_proposal_comments_pkey PRIMARY KEY (id);

CREATE INDEX pht_proposals_comments_id ON pht_proposals USING btree (comments_id);    

ALTER TABLE ONLY pht_proposals
    ADD CONSTRAINT pht_proposals_comments_id_fkey FOREIGN KEY (comments_id) REFERENCES pht_proposal_comments(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE pht_proposal_comments ADD COLUMN tac_to_pi text;

