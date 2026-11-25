// Thin fetch wrapper: one place for the base URL, query-string building and error messages.
const BASE = import.meta.env.VITE_API_URL || "";

const qs = (params) => {
  const p = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => v !== "" && v != null && p.set(k, v));
  const s = p.toString();
  return s ? `?${s}` : "";
};

async function get(path, params = {}) {
  let res;
  try {
    res = await fetch(`${BASE}${path}${qs(params)}`);
  } catch {
    throw new Error("Cannot reach the API. Start it with: uvicorn app.main:app --reload");
  }
  if (!res.ok) throw new Error(`API returned ${res.status} for ${path}`);
  return res.json();
}

export const api = {
  filters: () => get("/api/filters"),
  summary: (f) => get("/api/stats/summary", f),
  byCity: (f) => get("/api/stats/by-city", f),
  byCategory: (f) => get("/api/stats/by-category", f),
  bySource: (f) => get("/api/stats/by-source", f),
  listings: (f, page, q) => get("/api/listings", { ...f, page, page_size: 15, q }),
  exportUrl: (f) => `${BASE}/api/listings/export.csv${qs(f)}`,
};
