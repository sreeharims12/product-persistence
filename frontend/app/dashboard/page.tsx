'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import MonitoringCard, { MonitoringRequest } from '@/components/MonitoringCard';
import { monitoringApi } from '@/lib/api';
import { Plus, Activity, BarChart2, Bell, Package, RefreshCw, Loader2 } from 'lucide-react';

export default function DashboardPage() {
  const [requests, setRequests] = useState<MonitoringRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const load = async () => {
    setLoading(true);
    try {
      const res = await monitoringApi.list();
      setRequests(res.data);
    } catch (e: any) {
      if (e?.response?.status === 401) router.push('/auth');
    } finally { setLoading(false); }
  };

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) { router.push('/auth'); return; }
    load();
    const interval = setInterval(load, 30000); // refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const active = requests.filter(r => r.is_active);
  const inactive = requests.filter(r => !r.is_active);
  const totalSnapshots = requests.reduce((sum, r) => sum + (r.snapshot_count || 0), 0);

  const stats = [
    { label: 'Monitored Products', value: requests.length, icon: Package, color: '#8b5cf6' },
    { label: 'Active Monitors', value: active.length, icon: Activity, color: '#10b981' },
    { label: 'Total Snapshots', value: totalSnapshots.toLocaleString(), icon: BarChart2, color: '#3b82f6' },
    { label: 'Alert Channels', value: requests.filter(r => r.notify_email || r.notify_sms).length, icon: Bell, color: '#f59e0b' },
  ];

  return (
    <div style={{ minHeight: '100vh', position: 'relative', zIndex: 1 }}>
      <Navbar />
      <div style={{ maxWidth: 1280, margin: '0 auto', padding: '32px 24px' }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
          <div>
            <h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 4 }}>Monitoring Dashboard</h1>
            <p style={{ fontSize: 14, color: 'var(--text-muted)' }}>All your product monitors in one place</p>
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            <button onClick={load} className="btn-secondary" style={{ fontSize: 13, padding: '8px 14px' }}>
              <RefreshCw size={14} /> Refresh
            </button>
            <button onClick={() => router.push('/')} className="btn-primary" style={{ fontSize: 13, padding: '8px 16px' }}>
              <Plus size={14} /> Add Monitor
            </button>
          </div>
        </div>

        {/* Stats */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(180px,1fr))', gap: 16, marginBottom: 32 }}>
          {stats.map(({ label, value, icon: Icon, color }) => (
            <div key={label} className="glass" style={{ padding: 20 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                <div style={{ width: 38, height: 38, borderRadius: 10, background: `${color}22`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Icon size={18} color={color} />
                </div>
              </div>
              <div style={{ fontSize: 28, fontWeight: 800, marginBottom: 2, color }}>{value}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{label}</div>
            </div>
          ))}
        </div>

        {/* Loading */}
        {loading && requests.length === 0 && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(340px,1fr))', gap: 16 }}>
            {[...Array(4)].map((_, i) => <div key={i} className="glass shimmer" style={{ height: 180 }} />)}
          </div>
        )}

        {/* Empty */}
        {!loading && requests.length === 0 && (
          <div className="glass" style={{ textAlign: 'center', padding: '60px 24px' }}>
            <Package size={48} color="rgba(139,92,246,0.4)" style={{ margin: '0 auto 16px' }} />
            <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 8 }}>No monitors yet</h2>
            <p style={{ fontSize: 14, color: 'var(--text-muted)', marginBottom: 24 }}>Search for a product and click Monitor to start tracking</p>
            <button onClick={() => router.push('/')} className="btn-primary">
              <Plus size={14} /> Start Monitoring
            </button>
          </div>
        )}

        {/* Active monitors */}
        {active.length > 0 && (
          <div style={{ marginBottom: 28 }}>
            <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#10b981', display: 'inline-block', boxShadow: '0 0 8px #10b981' }} />
              Active Monitors ({active.length})
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(340px,1fr))', gap: 16 }}>
              {active.map(req => (
                <MonitoringCard
                  key={req.id}
                  req={req}
                  onDelete={id => setRequests(prev => prev.filter(r => r.id !== id))}
                  onUpdate={(id, data) => setRequests(prev => prev.map(r => r.id === id ? { ...r, ...data } : r))}
                />
              ))}
            </div>
          </div>
        )}

        {/* Paused monitors */}
        {inactive.length > 0 && (
          <div>
            <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#6b7280', display: 'inline-block' }} />
              Paused ({inactive.length})
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(340px,1fr))', gap: 16 }}>
              {inactive.map(req => (
                <MonitoringCard
                  key={req.id}
                  req={req}
                  onDelete={id => setRequests(prev => prev.filter(r => r.id !== id))}
                  onUpdate={(id, data) => setRequests(prev => prev.map(r => r.id === id ? { ...r, ...data } : r))}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
