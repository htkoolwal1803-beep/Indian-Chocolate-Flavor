SELECT s.source_id,s.brand,s.crawl_age_days_approx,COUNT(p.observation_id) AS retained_listings,
 SUM(p.price_inr IS NULL) AS missing_prices,SUM(p.rating IS NULL) AS missing_ratings,
 SUM(p.total_weight_g IS NULL) AS missing_weights
FROM sources s LEFT JOIN products p USING(source_id)
GROUP BY s.source_id ORDER BY s.crawl_age_days_approx DESC;
