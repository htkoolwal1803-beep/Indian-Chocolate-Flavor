# Interview walkthrough

“I analyzed mainstream chocolate listings sold in India using SQL and Python. I built a normalized SQLite database, preserved source provenance, parsed multipack weights, and compared flavors within brand and format. For a predictive component, I evaluated ridge regression against global and brand/format median baselines with grouped and unseen-brand validation. I also compared aggregate ratings using descriptive shrinkage. The project shows how data quality and evaluation design constrain what a business can conclude.”

Be ready to explain:

1. **Why mainstream brands?** The business scope is familiar consumer chocolate sold in India, including retailer channels; it is not limited to brand-owned storefronts.
2. **Why not call it India's favorite flavor?** Online assortment and self-selected retailer ratings are not representative preference or sales data.
3. **What was the key cleaning issue?** Multipack total mass. Three 51g bars cost a multipack price and must be divided by 153g, not 51g.
4. **Why group validation?** Pack sizes and related product families would otherwise make a random split unrealistically easy.
5. **What if the baseline wins?** Report the evidence. A more complex model is only useful if it adds held-out value.
6. **Are these today's prices?** No. These are public index observations retrieved on one date with different crawl ages and no exposed delivery postcode.
7. **What data would improve the business recommendation?** Synchronized multi-retailer prices, verified ingredients, complete authorized review exports and representative consumer/sales outcomes.

Read the executed notebook and generated findings before using the resume bullets. Change an assumption and rerun the project so you can explain it independently. Do not claim revenue impact, sentiment-model accuracy or representative national coverage.
