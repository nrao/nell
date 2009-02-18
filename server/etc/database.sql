CREATE TYPE type_name AS ENUM('fixed', 'open', 'windowed');

CREATE TABLE sessions (
    id           SERIAL PRIMARY KEY
  , name         VARCHAR(30)
  , project      VARCHAR(30)
  , session_type type_name
  , lst          REAL
  , dec          REAL
  , frequency    REAL
  , min_duration INTEGER
  , max_duration INTEGER
  , time_between INTEGER
  , allotted     INTEGER
);
