import { useEffect, useState } from "react";
import { api } from "./api";
import { RankedBars, SourceDonut } from "./components/Charts.jsx";
import ListingsTable from "./components/ListingsTable.jsx";
import { useDashboard } from "./useDashboard";

function Select({ label, value, options, all, onChange }) {
  return (
    <label className="sel">
      <span className="sr">{label}</span>
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="">{all}</option>
        {options.map((o) => <option key={o}>{o}</option>)}
      </select>
    </label>
  );
}

function Panel({ title, hint, children, className = "" }) {
  return (
    <section className={`panel ${className}`}>
      <header className="panel-head"><h2>{title}</h2>{hint && <p>{hint}</p>}</header>
      {children}
    </section>
  );
}

export default function App() {
  const { filters, data, loading, error, toggle, clear } = useDashboard();
  const [options, setOptions] = useState({ cities: [], categories: [], sources: [] });
  const [theme, setTheme] = useState(() => document.documentElement.dataset.theme || "");
  useEffect(() => { api.filters().then(setOptions).catch(() => {}); }, []);

  const dark = theme ? theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
  const flip = () => {
    const next = dark ? "light" : "dark";
    setTheme(next); document.documentElement.dataset.theme = next;
    try { localStorage.setItem("theme", next); } catch { /* private mode */ }
  };

  const s = data.summary;
  const active = Object.values(filters).some(Boolean);
  const sampleRow = data.source?.data.find((d) => d.label.startsWith("Sample"));
  // only warn when synthetic rows are actually inside the current view
  const synthetic = sampleRow && (!filters.source || filters.source.startsWith("Sample")) ? sampleRow : null;
  const n = (k, one, many) => `${k} ${k === 1 ? one : many}`;

  return (
    <div className={`app ${loading ? "is-loading" : ""}`}>
      <header className="top">
        <div>
          <h1>Listings Ledger</h1>
          <p className="sub">Scraped business listings, counted by city, category and source.</p>
        </div>
        <button className="btn" onClick={flip} aria-pressed={dark}>{dark ? "Light mode" : "Dark mode"}</button>
      </header>

      {error ? (
        <div className="error" role="alert"><b>Dashboard can't load.</b> {error}</div>
      ) : (
        <>
          <p className="sentence" aria-live="polite">
            Showing <b className="big">{s ? s.total_listings.toLocaleString() : "…"}</b> listings in
            <Select label="City" value={filters.city} options={options.cities} all="every city" onChange={(v) => toggle("city", v || filters.city)} />
            for
            <Select label="Category" value={filters.category} options={options.categories} all="every category" onChange={(v) => toggle("category", v || filters.category)} />
            from
            <Select label="Source" value={filters.source} options={options.sources} all="every source" onChange={(v) => toggle("source", v || filters.source)} />
            {active && <button className="link" onClick={clear}>Clear filters</button>}
          </p>
          {s && <p className="facts">{n(s.cities, "city", "cities")} · {n(s.categories, "category", "categories")} · {s.with_phone.toLocaleString()} with a phone number · {s.with_coordinates.toLocaleString()} with map coordinates</p>}
          {synthetic && (
            <p className="note" role="note">
              <b>{synthetic.count.toLocaleString()} of these rows are synthetic sample data</b> (grey), used to demo the pipeline offline.
              Filter on a real source to see only scraped listings.
            </p>
          )}

          <div className="grid">
            <Panel title="Listings by city" hint="Click a bar to filter" className="span-7">
              <RankedBars rows={data.city?.data ?? []} total={data.city?.total ?? 0} active={filters.city} onPick={(l) => toggle("city", l)} empty="No cities match these filters." />
            </Panel>
            <Panel title="Listings by source" hint="Click a slice or a name" className="span-5">
              <SourceDonut rows={data.source?.data ?? []} total={data.source?.total ?? 0} active={filters.source} onPick={(l) => toggle("source", l)} empty="No sources match these filters." />
            </Panel>
            <Panel title="Listings by category" hint="Click a bar to filter" className="span-12">
              <RankedBars rows={data.category?.data ?? []} total={data.category?.total ?? 0} active={filters.category} onPick={(l) => toggle("category", l)} empty="No categories match these filters." />
            </Panel>
          </div>
          <ListingsTable filters={filters} />
        </>
      )}
    </div>
  );
}
