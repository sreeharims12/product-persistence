'use client';
import { useEffect, useState, use } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import PriceChart from '@/components/PriceChart';
import { monitoringApi } from '@/lib/api';
import { ArrowLeft, Clock, Bell, Package, BarChart2, Grid, RefreshCw, Pause, Play, Loader2 } from 'lucide-react';

interface Snapshot {
  id: string;
  store_name: string;
  product_name: string;
  price: number | null;
  in_stock: boolean;
  rating: number | null;
  image_url: string | null;
  captured_at: string;
}

interface PricePoint {
  id: string;
  store_name: string;
  price: number | null;
  in_stock: boolean;
  recorded_at: string;
}

interface MonReq {
  id: string;
  product_name: string;
  interval_minutes: number;
  is_active: boolean;
  last_checked_at: string | null;
  notify_email: boolean;
  notify_sms: boolean;
  snapshot_count: number;
}

function timeAgo(dt: string | null) {
  if (!dt) return 'Never';
  const diff = Date.now() - new Date(dt).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return 'Just now';
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h/24)}d ago`;
}

export default function MonitoringDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const id = resolvedParams.id;
  const [req, setReq] = useState<MonReq | null>(null);
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [priceHistory, setPriceHistory] = useState<PricePoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<'chart'|'snapshots'>('chart');
  const router = useRouter();

  const load = async () => {
    try {
      const [reqRes, snapRes, histRes] = await Promise.all([
        monitoringApi.get(id),
        monitoringApi.snapshots(id),
        monitoringApi.priceHistory(id),
      ]);
      setReq(reqRes.data);
      setSnapshots(snapRes.data);
      setPriceHistory(histRes.data);
    } catch (e: any) {
      if (e?.response?.status === 401) router.push('/auth');
    } finally { setLoading(false); }
  };

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) { router.push('/auth'); return; }
    load();
    const iv = setInterval(load, 30000);
    return () => clearInterval(iv);
  }, [id]);

  const toggleActive = async () => {
    if (!req) return;
    await monitoringApi.update(id, { is_active: !req.is_active });
    setReq(prev => prev ? { ...prev, is_active: !prev.is_active } : null);
  };

  const allStores = [...new Set(priceHistory.map(p => p.store_name))];
  const latestByStore: Record<string, Snapshot> = {};
  for (const s of snapshots) {
    if (!latestByStore[s.store_name]) latestByStore[s.store_name] = s;
  }

  return (
    <div style={{ minHeight: '100vh', position: 'relative', zIndex: 1 }}>
      <Navbar />
      <div style={{ maxWidth: 1280, margin: '0 auto', padding: '32px 24px' }}>
        {/* Back */}
        <button onClick={() => router.push('/dashboard')} className="btn-secondary" style={{ marginBottom: 20, fontSize: 13, padding: '7px 14px' }}>
          <ArrowLeft size={14} /> Back to Dashboard
        </button>

        {loading && !req && (
          <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}>
            <Loader2 size={32} color="#8b5cf6" style={{ animation: 'spin 1s linear infinite' }} />
          </div>
        )}

        {req && (
          <>
            {/* Header */}
            <div className="glass" style={{ padding: 24, marginBottom: 24 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
                <div>
                  <h1 style={{ fontSize: 22, fontWeight: 800, marginBottom: 8 }}>{req.product_name}</h1>
                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    <span className={`badge ${req.is_active ? 'badge-purple' : 'badge-yellow'}`}>
                      {req.is_active ? '● Monitoring Active' : '○ Paused'}
                    </span>
                    <span className="badge badge-blue"><Clock size={9} /> Every {req.interval_minutes}m</span>
                    <span className="badge badge-purple"><Package size={9} /> {req.snapshot_count} snapshots</span>
                    <span className="badge" style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)', color: 'var(--text-muted)' }}>
                      Last: {timeAgo(req.last_checked_at)}
                    </span>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button onClick={load} className="btn-secondary" style={{ fontSize: 12, padding: '7px 12px' }}><RefreshCw size={13} /></button>
                  <button onClick={toggleActive} className="btn-secondary" style={{ fontSize: 12, padding: '7px 12px' }}>
                    {req.is_active ? <><Pause size={13} /> Pause</> : <><Play size={13} /> Resume</>}
                  </button>
                </div>
              </div>
            </div>

            {/* Latest prices by store */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(160px,1fr))', gap: 12, marginBottom: 24 }}>
              {Object.values(latestByStore).slice(0, 6).map(s => (
                <div key={s.store_name} className="glass" style={{ padding: 14, textAlign: 'center' }}>
                  <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 6 }}>{s.store_name.toUpperCase()}</div>
                  <div style={{ fontSize: 20, fontWeight: 800, color: '#a78bfa', marginBottom: 4 }}>
                    {s.price ? `$${s.price.toFixed(2)}` : 'N/A'}
                  </div>
                  <span className={`badge ${s.in_stock ? 'badge-green' : 'badge-red'}`} style={{ fontSize: 10 }}>
                    {s.in_stock ? 'In Stock' : 'Out of Stock'}
                  </span>
                </div>
              ))}
            </div>

            {/* Tab switcher */}
            <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
              {[
                { key: 'chart', label: 'Price History Chart', icon: BarChart2 },
                { key: 'snapshots', label: 'Snapshots', icon: Grid },
              ].map(({ key, label, icon: Icon }) => (
                <button key={key} onClick={() => setTab(key as any)} className={tab === key ? 'btn-primary' : 'btn-secondary'} style={{ fontSize: 13, padding: '8px 16px' }}>
                  <Icon size={13} /> {label}
                </button>
              ))}
            </div>

            {/* Chart */}
            {tab === 'chart' && (
              <div className="glass" style={{ padding: 24 }}>
                <h2 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Price History</h2>
                <PriceChart data={priceHistory} stores={allStores} />
              </div>
            )}

            {/* Snapshots */}
            {tab === 'snapshots' && (
              <div className="glass" style={{ padding: 24 }}>
                <h2 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>
                  Recent Snapshots ({snapshots.length})
                </h2>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {snapshots.slice(0, 30).map(s => (
                    <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 14px', background: 'rgba(255,255,255,0.03)', borderRadius: 8, border: '1px solid rgba(255,255,255,0.05)' }}>
                      <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                        <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', minWidth: 80 }}>{s.store_name}</span>
                        <span style={{ fontSize: 16, fontWeight: 700, color: '#a78bfa' }}>{s.price ? `$${s.price.toFixed(2)}` : 'N/A'}</span>
                        <span className={`badge ${s.in_stock ? 'badge-green' : 'badge-red'}`} style={{ fontSize: 10 }}>
                          {s.in_stock ? 'In Stock' : 'OOS'}
                        </span>
                      </div>
                      <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{new Date(s.captured_at).toLocaleString()}</span>
                    </div>
                  ))}
                  {snapshots.length === 0 && (
                    <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)', fontSize: 14 }}>
                      No snapshots yet — waiting for first monitoring cycle.
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
