# Model card: indexed retail price benchmarking

**Question:** Do pack mass, cocoa percentage and title-derived flavors improve prediction of listed INR/100g over brand/format baselines?

**Target population:** the observed retailer-index listings. Not national transactions, willingness to pay, sales or consumer preference.

## Models

- Global training-fold median.
- Brand/format training-fold median, falling back to brand median and then global median for unseen combinations.
- Ridge using brand and format only.
- Full ridge adding pack mass, explicit cocoa percentage and flavor flags.

Ridge uses a log target, alpha=10 fixed before evaluation, one-hot categories and standardized numeric inputs. Median imputation plus missing indicators is fit inside each fold. An entirely missing training feature is retained with zero fill and its missing indicator, rather than inferred from held-out data. The log inverse gives positive predictions; the estimand is evaluated on the original INR/100g scale. No price-derived feature, reference price, rating or target encoding is used.

## Validation

Five-fold GroupKFold uses brand × subbrand × format × flavor-family combination. This conservatively groups related flavors and pack variants; it can hold out a large fraction of a brand-format combination and is harder than random row splitting. It does not eliminate all possible recipe similarity.

Leave-one-brand-out tests transfer to each of six unseen brand groups. Recent-source-only evaluation retains approximate crawl ages <=30 days; this drops Ferrero and Silk and therefore confounds recency with coverage. Exclude-gifts evaluation tests the effect of removing assorted/gift formats. All four scenarios and every out-of-fold prediction are exported.

MAE and R² use held-out predictions. Paired error improvement of full ridge over the median baseline is cluster-bootstrapped 2,000 times by the evaluation group (seed 42). Positive improvement favors ridge. This resamples fixed OOF errors; it does not capture the full uncertainty of repeated training, overlapping folds or independent market samples. No causal confidence intervals or flavor-premium claims follow.

## Ratings

The descriptive smoothed score is `(n*r + m*C)/(n+m)`, where C is the unweighted mean displayed product rating within brand and m is 20, 100 or 500. Unweighted priors avoid summing potentially shared counts; duplicate listings and selection can still influence them. The prior includes the focal item. This is descriptive shrinkage, not a calibrated posterior or predictive procedure. Aggregate mean/count data are insufficient for a defensible variance estimate; no statistical significance of preference is claimed.

## Limitations

Single retailer ecosystem; location unspecified; index snapshots of different ages; missing prices and cocoa; promotional and gift-format confounding; incomplete category coverage; title-based features; pooled review counts; no sales or representative panel data. No production forecasting deployment is claimed.

Next steps: collect synchronized observations for a specified postcode, include competing retailers, verify ingredients/format, broaden brands and use independent consumer or sales outcomes. Keep simple baselines in the evaluation.
