'use client';
import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import SearchBar from '@/components/SearchBar';
import ProductCard, { Product } from '@/components/ProductCard';
import MonitorModal from '@/components/MonitorModal';
import { productsApi } from '@/lib/api';
import { TrendingDown, Activity, ShieldCheck, Zap } from 'lucide-react';

export default function HomePage() {
  const [results, setResults] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState('');
  const [error, setError] = useState('');
  const [monitored, setMonitored] = useState<Product | null>(null);
  const [showModal, setShowModal] = useState(false);
  const router = useRouter();

  const handleSearch = useCallback(async (q: string) => {
    setQuery(q);
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('access_token');
      if (!token) { router.push('/auth'); return; }
      const res = await productsApi.search(q);
      setResults(res.data);
    } catch (e: any) {
      if (e?.response?.status === 401) router.push('/auth');
      else setError('Search failed. Make sure the backend is running.');
    } finally { setLoading(false); }
  }, [router]);

  const handleMonitor = (product: Product) => {
    const token = localStorage.getItem('access_token');
    if (!token) { router.push('/auth'); return; }
    setMonitored(product);
    setShowModal(true);
  };

  const features = [
    { icon: Activity, title: 'Real-Time Monitoring', desc: 'Track prices and stock every 1–60 minutes automatically' },
    { icon: TrendingDown, title: 'Smart Change Detection', desc: 'Notified only when meaningful price drops or restocks occur' },
    { icon: Zap, title: 'Instant Alerts', desc: 'Email and SMS notifications the moment something changes' },
    { icon: ShieldCheck, title: 'Persistent & Reliable', desc: 'Monitoring continues even after you close the browser' },
  ];

  return (
    <div style={{ minHeight: '100vh', position: 'relative', zIndex: 1 }}>
      <Navbar />

      {/* Hero */}
      <section style={{ maxWidth: 1280, margin: '0 auto', padding: '60px 24px 40px', textAlign: 'center' }}>
        <div className="fade-in" style={{ marginBottom: 16 }}>
          <span className="badge badge-purple" style={{ fontSize: 12 }}>
            ● Live monitoring across 8+ stores
          </span>
        </div>
        <h1 className="gradient-text fade-in-delay-1" style={{ fontSize: 'clamp(36px,5vw,72px)', fontWeight: 900, letterSpacing: '-0.03em', lineHeight: 1.1, marginBottom: 20 }}>
          Never Miss a<br />Price Drop Again
        </h1>
        <p className="fade-in-delay-2" style={{ fontSize: 18, color: 'var(--text-secondary)', maxWidth: 540, margin: '0 auto 40px', lineHeight: 1.6 }}>
          Search any product, enable monitoring, and get instant alerts when prices drop or items come back in stock.
        </p>

        <div className="fade-in-delay-3" style={{ display: 'flex', justifyContent: 'center' }}>
          <SearchBar onSearch={handleSearch} loading={loading} />
        </div>
      </section>

      {/* Results */}
      {(results.length > 0 || loading || error) && (
        <section style={{ maxWidth: 1280, margin: '0 auto', padding: '0 24px 60px' }}>
          {error && (
            <div style={{ textAlign: 'center', padding: 40, color: '#f87171', background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.15)', borderRadius: 12 }}>
              {error}
            </div>
          )}
          {loading && !error && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(260px,1fr))', gap: 20 }}>
              {[...Array(6)].map((_, i) => (
                <div key={i} className="glass shimmer" style={{ height: 380, borderRadius: 16 }} />
              ))}
            </div>
          )}
          {results.length > 0 && !loading && (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                <h2 style={{ fontSize: 18, fontWeight: 700 }}>
                  {results.length} results for <span className="gradient-text">"{query}"</span>
                </h2>
                <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                  Prices updated live · click Monitor to track
                </span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {results.map((product, i) => (
                  <ProductCard key={`${product.store_name}-${i}`} product={product} onMonitor={handleMonitor} index={i} />
                ))}
              </div>
            </>
          )}
        </section>
      )}

      {/* Features grid (shown when no search yet) */}
      {results.length === 0 && !loading && !error && (
        <section style={{ maxWidth: 1280, margin: '0 auto', padding: '0 24px 80px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(220px,1fr))', gap: 16 }}>
            {features.map(({ icon: Icon, title, desc }, i) => (
              <div key={i} className="glass fade-in" style={{ padding: 24, animationDelay: `${i * 0.1}s`, animationFillMode: 'both' }}>
                <div style={{ width: 44, height: 44, borderRadius: 12, background: 'linear-gradient(135deg,rgba(139,92,246,0.3),rgba(79,70,229,0.2))', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 14 }}>
                  <Icon size={20} color="#a78bfa" />
                </div>
                <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 6 }}>{title}</div>
                <div style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.5 }}>{desc}</div>
              </div>
            ))}
          </div>
        </section>
      )}

      {showModal && monitored && (
        <MonitorModal
          product={monitored}
          onClose={() => setShowModal(false)}
          onSuccess={() => {}}
        />
      )}
    </div>
  );
}
