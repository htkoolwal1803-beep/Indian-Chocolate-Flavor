# Chocolate Flavor Intelligence · India

**SQL + Python data science on mainstream chocolate brands sold to Indian consumers.**

**Cadbury · Amul · Nestle · Hershey's · Ferrero Rocher · Snickers**

[Findings](reports/FINDINGS.md) · [Executed notebook](notebooks/01_chocolate_intelligence.ipynb) · [SQL](sql/) · [Data dictionary](docs/DATA_DICTIONARY.md) · [Model card](docs/MODEL_CARD.md)

![Mainstream chocolate price positioning](reports/figures/price_positioning.png)

## Business question

How do familiar chocolate brands differentiate their flavor assortments, how do listed prices compare after accounting for pack size and format, and how much evidence sits behind their customer ratings?

The dataset contains **161 retained retail listings**, **155 usable prices**, and **148 listings with aggregate ratings**, across six mainstream brand groups. The original 167 observed cards and all exclusion decisions are retained. Data comes from public BigBasket/bbnow category-page extracts, not synthetic sales or invented survey responses.

**Scope matters:** these are retailer-index observations retrieved on 12 October 2026, with differing crawl ages and an unspecified delivery location. They are not a synchronized live-price panel or a representative survey of India.

## Results

| Finding | Evidence | Business interpretation |
|---|---|---|
| Named inclusions do not always raise the listed price | Amul plain dark, tropical orange and fruit-and-nut: each **₹180 for 150g** in the sampled cards | Compare equivalent packs before assuming a flavor premium |
| Nuts and fruit recur across mainstream assortments | **36/161** listings name nuts; **19/161** name fruit | Describes available choices in this sample, not consumer demand; categories overlap |
| A simple baseline outperforms full ridge | Grouped MAE: **₹35.85/100g** for brand/format median vs **₹45.08/100g** for full ridge | Extra model complexity is not supported by this sample |
| Some ratings have limited evidence | **28/148** rated listings have fewer than 100 displayed ratings | Interpret small-count scores cautiously; counts may be pooled across packs |

Median indexed prices per 100g range from ₹100 for the sampled Nestle mix to ₹328.50 for Ferrero Rocher. These are descriptive: format, promotions, brand mix and source age differ. The SQL and models explicitly examine those limitations.

## What the project demonstrates

- **SQL:** relational SQLite schema, foreign keys, joins, CTEs, window functions and seven analytical queries.
- **Data preparation:** auditable source records, multipack-weight parsing, price/reference-price separation, explicit exclusions and duplicate handling.
- **Feature engineering:** inspectable title-based flavor tags, broad product formats and subbrands; sparse cocoa percentages remain missing until fold-local imputation.
- **Machine learning:** log-target ridge regression compared with global and brand/format median baselines; grouped and unseen-brand validation.
- **Uncertainty:** paired cluster bootstrap of held-out errors; sensitivity to older sources and gift assortments.
- **Consumer evidence:** descriptive within-brand rating shrinkage at three prior strengths; no unsupported sentiment or national-preference claims.
- **Quality:** 19 tests for data integrity, provenance, pack math, parsing edge cases, duplicate handling, matched comparisons and split isolation.

## Reproduce offline

Python 3.12+ recommended. SQLite comes with Python; no API keys, paid services or database server are required.

```bash
git clone https://github.com/htkoolwal1803-beep/Indian-Chocolate-Flavor.git
cd Indian-Chocolate-Flavor
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m src.run
python -m unittest discover -s tests -v
```

Open the executed notebook in Jupyter or VS Code, or regenerate it:

```bash
python -m src.notebook
```

The committed factual snapshot regenerates the SQLite database, all SQL output tables, model results, charts, findings and resume bullets. `requirements-tested.txt` records the local dependency versions; `requirements.txt` specifies compatible ranges. GitHub Actions runs the offline analysis and tests.

## Layout

```text
data/          raw factual observations, source manifest, analytical table
src/           capture importer, cleaning, SQLite build, modeling, reporting
sql/           schema and seven analytical queries
notebooks/     executed walkthrough with results and visualizations
reports/       findings, charts, metrics, query outputs, resume bullets
docs/          data dictionary, model card, interview guide
tests/         19 data and evaluation checks
.github/       offline reproduction workflow
```

## Source and refresh policy

Sources: [Amul](https://bbnow.bigbasket.com/pb/amul/chocolates/), [Nestle](https://www.bigbasket.com/pb/nestle/chocolates-candies/), [Cadbury Dairy Milk](https://www.bigbasket.com/pb/cadbury-dairy-milk/chocolates-candies/), [Cadbury Silk](https://www.bigbasket.com/pb/cadbury-dairy-milk-silk/?nc=fa), [Hershey's](https://www.bigbasket.com/pb/hersheys/chocolates-candies/?nc=nb), [Ferrero Rocher](https://www.bigbasket.com/pb/ferrero-rocher/?nc=fa), [Snickers](https://www.bigbasket.com/pb/snickers//).

Each observation includes its exact source page, source ID, card position and original pack label. `data/sources.json` records retrieval method and approximate crawl age. Direct retailer HTTP access was blocked; no access control was bypassed. Public indexed extracts were used, and some pages are older than others. Read the [data dictionary](docs/DATA_DICTIONARY.md) before interpreting results.

Refreshing requires new accessible public extracts or an authorized retailer export. It is deliberately separate from offline reproduction. The importer accepts saved text files named by source ID and writes a **candidate** snapshot for review:

```bash
python -m src.import_capture --captures path/to/extracts --out data/candidate.json
```

Review parsing, exclusions, source dates and coverage before adopting a refreshed dataset. No individual reviews were collected for this version; displayed rating counts must not be summed as unique consumers. No market share, sales, causal willingness-to-pay or India's favorite-flavor claim is made.

## Resume and interview use

Start with the [findings](reports/FINDINGS.md), then run the [notebook](notebooks/01_chocolate_intelligence.ipynb). Read the [interview guide](docs/INTERVIEW_GUIDE.md) and use the [resume bullets](reports/RESUME_BULLETS.md) only after understanding the work.

Developed with AI assistance. All reported results are generated from the factual snapshot; assumptions and limitations are explicit. Original code and documentation are MIT-licensed. No open license is asserted for third-party source material, and no marketing prose, source images or full pages are redistributed.
