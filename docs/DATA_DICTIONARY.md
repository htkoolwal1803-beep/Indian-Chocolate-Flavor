# Data and sampling contract

## Scope

Mainstream chocolate products sold to Indian consumers through retail: Cadbury, Amul, Nestle, Hershey's, Ferrero Rocher and Snickers. This is a convenience sample from seven BigBasket/bbnow brand/category pages, not a complete industry census. Cadbury includes Dairy Milk and Silk; Nestle includes KitKat, Munch, Milkybar and Classic. The six labels are consumer-facing brand groups, not six equivalent parent corporations. International ownership does not imply a product was manufactured in India; origin is not inferred.

## Capture provenance

The dataset contains **167 raw observed product-card records**, with 161 retained after excluding three baking slabs/compounds, one Polo mint, one incomplete search preview and one duplicate Silk Oreo Red Velvet card. Of the retained listings, 155 have usable listed prices.

Records were extracted programmatically from public web-retrieval text and reviewed for pack parsing, price/reference-price separation, missing values and duplicate titles. Direct HTTP access to BigBasket returned 403; it was not bypassed. Public indexed page extracts were used. The delivery postcode and exact underlying snapshot times were not exposed.

**Retrieval date is 12 October 2026; it is not the price-observation date.** Displayed crawl ages were: Amul today; Nestle two days; Dairy Milk five days; Hershey's and Snickers last month; Ferrero two months; Silk three months. Numeric ages 0/2/5/30/60/90 are approximate encodings, not exact crawl dates. Hershey's and Snickers use expanded search-result page extracts; the other pages were opened through public indexed retrieval. Source hashes identify locally retained retrieval text, not origin-server responses. Full captures are retained in the working audit files and are not redistributed.

## Raw observations

| Field | Meaning |
|---|---|
| observation_id | Source ID plus product-card position; snapshot-specific, not a manufacturer SKU |
| source_id / source_url | Foreign key and the exact category-page URL; not a guessed product URL |
| source_position | Card order within the captured extraction; useful for audit, may change on refresh |
| brand / title | Retail brand grouping and original title |
| pack_label | Original pack-size text |
| price_inr | First displayed numeric price; null if absent |
| reference_price_inr | Second displayed reference/struck-through price, if present; not assumed to be a prior paid price |
| rating / rating_count | Displayed average stars and count; null means missing, not zero |
| notify_me | The card contained a Notify Me marker; absence does not prove current availability |

No individual reviews, names, emails or author details are included. Displayed counts can be shared across variants, so they must not be summed as unique reviews, consumers or sales.

## Derived fields

- `total_weight_g`: `3x51 g` becomes 153g; `16 g (Pack of 9)` becomes 144g; `111 g (15x7.4 g)` remains 111g because the leading value is already total mass.
- `price_per_100g`: price / total grams × 100. Never use per-unit mass as the denominator for a multipack price.
- `format`: title-derived gift/assortment, wafer, bites/tubes, filled bar or bar/other; precedence is defined in `src/features.py`. These are broad merchandising categories, not lab-verified composition.
- `subbrand`: title-derived Silk, KitKat, Munch, Milkybar, Kisses, Exotic, Moments, Bar One, or brand fallback.
- `cocoa_pct`: explicit title percentage only; no inference from brand or product color. Sparse and strongly associated with Amul coverage.
- Flavor bridge: overlapping title-based families for nuts, fruit, coffee, caramel/butterscotch, cookie/brownie, salt, spice/tea and dessert specialties. `no_named_inclusion` means no lexicon match, not flavorless.
- `family_group`: brand × subbrand × format × flavor-family combination. Conservative grouping keeps related products and pack sizes together during validation.

## Deduplication and missingness

Exact normalized title plus total pack mass is the duplicate key. An explicit alias handles reordered/repeated names for Silk Oreo Red Velvet. First source-order observation is retained; the excluded row remains in the raw snapshot and exclusions table. This is not perfect recipe-level deduplication; sizes and merchandising editions can repeat formulas.

Listings without prices stay in assortment/rating analyses and are excluded from price modeling. Missing cocoa is imputed inside training folds only. Missing ratings are never changed to zero. Source age, unspecified location, promotions, non-random assortment and pooled ratings limit comparisons.

## Refresh and rights

The full analytical pipeline is reproducible offline from the factual snapshot. Refreshing the source capture requires newly accessible public page extracts or an authorized retailer export; it is not an unattended live scraper. `src/import_capture.py` can parse saved text extracts using the documented source manifest. Review the resulting raw records and duplicate rules before replacing the snapshot. Do not evade rate limits, login requirements or blocked endpoints.

Only product facts and derived analysis are distributed. No marketing paragraphs, product images, full HTML or review prose are republished. The MIT license covers original project code and documentation; no license is asserted for third-party material.
