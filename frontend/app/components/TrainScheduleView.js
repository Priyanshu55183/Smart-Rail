'use client';

import { formatDuration, getTrainTypeInfo } from '@/app/lib/utils';

/**
 * TrainScheduleView — Vertical timeline showing all stops for a train.
 * Used on the /train/[number] page.
 */
export default function TrainScheduleView({ schedule }) {
  if (!schedule || !schedule.stops) return null;

  const { train, stops, total_stops } = schedule;
  const typeInfo = getTrainTypeInfo(train.train_type);

  return (
    <div className="glass-card" style={{ padding: '24px', overflow: 'hidden' }}>
      {/* Train Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        marginBottom: '24px',
        flexWrap: 'wrap',
      }}>
        <span style={{
          padding: '4px 12px',
          background: `${typeInfo.color}18`,
          color: typeInfo.color,
          borderRadius: 'var(--radius-sm)',
          fontSize: '14px',
          fontWeight: 800,
          border: `1px solid ${typeInfo.color}30`,
        }}>
          {train.train_number}
        </span>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 700, margin: 0 }}>
            {train.train_name}
          </h2>
          <div style={{ fontSize: '12px', color: 'var(--text-tertiary)', marginTop: '2px' }}>
            {typeInfo.label} • {train.runs_on_days} • {total_stops} stops
            {train.total_distance_km && ` • ${Math.round(train.total_distance_km)} km`}
            {train.avg_speed_kmph && ` • ~${Math.round(train.avg_speed_kmph)} km/h avg`}
          </div>
        </div>
      </div>

      {/* Stops Timeline */}
      <div style={{ position: 'relative' }}>
        {stops.map((stop, idx) => {
          const isFirst = idx === 0;
          const isLast = idx === stops.length - 1;
          const isImportant = isFirst || isLast || (stop.halt_minutes && stop.halt_minutes >= 10);

          return (
            <div
              key={idx}
              className="animate-fade-in"
              style={{
                display: 'flex',
                gap: '16px',
                animationDelay: `${idx * 0.03}s`,
              }}
            >
              {/* Timeline column */}
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                width: '24px',
                flexShrink: 0,
              }}>
                {/* Dot */}
                <div style={{
                  width: isImportant ? '14px' : '8px',
                  height: isImportant ? '14px' : '8px',
                  borderRadius: '50%',
                  background: isFirst ? 'var(--success)' : isLast ? 'var(--danger)' : 'var(--accent-blue)',
                  boxShadow: isImportant ? `0 0 8px ${isFirst ? 'var(--success)' : isLast ? 'var(--danger)' : 'var(--accent-blue)'}40` : 'none',
                  flexShrink: 0,
                  marginTop: '6px',
                }} />
                {/* Line */}
                {!isLast && (
                  <div style={{
                    width: '2px',
                    flex: 1,
                    minHeight: '20px',
                    background: 'var(--border-light)',
                  }} />
                )}
              </div>

              {/* Stop Content */}
              <div style={{
                flex: 1,
                paddingBottom: isLast ? '0' : '16px',
                borderBottom: !isLast ? '1px solid var(--border-subtle)' : 'none',
                marginBottom: !isLast ? '4px' : '0',
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'baseline',
                  gap: '12px',
                  flexWrap: 'wrap',
                }}>
                  {/* Station Code */}
                  <span style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minWidth: '48px',
                    padding: '2px 8px',
                    background: isImportant ? 'rgba(59, 130, 246, 0.12)' : 'transparent',
                    color: isImportant ? 'var(--accent-blue-light)' : 'var(--text-secondary)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '12px',
                    fontWeight: 700,
                    letterSpacing: '0.3px',
                  }}>
                    {stop.station_code}
                  </span>

                  {/* Station Name */}
                  <span style={{
                    fontSize: isImportant ? '14px' : '13px',
                    fontWeight: isImportant ? 600 : 400,
                    color: isImportant ? 'var(--text-primary)' : 'var(--text-secondary)',
                  }}>
                    {stop.station_name}
                  </span>

                  {/* Times */}
                  <div style={{ display: 'flex', gap: '8px', marginLeft: 'auto' }}>
                    {stop.arrival_time && (
                      <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: 500 }}>
                        Arr {stop.arrival_time}
                      </span>
                    )}
                    {stop.departure_time && (
                      <span style={{ fontSize: '13px', color: 'var(--text-primary)', fontWeight: 600 }}>
                        Dep {stop.departure_time}
                      </span>
                    )}
                    {stop.day_offset > 0 && (
                      <span style={{ fontSize: '10px', color: 'var(--warning)', fontWeight: 600 }}>
                        +{stop.day_offset}d
                      </span>
                    )}
                  </div>
                </div>

                {/* Meta row */}
                <div style={{
                  display: 'flex',
                  gap: '12px',
                  marginTop: '3px',
                  fontSize: '11px',
                  color: 'var(--text-muted)',
                }}>
                  {stop.halt_minutes > 0 && <span>⏱️ {stop.halt_minutes}m halt</span>}
                  {stop.distance_from_source > 0 && <span>📏 {stop.distance_from_source} km</span>}
                  {stop.platform_number && <span>🚏 Pf {stop.platform_number}</span>}
                  <span>#{stop.stop_sequence}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
