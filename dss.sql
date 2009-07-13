BEGIN;
CREATE TABLE "users" (
    "id" serial NOT NULL PRIMARY KEY,
    "original_id" integer NOT NULL,
    "pst_id" integer NULL,
    "username" varchar(32) NULL,
    "sanctioned" boolean NOT NULL,
    "first_name" varchar(32) NOT NULL,
    "last_name" varchar(150) NOT NULL
)
;
CREATE TABLE "sesshuns_email" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "email" varchar(255) NOT NULL
)
;
CREATE TABLE "semesters" (
    "id" serial NOT NULL PRIMARY KEY,
    "semester" varchar(64) NOT NULL
)
;
CREATE TABLE "project_types" (
    "id" serial NOT NULL PRIMARY KEY,
    "type" varchar(64) NOT NULL
)
;
CREATE TABLE "allotment" (
    "id" serial NOT NULL PRIMARY KEY,
    "psc_time" double precision NOT NULL,
    "total_time" double precision NOT NULL,
    "max_semester_time" double precision NOT NULL,
    "grade" double precision NOT NULL
)
;
CREATE TABLE "projects" (
    "id" serial NOT NULL PRIMARY KEY,
    "semester_id" integer NOT NULL REFERENCES "semesters" ("id") DEFERRABLE INITIALLY DEFERRED,
    "project_type_id" integer NOT NULL REFERENCES "project_types" ("id") DEFERRABLE INITIALLY DEFERRED,
    "pcode" varchar(32) NOT NULL,
    "name" varchar(150) NOT NULL,
    "thesis" boolean NOT NULL,
    "complete" boolean NOT NULL,
    "ignore_grade" boolean NOT NULL,
    "start_date" timestamp with time zone NULL,
    "end_date" timestamp with time zone NULL
)
;
CREATE TABLE "investigators" (
    "id" serial NOT NULL PRIMARY KEY,
    "project_id" integer NOT NULL REFERENCES "projects" ("id") DEFERRABLE INITIALLY DEFERRED,
    "user_id" integer NOT NULL REFERENCES "users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "friend" boolean NOT NULL,
    "observer" boolean NOT NULL,
    "principal_contact" boolean NOT NULL,
    "priority" integer NOT NULL
)
;
CREATE TABLE "session_types" (
    "id" serial NOT NULL PRIMARY KEY,
    "type" varchar(64) NOT NULL
)
;
CREATE TABLE "observing_types" (
    "id" serial NOT NULL PRIMARY KEY,
    "type" varchar(64) NOT NULL
)
;
CREATE TABLE "receivers" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(32) NOT NULL,
    "abbreviation" varchar(32) NOT NULL,
    "freq_low" double precision NOT NULL,
    "freq_hi" double precision NOT NULL
)
;
CREATE TABLE "receiver_schedule" (
    "id" serial NOT NULL PRIMARY KEY,
    "receiver_id" integer NOT NULL REFERENCES "receivers" ("id") DEFERRABLE INITIALLY DEFERRED,
    "start_date" timestamp with time zone NULL
)
;
CREATE TABLE "parameters" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(64) NOT NULL,
    "type" varchar(32) NOT NULL
)
;
CREATE TABLE "status" (
    "id" serial NOT NULL PRIMARY KEY,
    "enabled" boolean NOT NULL,
    "authorized" boolean NOT NULL,
    "complete" boolean NOT NULL,
    "backup" boolean NOT NULL
)
;
CREATE TABLE "sessions" (
    "id" serial NOT NULL PRIMARY KEY,
    "project_id" integer NOT NULL REFERENCES "projects" ("id") DEFERRABLE INITIALLY DEFERRED,
    "session_type_id" integer NOT NULL REFERENCES "session_types" ("id") DEFERRABLE INITIALLY DEFERRED,
    "observing_type_id" integer NOT NULL REFERENCES "observing_types" ("id") DEFERRABLE INITIALLY DEFERRED,
    "allotment_id" integer NOT NULL REFERENCES "allotment" ("id") DEFERRABLE INITIALLY DEFERRED,
    "status_id" integer NOT NULL REFERENCES "status" ("id") DEFERRABLE INITIALLY DEFERRED,
    "original_id" integer NULL,
    "name" varchar(64) NULL,
    "frequency" double precision NULL,
    "max_duration" double precision NULL,
    "min_duration" double precision NULL,
    "time_between" double precision NULL
)
;
CREATE TABLE "cadences" (
    "id" serial NOT NULL PRIMARY KEY,
    "session_id" integer NOT NULL REFERENCES "sessions" ("id") DEFERRABLE INITIALLY DEFERRED,
    "start_date" timestamp with time zone NULL,
    "end_date" timestamp with time zone NULL,
    "repeats" integer NULL,
    "full_size" varchar(64) NULL,
    "intervals" varchar(64) NULL
)
;
CREATE TABLE "receiver_groups" (
    "id" serial NOT NULL PRIMARY KEY,
    "session_id" integer NOT NULL REFERENCES "sessions" ("id") DEFERRABLE INITIALLY DEFERRED
)
;
CREATE TABLE "observing_parameters" (
    "id" serial NOT NULL PRIMARY KEY,
    "session_id" integer NOT NULL REFERENCES "sessions" ("id") DEFERRABLE INITIALLY DEFERRED,
    "parameter_id" integer NOT NULL REFERENCES "parameters" ("id") DEFERRABLE INITIALLY DEFERRED,
    "string_value" varchar(64) NULL,
    "integer_value" integer NULL,
    "float_value" double precision NULL,
    "boolean_value" boolean NULL,
    "datetime_value" timestamp with time zone NULL,
    UNIQUE ("session_id", "parameter_id")
)
;
CREATE TABLE "windows" (
    "id" serial NOT NULL PRIMARY KEY,
    "session_id" integer NOT NULL REFERENCES "sessions" ("id") DEFERRABLE INITIALLY DEFERRED,
    "required" boolean NOT NULL
)
;
CREATE TABLE "opportunities" (
    "id" serial NOT NULL PRIMARY KEY,
    "window_id" integer NOT NULL REFERENCES "windows" ("id") DEFERRABLE INITIALLY DEFERRED,
    "start_time" timestamp with time zone NOT NULL,
    "duration" double precision NOT NULL
)
;
CREATE TABLE "systems" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(32) NOT NULL,
    "v_unit" varchar(32) NOT NULL,
    "h_unit" varchar(32) NOT NULL
)
;
CREATE TABLE "targets" (
    "id" serial NOT NULL PRIMARY KEY,
    "session_id" integer NOT NULL REFERENCES "sessions" ("id") DEFERRABLE INITIALLY DEFERRED,
    "system_id" integer NOT NULL REFERENCES "systems" ("id") DEFERRABLE INITIALLY DEFERRED,
    "source" varchar(32) NULL,
    "vertical" double precision NOT NULL,
    "horizontal" double precision NOT NULL
)
;
CREATE TABLE "projects_allotments" (
    "id" serial NOT NULL PRIMARY KEY,
    "project_id" integer NOT NULL REFERENCES "projects" ("id") DEFERRABLE INITIALLY DEFERRED,
    "allotment_id" integer NOT NULL REFERENCES "allotment" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("project_id", "allotment_id")
)
;
CREATE TABLE "receiver_groups_receivers" (
    "id" serial NOT NULL PRIMARY KEY,
    "receiver_group_id" integer NOT NULL REFERENCES "receiver_groups" ("id") DEFERRABLE INITIALLY DEFERRED,
    "receiver_id" integer NOT NULL REFERENCES "receivers" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("receiver_group_id", "receiver_id")
)
;
COMMIT;
