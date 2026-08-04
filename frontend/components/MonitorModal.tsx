'use client';
import { useState } from 'react';
import { X, Bell, Clock, Mail, MessageSquare, Loader2 } from 'lucide-react';
import { monitoringApi } from '@/lib/api';
import { Product } from './ProductCard';

interface Props {
  product: Product;
  onClose: () => void;
  onSuccess: () => void;
}

export default function MonitorModal({ product, onClose, onSuccess }: Props) {
  const [interval, setInterval] = useState(10);
  const [notifyEmail, setNotifyEmail] = useState(false);
  const [notifySms, setNotifySms] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = async () => {
    setLoading(true); setError('');
    try {
      await monitoringApi.create({
        product_name: product.product_name,
        interval_minutes: interval,
        notify_email: notifyEmail,
        notify_sms: notifySms,
      });
      onSuccess();
      onClose();
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to create monitoring request');
    } finally { setLoading(false); }
  };

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 100,
      background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: 16,
    }} onClick={onClose}>
      <div
        className="glass"
        onClick={e => e.stopPropagation()}
        style={{ width: '100%', maxWidth: 440, padding: 28 }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: 'linear-gradient(135deg,#7c3aed,#4f46e5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Bell size={16} color="white" />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: 16 }}>Start Monitoring</div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Set up persistent price & stock alerts</div>
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        {/* Product info */}
        <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: 10, padding: 12, marginBottom: 20, border: '1px solid rgba(255,255,255,0.06)' }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4 }}>{product.product_name}</div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
            {product.store_name} · {product.price ? `$${product.price.toFixed(2)}` : 'Price unavailable'}
          </div>
        </div>

        {/* Interval */}
        <div style={{ marginBottom: 20 }}>
          <label style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
            <Clock size={13} /> Check Interval
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5,1fr)', gap: 8 }}>
            {[1, 5, 10, 30, 60].map(m => (
              <button
                key={m}
                onClick={() => setInterval(m)}
                style={{
                  padding: '8px 4px', borderRadius: 8, border: `1px solid ${interval === m ? 'var(--accent)' : 'rgba(255,255,255,0.08)'}`,
                  background: interval === m ? 'rgba(139,92,246,0.15)' : 'rgba(255,255,255,0.03)',
                  color: interval === m ? '#a78bfa' : 'var(--text-secondary)',
                  cursor: 'pointer', fontSize: 12, fontWeight: interval === m ? 700 : 400,
                  transition: 'all 0.2s',
                }}
              >
                {m < 60 ? `${m}m` : '1h'}
              </button>
            ))}
          </div>
        </div>

        {/* Notifications */}
        <div style={{ marginBottom: 24 }}>
          <label style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
            <Bell size={13} /> Alerts
          </label>
          <div style={{
            background: 'rgba(139,92,246,0.06)',
            border: '1px solid rgba(139,92,246,0.15)',
            borderRadius: 10,
            padding: '12px 14px',
            fontSize: 12,
            color: 'var(--text-secondary)',
            lineHeight: 1.5,
            display: 'flex',
            alignItems: 'center',
            gap: 10,
          }}>
            <span style={{ fontSize: 16 }}>🌐</span>
            <span>Alerts will be saved instantly to your <strong>Alerts</strong> tab in the navigation bar. No email or SMS setup required.</span>
          </div>
        </div>

        {error && (
          <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 8, padding: '10px 14px', marginBottom: 16, fontSize: 13, color: '#f87171' }}>
            {error}
          </div>
        )}

        <button
          id="confirm-monitor-btn"
          onClick={submit}
          disabled={loading}
          className="btn-primary"
          style={{ width: '100%', justifyContent: 'center', padding: '12px', fontSize: 14 }}
        >
          {loading ? <><Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} /> Starting...</> : '🔔 Start Monitoring'}
        </button>
      </div>
    </div>
  );
}
