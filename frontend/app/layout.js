import './globals.css';

export const metadata = {
  title: 'SmartRail — Intelligent Railway Journey Planner',
  description:
    'AI-powered multi-train journey planner for Indian Railways. Uses graph algorithms, ML delay prediction, and smart scoring to find the best routes.',
  keywords: 'Indian Railways, train booking, journey planner, smart rail, AI travel',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <main style={{ minHeight: 'calc(100vh - 140px)', position: 'relative', zIndex: 1 }}>
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}

/* ── Navbar ─────────────────────────────────── */
function Navbar() {
  return (
    <nav style={{
      position: 'sticky',
      top: 0,
      zIndex: 100,
      background: 'rgba(10, 14, 26, 0.8)',
      backdropFilter: 'blur(20px)',
      WebkitBackdropFilter: 'blur(20px)',
      borderBottom: '1px solid rgba(148, 163, 184, 0.06)',
    }}>
      <div className="container" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '64px',
      }}>
        <a href="/" style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          textDecoration: 'none',
          color: 'var(--text-primary)',
        }}>
          <span style={{ fontSize: '24px' }}>🚂</span>
          <span style={{
            fontSize: '20px',
            fontWeight: 800,
            background: 'linear-gradient(135deg, var(--accent-blue-light), var(--accent-cyan))',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: '-0.5px',
          }}>
            SmartRail
          </span>
        </a>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <a href="/" className="btn btn-ghost" style={{ fontSize: '13px' }}>Home</a>
          <a href="/search" className="btn btn-ghost" style={{ fontSize: '13px' }}>Search</a>
          <a
            href="/api/health"
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-ghost"
            style={{ fontSize: '13px' }}
          >
            API Health
          </a>
        </div>
      </div>
    </nav>
  );
}

/* ── Footer ─────────────────────────────────── */
function Footer() {
  return (
    <footer style={{
      borderTop: '1px solid var(--border-subtle)',
      padding: '24px 0',
      marginTop: '64px',
      position: 'relative',
      zIndex: 1,
    }}>
      <div className="container" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px',
      }}>
        <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
          🚂 SmartRail — AI-Powered Railway Journey Planner
        </span>
        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
          Graph Algorithms • ML Delay Prediction • Smart Scoring
        </span>
      </div>
    </footer>
  );
}
