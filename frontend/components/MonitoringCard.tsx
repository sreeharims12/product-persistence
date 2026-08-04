'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Clock, Pause, Play, Trash2, TrendingDown, TrendingUp, Package, Bell } from 'lucide-react';
import { monitoringApi } from '@/lib/api';

export interface MonitoringRequest {
  id: string;
  product_name: string;
  interval_minutes: number;
  is_active: boolean;
  last_checked_at: string | null;
  notify_email: boolean;
  notify_sms: boolean;
  snapshot_count: number;
  latest_price: number | null;
  latest_store: string | null;
  latest_in_stock: boolean | null;
  created_at: string;
}

interface Props {
  req: MonitoringRequest;
  onDelete: (id: string) => void;
  onUpdate: (id: string, data: Partial<MonitoringRequest>) => void;
}

function timeAgo(dt: string | null) {
  if (!dt) return 'Never';
  const diff = Date.now() - new Date(dt).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return 'Just now';
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

export default function MonitoringCard({ req, onDelete, onUpdate }: Props) {
  const [busy, setBusy] = useState(false);
  const router = useRouter();

  const toggle = async () => {
    setBusy(true);
    try {
      await monitoringApi.update(req.id, { is_active: !req.is_active });
      onUpdate(req.id, { is_active: !req.is_active });
    } finally { setBusy(false); }
  };

  const remove = async () => {
    if (!confirm('Remove this monitoring request?')) return;
    setBusy(true);
    try {
      await monitoringApi.remove(req.id);
      onDelete(req.id);
    } finally { setBusy(false); }
  };

  return (
    <div className="glass" style={{
      padding: 20, cursor: 'default',
      transition: 'all 0.3s ease',
      opacity: req.is_active ? 1 : 0.7,
      borderLeft: `3px solid ${req.is_active ? 'var(--accent)' : 'rgba(255,255,255,0.1)'}`,
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14 }}>
        <div style={{ flex: 1, minWidth: 0, paddingRight: 12 }}>
          <h3 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {req.product_name}
          </h3>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <span className={`badge ${req.is_active ? 'badge-purple' : 'badge-yellow'}`}>
              {req.is_active ? '● Monitoring' : '○ Paused'}
            </span>
            <span className="badge badge-blue">
              <Clock size={9} /> Every {req.interval_minutes}m
            </span>
            {req.latest_in_stock !== null && (
              <span className={`badge ${req.latest_in_stock ? 'badge-green' : 'badge-red'}`}>
                {req.latest_in_stock ? '✓ In Stock' : '✗ Out of Stock'}
              </span>
            )}
          </div>
        </div>

        {/* Price */}
        {req.latest_price && (
          <div style={{ textAlign: 'right', flexShrink: 0 }}>
            <div style={{ fontSize: 22, fontWeight: 800, color: '#a78bfa' }}>
              ${req.latest_price.toFixed(2)}
            </div>
            {req.latest_store && (
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{req.latest_store}</div>
            )}
          </div>
        )}
      </div>

      {/* Stats */}
      <div style={{ display: 'flex', gap: 16, marginBottom: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 5, color: 'var(--text-muted)', fontSize: 12 }}>
          <Clock size={12} /> Last checked: {timeAgo(req.last_checked_at)}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 5, color: 'var(--text-muted)', fontSize: 12 }}>
          <Package size={12} /> {req.snapshot_count} snapshots
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 5, color: 'var(--text-muted)', fontSize: 12 }}>
          <Bell size={12} /> {req.notify_email ? 'Email' : ''}{req.notify_email && req.notify_sms ? ' + ' : ''}{req.notify_sms ? 'SMS' : ''}
        </div>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: 8 }}>
        <button
          onClick={() => router.push(`/monitoring/${req.id}`)}
          className="btn-secondary"
          style={{ flex: 1, justifyContent: 'center', fontSize: 12, padding: '7px 12px' }}
        >
          View Details
        </button>
        <button
          onClick={toggle}
          disabled={busy}
          className="btn-secondary"
          style={{ fontSize: 12, padding: '7px 12px' }}
        >
          {req.is_active ? <Pause size={13} /> : <Play size={13} />}
        </button>
        <button
          onClick={remove}
          disabled={busy}
          style={{
            background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.15)',
            color: '#f87171', borderRadius: 8, padding: '7px 12px',
            cursor: 'pointer', fontSize: 12,
          }}
        >
          <Trash2 size={13} />
        </button>
      </div>
    </div>
  );
}
