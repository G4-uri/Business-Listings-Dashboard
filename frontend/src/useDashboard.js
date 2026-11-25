import { useCallback, useEffect, useState } from "react";
import { api } from "./api";

const EMPTY = { city: "", category: "", source: "" };

/** All dashboard state in one hook: the 3 filters live in the URL hash so a view is shareable/bookmarkable. */
export function useDashboard() {
  const [filters, setFilters] = useState(() => ({ ...EMPTY, ...Object.fromEntries(new URLSearchParams(location.hash.slice(1))) }));
  const [data, setData] = useState({ summary: null, city: null, category: null, source: null });
  const [state, setState] = useState({ loading: true, error: null });

  useEffect(() => {
    const h = new URLSearchParams(Object.entries(filters).filter(([, v]) => v)).toString();
    history.replaceState(null, "", h ? `#${h}` : location.pathname);
  }, [filters]);

  useEffect(() => {
    let alive = true; // ignore responses from stale filter combinations
    setState((s) => ({ ...s, loading: true }));
    Promise.all([api.summary(filters), api.byCity(filters), api.byCategory(filters), api.bySource(filters)])
      .then(([summary, city, category, source]) => alive && (setData({ summary, city, category, source }), setState({ loading: false, error: null })))
      .catch((e) => alive && setState({ loading: false, error: e.message }));
    return () => { alive = false; };
  }, [filters]);

  /** Clicking the active value again clears it (toggle) - same gesture for bars, slices and chips. */
  const toggle = useCallback((key, value) => setFilters((f) => ({ ...f, [key]: f[key] === value ? "" : value })), []);
  const clear = useCallback(() => setFilters(EMPTY), []);
  return { filters, data, ...state, toggle, clear };
}
