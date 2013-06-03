ALTER TABLE pht_proposals ADD COLUMN contact_id integer;

CREATE INDEX pht_proposals_contact_id ON pht_proposals USING btree (contact_id);

ALTER TABLE ONLY pht_proposals
    ADD CONSTRAINT pht_proposals_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES pht_authors(id) DEFERRABLE INITIALLY DEFERRED;


