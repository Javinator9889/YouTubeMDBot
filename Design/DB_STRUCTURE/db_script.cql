CREATE TABLE IF NOT EXISTS history (
    user_id    INT NOT NULL,
    file_id    VARCHAR2(256 CHAR) NOT NULL
);

CREATE TABLE IF NOT EXISTS metadata (
    title           VARCHAR2(256 CHAR),
    artist          VARCHAR2(256 CHAR),
    cover           TEXT,
    duration        VARCHAR2(20 CHAR),
    music_file_id   VARCHAR2(256 CHAR) NOT NULL,
    PRIMARY KEY (music_file_id)
);

CREATE TABLE IF NOT EXISTS music (
    file_id               VARCHAR2(256 CHAR) NOT NULL,
    video_id              VARCHAR2(20 CHAR),
    audio_quality         INT,
    audio_format          INT,
    times_requested       INT,
    is_metadata_by_user   CHAR(1),
    PRIMARY KEY (file_id)
);

CREATE TABLE IF NOT EXISTS playlist (
    playlist_id       VARCHAR2(256 CHAR) NOT NULL,
    number_elements   INT,
    times_requested   INT,
    PRIMARY KEY (playlist_id)
);

CREATE TABLE IF NOT EXISTS playlist_has_music (
    playlist_playlist_id   VARCHAR2(256 CHAR) NOT NULL,
    music_file_id          VARCHAR2(256 CHAR) NOT NULL
);

CREATE TABLE IF NOT EXISTS preferences (
    audio_quality         VARCHAR2(5 CHAR),
    audio_format          VARCHAR2(5 CHAR),
    os                    VARCHAR2(10 CHAR),
    should_ask_metadata   CHAR(1),
    user_id          	  INT NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS "User" (
    user_id    INT NOT NULL,
    username   VARCHAR2(45 CHAR),
    name       TEXT,
    PRIMARY KEY (user_id)
);
