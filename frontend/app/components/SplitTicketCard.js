'use client';

import React, { useState } from 'react';
import { formatFare } from '@/app/lib/utils';

/**
 * SplitTicketCard
 * ===============
 * Displays a Break-Journey / Split-Ticket alternative discovering
 * confirmed berths when direct trains are waitlisted.
 */
export default function SplitTicketCard({ data, travelClass = '3A' }) {
  const [expanded, setExpanded] = useState(false);

  if (!data || !data.options || data.options.length === 0) {
    return null;
  }

  const best = data.best_option || data.options[0];

  return (
    <div
      className="glass-card animate-fade-in-up"
      style={{
        marginBottom: '28px',
        border: '1px solid rgba(34, 211, 238, 0.35)',
        background: 'linear-gradient(135deg, rgba(17, 24, 39, 0.85) 0%, rgba(15, 30, 50, 0.75) 100%)',
        boxShadow: '0 8px 32px rgba(34, 211, 238, 0.08), 0 0 20px rgba(59, 130, 246, 0.05)',
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      {/* Top Banner */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 20px',
          background: 'linear-gradient(90deg, rgba(34, 211, 238, 0.15) 0%, rgba(16, 185, 129, 0.15) 100%)',
          borderBottom: '1px solid rgba(34, 211, 238, 0.2)',
          flexWrap: 'wrap',
          gap: '10px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '4px 10px',
              fontSize: '11px',
              fontWeight: 800,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              color: '#22d3ee',
              background: 'rgba(34, 211, 238, 0.12)',
              border: '1px solid rgba(34, 211, 238, 0.3)',
              borderRadius: '9999px',
            }}
          >
            ⚡ Split-Ticket Hack
          </span>
          <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
            Waitlist Bypass Engine: 100% Confirmed Berths Discovered
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-tertiary)' }}>
            Class: <strong style={{ color: 'var(--accent-cyan)' }}>{travelClass}</strong>
          </span>
          <span
            style={{
              padding: '3px 8px',
              fontSize: '11px',
              fontWeight: 700,
              color: 'var(--success)',
              background: 'var(--success-bg)',
              borderRadius: '4px',
              border: '1px solid rgba(16, 185, 129, 0.25)',
            }}
          >
            ✓ Guaranteed Confirmed
          </span>
        </div>
      </div>

      {/* Main Body */}
      <div style={{ padding: '20px' }}>
        {/* Comparison Header */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: '16px',
            marginBottom: '20px',
            padding: '16px',
            borderRadius: 'var(--radius-md)',
            background: 'rgba(255, 255, 255, 0.02)',
            border: '1px solid var(--border-subtle)',
          }}
        >
          {/* Direct Route Status */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-tertiary)', textTransform: 'uppercase' }}>
              Direct End-to-End Quota
            </span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span
                style={{
                  fontSize: '13px',
                  fontWeight: 700,
                  color: best.direct_status === 'AVAILABLE' ? 'var(--success)' : 'var(--warning)',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  background: best.direct_status === 'AVAILABLE' ? 'var(--success-bg)' : 'var(--warning-bg)',
                }}
              >
                {best.direct_status_display}
              </span>
              <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                Fare: {formatFare(best.direct_fare)}
              </span>
            </div>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              Chance: {Math.round((best.direct_confirmation_probability || 0.4) * 100)}% clearance
            </span>
          </div>

          {/* Split Alternative Status */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--accent-cyan)', textTransform: 'uppercase' }}>
              Split-Booking Optimization
            </span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span
                style={{
                  fontSize: '13px',
                  fontWeight: 700,
                  color: 'var(--success)',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  background: 'var(--success-bg)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                }}
              >
                100% CONFIRMED (2 Berths)
              </span>
              <span style={{ fontSize: '13px', color: 'var(--text-primary)', fontWeight: 600 }}>
                Total: {formatFare(best.total_split_fare)}
              </span>
            </div>
            <span style={{ fontSize: '11px', color: 'var(--success-light)' }}>
              +{formatFare(best.fare_difference)} difference for zero waitlist risk
            </span>
          </div>
        </div>

        {/* Action Tip */}
        <div
          style={{
            padding: '12px 16px',
            background: 'rgba(59, 130, 246, 0.08)',
            borderLeft: '4px solid var(--accent-cyan)',
            borderRadius: '4px',
            marginBottom: '20px',
            fontSize: '13px',
            color: 'var(--text-primary)',
            lineHeight: 1.5,
          }}
        >
          <strong>💡 How this works: </strong>
          {best.berth_action_tip}
        </div>

        {/* Visual Split Path */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
          }}
        >
          {/* Leg 1 */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '14px 18px',
              background: 'rgba(255, 255, 255, 0.03)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-light)',
              flexWrap: 'wrap',
              gap: '12px',
            }}
          >
            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', fontWeight: 600 }}>
                TICKET 1 (Leg 1) • Train {best.leg1.train_number} ({best.leg1.train_name})
              </div>
              <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '2px' }}>
                {best.leg1.from_station_code} ({best.leg1.departure_time}) → {best.leg1.to_station_code} ({best.leg1.arrival_time})
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-tertiary)' }}>
                {best.leg1.from_station_name} to {best.leg1.to_station_name} ({best.leg1.distance_km} km)
              </div>
            </div>

            <div style={{ textAlign: 'right' }}>
              <div
                style={{
                  display: 'inline-block',
                  padding: '3px 8px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  fontWeight: 700,
                  color: 'var(--success)',
                  background: 'var(--success-bg)',
                }}
              >
                {best.leg1.status_display}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '3px' }}>
                {formatFare(best.leg1.fare)}
              </div>
            </div>
          </div>

          {/* Intermediate Junction Node */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative',
              padding: '4px 0',
            }}
          >
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '4px 14px',
                borderRadius: '9999px',
                background: 'rgba(34, 211, 238, 0.1)',
                border: '1px solid rgba(34, 211, 238, 0.3)',
                fontSize: '11px',
                fontWeight: 600,
                color: '#22d3ee',
              }}
            >
              🔄 Berth Switch Junction: {best.intermediate_station_name} ({best.intermediate_station_code})
            </div>
          </div>

          {/* Leg 2 */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '14px 18px',
              background: 'rgba(255, 255, 255, 0.03)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-light)',
              flexWrap: 'wrap',
              gap: '12px',
            }}
          >
            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', fontWeight: 600 }}>
                TICKET 2 (Leg 2) • Train {best.leg2.train_number} ({best.leg2.train_name})
              </div>
              <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '2px' }}>
                {best.leg2.from_station_code} ({best.leg2.departure_time}) → {best.leg2.to_station_code} ({best.leg2.arrival_time})
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-tertiary)' }}>
                {best.leg2.from_station_name} to {best.leg2.to_station_name} ({best.leg2.distance_km} km)
              </div>
            </div>

            <div style={{ textAlign: 'right' }}>
              <div
                style={{
                  display: 'inline-block',
                  padding: '3px 8px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  fontWeight: 700,
                  color: 'var(--success)',
                  background: 'var(--success-bg)',
                }}
              >
                {best.leg2.status_display}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '3px' }}>
                {formatFare(best.leg2.fare)}
              </div>
            </div>
          </div>
        </div>

        {/* More alternatives toggle if > 1 option */}
        {data.options.length > 1 && (
          <div style={{ marginTop: '16px', textAlign: 'center' }}>
            <button
              className="btn btn-ghost"
              onClick={() => setExpanded(!expanded)}
              style={{ fontSize: '12px', color: 'var(--accent-cyan)' }}
            >
              {expanded ? '▲ Hide alternative split stations' : `▼ View ${data.options.length - 1} other split options`}
            </button>

            {expanded && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '12px', textAlign: 'left' }}>
                {data.options.slice(1).map((opt) => (
                  <div
                    key={opt.option_id}
                    style={{
                      padding: '12px 16px',
                      background: 'rgba(0, 0, 0, 0.25)',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--border-subtle)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      flexWrap: 'wrap',
                      gap: '8px',
                    }}
                  >
                    <div>
                      <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                        Split at {opt.intermediate_station_name} ({opt.intermediate_station_code})
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>
                        Train {opt.leg1.train_number} • Total Fare: {formatFare(opt.total_split_fare)}
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: '6px' }}>
                      <span style={{ fontSize: '11px', padding: '2px 6px', background: 'var(--success-bg)', color: 'var(--success)', borderRadius: '4px' }}>
                        Leg 1: {opt.leg1.status_display}
                      </span>
                      <span style={{ fontSize: '11px', padding: '2px 6px', background: 'var(--success-bg)', color: 'var(--success)', borderRadius: '4px' }}>
                        Leg 2: {opt.leg2.status_display}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
