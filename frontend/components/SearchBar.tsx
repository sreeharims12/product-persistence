'use client';
import { useState } from 'react';
import { Search, Loader2 } from 'lucide-react';

interface Props {
  onSearch: (query: string) => void;
  loading?: boolean;
}

export default function SearchBar({ onSearch, loading }: Props) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) onSearch(query.trim());
  };

  return (
    <form onSubmit={handleSubmit} style={{ width: '100%', maxWidth: 680, position: 'relative' }}>
      <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
        <div style={{ position: 'absolute', left: 18, color: 'var(--text-muted)', pointerEvents: 'none' }}>
          {loading ? <Loader2 size={20} className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} /> : <Search size={20} />}
        </div>
        <input
          id="product-search-input"
          className="input"
          type="text"
          placeholder='Try "iPhone 15 Pro", "Sony WH-1000XM5", "RTX 4090"...'
          value={query}
          onChange={e => setQuery(e.target.value)}
          style={{
            paddingLeft: 52,
            paddingRight: 140,
            height: 56,
            fontSize: 16,
            borderRadius: 14,
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.1)',
          }}
        />
        <button
          id="search-submit-btn"
          type="submit"
          disabled={loading || !query.trim()}
          className="btn-primary"
          style={{
            position: 'absolute', right: 6,
            padding: '10px 22px',
            borderRadius: 10,
            fontSize: 14,
            opacity: (!query.trim() || loading) ? 0.5 : 1,
          }}
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {/* Popular searches */}
      <div style={{ display: 'flex', gap: 8, marginTop: 12, flexWrap: 'wrap' }}>
        {['iPhone 15', 'RTX 4090', 'PS5', 'MacBook Pro', 'AirPods Pro', 'Samsung TV'].map(term => (
          <button
            key={term}
            type="button"
            onClick={() => { setQuery(term); onSearch(term); }}
            style={{
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(255,255,255,0.08)',
              color: 'rgba(241,241,255,0.6)',
              borderRadius: 999,
              padding: '4px 12px',
              fontSize: 12,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
          >
            {term}
          </button>
        ))}
      </div>
    </form>
  );
}
