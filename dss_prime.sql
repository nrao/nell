BEGIN;
CREATE TABLE `authors` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `project_id` integer NOT NULL,
    `first` varchar(32) NOT NULL,
    `last` varchar(150) NOT NULL,
    `peoplekey` varchar(150) NOT NULL,
    `email` varchar(150) NOT NULL,
    `pi` bool NOT NULL,
    `co_i` bool NOT NULL
)
;
ALTER TABLE `authors` ADD CONSTRAINT project_id FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`);
CREATE TABLE `friends` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `first` varchar(32) NOT NULL,
    `last` varchar(150) NOT NULL,
    `peoplekey` varchar(150) NOT NULL,
    `email` varchar(150) NOT NULL,
    `pi` bool NOT NULL,
    `co_i` bool NOT NULL
)
;
CREATE TABLE `dispositions` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `pcode` varchar(32) NOT NULL,
    `disposition` varchar(4000) NOT NULL
)
;
CREATE TABLE `semesters` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `semester` varchar(64) NOT NULL
)
;
CREATE TABLE `project_types` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `type` varchar(64) NOT NULL
)
;
CREATE TABLE `allotment` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `psc_time` varchar(12) NOT NULL,
    `total_time` varchar(12) NOT NULL,
    `max_semester_time` varchar(12) NOT NULL,
    `grade` varchar(12) NOT NULL,
    `ignore_grade` bool NOT NULL
)
;
CREATE TABLE `projects` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `semester_id` integer NOT NULL,
    `project_type_id` integer NOT NULL,
    `friend_id` integer,
    `pcode` varchar(32) NOT NULL,
    `name` varchar(150) NOT NULL,
    `thesis` bool NOT NULL,
    `complete` bool NOT NULL,
    `start_date` datetime NULL,
    `end_date` datetime NULL
)
;
ALTER TABLE `projects` ADD CONSTRAINT friend_id FOREIGN KEY (`friend_id`) REFERENCES `friends` (`id`);
ALTER TABLE `projects` ADD CONSTRAINT project_type_id_refs_id_30e1275 FOREIGN KEY (`project_type_id`) REFERENCES `project_types` (`id`);
ALTER TABLE `projects` ADD CONSTRAINT semester_id_refs_id_7b0fb7e9 FOREIGN KEY (`semester_id`) REFERENCES `semesters` (`id`);
CREATE TABLE `session_types` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `type` varchar(64) NOT NULL
)
;
CREATE TABLE `observing_types` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `type` varchar(64) NOT NULL
)
;
CREATE TABLE `receivers` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `abbreviation` varchar(32) NOT NULL,
    `freq_low` varchar(12) NOT NULL,
    `freq_hi` varchar(12) NOT NULL
)
;
CREATE TABLE `receiver_schedule` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `receiver_id` integer NOT NULL,
    `start_date` datetime NULL
)
;
ALTER TABLE `receiver_schedule` ADD CONSTRAINT receiver_id29394 FOREIGN KEY (`receiver_id`) REFERENCES `receiver_id` (`id`);
CREATE TABLE `parameters` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(64) NOT NULL,
    `type` varchar(32) NOT NULL
)
;
CREATE TABLE `sessions` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `project_id` integer NOT NULL,
    `session_type_id` integer NOT NULL,
    `observing_type_id` integer NOT NULL,
    `allotment_id` integer NOT NULL,
    `status_id` integer NOT NULL,
    `original_id` integer NULL,
    `name` varchar(64) NULL,
    `frequency` varchar(12) NULL,
    `max_duration` varchar(12) NULL,
    `min_duration` varchar(12) NULL,
    `time_between` varchar(12) NULL
)
;
ALTER TABLE `sessions` ADD CONSTRAINT status_id29393 FOREIGN KEY (`status_id`) REFERENCES `status_id` (`id`);
ALTER TABLE `sessions` ADD CONSTRAINT session_type_id_refs_id_10cc792b FOREIGN KEY (`session_type_id`) REFERENCES `session_types` (`id`);
ALTER TABLE `sessions` ADD CONSTRAINT observing_type_id_refs_id_7e9f43c0 FOREIGN KEY (`observing_type_id`) REFERENCES `observing_types` (`id`);
ALTER TABLE `sessions` ADD CONSTRAINT project_id_refs_id_3043d88e FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`);
ALTER TABLE `sessions` ADD CONSTRAINT allotment_id_refs_id_f6ee69d FOREIGN KEY (`allotment_id`) REFERENCES `allotment` (`id`);
CREATE TABLE `cadences` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `session_id` integer NOT NULL,
    `start_date` datetime NULL,
    `end_date` datetime NULL,
    `repeats` integer NULL,
    `full_size` varchar(64) NULL,
    `intervals` varchar(64) NULL
)
;
ALTER TABLE `cadences` ADD CONSTRAINT session_id_refs_id_61d9fde FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`);
CREATE TABLE `receiver_groups` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `session_id` integer NOT NULL
)
;
ALTER TABLE `receiver_groups` ADD CONSTRAINT session_id_refs_id_46df204b FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`);
CREATE TABLE `rg_receiver` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `group_id` integer NOT NULL,
    `receiver_id` integer NOT NULL
)
;
ALTER TABLE `rg_receiver` ADD CONSTRAINT receiver_id_refs_id_2114f018 FOREIGN KEY (`receiver_id`) REFERENCES `receivers` (`id`);
ALTER TABLE `rg_receiver` ADD CONSTRAINT group_id_refs_id_369b9b32 FOREIGN KEY (`group_id`) REFERENCES `receiver_groups` (`id`);
CREATE TABLE `observing_parameters` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `session_id` integer NOT NULL,
    `parameter_id` integer NOT NULL,
    `string_value` varchar(64) NULL,
    `integer_value` integer NULL,
    `float_value` varchar(12) NULL,
    `boolean_value` bool NULL,
    `datetime_value` datetime NULL,
    UNIQUE (`session_id`, `parameter_id`)
)
;
ALTER TABLE `observing_parameters` ADD CONSTRAINT parameter_id_refs_id_6ead48a9 FOREIGN KEY (`parameter_id`) REFERENCES `parameters` (`id`);
ALTER TABLE `observing_parameters` ADD CONSTRAINT session_id_refs_id_30d47126 FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`);
CREATE TABLE `status` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `enabled` bool NOT NULL,
    `authorized` bool NOT NULL,
    `complete` bool NOT NULL,
    `backup` bool NOT NULL
)
;
CREATE TABLE `windows` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `session_id` integer NOT NULL,
    `required` bool NOT NULL
)
;
ALTER TABLE `windows` ADD CONSTRAINT session_id_refs_id_21a1b976 FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`);
CREATE TABLE `opportunities` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `window_id` integer NOT NULL,
    `start_time` datetime NOT NULL,
    `duration` varchar(12) NOT NULL
)
;
ALTER TABLE `opportunities` ADD CONSTRAINT window_id_refs_id_cff0f03 FOREIGN KEY (`window_id`) REFERENCES `windows` (`id`);
CREATE TABLE `systems` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `v_unit` varchar(32) NOT NULL,
    `h_unit` varchar(32) NOT NULL
)
;
CREATE TABLE `targets` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `session_id` integer NOT NULL,
    `system_id` integer NOT NULL,
    `source` varchar(32) NULL,
    `vertical` varchar(12) NOT NULL,
    `horizontal` varchar(12) NOT NULL
)
;
ALTER TABLE `targets` ADD CONSTRAINT system_id_refs_id_3711fc53 FOREIGN KEY (`system_id`) REFERENCES `systems` (`id`);
ALTER TABLE `targets` ADD CONSTRAINT session_id_refs_id_63199dfd FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`);
CREATE TABLE `projects_allotments` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `project_id` integer NOT NULL,
    `allotment_id` integer NOT NULL,
    UNIQUE (`project_id`, `allotment_id`)
)
;
ALTER TABLE `projects_allotments` ADD CONSTRAINT project_id_refs_id_57532c1c FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`);
ALTER TABLE `projects_allotments` ADD CONSTRAINT allotment_id_refs_id_691157c1 FOREIGN KEY (`allotment_id`) REFERENCES `allotment` (`id`);
COMMIT;
