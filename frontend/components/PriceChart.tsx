'use client';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend, ReferenceLine
} from 'recharts';

interface PricePoint {
  recorded_at: string;
  price: number | null;
  store_name: string;
  in_stock: boolean;
}

interface Props {
  data: PricePoint[];
  stores?: string[];
}

const STORE_COLORS = ['#8b5cf6','#3b82f6','#10b981','#f59e0b','#ef4444','#ec4899','#06b6d4','#84cc16'];

function formatDate(iso: string) {
  const d = new Date(iso);
  return `${d.getMonth()+1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2,'0')}`;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: 'rgba(10,10,28,0.95)', border: '1px solid rgba(139,92,246,0.3)',
      borderRadius: 10, padding: '10px 14px', backdropFilter: 'blur(10px)',
    }}>
      <div style={{ fontSize: 11, color: 'rgba(241,241,255,0.5)', marginBottom: 6 }}>{label}</div>
      {payload.map((p: any) => (
        <div key={p.dataKey} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 3 }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: p.color }} />
          <span style={{ fontSize: 12, color: 'rgba(241,241,255,0.7)' }}>{p.name}:</span>
          <span style={{ fontSize: 13, fontWeight: 700, color: p.color }}>
            ${p.value?.toFixed(2) ?? 'N/A'}
          </span>
        </div>
      ))}
    </div>
  );
};

export default function PriceChart({ data, stores = [] }: Props) {
  if (!data || data.length === 0) {
    return (
      <div style={{
        height: 240, display: 'flex', alignItems: 'center', justifyContent: 'center',
        color: 'var(--text-muted)', fontSize: 14,
      }}>
        No price history yet — check back after the first monitoring cycle.
      </div>
    );
  }

  // Pivot data: one row per timestamp, with each store as a column
  const allStores = stores.length > 0 ? stores : [...new Set(data.map(d => d.store_name))];
  const byTime: Record<string, Record<string, number | null>> = {};

  for (const point of data) {
    const key = formatDate(point.recorded_at);
    if (!byTime[key]) byTime[key] = { time: key as any };
    byTime[key][point.store_name] = point.price;
  }

  const chartData = Object.values(byTime);

  // Compute all prices for domain
  const allPrices = data.map(d => d.price).filter(Boolean) as number[];
  const minP = Math.min(...allPrices);
  const maxP = Math.max(...allPrices);
  const padding = (maxP - minP) * 0.1 || 5;

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis dataKey="time" tick={{ fill: 'rgba(241,241,255,0.4)', fontSize: 11 }} tickLine={false} axisLine={false} />
        <YAxis
          tick={{ fill: 'rgba(241,241,255,0.4)', fontSize: 11 }}
          tickLine={false} axisLine={false}
          tickFormatter={v => `$${v}`}
          domain={[Math.max(0, minP - padding), maxP + padding]}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend
          iconType="circle"
          iconSize={8}
          wrapperStyle={{ fontSize: 12, color: 'rgba(241,241,255,0.6)' }}
        />
        {allStores.map((store, i) => (
          <Line
            key={store}
            type="monotone"
            dataKey={store}
            stroke={STORE_COLORS[i % STORE_COLORS.length]}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
            connectNulls
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
