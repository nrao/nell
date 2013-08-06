ALTER TABLE pht_proposals ADD COLUMN sponsor_id integer;

CREATE INDEX pht_proposals_sponsor_id ON pht_proposals USING btree (sponsor_id);

ALTER TABLE ONLY pht_proposals
    ADD CONSTRAINT pht_proposals_sponsor_id_fkey FOREIGN KEY (sponsor_id) REFERENCES sponsors(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE projects ADD COLUMN sponsor_id integer;

CREATE INDEX projects_sponsor_id ON projects USING btree (sponsor_id);

ALTER TABLE ONLY projects
    ADD CONSTRAINT projects_sponsor_id_fkey FOREIGN KEY (sponsor_id) REFERENCES sponsors(id) DEFERRABLE INITIALLY DEFERRED;



