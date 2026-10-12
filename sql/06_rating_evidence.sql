SELECT brand,COUNT(*) AS listings,COUNT(rating) AS rated_listings,
 SUM(CASE WHEN rating_count<100 THEN 1 ELSE 0 END) AS rated_below_100,
 ROUND(AVG(rating),3) AS unweighted_mean_displayed_stars
FROM products GROUP BY brand;
