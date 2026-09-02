'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { searchStations } from '@/app/lib/api';
import { debounce } from '@/app/lib/utils';

/**
 * StationAutocomplete — Real-time station search with keyboard navigation.
 *
 * Features:
 * - Debounced API calls (300ms)
 * - Keyboard navigation (↑↓ Enter Esc)
 * - Shows station code, name, city
 * - Junction badge for major stations
 */
export default function StationAutocomplete({
  label,
  placeholder = 'Search station...',
  value,
  onChange,
  icon = '📍',
  id,
}) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);

  // Display the selected station
  const displayValue = value ? `${value.code} — ${value.name}` : query;

  // Debounced search
  const debouncedSearch = useCallback(
    debounce(async (q) => {
      if (q.length < 1) {
        setResults([]);
        setIsOpen(false);
        return;
      }
      setLoading(true);
      try {
        const data = await searchStations(q, 8);
        setResults(data.stations || []);
        setIsOpen(true);
        setActiveIndex(-1);
      } catch (err) {
        console.error('Station search failed:', err);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300),
    []
  );

  const handleInputChange = (e) => {
    const val = e.target.value;
    setQuery(val);
    if (value) onChange(null); // Clear selection when typing
    debouncedSearch(val);
  };

  const handleSelect = (station) => {
    onChange(station);
    setQuery('');
    setIsOpen(false);
    setResults([]);
  };

  const handleKeyDown = (e) => {
    if (!isOpen || results.length === 0) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveIndex((prev) => Math.min(prev + 1, results.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveIndex((prev) => Math.max(prev - 1, 0));
    } else if (e.key === 'Enter' && activeIndex >= 0) {
      e.preventDefault();
      handleSelect(results[activeIndex]);
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div ref={dropdownRef} style={{ position: 'relative', flex: 1 }} id={id}>
      {label && (
        <label style={{
          display: 'block',
          fontSize: '12px',
          fontWeight: 600,
          color: 'var(--text-secondary)',
          marginBottom: '6px',
          textTransform: 'uppercase',
          letterSpacing: '0.5px',
        }}>
          {icon} {label}
        </label>
      )}
      <div style={{ position: 'relative' }}>
        <input
          ref={inputRef}
          type="text"
          className="input input-lg"
          placeholder={placeholder}
          value={displayValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => { if (results.length > 0) setIsOpen(true); }}
          autoComplete="off"
          style={{
            paddingRight: '40px',
            background: value ? 'rgba(59, 130, 246, 0.08)' : undefined,
            borderColor: value ? 'rgba(59, 130, 246, 0.3)' : undefined,
          }}
        />
        {loading && (
          <span style={{
            position: 'absolute', right: '14px', top: '50%',
            transform: 'translateY(-50%)', fontSize: '14px',
            animation: 'pulse 1s infinite',
          }}>⏳</span>
        )}
        {value && !loading && (
          <button
            onClick={() => { onChange(null); setQuery(''); inputRef.current?.focus(); }}
            style={{
              position: 'absolute', right: '10px', top: '50%',
              transform: 'translateY(-50%)',
              background: 'none', border: 'none', cursor: 'pointer',
              color: 'var(--text-muted)', fontSize: '16px', padding: '4px',
            }}
            title="Clear"
          >✕</button>
        )}
      </div>

      {/* Dropdown */}
      {isOpen && results.length > 0 && (
        <div style={{
          position: 'absolute',
          top: '100%',
          left: 0,
          right: 0,
          marginTop: '4px',
          background: 'var(--bg-glass-strong)',
          backdropFilter: 'blur(20px)',
          border: '1px solid var(--border-light)',
          borderRadius: 'var(--radius-md)',
          boxShadow: 'var(--shadow-lg)',
          zIndex: 50,
          maxHeight: '320px',
          overflowY: 'auto',
          animation: 'slideDown 0.2s ease-out',
        }}>
          {results.map((station, idx) => (
            <button
              key={station.code}
              onClick={() => handleSelect(station)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                width: '100%',
                padding: '12px 16px',
                background: idx === activeIndex ? 'rgba(59, 130, 246, 0.12)' : 'transparent',
                border: 'none',
                borderBottom: idx < results.length - 1 ? '1px solid var(--border-subtle)' : 'none',
                cursor: 'pointer',
                textAlign: 'left',
                color: 'var(--text-primary)',
                fontFamily: 'var(--font-sans)',
                fontSize: '14px',
                transition: 'background var(--transition-fast)',
              }}
              onMouseEnter={() => setActiveIndex(idx)}
            >
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '46px',
                padding: '4px 6px',
                background: 'rgba(59, 130, 246, 0.12)',
                color: 'var(--accent-blue-light)',
                borderRadius: 'var(--radius-sm)',
                fontSize: '12px',
                fontWeight: 700,
                letterSpacing: '0.5px',
                flexShrink: 0,
              }}>
                {station.code}
              </span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  fontWeight: 500,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}>
                  {station.name}
                </div>
                <div style={{
                  fontSize: '12px',
                  color: 'var(--text-tertiary)',
                  marginTop: '1px',
                }}>
                  {station.city}, {station.state}
                </div>
              </div>
              {station.is_junction && (
                <span className="badge badge-blue" style={{ fontSize: '9px', flexShrink: 0 }}>
                  JN
                </span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
