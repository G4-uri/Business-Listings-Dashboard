import { Bar, BarChart, Cell, LabelList, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

/** Source colours follow the ENTITY, not its rank, so filtering never repaints survivors.
 *  Palette validated with the dataviz validator (CVD + normal-vision floors pass, light & dark). */
export const SOURCE_COLOR = {
  MagicPin: "var(--series-1)",
  OpenStreetMap: "var(--series-3)",
  "Sample (synthetic)": "var(--muted)",
};
const colorOf = (label, i) => SOURCE_COLOR[label] ?? ["var(--series-1)", "var(--series-3)", "var(--series-2)"][i % 3];

function Tip({ active, payload, total }) {
  if (!active || !payload?.length) return null;
  const { label, count } = payload[0].payload;
  return (
    <div className="tip" role="status">
      <strong>{label}</strong>
      <span>{count.toLocaleString()} listings · {((count / total) * 100).toFixed(1)}%</span>
      <em>Click to filter</em>
    </div>
  );
}

/** Horizontal ranked bars. `active` is the currently-selected label (accent colour). */
export function RankedBars({ rows, total, active, onPick, empty }) {
  if (!rows.length) return <p className="empty">{empty}</p>;
  return (
    <ResponsiveContainer width="100%" height={Math.max(120, rows.length * 34 + 8)}>
      <BarChart data={rows} layout="vertical" margin={{ top: 0, right: 44, bottom: 0, left: 0 }} barCategoryGap={6}>
        <XAxis type="number" hide />
        <YAxis type="category" dataKey="label" width={128} tickLine={false} axisLine={false}
               tick={{ fill: "var(--text-2)", fontSize: 13 }} interval={0} />
        <Tooltip cursor={{ fill: "var(--wash)" }} content={<Tip total={total} />} />
        <Bar dataKey="count" radius={[0, 4, 4, 0]} onClick={(d) => onPick(d.label)} cursor="pointer" maxBarSize={22} isAnimationActive={false}>
          {rows.map((r) => (
            <Cell key={r.label} fill={active && r.label === active ? "var(--accent)" : "var(--series-1)"}
                  fillOpacity={active && r.label !== active ? 0.55 : 1} />
          ))}
          <LabelList dataKey="count" position="right" fill="var(--text-1)" fontSize={12} />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

/** Donut + legend (legend doubles as the keyboard-accessible control, with counts as direct labels). */
export function SourceDonut({ rows, total, active, onPick, empty }) {
  if (!rows.length) return <p className="empty">{empty}</p>;
  return (
    <div className="donut">
      <div className="donut-chart">
        <ResponsiveContainer width="100%" height={190}>
          <PieChart>
            <Tooltip content={<Tip total={total} />} />
            <Pie data={rows} dataKey="count" nameKey="label" innerRadius={52} outerRadius={84} paddingAngle={2}
                 stroke="var(--surface)" strokeWidth={2} onClick={(d) => onPick(d.label)} cursor="pointer" isAnimationActive={false}>
              {rows.map((r, i) => (
                <Cell key={r.label} fill={colorOf(r.label, i)} fillOpacity={active && r.label !== active ? 0.4 : 1} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="donut-centre"><b>{total.toLocaleString()}</b><span>listings</span></div>
      </div>
      <ul className="legend">
        {rows.map((r, i) => (
          <li key={r.label}>
            <button type="button" aria-pressed={active === r.label} onClick={() => onPick(r.label)}>
              <i style={{ background: colorOf(r.label, i) }} />
              <span>{r.label}</span>
              <b>{r.count.toLocaleString()}</b>
              <small>{((r.count / total) * 100).toFixed(0)}%</small>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
