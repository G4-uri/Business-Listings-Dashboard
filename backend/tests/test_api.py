def row(name, city="Ahmedabad", cat="Gym", src="MagicPin", **kw):
    return {"business_name": name, "category": cat, "city": city, "source": src, **kw}


def seed(client):
    rows = [row("Gold Gym", address="CG Road", phone="98250 12345"),
            row("Fit Hub", cat="Gym"), row("Taj Cafe", cat="Cafe", src="OSM"),
            row("Sabarmati Park", cat="Park", src="OSM"), row("Pune Gym", city="pune")]
    return client.post("/api/listings/bulk", json={"listings": rows})


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_bulk_insert_and_idempotency(client):
    r = seed(client)
    assert r.status_code == 201 and r.json() == {"received": 5, "inserted": 5, "duplicates_skipped": 0}
    r2 = seed(client)  # re-post the same scrape
    assert r2.json() == {"received": 5, "inserted": 0, "duplicates_skipped": 5}


def test_payload_internal_duplicates(client):
    r = client.post("/api/listings/bulk", json={"listings": [row("Same"), row("  same "), row("SAME")]})
    assert r.json()["inserted"] == 1


def test_validation_errors(client):
    assert client.post("/api/listings/bulk", json={"listings": []}).status_code == 422
    assert client.post("/api/listings/bulk", json={"listings": [{"business_name": "x"}]}).status_code == 422


def test_normalisation(client):
    seed(client)
    items = client.get("/api/listings", params={"q": "Gold"}).json()["items"]
    assert items[0]["phone"] == "+91 9825012345"
    assert "Pune" in client.get("/api/filters").json()["cities"]  # 'pune' -> 'Pune'


def test_counts(client):
    seed(client)
    by_city = client.get("/api/stats/by-city").json()
    assert by_city["total"] == 5 and by_city["data"][0] == {"label": "Ahmedabad", "count": 4}
    by_cat = client.get("/api/stats/by-category").json()["data"]
    assert {"label": "Gym", "count": 3} in by_cat
    by_src = client.get("/api/stats/by-source").json()["data"]
    assert {"label": "OSM", "count": 2} in by_src


def test_cross_filtering(client):
    seed(client)
    # filter: category=Gym -> city chart shows only gyms, sources chart only gym sources
    d = client.get("/api/stats/by-city", params={"category": "Gym"}).json()
    assert d["total"] == 3
    # the category chart keeps sibling bars when it is itself filtered (cross=true)
    d = client.get("/api/stats/by-category", params={"category": "Gym"}).json()
    assert len(d["data"]) == 3
    d = client.get("/api/stats/by-category", params={"category": "Gym", "cross": "false"}).json()
    assert len(d["data"]) == 1


def test_summary_and_pagination(client):
    seed(client)
    s = client.get("/api/stats/summary", params={"city": "Ahmedabad"}).json()
    assert s["total_listings"] == 4 and s["with_phone"] == 1
    p = client.get("/api/listings", params={"page_size": 2, "page": 2}).json()
    assert p["total"] == 5 and len(p["items"]) == 2


def test_csv_export(client):
    seed(client)
    r = client.get("/api/listings/export.csv", params={"category": "Park"})
    assert r.headers["content-type"].startswith("text/csv")
    assert "Sabarmati Park" in r.text and "Gold Gym" not in r.text


def test_unfiltered_summary_counts_all_rows(client):
    seed(client)
    s = client.get("/api/stats/summary").json()
    assert s["total_listings"] == 5 and s["cities"] == 2 and s["sources"] == 2
