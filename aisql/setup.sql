PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS `players` (
  `id` INTEGER NOT NULL PRIMARY KEY,
  `source_player_id` INTEGER NULL,
  `first_name` TEXT NOT NULL,
  `last_name` TEXT NOT NULL,
  `gender` TEXT,
  `country_code` TEXT NULL,
  `birth_date` TEXT NULL DEFAULT NULL,
  UNIQUE (`source_player_id`)
);

CREATE TABLE IF NOT EXISTS `tournaments` (
  `id` INTEGER NOT NULL PRIMARY KEY,
  `name` TEXT NOT NULL,
  `level` TEXT NULL,
  `surface` TEXT NULL,
  UNIQUE (`name`)
);

CREATE TABLE IF NOT EXISTS `tournament_editions` (
  `id` INTEGER NOT NULL PRIMARY KEY,
  `tournament_id` INTEGER NOT NULL,
  `year` INTEGER NOT NULL,
  `end_date` TEXT NOT NULL,
  UNIQUE (`tournament_id`, `year`),
  FOREIGN KEY (`tournament_id`) REFERENCES `tournaments` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS `matches` (
  `id` INTEGER PRIMARY KEY,
  `tournament_edition_id` INTEGER NOT NULL,
  `winner_id` INTEGER NOT NULL,
  `loser_id` INTEGER NOT NULL,
  `round` TEXT NOT NULL,
  `score` TEXT NULL,
  FOREIGN KEY (`tournament_edition_id`) REFERENCES `tournament_editions` (`id`) 
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`winner_id`) REFERENCES `players` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`loser_id`) REFERENCES `players` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS `rankings` (
  `id` INTEGER PRIMARY KEY,
  `player_id` INTEGER NOT NULL,
  `ranking_date` TEXT NOT NULL,
  `rank` INTEGER NOT NULL,
  `points` INTEGER NULL,
  UNIQUE (`player_id`, `ranking_date`),
  FOREIGN KEY (`player_id`) REFERENCES `players` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
);

