-- Generado por Oracle SQL Developer Data Modeler 18.1.0.082.1035
--   en:        2018-06-18 16:59:15 CEST
--   sitio:      Oracle Database 11g
--   tipo:      Oracle Database 11g



CREATE TABLE history (
    user_user_id    INTEGER NOT NULL,
    music_file_id   VARCHAR2(256 CHAR) NOT NULL
);

ALTER TABLE history ADD CONSTRAINT history_pk PRIMARY KEY ( user_user_id,
                                                            music_file_id );

CREATE TABLE metadata (
    title           VARCHAR2(256 CHAR),
    artist          VARCHAR2(256 CHAR),
    cover           CLOB,
    duration        VARCHAR2(20 CHAR),
    music_file_id   VARCHAR2(256 CHAR) NOT NULL
);

CREATE UNIQUE INDEX metadata__idx ON
    metadata (
        music_file_id
    ASC );

CREATE TABLE music (
    file_id               VARCHAR2(256 CHAR) NOT NULL,
    video_id              VARCHAR2(20 CHAR),
    audio_quality         INTEGER,
    audio_format          INTEGER,
    times_requested       INTEGER,
    is_metadata_by_user   CHAR(1)
);

ALTER TABLE music ADD CONSTRAINT music_pk PRIMARY KEY ( file_id );

CREATE TABLE playlist (
    playlist_id       VARCHAR2(256 CHAR) NOT NULL,
    number_elements   INTEGER,
    times_requested   INTEGER
);

ALTER TABLE playlist ADD CONSTRAINT playlist_pk PRIMARY KEY ( playlist_id );

CREATE TABLE playlist_has_music (
    playlist_playlist_id   VARCHAR2(256 CHAR) NOT NULL,
    music_file_id          VARCHAR2(256 CHAR) NOT NULL
);

ALTER TABLE playlist_has_music ADD CONSTRAINT playlist_has_music_pk PRIMARY KEY ( playlist_playlist_id,
                                                                                  music_file_id );

CREATE TABLE preferences (
    audio_quality         VARCHAR2(5 CHAR),
    audio_format          VARCHAR2(5 CHAR),
    os                    VARCHAR2(10 CHAR),
    should_ask_metadata   CHAR(1),
    user_user_id          INTEGER NOT NULL
);

CREATE UNIQUE INDEX preferences__idx ON
    preferences (
        user_user_id
    ASC );

CREATE TABLE "User" (
    user_id    INTEGER NOT NULL,
    username   VARCHAR2(45 CHAR),
    name       CLOB
);

ALTER TABLE "User" ADD CONSTRAINT user_pk PRIMARY KEY ( user_id );

ALTER TABLE history
    ADD CONSTRAINT history_music_fk FOREIGN KEY ( music_file_id )
        REFERENCES music ( file_id )
            ON DELETE CASCADE;

ALTER TABLE history
    ADD CONSTRAINT history_user_fk FOREIGN KEY ( user_user_id )
        REFERENCES "User" ( user_id )
            ON DELETE CASCADE;

ALTER TABLE metadata
    ADD CONSTRAINT metadata_music_fk FOREIGN KEY ( music_file_id )
        REFERENCES music ( file_id )
            ON DELETE CASCADE;

ALTER TABLE playlist_has_music
    ADD CONSTRAINT playlist_has_music_music_fk FOREIGN KEY ( music_file_id )
        REFERENCES music ( file_id );

ALTER TABLE playlist_has_music
    ADD CONSTRAINT playlist_has_music_playlist_fk FOREIGN KEY ( playlist_playlist_id )
        REFERENCES playlist ( playlist_id );

ALTER TABLE preferences
    ADD CONSTRAINT preferences_user_fk FOREIGN KEY ( user_user_id )
        REFERENCES "User" ( user_id )
            ON DELETE CASCADE;



-- Informe de Resumen de Oracle SQL Developer Data Modeler: 
-- 
-- CREATE TABLE                             7
-- CREATE INDEX                             2
-- ALTER TABLE                             11
-- CREATE VIEW                              0
-- ALTER VIEW                               0
-- CREATE PACKAGE                           0
-- CREATE PACKAGE BODY                      0
-- CREATE PROCEDURE                         0
-- CREATE FUNCTION                          0
-- CREATE TRIGGER                           0
-- ALTER TRIGGER                            0
-- CREATE COLLECTION TYPE                   0
-- CREATE STRUCTURED TYPE                   0
-- CREATE STRUCTURED TYPE BODY              0
-- CREATE CLUSTER                           0
-- CREATE CONTEXT                           0
-- CREATE DATABASE                          0
-- CREATE DIMENSION                         0
-- CREATE DIRECTORY                         0
-- CREATE DISK GROUP                        0
-- CREATE ROLE                              0
-- CREATE ROLLBACK SEGMENT                  0
-- CREATE SEQUENCE                          0
-- CREATE MATERIALIZED VIEW                 0
-- CREATE SYNONYM                           0
-- CREATE TABLESPACE                        0
-- CREATE USER                              0
-- 
-- DROP TABLESPACE                          0
-- DROP DATABASE                            0
-- 
-- REDACTION POLICY                         0
-- 
-- ORDS DROP SCHEMA                         0
-- ORDS ENABLE SCHEMA                       0
-- ORDS ENABLE OBJECT                       0
-- 
-- ERRORS                                   0
-- WARNINGS                                 0
