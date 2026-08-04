import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'ProductPulse — Real-Time Product Monitoring',
  description: 'Monitor product prices and stock across Amazon, Walmart, Best Buy and more. Get instant alerts when prices drop or items restock.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {/* Background orbs */}
        <div className="orb" style={{ width: 600, height: 600, background: '#7c3aed', top: -200, left: -200 }} />
        <div className="orb" style={{ width: 400, height: 400, background: '#2563eb', top: '40%', right: -100 }} />
        <div className="orb" style={{ width: 300, height: 300, background: '#059669', bottom: -100, left: '30%' }} />
        {children}
      </body>
    </html>
  );
}
