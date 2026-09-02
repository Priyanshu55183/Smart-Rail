'use client';

import { useState, useEffect } from 'react';
import SearchForm from './components/SearchForm';
import { getHealth } from './lib/api';

export default function HomeClient() {
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    getHealth()
      .then((d) => setApiStatus(d.status === 'healthy' ? 'connected' : 'degraded'))
      .catch(() => setApiStatus('offline'));
  }, []);

  return (
    <>
      {/* ── Hero Section ─────────────────────────── */}
      <section style={{
        position: 'relative',
        overflow: 'hidden',
        padding: '80px 0 60px',
      }}>
        {/* Background effects */}
        <div style={{
          position: 'absolute',
          top: '-40%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '800px',
          height: '800px',
          background: 'radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />
        <div style={{
          position: 'absolute',
          top: '20%',
          right: '10%',
          width: '300px',
          height: '300px',
          background: 'radial-gradient(circle, rgba(139, 92, 246, 0.08) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        <div className="container" style={{ position: 'relative', zIndex: 1 }}>
          {/* API Status */}
          <div className="animate-fade-in" style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 14px',
            background: apiStatus === 'connected' ? 'var(--success-bg)' : apiStatus === 'offline' ? 'var(--danger-bg)' : 'var(--warning-bg)',
            borderRadius: 'var(--radius-full)',
            fontSize: '12px',
            fontWeight: 600,
            marginBottom: '32px',
            border: `1px solid ${apiStatus === 'connected' ? 'rgba(16, 185, 129, 0.2)' : apiStatus === 'offline' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)'}`,
          }}>
            <span style={{
              width: '6px', height: '6px', borderRadius: '50%',
              background: apiStatus === 'connected' ? 'var(--success)' : apiStatus === 'offline' ? 'var(--danger)' : 'var(--warning)',
              animation: apiStatus === 'checking' ? 'pulse 1s infinite' : 'none',
            }} />
            <span style={{
              color: apiStatus === 'connected' ? 'var(--success-light)' : apiStatus === 'offline' ? 'var(--danger-light)' : 'var(--warning-light)',
            }}>
              {apiStatus === 'connected' ? 'API Connected' : apiStatus === 'checking' ? 'Connecting...' : apiStatus === 'degraded' ? 'Degraded' : 'API Offline'}
            </span>
          </div>

          {/* Title */}
          <h1 className="animate-fade-in-up" style={{
            fontSize: 'clamp(36px, 6vw, 64px)',
            fontWeight: 900,
            lineHeight: 1.1,
            letterSpacing: '-1.5px',
            marginBottom: '20px',
            maxWidth: '700px',
          }}>
            <span style={{
              background: 'linear-gradient(135deg, var(--text-primary) 30%, var(--accent-blue-light) 60%, var(--accent-cyan) 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}>
              Intelligent Railway
            </span>
            <br />
            <span style={{ color: 'var(--text-primary)' }}>Journey Planner</span>
          </h1>

          <p className="animate-fade-in-up" style={{
            fontSize: '17px',
            color: 'var(--text-secondary)',
            maxWidth: '560px',
            lineHeight: 1.7,
            marginBottom: '40px',
            animationDelay: '0.1s',
          }}>
            AI-powered multi-train route planning for Indian Railways.
            Graph algorithms find the paths. ML predicts delays.
            Smart scoring ranks the best options.
          </p>
        </div>
      </section>

      {/* ── Search Form ──────────────────────────── */}
      <section style={{ padding: '0 0 60px' }}>
        <div className="container">
          <div className="glass-card animate-fade-in-up" style={{
            padding: '32px',
            animationDelay: '0.15s',
          }}>
            <h2 style={{
              fontSize: '16px',
              fontWeight: 700,
              color: 'var(--text-secondary)',
              marginBottom: '20px',
              textTransform: 'uppercase',
              letterSpacing: '1px',
            }}>
              🔍 Search Journeys
            </h2>
            <SearchForm />
          </div>
        </div>
      </section>

      {/* ── Features Section ─────────────────────── */}
      <section style={{ padding: '20px 0 60px' }}>
        <div className="container">
          <h2 className="animate-fade-in" style={{
            fontSize: '14px',
            fontWeight: 600,
            color: 'var(--text-muted)',
            textTransform: 'uppercase',
            letterSpacing: '2px',
            textAlign: 'center',
            marginBottom: '32px',
          }}>
            How SmartRail Works
          </h2>

          <div className="stagger" style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: '16px',
          }}>
            <FeatureCard
              icon="🗺️"
              title="Graph-Based Routing"
              description="Builds a time-dependent directed graph from ~120 stations and ~75 trains. Dijkstra's algorithm finds optimal multi-train paths respecting real-time constraints."
              tags={['NetworkX', 'Dijkstra', 'Transfer Edges']}
            />
            <FeatureCard
              icon="🧠"
              title="ML Delay Prediction"
              description="XGBoost model trained on 50,000+ historical delay records. Predicts delays based on train type, season, station, and time — accounting for fog, monsoon, and congestion."
              tags={['XGBoost', 'Monte Carlo', '50K Records']}
            />
            <FeatureCard
              icon="⚡"
              title="Smart Scoring"
              description="Five-dimensional scoring: travel time, layover quality, reliability, price, and convenience. Weighted composite ranks journeys and tags the Best, Fastest, Cheapest, and Safest."
              tags={['Multi-Criteria', 'Weighted', 'Top-K']}
            />
            <FeatureCard
              icon="🚀"
              title="Redis-Cached API"
              description="Station searches cached 24h, journey results 30min. Redis delivers sub-millisecond reads while PostgreSQL handles complex joins across 6 normalized tables."
              tags={['Redis', 'PostgreSQL', 'FastAPI']}
            />
          </div>
        </div>
      </section>

      {/* ── Animated Train Bar ────────────────────── */}
      <div style={{
        overflow: 'hidden',
        padding: '20px 0',
        borderTop: '1px solid var(--border-subtle)',
        borderBottom: '1px solid var(--border-subtle)',
        background: 'rgba(59, 130, 246, 0.02)',
      }}>
        <div style={{
          display: 'flex',
          gap: '80px',
          animation: 'trainMove 25s linear infinite',
          whiteSpace: 'nowrap',
          fontSize: '24px',
          opacity: 0.15,
        }}>
          {'🚂 🚃 🚃 🚃 🚃 🚃 🚃 🚃'.split(' ').map((emoji, i) => (
            <span key={i}>{emoji}</span>
          ))}
        </div>
      </div>

      {/* ── Stats Section ─────────────────────────── */}
      <section style={{ padding: '60px 0' }}>
        <div className="container">
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
            gap: '24px',
            textAlign: 'center',
          }}>
            <StatCard value="120" label="Stations" icon="🏛️" />
            <StatCard value="75" label="Trains" icon="🚂" />
            <StatCard value="600+" label="Train Stops" icon="🚏" />
            <StatCard value="50K" label="Delay Records" icon="📊" />
            <StatCard value="5" label="Scoring Dims" icon="⚡" />
          </div>
        </div>
      </section>
    </>
  );
}

function FeatureCard({ icon, title, description, tags }) {
  return (
    <div className="glass-card animate-fade-in-up" style={{ padding: '24px' }}>
      <div style={{ fontSize: '32px', marginBottom: '14px' }}>{icon}</div>
      <h3 style={{
        fontSize: '16px',
        fontWeight: 700,
        marginBottom: '8px',
        color: 'var(--text-primary)',
      }}>
        {title}
      </h3>
      <p style={{
        fontSize: '13px',
        color: 'var(--text-tertiary)',
        lineHeight: 1.6,
        marginBottom: '14px',
      }}>
        {description}
      </p>
      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
        {tags.map((tag) => (
          <span key={tag} className="badge badge-blue" style={{ fontSize: '9px' }}>
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
}

function StatCard({ value, label, icon }) {
  return (
    <div className="animate-fade-in" style={{ padding: '16px' }}>
      <div style={{ fontSize: '24px', marginBottom: '4px' }}>{icon}</div>
      <div style={{
        fontSize: '28px',
        fontWeight: 900,
        background: 'linear-gradient(135deg, var(--accent-blue-light), var(--accent-cyan))',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
      }}>
        {value}
      </div>
      <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
        {label}
      </div>
    </div>
  );
}
