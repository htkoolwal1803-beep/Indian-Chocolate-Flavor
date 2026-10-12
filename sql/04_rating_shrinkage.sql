-- Avoid summing potentially shared review counts. Equal-weight brand mean is a descriptive prior.
WITH prior AS (SELECT brand,AVG(rating) mean_rating FROM products WHERE rating IS NOT NULL GROUP BY brand),
scores AS (
 SELECT p.observation_id,p.brand,p.title,p.pack_label,p.rating,p.rating_count,
 (p.rating*p.rating_count+100*b.mean_rating)/(p.rating_count+100) AS smoothed_score
 FROM products p JOIN prior b USING(brand) WHERE p.rating_count>0
)
SELECT *,DENSE_RANK() OVER(PARTITION BY brand ORDER BY smoothed_score DESC) AS within_brand_rank
FROM scores ORDER BY brand,within_brand_rank;
