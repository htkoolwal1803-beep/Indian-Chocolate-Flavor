SELECT brand,format,COUNT(*) AS listings,ROUND(AVG(price_per_100g),2) AS mean_inr_per_100g
FROM priced_products GROUP BY brand,format ORDER BY brand,listings DESC;
