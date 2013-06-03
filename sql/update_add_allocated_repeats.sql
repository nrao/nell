ALTER TABLE pht_allotements add COLUMN allocated_repeats integer;
ALTER TABLE pht_allotements ALTER COLUMN allocated_repeats SET DEFAULT 1;
