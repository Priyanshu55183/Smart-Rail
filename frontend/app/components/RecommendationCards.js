'use client';

import { getTagInfo, formatDuration, formatFare, getRiskInfo } from '@/app/lib/utils';

/**
 * RecommendationCards — Horizontal cards for Best/Fastest/Cheapest/Safest.
 * Shown at the top of search results for quick decision-making.
 */
export default function RecommendationCards({ recommendations }) {
  // recommendations = { best_overall, fastest, cheapest, safest }
  const cards = [
    { key: 'best_overall', tag: 'BEST_OVERALL', data: recommendations.best_overall },
    { key: 'fastest', tag: 'FASTEST', data: recommendations.fastest },
    { key: 'cheapest', tag: 'CHEAPEST', data: recommendations.cheapest },
    { key: 'safest', tag: 'SAFEST', data: recommendations.safest },
  ].filter(c => c.data);

  if (cards.length === 0) return null;

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: `repeat(${Math.min(cards.length, 4)}, 1fr)`,
      gap: '12px',
      marginBottom: '28px',
    }}>
      {cards.map(({ key, tag, data }, idx) => (
        <RecommendationCard key={key} tag={tag} journey={data} index={idx} />
      ))}
    </div>
  );
}

function RecommendationCard({ tag, journey, index }) {
  const tagInfo = getTagInfo(tag);
  const riskInfo = getRiskInfo(journey.overall_risk);
  
  const firstTrain = journey.segments?.find(s => s.segment_type === 'TRAIN');

  return (
    <div
      className="glass-card animate-fade-in-up"
      style={{
        padding: '16px',
        cursor: 'pointer',
        animationDelay: `${index * 0.08}s`,
        borderColor: `${tagInfo.color}20`,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Glow accent */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '3px',
        background: `linear-gradient(90deg, ${tagInfo.color}, ${tagInfo.color}00)`,
      }} />

      {/* Tag */}
      <div style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        padding: '3px 10px',
        fontSize: '10px',
        fontWeight: 700,
        color: tagInfo.color,
        background: tagInfo.bg,
        borderRadius: 'var(--radius-full)',
        marginBottom: '12px',
        border: `1px solid ${tagInfo.color}20`,
      }}>
        {tagInfo.label}
      </div>

      {/* Duration + Score */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '8px' }}>
        <span style={{ fontSize: '20px', fontWeight: 800, color: 'var(--text-primary)' }}>
          {journey.total_duration_display || formatDuration(journey.total_duration_minutes)}
        </span>
        <span style={{
          fontSize: '14px',
          fontWeight: 700,
          color: tagInfo.color,
        }}>
          {journey.score?.composite}
        </span>
      </div>

      {/* Details */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
        <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
          {journey.num_connections === 0 ? '🚂 Direct' : `🔄 ${journey.num_connections} change${journey.num_connections > 1 ? 's' : ''}`}
          {firstTrain && ` • ${firstTrain.train_name}`}
        </div>
        {journey.total_fare && (
          <div style={{ fontSize: '12px', color: 'var(--text-tertiary)' }}>
            💰 {formatFare(journey.total_fare)}
          </div>
        )}
        <div style={{ fontSize: '11px', color: riskInfo.color, marginTop: '2px' }}>
          {riskInfo.emoji} {journey.overall_risk === 'NONE' ? 'Direct — No risk' : `${riskInfo.label} ${journey.overall_success_probability ? `(${Math.round(journey.overall_success_probability * 100)}%)` : ''}`}
        </div>
      </div>
    </div>
  );
}
