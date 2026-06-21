--  CRYSTALS-Kyber Training Platform, MySQL 8 Schema
--  Executed automatically on first container start via docker-entrypoint-initdb.d
--  Engine: InnoDB  |  Charset: utf8mb4  |  Collation: utf8mb4_unicode_ci

SET NAMES utf8mb4;
SET time_zone = '+00:00';

-- Users
CREATE TABLE IF NOT EXISTS users (
    id             BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    username       VARCHAR(32)      NOT NULL,
    email          VARCHAR(255)     NOT NULL,
    password_hash  VARCHAR(255)     NOT NULL,
    is_active      TINYINT(1)       NOT NULL DEFAULT 1,
    is_admin       TINYINT(1)       NOT NULL DEFAULT 0,
    login_attempts SMALLINT         NOT NULL DEFAULT 0,
    locked_until   DATETIME(6)               DEFAULT NULL,
    created_at     DATETIME(6)      NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    last_login     DATETIME(6)               DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_username (username),
    UNIQUE KEY uq_users_email    (email)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;

-- Submissions, every answer attempt
CREATE TABLE IF NOT EXISTS submissions (
    id           BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    user_id      BIGINT UNSIGNED  NOT NULL,
    mode         VARCHAR(16)      NOT NULL  COMMENT 'veryeasy|easy|medium|hard|veryhard|insane',
    question_id  INT UNSIGNED     NOT NULL,
    correct      TINYINT(1)       NOT NULL,
    score_delta  INT              NOT NULL DEFAULT 0,
    created_at   DATETIME(6)      NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    KEY ix_submissions_user_mode (user_id, mode),
    KEY ix_submissions_created   (created_at),
    CONSTRAINT fk_submissions_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;

-- Leaderboard, best score per user per mode
CREATE TABLE IF NOT EXISTS leaderboard (
    id              BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    user_id         BIGINT UNSIGNED  NOT NULL,
    mode            VARCHAR(16)      NOT NULL,
    best_score      INT              NOT NULL DEFAULT 0,
    total_correct   INT              NOT NULL DEFAULT 0,
    total_attempts  INT              NOT NULL DEFAULT 0,
    best_streak     INT              NOT NULL DEFAULT 0,
    completed_at    DATETIME(6)               DEFAULT NULL,
    updated_at      DATETIME(6)      NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                                     ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    UNIQUE KEY uq_leaderboard_user_mode (user_id, mode),
    KEY ix_leaderboard_mode_score       (mode, best_score DESC),
    CONSTRAINT fk_leaderboard_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;

-- Revoked tokens, JWT refresh token blacklist
CREATE TABLE IF NOT EXISTS revoked_tokens (
    id         BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    jti        VARCHAR(64)      NOT NULL,
    revoked_at DATETIME(6)      NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    expires_at DATETIME(6)      NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_revoked_jti (jti),
    KEY ix_revoked_expires    (expires_at)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;
