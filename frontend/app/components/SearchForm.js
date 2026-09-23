'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import StationAutocomplete from './StationAutocomplete';
import { getDefaultDate } from '@/app/lib/utils';

/**
 * SearchForm — The main journey search form.
 * 
 * Features:
 * - Station autocomplete for source/destination
 * - Swap stations button
 * - Date picker
 * - Max connections selector
 * - Navigates to /search with query params
 */
export default function SearchForm({ compact = false }) {
  const router = useRouter();
  const [fromStation, setFromStation] = useState(null);
  const [toStation, setToStation] = useState(null);
  const [date, setDate] = useState(getDefaultDate());
  const [maxConnections, setMaxConnections] = useState(2);
  const [quota, setQuota] = useState('GN');
  const [error, setError] = useState('');

  const handleSwap = () => {
    const temp = fromStation;
    setFromStation(toStation);
    setToStation(temp);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!fromStation) { setError('Please select a source station'); return; }
    if (!toStation) { setError('Please select a destination station'); return; }
    if (fromStation.code === toStation.code) { setError('Source and destination cannot be the same'); return; }
    if (!date) { setError('Please select a date'); return; }

    const params = new URLSearchParams({
      from: fromStation.code,
      to: toStation.code,
      date,
      max_connections: String(maxConnections),
      quota,
    });

    router.push(`/search?${params.toString()}`);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div style={{
        display: 'flex',
        flexDirection: compact ? 'row' : 'column',
        gap: compact ? '12px' : '20px',
        flexWrap: 'wrap',
      }}>
        {/* Station Row */}
        <div style={{
          display: 'flex',
          gap: '12px',
          alignItems: 'flex-end',
          flex: 1,
          minWidth: compact ? '400px' : undefined,
          flexWrap: 'wrap',
        }}>
          <StationAutocomplete
            label="From"
            placeholder="e.g. Bangalore, SBC"
            value={fromStation}
            onChange={setFromStation}
            icon="🟢"
            id="search-from"
          />

          {/* Swap Button */}
          <button
            type="button"
            onClick={handleSwap}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '42px',
              height: '42px',
              borderRadius: 'var(--radius-full)',
              background: 'var(--bg-glass)',
              border: '1px solid var(--border-light)',
              cursor: 'pointer',
              fontSize: '18px',
              transition: 'all var(--transition-fast)',
              flexShrink: 0,
              marginBottom: compact ? '0' : undefined,
              backdropFilter: 'blur(8px)',
            }}
            title="Swap stations"
            onMouseOver={(e) => { e.currentTarget.style.borderColor = 'var(--accent-blue)'; e.currentTarget.style.transform = 'rotate(180deg)'; }}
            onMouseOut={(e) => { e.currentTarget.style.borderColor = 'var(--border-light)'; e.currentTarget.style.transform = 'rotate(0deg)'; }}
          >
            ⇆
          </button>

          <StationAutocomplete
            label="To"
            placeholder="e.g. New Delhi, NDLS"
            value={toStation}
            onChange={setToStation}
            icon="🔴"
            id="search-to"
          />
        </div>

        {/* Date & Options Row */}
        <div style={{
          display: 'flex',
          gap: '12px',
          alignItems: 'flex-end',
          flexWrap: 'wrap',
        }}>
          <div style={{ minWidth: '160px' }}>
            <label style={{
              display: 'block',
              fontSize: '12px',
              fontWeight: 600,
              color: 'var(--text-secondary)',
              marginBottom: '6px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
            }}>
              📅 Date
            </label>
            <input
              type="date"
              className="input input-lg"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              min={new Date().toISOString().split('T')[0]}
              id="search-date"
              style={{ colorScheme: 'dark' }}
            />
          </div>

          <div style={{ minWidth: '120px' }}>
            <label style={{
              display: 'block',
              fontSize: '12px',
              fontWeight: 600,
              color: 'var(--text-secondary)',
              marginBottom: '6px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
            }}>
              🔄 Max Changes
            </label>
            <select
              className="input input-lg"
              value={maxConnections}
              onChange={(e) => setMaxConnections(Number(e.target.value))}
              id="search-connections"
              style={{
                colorScheme: 'dark',
                cursor: 'pointer',
              }}
            >
              <option value={0}>Direct Only</option>
              <option value={1}>1 Change</option>
              <option value={2}>2 Changes</option>
              <option value={3}>3 Changes</option>
            </select>
          </div>

          <div style={{ minWidth: '140px' }}>
            <label style={{
              display: 'block',
              fontSize: '12px',
              fontWeight: 600,
              color: 'var(--text-secondary)',
              marginBottom: '6px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
            }}>
              🎟️ Quota
            </label>
            <select
              className="input input-lg"
              value={quota}
              onChange={(e) => setQuota(e.target.value)}
              id="search-quota"
              style={{
                colorScheme: 'dark',
                cursor: 'pointer',
              }}
            >
              <option value="GN">General (GN)</option>
              <option value="TQ">Tatkal (TQ)</option>
              <option value="LD">Ladies (LD)</option>
              <option value="SS">Senior Citizen (SS)</option>
            </select>
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-lg"
            id="search-submit"
            style={{ minWidth: '160px', height: '54px' }}
          >
            🔍 Find Journeys
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div style={{
          marginTop: '12px',
          padding: '10px 16px',
          background: 'var(--danger-bg)',
          border: '1px solid rgba(239, 68, 68, 0.2)',
          borderRadius: 'var(--radius-md)',
          color: 'var(--danger-light)',
          fontSize: '13px',
          animation: 'fadeIn 0.3s ease-out',
        }}>
          ⚠️ {error}
        </div>
      )}
    </form>
  );
}
