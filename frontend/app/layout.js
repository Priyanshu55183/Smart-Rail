'use client';

import './globals.css';
import { AuthProvider, useAuth } from './lib/AuthContext';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <title>SmartRail — Intelligent Railway Journey Planner</title>
        <meta
          name="description"
          content="AI-powered multi-train journey planner for Indian Railways. Uses graph algorithms, ML delay prediction, and smart scoring to find the best routes."
        />
        <meta name="keywords" content="Indian Railways, train booking, journey planner, smart rail, AI travel" />
      </head>
      <body>
        <AuthProvider>
          <Navbar />
          <main style={{ minHeight: 'calc(100vh - 140px)', position: 'relative', zIndex: 1 }}>
            {children}
          </main>
          <Footer />
        </AuthProvider>
      </body>
    </html>
  );
}

/* ── Navbar ─────────────────────────────────── */
function Navbar() {
  const { user, isAuthenticated, logout, loading } = useAuth();

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

          {/* Auth buttons */}
          {!loading && (
            <>
              {isAuthenticated ? (
                /* ── Logged-in state ── */
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginLeft: '8px' }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '6px 14px',
                    background: 'rgba(59, 130, 246, 0.1)',
                    border: '1px solid rgba(59, 130, 246, 0.2)',
                    borderRadius: 'var(--radius-full)',
                  }}>
                    <div style={{
                      width: '28px',
                      height: '28px',
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-cyan))',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '13px',
                      fontWeight: 700,
                      color: 'white',
                    }}>
                      {user?.name?.charAt(0)?.toUpperCase() || '?'}
                    </div>
                    <span style={{
                      fontSize: '13px',
                      fontWeight: 600,
                      color: 'var(--text-primary)',
                      maxWidth: '120px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}>
                      {user?.name}
                    </span>
                  </div>
                  <button
                    onClick={logout}
                    className="btn btn-ghost"
                    style={{
                      fontSize: '13px',
                      color: 'var(--danger-light)',
                      cursor: 'pointer',
                    }}
                  >
                    Logout
                  </button>
                </div>
              ) : (
                /* ── Logged-out state ── */
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginLeft: '8px' }}>
                  <a href="/login" className="btn btn-ghost" style={{ fontSize: '13px' }}>
                    Sign In
                  </a>
                  <a
                    href="/register"
                    className="btn btn-primary"
                    style={{
                      fontSize: '13px',
                      padding: '8px 18px',
                      borderRadius: 'var(--radius-full)',
                    }}
                  >
                    Sign Up
                  </a>
                </div>
              )}
            </>
          )}
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

