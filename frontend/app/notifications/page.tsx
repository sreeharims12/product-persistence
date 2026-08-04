'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import { notificationsApi } from '@/lib/api';
import { Bell, TrendingDown, TrendingUp, Package, ShoppingBag, RefreshCw, Filter } from 'lucide-react';

interface Notification {
  id: string;
  monitoring_request_id: string;
  type: string;
  channel: string;
  message: string;
  sent_at: string;
  status: string;
  product_name: string | null;
}

const TYPE_CONFIG: Record<string, { label: string; color: string; bg: string; icon: any }> = {
  price_drop:     { label: 'Price Drop',    color: '#34d399', bg: 'rgba(16,185,129,0.1)', icon: TrendingDown },
  price_increase: { label: 'Price Increase',color: '#f87171', bg: 'rgba(239,68,68,0.1)',  icon: TrendingUp },
  restock:        { label: 'Restocked',     color: '#34d399', bg: 'rgba(52,211,153,0.15)', icon: Package },
  out_of_stock:   { label: 'Out of Stock',  color: '#fbbf24', bg: 'rgba(245,158,11,0.1)', icon: Package },
  new_seller:     { label: 'New Seller',    color: '#c084fc', bg: 'rgba(192,132,252,0.1)',icon: ShoppingBag },
};

function timeAgo(dt: string) {
  const diff = Date.now() - new Date(dt).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return 'Just now';
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h/24)}d ago`;
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const router = useRouter();

  const load = async () => {
    setLoading(true);
    try {
      const res = await notificationsApi.list();
      setNotifications(res.data);
    } catch (e: any) {
      if (e?.response?.status === 401) router.push('/auth');
    } finally { setLoading(false); }
  };

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) { router.push('/auth'); return; }
    load();
  }, []);

  const filtered = filter === 'all' ? notifications : notifications.filter(n => n.type === filter);
  const counts: Record<string, number> = {};
  for (const n of notifications) { counts[n.type] = (counts[n.type] || 0) + 1; }

  return (
    <div style={{ minHeight: '100vh', position: 'relative', zIndex: 1 }}>
      <Navbar />
      <div style={{ maxWidth: 1280, margin: '0 auto', padding: '32px 24px' }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
          <div>
            <h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 4 }}>Notifications</h1>
            <p style={{ fontSize: 14, color: 'var(--text-muted)' }}>{notifications.length} total alerts received</p>
          </div>
          <button onClick={load} className="btn-secondary" style={{ fontSize: 13, padding: '8px 14px' }}>
            <RefreshCw size={14} /> Refresh
          </button>
        </div>

        {/* Filter tabs */}
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 24 }}>
          {['all', ...Object.keys(TYPE_CONFIG)].map(type => {
            const cfg = TYPE_CONFIG[type];
            const count = type === 'all' ? notifications.length : (counts[type] || 0);
            return (
              <button
                key={type}
                onClick={() => setFilter(type)}
                style={{
                  padding: '6px 14px', borderRadius: 999, fontSize: 12, fontWeight: 500,
                  border: `1px solid ${filter === type ? (cfg?.color || '#a78bfa') : 'rgba(255,255,255,0.08)'}`,
                  background: filter === type ? (cfg?.bg || 'rgba(139,92,246,0.1)') : 'rgba(255,255,255,0.03)',
                  color: filter === type ? (cfg?.color || '#a78bfa') : 'var(--text-muted)',
                  cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6,
                  transition: 'all 0.2s',
                }}
              >
                {type === 'all' ? 'All' : cfg?.label}
                {count > 0 && <span style={{ background: 'rgba(255,255,255,0.1)', borderRadius: 999, padding: '0 6px', fontSize: 10 }}>{count}</span>}
              </button>
            );
          })}
        </div>

        {/* Loading */}
        {loading && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {[...Array(5)].map((_, i) => <div key={i} className="glass shimmer" style={{ height: 80 }} />)}
          </div>
        )}

        {/* Empty */}
        {!loading && filtered.length === 0 && (
          <div className="glass" style={{ textAlign: 'center', padding: '60px 24px' }}>
            <Bell size={48} color="rgba(139,92,246,0.3)" style={{ margin: '0 auto 16px' }} />
            <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>No notifications yet</h2>
            <p style={{ fontSize: 14, color: 'var(--text-muted)' }}>
              Notifications appear here when monitored products have price drops or stock changes.
            </p>
          </div>
        )}

        {/* Notifications list */}
        {!loading && filtered.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {filtered.map(n => {
              const cfg = TYPE_CONFIG[n.type] || { label: n.type, color: '#a78bfa', bg: 'rgba(139,92,246,0.1)', icon: Bell };
              const Icon = cfg.icon;
              return (
                <div
                  key={n.id}
                  className="glass"
                  style={{ padding: '16px 20px', display: 'flex', alignItems: 'flex-start', gap: 16, borderLeft: `3px solid ${cfg.color}` }}
                >
                  <div style={{ width: 40, height: 40, borderRadius: 10, background: cfg.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <Icon size={18} color={cfg.color} />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4, gap: 8 }}>
                      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                        <span className="badge" style={{ background: cfg.bg, color: cfg.color, border: `1px solid ${cfg.color}33` }}>
                          {cfg.label}
                        </span>
                        <span className="badge badge-blue" style={{ fontSize: 10 }}>{n.channel.toUpperCase()}</span>
                        <span className={`badge ${n.status === 'sent' ? 'badge-green' : 'badge-red'}`} style={{ fontSize: 10 }}>
                          {n.status}
                        </span>
                      </div>
                      <span style={{ fontSize: 11, color: 'var(--text-muted)', flexShrink: 0 }}>{timeAgo(n.sent_at)}</span>
                    </div>
                    {n.product_name && (
                      <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 4 }}>
                        {n.product_name}
                      </div>
                    )}
                    <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{n.message}</p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
