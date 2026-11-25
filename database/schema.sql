-- Business Listings Dashboard - MySQL 8 schema
-- Run:  mysql -u root -p < database/schema.sql
CREATE DATABASE IF NOT EXISTS business_listings
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE business_listings;

CREATE TABLE IF NOT EXISTS listing_master (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  business_name VARCHAR(255)  NOT NULL,
  category      VARCHAR(100)  NOT NULL,
  sub_category  VARCHAR(100)  NULL,
  address       VARCHAR(500)  NULL,
  area          VARCHAR(150)  NULL,
  city          VARCHAR(100)  NOT NULL,
  state         VARCHAR(100)  NULL,
  phone         VARCHAR(30)   NULL,
  website       VARCHAR(500)  NULL,
  latitude      DECIMAL(9,6)  NULL,
  longitude     DECIMAL(9,6)  NULL,
  source        VARCHAR(60)   NOT NULL COMMENT 'where the row was scraped from',
  source_url    VARCHAR(500)  NULL,
  fingerprint   CHAR(64)      NOT NULL COMMENT 'sha256(name|city|address) - makes bulk insert idempotent',
  scraped_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_listing_fingerprint (fingerprint),
  KEY idx_city (city),
  KEY idx_category (category),
  KEY idx_source (source),
  KEY idx_city_category (city, category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
