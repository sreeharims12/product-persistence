'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Mail, Lock, User, Phone, Eye, EyeOff, Activity, Loader2 } from 'lucide-react';
import { authApi } from '@/lib/api';

function InputField({ id, icon: Icon, placeholder, type, value, onChange, children }: any) {
  return (
    <div style={{ position: 'relative' }}>
      <div style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', pointerEvents: 'none' }}>
        <Icon size={16} />
      </div>
      <input
        id={id}
        className="input"
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        style={{ paddingLeft: 42, paddingRight: children ? 44 : 14, height: 46 }}
        required
      />
      {children}
    </div>
  );
}

export default function AuthPage() {
  const [tab, setTab] = useState<'login'|'register'>('login');
  const [formData, setFormData] = useState({ email: '', password: '', full_name: '', phone: '' });
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const update = (key: string, val: string) => setFormData(prev => ({ ...prev, [key]: val }));

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      let res;
      if (tab === 'login') {
        res = await authApi.login(formData.email, formData.password);
      } else {
        res = await authApi.register({ email: formData.email, password: formData.password, full_name: formData.full_name, phone: formData.phone });
      }
      localStorage.setItem('access_token', res.data.access_token);
      localStorage.setItem('user', JSON.stringify(res.data.user));
      router.push('/dashboard');
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Authentication failed');
    } finally { setLoading(false); }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16, position: 'relative', zIndex: 1 }}>
      <div className="glass fade-in" style={{ width: '100%', maxWidth: 420, padding: 36 }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div className="glow-pulse" style={{ width: 56, height: 56, borderRadius: 16, background: 'linear-gradient(135deg,#7c3aed,#4f46e5)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: 14 }}>
            <Activity size={24} color="white" />
          </div>
          <h1 style={{ fontSize: 24, fontWeight: 800, marginBottom: 4 }}>
            Product<span style={{ color: '#8b5cf6' }}>Pulse</span>
          </h1>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>Real-time product price monitoring</p>
        </div>

        {/* Tab switcher */}
        <div style={{ display: 'flex', background: 'rgba(255,255,255,0.04)', borderRadius: 10, padding: 4, marginBottom: 24 }}>
          {(['login','register'] as const).map(t => (
            <button key={t} onClick={() => setTab(t)} style={{
              flex: 1, padding: '8px', borderRadius: 7, border: 'none',
              background: tab === t ? 'linear-gradient(135deg,#7c3aed,#4f46e5)' : 'transparent',
              color: tab === t ? 'white' : 'var(--text-muted)',
              fontWeight: tab === t ? 700 : 400, fontSize: 13, cursor: 'pointer',
              transition: 'all 0.2s', boxShadow: tab === t ? '0 2px 12px rgba(139,92,246,0.3)' : 'none',
            }}>
              {t === 'login' ? 'Sign In' : 'Create Account'}
            </button>
          ))}
        </div>

        <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {tab === 'register' && (
            <>
              <InputField id="full-name-input" icon={User} placeholder="Full name" type="text" value={formData.full_name} onChange={(e: any) => update('full_name', e.target.value)} />
              <InputField id="phone-input" icon={Phone} placeholder="Phone number (optional)" type="tel" value={formData.phone} onChange={(e: any) => update('phone', e.target.value)} />
            </>
          )}
          <InputField id="email-input" icon={Mail} placeholder="Email address" type="email" value={formData.email} onChange={(e: any) => update('email', e.target.value)} />
          <InputField id="password-input" icon={Lock} placeholder="Password" type={showPw ? 'text' : 'password'} value={formData.password} onChange={(e: any) => update('password', e.target.value)}>
            <button type="button" onClick={() => setShowPw(!showPw)} style={{ position: 'absolute', right: 14, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
              {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </InputField>

          {error && (
            <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 8, padding: '10px 14px', fontSize: 13, color: '#f87171' }}>
              {error}
            </div>
          )}

          <button id="auth-submit-btn" type="submit" disabled={loading} className="btn-primary" style={{ justifyContent: 'center', padding: '13px', fontSize: 14, marginTop: 4 }}>
            {loading ? <><Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} /> {tab === 'login' ? 'Signing in...' : 'Creating account...'}</> : (tab === 'login' ? 'Sign In →' : 'Create Account →')}
          </button>
        </form>

        <p style={{ textAlign: 'center', fontSize: 12, color: 'var(--text-muted)', marginTop: 20 }}>
          {tab === 'login' ? "Don't have an account? " : 'Already have an account? '}
          <button onClick={() => setTab(tab === 'login' ? 'register' : 'login')} style={{ background: 'none', border: 'none', color: '#a78bfa', cursor: 'pointer', fontWeight: 600 }}>
            {tab === 'login' ? 'Sign up' : 'Sign in'}
          </button>
        </p>
      </div>
    </div>
  );
}
