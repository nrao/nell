alter table pht_scientific_categories add code character varying(3);

update pht_scientific_categories set code = 'S' where category = 'Stellar';
update pht_scientific_categories set code = 'SS' where category = 'Solar System';
update pht_scientific_categories set code = 'AST' where category = 'Astrometry/Geodesy';
update pht_scientific_categories set code = 'EGS' where category = 'Extragalactic Structure';
update pht_scientific_categories set code = 'NGA' where category = 'Normal Galaxies; Groups; and Clusters';
update pht_scientific_categories set code = 'ETP' where category = 'Energetic Transients and Pulsars';
update pht_scientific_categories set code = 'SSP' where category = 'Solar System; Stars; Planetary Systems';
update pht_scientific_categories set code = 'SFM' where category = 'Star Formation';
update pht_scientific_categories set code = 'ISM' where category = 'Interstellar Medium';
update pht_scientific_categories set code = 'HIZ' where category = 'High Redshift and Source Surveys';
update pht_scientific_categories set code = 'AGN' where category = 'Active Galactic Nuclei';

update pht_scientific_categories set code = 'E' where category = 'Extragalactic';
update pht_scientific_categories set code = 'G' where category = 'Galactic';
