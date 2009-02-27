CREATE TABLE sessions (
    id    SERIAL PRIMARY KEY
  , dummy INTEGER NOT NULL
);

CREATE TABLE fields (
    session_id INTEGER     REFERENCES sessions(id)
  , key        VARCHAR(64) NOT NULL
  , value      VARCHAR(64) NOT NULL

  , UNIQUE(session_id, key)
);
