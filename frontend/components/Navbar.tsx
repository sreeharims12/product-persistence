'use client';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Bell, BarChart2, Search, LogOut, Package, Activity } from 'lucide-react';
import { useEffect, useState } from 'react';
import { notificationsApi } from '@/lib/api';

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<{ full_name: string; email: string } | null>(null);
  const [alertCount, setAlertCount] = useState(0);

  useEffect(() => {
    const stored = localStorage.getItem('user');
    if (stored) setUser(JSON.parse(stored));
  }, []);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (token) {
          const res = await notificationsApi.list();
          // Filter to show counts of web channel notifications
          const webNotifications = res.data.filter((n: any) => n.channel === 'web');
          setAlertCount(webNotifications.length);
        } else {
          setAlertCount(0);
        }
      } catch (e) {
        // ignore
      }
    };
    fetchAlerts();
    const iv = setInterval(fetchAlerts, 15000);
    return () => clearInterval(iv);
  }, [pathname]);

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    router.push('/auth');
  };

  const links = [
    { href: '/', label: 'Search', icon: Search },
    { href: '/dashboard', label: 'Dashboard', icon: BarChart2 },
    { href: '/notifications', label: 'Alerts', icon: Bell },
  ];

  return (
    <nav style={{
      position: 'sticky', top: 0, zIndex: 50,
      background: 'rgba(6,6,18,0.8)',
      backdropFilter: 'blur(20px)',
      borderBottom: '1px solid rgba(255,255,255,0.06)',
      padding: '0 24px',
    }}>
      <div style={{ maxWidth: 1280, margin: '0 auto', display: 'flex', alignItems: 'center', height: 64, gap: 8 }}>
        {/* Logo */}
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none', marginRight: 32 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: 'linear-gradient(135deg,#7c3aed,#4f46e5)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 16px rgba(139,92,246,0.4)',
          }}>
            <Activity size={18} color="white" />
          </div>
          <span style={{ fontWeight: 800, fontSize: 18, letterSpacing: '-0.02em', color: '#f1f1ff' }}>
            Product<span style={{ color: '#8b5cf6' }}>Pulse</span>
          </span>
        </Link>

        {/* Nav links */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, flex: 1 }}>
          {links.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link key={href} href={href} style={{
                display: 'flex', alignItems: 'center', gap: 6,
                padding: '6px 14px', borderRadius: 8,
                textDecoration: 'none',
                fontSize: 14, fontWeight: 500,
                color: active ? '#a78bfa' : 'rgba(241,241,255,0.6)',
                background: active ? 'rgba(139,92,246,0.1)' : 'transparent',
                border: active ? '1px solid rgba(139,92,246,0.2)' : '1px solid transparent',
                transition: 'all 0.2s',
              }}>
                <Icon size={15} />
                {label}
                {label === 'Alerts' && alertCount > 0 && (
                  <span style={{
                    background: '#ef4444',
                    color: 'white',
                    fontSize: 10,
                    fontWeight: 700,
                    borderRadius: 999,
                    padding: '1px 6px',
                    marginLeft: 4,
                    boxShadow: '0 0 10px rgba(239,68,68,0.5)',
                  }}>
                    {alertCount}
                  </span>
                )}
              </Link>
            );
          })}
        </div>

        {/* User section */}
        {user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: '#f1f1ff' }}>{user.full_name}</div>
              <div style={{ fontSize: 11, color: 'rgba(241,241,255,0.4)' }}>{user.email}</div>
            </div>
            <button onClick={logout} style={{
              background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)',
              color: '#f87171', borderRadius: 8, padding: '6px 12px',
              cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6,
              fontSize: 13, transition: 'all 0.2s',
            }}>
              <LogOut size={14} />
            </button>
          </div>
        ) : (
          <Link href="/auth" className="btn-primary" style={{ fontSize: 13, padding: '7px 16px' }}>
            Sign In
          </Link>
        )}
      </div>
    </nav>
  );
}
