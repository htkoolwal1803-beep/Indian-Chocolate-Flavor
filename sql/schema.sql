PRAGMA foreign_keys=ON;
CREATE TABLE sources (
 source_id TEXT PRIMARY KEY,url TEXT NOT NULL,brand TEXT NOT NULL,retrieved_date TEXT NOT NULL,
 crawl_age_days_approx INTEGER,method TEXT NOT NULL,location TEXT NOT NULL
);
CREATE TABLE products (
 observation_id TEXT PRIMARY KEY,source_id TEXT REFERENCES sources(source_id),brand TEXT NOT NULL,
 title TEXT NOT NULL,pack_label TEXT,total_weight_g REAL CHECK(total_weight_g>0),
 price_inr REAL CHECK(price_inr>0),reference_price_inr REAL,
 rating REAL CHECK(rating BETWEEN 1 AND 5),rating_count INTEGER CHECK(rating_count>0),
 notify_me INTEGER,format TEXT NOT NULL,subbrand TEXT NOT NULL,cocoa_pct REAL,
 family_group TEXT NOT NULL,source_url TEXT NOT NULL
);
CREATE TABLE product_flavors (
 observation_id TEXT REFERENCES products(observation_id),flavor TEXT NOT NULL,
 PRIMARY KEY(observation_id,flavor)
);
CREATE TABLE exclusions (observation_id TEXT PRIMARY KEY,title TEXT,reason TEXT);
CREATE VIEW priced_products AS
 SELECT p.*,s.crawl_age_days_approx,
  100.0*price_inr/total_weight_g AS price_per_100g,
  CASE WHEN reference_price_inr>=price_inr THEN 100.0*(1-price_inr/reference_price_inr) ELSE NULL END AS advertised_discount_pct
 FROM products p JOIN sources s USING(source_id)
 WHERE price_inr IS NOT NULL AND total_weight_g IS NOT NULL;
CREATE INDEX ix_products_brand ON products(brand);
CREATE INDEX ix_products_family ON products(family_group);
