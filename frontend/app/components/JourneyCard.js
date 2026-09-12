'use client';

import { formatDuration, formatFare, getRiskInfo, getTagInfo, getTrainTypeInfo } from '@/app/lib/utils';

/**
 * JourneyCard — Displays a complete journey with segments, scores, and tags.
 * 
 * Shows:
 * - Recommendation tags (Best, Fastest, etc.)
 * - Journey summary (duration, connections, fare, risk)
 * - Visual timeline with train + layover segments
 * - Score breakdown
 */
export default function JourneyCard({ journey, index = 0 }) {
  if (!journey) return null;

  return (
    <div
      className="glass-card animate-fade-in-up"
      style={{
        padding: '0',
        overflow: 'hidden',
        animationDelay: `${index * 0.08}s`,
      }}
    >
      {/* Tags Bar */}
      {journey.tags && journey.tags.length > 0 && (
        <div style={{
          display: 'flex',
          gap: '8px',
          padding: '10px 20px',
          background: 'rgba(251, 191, 36, 0.04)',
          borderBottom: '1px solid var(--border-subtle)',
          flexWrap: 'wrap',
        }}>
          {journey.tags.map((tag) => {
            const info = getTagInfo(tag);
            return (
              <span key={tag} style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                padding: '3px 10px',
                fontSize: '11px',
                fontWeight: 700,
                color: info.color,
                background: info.bg,
                borderRadius: 'var(--radius-full)',
                border: `1px solid ${info.color}22`,
              }}>
                {info.label}
              </span>
            );
          })}
        </div>
      )}

      <div style={{ padding: '20px' }}>
        {/* Header Row: Endpoints + Summary */}
        <div style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          gap: '20px',
          marginBottom: '20px',
          flexWrap: 'wrap',
        }}>
          {/* Route */}
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
              <div>
                <div style={{ fontSize: '18px', fontWeight: 700 }}>{journey.from_station}</div>
                <div style={{ fontSize: '12px', color: 'var(--text-tertiary)' }}>{journey.from_station_name}</div>
              </div>
              <div style={{ color: 'var(--accent-blue-light)', fontSize: '16px', fontWeight: 300 }}>→</div>
              <div>
                <div style={{ fontSize: '18px', fontWeight: 700 }}>{journey.to_station}</div>
                <div style={{ fontSize: '12px', color: 'var(--text-tertiary)' }}>{journey.to_station_name}</div>
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
            <Stat label="Duration" value={journey.total_duration_display || formatDuration(journey.total_duration_minutes)} />
            <Stat label="Changes" value={journey.num_connections === 0 ? 'Direct' : `${journey.num_connections}`} />
            {journey.total_fare && <Stat label="Fare" value={formatFare(journey.total_fare)} />}
            <RiskStat risk={journey.overall_risk} probability={journey.overall_success_probability} />
          </div>
        </div>

        {/* Timeline Segments */}
        <JourneyTimeline segments={journey.segments} />

        {/* Score */}
        {journey.score && (
          <ScoreBar score={journey.score} />
        )}
      </div>
    </div>
  );
}

/* ── Stat Block ──────────────────────────────── */
function Stat({ label, value }) {
  return (
    <div style={{ textAlign: 'center', minWidth: '60px' }}>
      <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)' }}>{value}</div>
      <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.3px' }}>{label}</div>
    </div>
  );
}

/* ── Risk Stat ───────────────────────────────── */
function RiskStat({ risk, probability }) {
  const info = getRiskInfo(risk);
  return (
    <div style={{ textAlign: 'center', minWidth: '60px' }}>
      <div style={{ fontSize: '16px', fontWeight: 700, color: info.color }}>
        {probability ? `${Math.round(probability * 100)}%` : info.emoji}
      </div>
      <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.3px' }}>
        {risk === 'NONE' ? 'Direct' : 'Success'}
      </div>
    </div>
  );
}

/* ── Journey Timeline ────────────────────────── */
function JourneyTimeline({ segments }) {
  if (!segments || segments.length === 0) return null;

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '0',
      margin: '16px 0',
      padding: '16px',
      background: 'rgba(0, 0, 0, 0.15)',
      borderRadius: 'var(--radius-md)',
      border: '1px solid var(--border-subtle)',
    }}>
      {segments.map((seg, idx) => (
        <div key={idx}>
          {seg.segment_type === 'TRAIN' ? (
            <TrainSegmentBlock seg={seg} />
          ) : (
            <LayoverSegmentBlock seg={seg} />
          )}
        </div>
      ))}
    </div>
  );
}

/* ── Train Segment ───────────────────────────── */
function TrainSegmentBlock({ seg }) {
  const typeInfo = getTrainTypeInfo(seg.train_type);
  return (
    <div style={{
      display: 'flex',
      alignItems: 'stretch',
      gap: '16px',
      padding: '12px 0',
    }}>
      {/* Timeline line */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: '20px',
        flexShrink: 0,
      }}>
        <div style={{
          width: '10px', height: '10px', borderRadius: '50%',
          background: 'var(--accent-blue)',
          boxShadow: '0 0 8px var(--accent-blue-glow)',
          flexShrink: 0,
        }} />
        <div style={{
          width: '3px', flex: 1, minHeight: '40px',
          background: 'linear-gradient(180deg, var(--accent-blue), var(--accent-blue-light))',
          borderRadius: '2px',
        }} />
        <div style={{
          width: '10px', height: '10px', borderRadius: '50%',
          background: 'var(--accent-blue-light)',
          flexShrink: 0,
        }} />
      </div>

      {/* Content */}
      <div style={{ flex: 1 }}>
        {/* Train Info */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          marginBottom: '10px',
          flexWrap: 'wrap',
        }}>
          <span style={{
            padding: '2px 8px',
            background: `${typeInfo.color}18`,
            color: typeInfo.color,
            borderRadius: 'var(--radius-sm)',
            fontSize: '11px',
            fontWeight: 700,
            border: `1px solid ${typeInfo.color}30`,
          }}>
            {seg.train_number}
          </span>
          <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
            {seg.train_name}
          </span>
          <span className="badge badge-blue" style={{ fontSize: '9px' }}>
            {typeInfo.label}
          </span>
        </div>

        {/* From */}
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginBottom: '4px' }}>
          <span style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', minWidth: '50px' }}>
            {seg.departure_time}
          </span>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
            {seg.from_station_code}
          </span>
          <span style={{ fontSize: '12px', color: 'var(--text-tertiary)' }}>
            {seg.from_station_name}
          </span>
          {seg.departure_day_offset > 0 && (
            <span style={{ fontSize: '10px', color: 'var(--warning)', fontWeight: 600 }}>
              +{seg.departure_day_offset}d
            </span>
          )}
        </div>

        {/* Duration & distance */}
        <div style={{
          fontSize: '11px', color: 'var(--text-muted)',
          padding: '4px 0', marginLeft: '58px',
          display: 'flex', gap: '12px',
        }}>
          <span>🕐 {formatDuration(seg.duration_minutes)}</span>
          {seg.distance_km && <span>📏 {seg.distance_km} km</span>}
          {seg.fare && <span>💰 {formatFare(seg.fare)}</span>}
          {seg.predicted_delay_minutes != null && (
            <span style={{ color: seg.predicted_delay_minutes > 15 ? 'var(--warning)' : 'var(--success)' }}>
              ⏱️ ~{seg.predicted_delay_minutes}min delay
            </span>
          )}
        </div>

        {/* To */}
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: '4px' }}>
          <span style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', minWidth: '50px' }}>
            {seg.arrival_time}
          </span>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
            {seg.to_station_code}
          </span>
          <span style={{ fontSize: '12px', color: 'var(--text-tertiary)' }}>
            {seg.to_station_name}
          </span>
          {seg.arrival_day_offset > 0 && (
            <span style={{ fontSize: '10px', color: 'var(--warning)', fontWeight: 600 }}>
              +{seg.arrival_day_offset}d
            </span>
          )}
        </div>

        {/* Seat Availability & Waitlist Status Badges */}
        {seg.availabilities && seg.availabilities.length > 0 && (
          <div style={{
            display: 'flex',
            gap: '8px',
            marginTop: '12px',
            flexWrap: 'wrap',
          }}>
            {seg.availabilities.map((avail) => {
              const isAvail = avail.status === 'AVAILABLE';
              const isRac = avail.status === 'RAC';
              const bg = isAvail
                ? 'rgba(16, 185, 129, 0.10)'
                : isRac
                ? 'rgba(245, 158, 11, 0.10)'
                : 'rgba(239, 68, 68, 0.10)';
              const border = isAvail
                ? 'rgba(16, 185, 129, 0.25)'
                : isRac
                ? 'rgba(245, 158, 11, 0.25)'
                : 'rgba(239, 68, 68, 0.25)';
              const color = isAvail
                ? 'var(--success-light)'
                : isRac
                ? 'var(--warning-light)'
                : 'var(--danger-light)';

              return (
                <div
                  key={avail.travel_class}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    padding: '6px 10px',
                    background: bg,
                    border: `1px solid ${border}`,
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '11px',
                    minWidth: '105px',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontWeight: 800, color: 'var(--text-primary)' }}>
                      {avail.travel_class}
                    </span>
                    <span style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>
                      ₹{Math.round(avail.fare)}
                    </span>
                  </div>
                  <div style={{ fontWeight: 700, color, marginTop: '2px', fontSize: '11px' }}>
                    {avail.status_display}
                  </div>
                  {avail.status === 'WAITLIST' && (
                    <div style={{ fontSize: '9px', color: 'var(--accent-cyan)', marginTop: '2px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>~{Math.round((avail.confirmation_probability || 0.4) * 100)}% chance</span>
                      <span title="Split-ticket can bypass this waitlist" style={{ cursor: 'help' }}>⚡ Split Opt</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

/* ── Layover Segment ─────────────────────────── */
function LayoverSegmentBlock({ seg }) {
  const layover = seg.layover;
  if (!layover) return null;

  const riskInfo = getRiskInfo(layover.risk_level);

  return (
    <div style={{
      display: 'flex',
      alignItems: 'stretch',
      gap: '16px',
      padding: '4px 0',
    }}>
      {/* Timeline connector */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: '20px',
        flexShrink: 0,
      }}>
        <div style={{
          width: '2px', flex: 1,
          background: riskInfo.color,
          borderRadius: '2px',
          opacity: 0.4,
          borderStyle: 'dashed',
        }} />
      </div>

      {/* Layover Info */}
      <div style={{
        flex: 1,
        padding: '10px 14px',
        background: riskInfo.bg,
        borderRadius: 'var(--radius-sm)',
        border: `1px solid ${riskInfo.color}20`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '12px',
        flexWrap: 'wrap',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '16px' }}>{riskInfo.emoji}</span>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
              Change at {layover.station_name} ({layover.station_code})
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-tertiary)' }}>
              {layover.duration_display || formatDuration(layover.duration_minutes)} layover • Arr {layover.arrival_time} → Dep {layover.departure_time}
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className={`badge ${riskInfo.badgeClass}`}>
            {riskInfo.label}
          </span>
          {layover.success_probability && (
            <span style={{
              fontSize: '12px',
              fontWeight: 700,
              color: riskInfo.color,
            }}>
              {Math.round(layover.success_probability * 100)}%
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

/* ── Score Bar ────────────────────────────────── */
function ScoreBar({ score }) {
  const dimensions = [
    { key: 'travel_time_score', label: 'Speed', icon: '⚡' },
    { key: 'layover_score', label: 'Layover', icon: '⏱️' },
    { key: 'reliability_score', label: 'Reliable', icon: '🛡️' },
    { key: 'price_score', label: 'Price', icon: '💰' },
    { key: 'convenience_score', label: 'Ease', icon: '✨' },
  ];

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '16px',
      padding: '12px 0 0',
      borderTop: '1px solid var(--border-subtle)',
      marginTop: '12px',
      flexWrap: 'wrap',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'baseline',
        gap: '6px',
        marginRight: '8px',
      }}>
        <span style={{
          fontSize: '22px',
          fontWeight: 800,
          background: 'linear-gradient(135deg, var(--accent-blue-light), var(--accent-cyan))',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
        }}>
          {score.composite}
        </span>
        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>/100</span>
      </div>
      <div style={{ display: 'flex', gap: '10px', flex: 1, flexWrap: 'wrap' }}>
        {dimensions.map(({ key, label, icon }) => (
          <ScoreDimension key={key} icon={icon} label={label} value={score[key] || 0} />
        ))}
      </div>
    </div>
  );
}

function ScoreDimension({ icon, label, value }) {
  const color = value >= 80 ? 'var(--success)' : value >= 50 ? 'var(--warning)' : 'var(--danger)';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', minWidth: '90px' }}>
      <span style={{ fontSize: '12px' }}>{icon}</span>
      <div style={{ flex: 1 }}>
        <div style={{
          display: 'flex', justifyContent: 'space-between',
          fontSize: '10px', color: 'var(--text-muted)', marginBottom: '2px',
        }}>
          <span>{label}</span>
          <span style={{ fontWeight: 600, color }}>{Math.round(value)}</span>
        </div>
        <div style={{
          height: '3px',
          background: 'var(--bg-tertiary)',
          borderRadius: 'var(--radius-full)',
          overflow: 'hidden',
        }}>
          <div style={{
            width: `${value}%`,
            height: '100%',
            background: color,
            borderRadius: 'var(--radius-full)',
            transition: 'width 0.8s ease-out',
          }} />
        </div>
      </div>
    </div>
  );
}
