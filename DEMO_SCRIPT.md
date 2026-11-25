# Demo video script (3-5 minutes)

**0:00-0:30 - Intro.** "A pipeline from scraped listings to a MySQL table, a FastAPI service and a React dashboard."
Show the repo tree (backend / frontend / database / notebooks).

**0:30-1:45 - Scraping approach (notebook).** Open `01_collect_clean_load.ipynb`.
* Why OpenStreetMap + my own MagicPin scrape instead of JustDial/Google (Terms of Use).
* Run the Overpass cell: per-city query, mirror fail-over, cache.
* Show the validation cell: same Pydantic model as the API, reject report, fingerprint de-duplication.
* Show the data-quality report and the 500+ assertion.

**1:45-2:45 - API working.** Open `http://127.0.0.1:8000/docs`.
* `POST /api/listings/bulk` - run the notebook's load cell, point at `inserted: 547`; run it again -> `inserted: 0, duplicates_skipped: 547` (idempotent).
* `GET /api/stats/by-city`, `by-category`, `by-source`; then add `?category=Gym%20%26%20Fitness` to show cross-filtering.
* In MySQL: `SELECT source, COUNT(*) FROM listing_master GROUP BY source;`

**2:45-4:15 - Dashboard.** Open `localhost:5173`.
* Read the sentence filter. Click the Ahmedabad bar -> all charts and the table update; click again to clear.
* Click the OpenStreetMap slice. Show the URL hash changing (shareable view).
* Search the table, Download CSV, toggle dark mode, shrink the window to show mobile.
* Mention the synthetic-data banner and why it exists.

**4:15-4:45 - Wrap-up.** Challenges (Overpass outages, duplicates, the COUNT(*) bug caught by running end-to-end),
what you'd do next (auth, Alembic migrations, more sources, deployment).
