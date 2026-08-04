'use client';

import { useState } from 'react';
import { Star, Bell, ExternalLink, Globe, Package } from 'lucide-react';
import { formatPrice } from '@/lib/utils';

export interface Product {
  product_name: string;
  store_name: string;
  price: number | null;
  currency: string;
  in_stock: boolean;
  rating: number | null;
  review_count: number | null;
  image_url: string | null;
  product_url: string | null;
}

interface Props {
  product: Product;
  onMonitor: (product: Product) => void;
  index?: number;
}

export default function ProductCard({ product, onMonitor, index = 0 }: Props) {
  const [hovered, setHovered] = useState(false);
  const [imgError, setImgError] = useState(false);

  const storeColors: Record<string, string> = {
    'Amazon': '#ff9900',
    'Walmart': '#0071ce',
    'Best Buy': '#003087',
    'Target': '#cc0000',
    'eBay': '#e53238',
    'Flipkart': '#2874f0',
  };

  const storeColor = storeColors[product.store_name] || '#8b5cf6';

  return (
    <div
      className="glass fade-in"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        padding: '16px 20px',
        borderRadius: 14,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 16,
        transition: 'all 0.25s ease',
        transform: hovered ? 'translateY(-2px)' : 'translateY(0)',
        borderLeft: `4px solid ${storeColor}`,
        boxShadow: hovered ? '0 12px 30px rgba(0,0,0,0.3), 0 0 0 1px rgba(139,92,246,0.2)' : '0 4px 12px rgba(0,0,0,0.2)',
        animationDelay: `${index * 0.04}s`,
        animationFillMode: 'both',
      }}
    >
      {/* Product Image Thumbnail */}
      <div style={{
        width: 76,
        height: 76,
        borderRadius: 10,
        background: 'rgba(255, 255, 255, 0.06)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
        flexShrink: 0,
        padding: 4,
      }}>
        {product.image_url && !imgError ? (
          <img
            src={product.image_url}
            alt={product.product_name}
            onError={() => setImgError(true)}
            style={{
              maxWidth: '100%',
              maxHeight: '100%',
              objectFit: 'contain',
              borderRadius: 6,
              transition: 'transform 0.25s ease',
              transform: hovered ? 'scale(1.08)' : 'scale(1)',
            }}
          />
        ) : (
          <Package size={28} color="#a78bfa" style={{ opacity: 0.6 }} />
        )}
      </div>

      {/* Center Details */}
      <div style={{ flex: 1, minWidth: 0 }}>
        {/* Store and Stock Badges */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6, flexWrap: 'wrap' }}>
          <span style={{
            background: storeColor,
            color: 'white',
            fontSize: 11,
            fontWeight: 700,
            padding: '3px 10px',
            borderRadius: 6,
            letterSpacing: '0.03em',
          }}>
            {product.store_name.toUpperCase()}
          </span>

          <span className={`badge ${product.in_stock ? 'badge-green' : 'badge-red'}`} style={{ fontSize: 11 }}>
            {product.in_stock ? '● IN STOCK' : '○ OUT OF STOCK'}
          </span>

          {product.rating && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <Star size={12} fill="#f59e0b" color="#f59e0b" />
              <span style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
                {product.rating.toFixed(1)} {product.review_count ? `(${product.review_count.toLocaleString()})` : ''}
              </span>
            </div>
          )}
        </div>

        {/* Product Name */}
        <h3 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.3, marginBottom: 4 }}>
          {product.product_name}
        </h3>

        {/* Direct Link Info */}
        {product.product_url && (
          <a
            href={product.product_url}
            target="_blank"
            rel="noopener noreferrer"
            style={{ fontSize: 12, color: '#a78bfa', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 4 }}
          >
            <Globe size={12} />
            {product.product_url.replace(/^https?:\/\/(www\.)?/, '').split('/')[0]}
            <ExternalLink size={11} />
          </a>
        )}
      </div>

      {/* Right Price & Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexShrink: 0 }}>
        {product.price !== null && (
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 20, fontWeight: 800, color: '#a78bfa' }}>
              {formatPrice(product.price, product.currency)}
            </div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>{product.currency}</div>
          </div>
        )}

        <div style={{ display: 'flex', gap: 8 }}>
          <button
            id={`monitor-btn-${product.store_name.replace(/\s/g,'-')}`}
            onClick={() => onMonitor(product)}
            className="btn-primary"
            style={{
              fontSize: 12, padding: '9px 16px',
              background: product.in_stock ? undefined : 'linear-gradient(135deg, #059669, #10b981)',
              boxShadow: product.in_stock ? undefined : '0 2px 12px rgba(16, 185, 129, 0.3)'
            }}
          >
            <Bell size={13} />
            {product.in_stock ? 'Monitor' : 'Notify when Restocked'}
          </button>
        </div>
      </div>
    </div>
  );
}
