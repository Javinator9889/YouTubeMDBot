-- PostgreSQL model for YouTubeMDBot application
-- Created by Javinator9889 - thu, 24 October, 2019
-- Last modification: Wed, 12 Aug, 2020
-- Version 1.31

-- DROP schema - only for testing
DROP SCHEMA IF EXISTS youtubemd CASCADE;
--#
DROP TYPE IF EXISTS AFORMAT;
--#
DROP TYPE IF EXISTS aquality;
--#
DROP TYPE IF EXISTS behaviour;
--#

-- Custom "enum" types
CREATE TYPE AFORMAT AS ENUM ('mp3', 'm4a', 'ogg');
--#
CREATE TYPE AQUALITY AS ENUM ('128k', '96k');
--#
CREATE TYPE BEHAVIOUR AS ENUM ('always', 'not_found', 'ask', 'never');
--#

-- Create DB schema
CREATE SCHEMA IF NOT EXISTS youtubemd;
--#

-- ---------------------------------------
--             Table User               --
-- ---------------------------------------
CREATE TABLE IF NOT EXISTS youtubemd.User
(
    "id"           INT PRIMARY KEY NOT NULL,
    "name"         VARCHAR(45),
    "tag"          VARCHAR(45),
    "lang"         VARCHAR(2),
    "first_access" date,
    "is_premium"   BOOLEAN DEFAULT FALSE
);
--#

-- ---------------------------------------------
--             Table Preferences              --
-- ---------------------------------------------
CREATE TABLE IF NOT EXISTS youtubemd.Preferences
(
    "audio_format"   AFORMAT   NOT NULL DEFAULT 'm4a',
    "audio_quality"  AQUALITY  NOT NULL DEFAULT '128k',
    "song_behaviour" BEHAVIOUR NOT NULL DEFAULT 'not_found',
    "send_song_link" BOOLEAN            DEFAULT False,
    "user_id"        INT       NOT NULL,
    PRIMARY KEY ("user_id"),
    CONSTRAINT "fk_user_id"
        FOREIGN KEY ("user_id")
            REFERENCES youtubemd.User ("id")
            ON DELETE CASCADE
            ON UPDATE CASCADE
);
--#

-- ------------------------------------------
--               Table YouTube             --
-- ------------------------------------------
CREATE TABLE IF NOT EXISTS youtubemd.YouTube
(
    "id"              VARCHAR(11) UNIQUE NOT NULL,
    "file_id"         VARCHAR(50) UNIQUE NOT NULL,
    "times_requested" INT                NOT NULL DEFAULT 0,
    PRIMARY KEY ("id")
);
--#

-- ------------------------------------------
--               Table Metadata            --
-- ------------------------------------------
CREATE TABLE IF NOT EXISTS youtubemd.Metadata
(
    "id"              BIGSERIAL   NOT NULL,
    "artist"          VARCHAR(45) NOT NULL,
    "album"           VARCHAR(45) NOT NULL,
    "cover"           BYTEA       NOT NULL,
    "release_id"      VARCHAR(36),
    "recording_id"    VARCHAR(36),
    "duration"        INT,
    "title"           VARCHAR(45),
    "custom_metadata" BOOLEAN,
    PRIMARY KEY ("id")
);
--#

-- ----------------------------------------------------
--       Relation between YouTube and Metadata       --
-- ----------------------------------------------------
CREATE TABLE IF NOT EXISTS youtubemd.Video_Has_Metadata
(
    "id"          VARCHAR(11) NOT NULL,
    "metadata_id" INT         NOT NULL,
    PRIMARY KEY ("id", "metadata_id"),
    CONSTRAINT "fk_video_id"
        FOREIGN KEY ("id")
            REFERENCES youtubemd.YouTube ("id"),
    CONSTRAINT "fk_metadata_id"
        FOREIGN KEY ("metadata_id")
            REFERENCES youtubemd.Metadata ("id")
);
--#

-- --------------------------------------
--             Table File              --
-- --------------------------------------
CREATE TABLE IF NOT EXISTS youtubemd.File
(
    "id"            VARCHAR(50) UNIQUE NOT NULL,
    "metadata_id"   INT UNIQUE         NOT NULL,
    "audio_quality" AQUALITY           NOT NULL,
    "size"          INT,
    PRIMARY KEY ("id", "metadata_id"),
    CONSTRAINT "fk_metadata_id"
        FOREIGN KEY ("metadata_id")
            REFERENCES youtubemd.Metadata ("id")
);
--#

-- -----------------------------------------
--               Table History            --
-- -----------------------------------------
CREATE TABLE IF NOT EXISTS youtubemd.History
(
    "id"          BIGSERIAL   NOT NULL,
    "file_id"     VARCHAR(50) NOT NULL,
    "user_id"     INT         NOT NULL,
    "metadata_id" INT         NOT NULL,
    "date"        date,
    PRIMARY KEY ("id", "file_id", "user_id", "metadata_id"),
    CONSTRAINT "fk_user_id"
        FOREIGN KEY ("user_id")
            REFERENCES youtubemd.User ("id")
            ON DELETE CASCADE
            ON UPDATE CASCADE,
    CONSTRAINT "fk_file_id"
        FOREIGN KEY ("file_id")
            REFERENCES youtubemd.File ("id"),
    CONSTRAINT "fk_metadata_id"
        FOREIGN KEY ("metadata_id")
            REFERENCES youtubemd.Metadata ("id")
);
--#

-- ------------------------------------------
--               Table Playlist            --
-- ------------------------------------------
CREATE TABLE IF NOT EXISTS youtubemd.Playlist
(
    "id" VARCHAR(22) NOT NULL UNIQUE,
    PRIMARY KEY ("id")
);
--#

-- ----------------------------------------------
--             Table YouTube stats             --
-- ----------------------------------------------
CREATE TABLE IF NOT EXISTS youtubemd.YouTubeStats
(
    "id"               VARCHAR(11) NOT NULL UNIQUE,
    "daily_requests"   INT         NOT NULL DEFAULT 1,
    "weekly_requests"  INT         NOT NULL DEFAULT 1,
    "monthly_requests" INT         NOT NULL DEFAULT 1,
    PRIMARY KEY ("id"),
    CONSTRAINT "fk_youtube_id"
        FOREIGN KEY ("id")
            REFERENCES youtubemd.YouTube ("id")
);
--#

-- Additional indexes
CREATE INDEX user_preferences_idx ON youtubemd.Preferences ("user_id");
--#
CREATE INDEX video_metadata_idx ON youtubemd.Video_Has_Metadata ("id", "metadata_id");
--#
CREATE INDEX history_idx ON youtubemd.History ("id", "file_id", "user_id", "metadata_id");
--#

-- Trigger that updates different stats
CREATE FUNCTION youtubemd.process_stats() RETURNS trigger AS
$$
DECLARE
    daily_value   INT;
    weekly_value  INT;
    monthly_value INT;
BEGIN
    IF (SELECT EXISTS(SELECT 1 FROM youtubemd.YouTubeStats WHERE youtubemd.YouTubeStats.id = NEW.id)) THEN
        SELECT INTO daily_value, weekly_value, monthly_value youtubemd.YouTubeStats.daily_requests,
                                                             youtubemd.YouTubeStats.weekly_requests,
                                                             youtubemd.YouTubeStats.monthly_requests
        FROM youtubemd.YouTubeStats
        WHERE youtubemd.YouTubeStats.id = NEW.id;
        daily_value = daily_value + 1;
        weekly_value = weekly_value + 1;
        monthly_value = monthly_value + 1;

        UPDATE youtubemd.YouTubeStats
        SET daily_requests   = daily_value,
            weekly_requests  = weekly_value,
            monthly_requests = monthly_value
        WHERE id = NEW.id;
    ELSE
        INSERT INTO youtubemd.YouTubeStats (id) VALUES (NEW.id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
--#

-- Complementary functions with useful operations
CREATE FUNCTION youtubemd.top_10_daily()
    RETURNS TABLE
            (
                id             VARCHAR(11),
                daily_requests INT
            )
AS
$$
BEGIN
    RETURN QUERY SELECT DISTINCT youtubemd.YouTubeStats.id, youtubemd.YouTubeStats.daily_requests
                 FROM youtubemd.youtubestats
                 ORDER BY daily_requests DESC
                     FETCH FIRST 10 ROWS ONLY;
END;
$$ LANGUAGE plpgsql;
--#

CREATE FUNCTION youtubemd.top_10_weekly()
    RETURNS TABLE
            (
                id              VARCHAR(11),
                weekly_requests INT
            )
AS
$$
BEGIN
    RETURN QUERY SELECT DISTINCT youtubemd.YouTubeStats.id, youtubemd.YouTubeStats.weekly_requests
                 FROM youtubemd.youtubestats
                 ORDER BY weekly_requests DESC
                     FETCH FIRST 10 ROWS ONLY;
END;
$$ LANGUAGE plpgsql;
--#

CREATE FUNCTION youtubemd.top_10_monthly()
    RETURNS TABLE
            (
                id               VARCHAR(11),
                monthly_requests INT
            )
AS
$$
BEGIN
    RETURN QUERY SELECT DISTINCT youtubemd.YouTubeStats.id, youtubemd.YouTubeStats.monthly_requests
                 FROM youtubemd.youtubestats
                 ORDER BY monthly_requests DESC
                     FETCH FIRST 10 ROWS ONLY;
END;
$$ LANGUAGE plpgsql;
--#

CREATE FUNCTION youtubemd.clear_daily_stats() RETURNS VOID AS
$$
BEGIN
    UPDATE youtubemd.YouTubeStats SET daily_requests = 0;
END;
$$ LANGUAGE plpgsql;
--#

CREATE FUNCTION youtubemd.clear_weekly_stats() RETURNS VOID AS
$$
BEGIN
    UPDATE youtubemd.YouTubeStats SET weekly_requests = 0;
END;
$$ LANGUAGE plpgsql;
--#

CREATE FUNCTION youtubemd.clear_monthly_stats() RETURNS VOID AS
$$
BEGIN
    UPDATE youtubemd.YouTubeStats SET monthly_requests = 0;
END;
$$ LANGUAGE plpgsql;
--#

-- Init the trigger
CREATE TRIGGER stats_update
    AFTER INSERT OR UPDATE
    ON youtubemd.YouTube
    FOR EACH ROW
EXECUTE PROCEDURE youtubemd.process_stats();
--#
