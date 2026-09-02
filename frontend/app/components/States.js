'use client';

/**
 * LoadingState — Skeleton loading placeholder for search results.
 */
export function LoadingState({ message = 'Searching for the best journeys...' }) {
  return (
    <div style={{ padding: '40px 0' }}>
      <div style={{
        textAlign: 'center',
        marginBottom: '32px',
        animation: 'fadeIn 0.4s ease-out',
      }}>
        <div style={{
          fontSize: '40px',
          marginBottom: '12px',
          animation: 'float 2s ease-in-out infinite',
        }}>
          🚂
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
          {message}
        </p>
        <div style={{
          display: 'flex',
          gap: '6px',
          justifyContent: 'center',
          marginTop: '12px',
        }}>
          {[0, 1, 2].map(i => (
            <div key={i} style={{
              width: '8px', height: '8px',
              borderRadius: '50%',
              background: 'var(--accent-blue)',
              animation: `pulse 1.2s ease-in-out ${i * 0.2}s infinite`,
            }} />
          ))}
        </div>
      </div>

      {/* Skeleton cards */}
      {[1, 2, 3].map(i => (
        <div key={i} className="glass-card" style={{
          padding: '24px',
          marginBottom: '12px',
          opacity: 0.5,
        }}>
          <div style={{ display: 'flex', gap: '16px', marginBottom: '16px' }}>
            <div className="skeleton" style={{ width: '120px', height: '24px' }} />
            <div className="skeleton" style={{ width: '30px', height: '24px' }} />
            <div className="skeleton" style={{ width: '120px', height: '24px' }} />
            <div style={{ flex: 1 }} />
            <div className="skeleton" style={{ width: '80px', height: '24px' }} />
          </div>
          <div className="skeleton" style={{ width: '100%', height: '60px' }} />
        </div>
      ))}
    </div>
  );
}

/**
 * ErrorState — Error display with retry option.
 */
export function ErrorState({ message, onRetry }) {
  return (
    <div style={{
      textAlign: 'center',
      padding: '60px 20px',
      animation: 'fadeIn 0.4s ease-out',
    }}>
      <div style={{ fontSize: '48px', marginBottom: '16px' }}>😔</div>
      <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>
        Something went wrong
      </h3>
      <p style={{ color: 'var(--text-tertiary)', fontSize: '14px', marginBottom: '20px', maxWidth: '400px', margin: '0 auto 20px' }}>
        {message}
      </p>
      {onRetry && (
        <button className="btn btn-secondary" onClick={onRetry}>
          🔄 Try Again
        </button>
      )}
    </div>
  );
}

/**
 * EmptyState — No results found.
 */
export function EmptyState({ from, to }) {
  return (
    <div style={{
      textAlign: 'center',
      padding: '60px 20px',
      animation: 'fadeIn 0.4s ease-out',
    }}>
      <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
      <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>
        No journeys found
      </h3>
      <p style={{ color: 'var(--text-tertiary)', fontSize: '14px', maxWidth: '400px', margin: '0 auto' }}>
        We couldn&apos;t find any trains from {from} to {to} on this date.
        Try adjusting your search, increasing max connections, or picking a different date.
      </p>
    </div>
  );
}
