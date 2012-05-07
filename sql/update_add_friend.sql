ALTER TABLE pht_proposals ADD COLUMN friend_id integer;

CREATE INDEX pht_proposals_friend_id ON pht_proposals USING btree (friend_id);

ALTER TABLE ONLY pht_proposals
    ADD CONSTRAINT pht_proposals_friend_id_fkey FOREIGN KEY (friend_id) REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED;


