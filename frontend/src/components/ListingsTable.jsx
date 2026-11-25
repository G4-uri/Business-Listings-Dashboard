import { useEffect, useState } from "react";
import { api } from "../api";

/** The accessible "table view" of the charts: same filters, plus text search and pagination. */
export default function ListingsTable({ filters }) {
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);
  const [res, setRes] = useState({ items: [], total: 0 });
  const [status, setStatus] = useState("loading");

  useEffect(() => setPage(1), [filters, q]);
  useEffect(() => {
    let alive = true;
    setStatus("loading");
    const t = setTimeout(() => {   // debounce typing
      api.listings(filters, page, q)
        .then((r) => alive && (setRes(r), setStatus("ok")))
        .catch(() => alive && setStatus("error"));
    }, 200);
    return () => { alive = false; clearTimeout(t); };
  }, [filters, page, q]);

  const pages = Math.max(1, Math.ceil(res.total / 15));
  return (
    <section className="panel table-panel" aria-labelledby="tbl-h">
      <header className="panel-head">
        <h2 id="tbl-h">Listings</h2>
        <input type="search" placeholder="Search name, address or area" value={q} onChange={(e) => setQ(e.target.value)}
               aria-label="Search listings" />
        <a className="btn" href={api.exportUrl(filters)} download>Download CSV</a>
      </header>
      <div className="table-wrap" aria-busy={status === "loading"}>
        <table>
          <thead><tr><th>Business</th><th>Category</th><th>Area, city</th><th>Phone</th><th>Source</th></tr></thead>
          <tbody>
            {res.items.map((l) => (
              <tr key={l.id}>
                <td>{l.business_name}</td>
                <td>{l.category}</td>
                <td>{[l.area, l.city].filter(Boolean).join(", ")}</td>
                <td className="num">{l.phone || <span className="dash">–</span>}</td>
                <td>{l.source_url?.startsWith("http") ? <a href={l.source_url} target="_blank" rel="noreferrer">{l.source}</a> : l.source}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {status === "ok" && !res.items.length && <p className="empty">No listings match. Clear a filter or change the search.</p>}
        {status === "error" && <p className="empty">Could not load listings. Check that the API is running.</p>}
      </div>
      <footer className="pager">
        <span>{res.total.toLocaleString()} results</span>
        <button className="btn" disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</button>
        <span>Page {page} of {pages}</span>
        <button className="btn" disabled={page >= pages} onClick={() => setPage(page + 1)}>Next</button>
      </footer>
    </section>
  );
}
