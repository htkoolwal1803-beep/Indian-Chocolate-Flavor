WITH benchmark AS (
 SELECT brand,format,AVG(price_per_100g) mean_price FROM priced_products GROUP BY brand,format
)
SELECT p.brand,p.format,f.flavor,COUNT(*) n,
 ROUND(AVG(p.price_per_100g),2) AS mean_inr_per_100g,
 ROUND(AVG(p.price_per_100g-b.mean_price),2) AS difference_from_brand_format_mean
FROM priced_products p JOIN product_flavors f USING(observation_id)
JOIN benchmark b ON p.brand=b.brand AND p.format=b.format
GROUP BY p.brand,p.format,f.flavor ORDER BY p.brand,p.format,n DESC;
