SELECT brand,COUNT(*) AS priced_listings,ROUND(AVG(price_per_100g),2) AS mean_inr_per_100g,
 ROUND(MIN(price_per_100g),2) AS min_inr_per_100g,ROUND(MAX(price_per_100g),2) AS max_inr_per_100g,
 COUNT(rating) AS rated_listings
FROM priced_products GROUP BY brand ORDER BY mean_inr_per_100g;
