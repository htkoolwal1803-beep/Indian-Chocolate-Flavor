-- Categories overlap. Denominator includes unpriced listings; this is not demand.
SELECT flavor,COUNT(*) AS listings,COUNT(DISTINCT brand) AS brands,
 ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM products),1) AS pct_listings
FROM product_flavors JOIN products USING(observation_id)
GROUP BY flavor ORDER BY listings DESC;
