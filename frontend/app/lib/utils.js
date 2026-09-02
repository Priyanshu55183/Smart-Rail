/**
 * Utility functions for SmartRail frontend.
 */

/**
 * Format duration in minutes to human-readable string.
 * E.g., 135 → "2h 15m"
 */
export function formatDuration(minutes) {
  if (!minutes || minutes <= 0) return '0m';
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  if (h === 0) return `${m}m`;
  if (m === 0) return `${h}h`;
  return `${h}h ${m}m`;
}

/**
 * Format fare to Indian Rupees.
 * E.g., 1850 → "₹1,850"
 */
export function formatFare(amount) {
  if (!amount) return null;
  return `₹${Math.round(amount).toLocaleString('en-IN')}`;
}

/**
 * Get risk level color and label.
 */
export function getRiskInfo(level) {
  const map = {
    HIGH_RISK: { color: 'var(--danger)', bg: 'var(--danger-bg)', label: 'High Risk', emoji: '🔴', badgeClass: 'badge-danger' },
    MODERATE_RISK: { color: 'var(--warning)', bg: 'var(--warning-bg)', label: 'Moderate', emoji: '🟡', badgeClass: 'badge-warning' },
    LOW_RISK: { color: 'var(--success)', bg: 'var(--success-bg)', label: 'Low Risk', emoji: '🟢', badgeClass: 'badge-success' },
    LONG_LAYOVER: { color: 'var(--info)', bg: 'var(--info-bg)', label: 'Long Wait', emoji: '🔵', badgeClass: 'badge-info' },
    NONE: { color: 'var(--success)', bg: 'var(--success-bg)', label: 'Direct', emoji: '✅', badgeClass: 'badge-success' },
  };
  return map[level] || map.LOW_RISK;
}

/**
 * Get recommendation tag styling.
 */
export function getTagInfo(tag) {
  const map = {
    BEST_OVERALL: { label: '⭐ Best Overall', color: '#fbbf24', bg: 'rgba(251, 191, 36, 0.12)' },
    FASTEST: { label: '⚡ Fastest', color: '#3b82f6', bg: 'rgba(59, 130, 246, 0.12)' },
    CHEAPEST: { label: '💰 Cheapest', color: '#10b981', bg: 'rgba(16, 185, 129, 0.12)' },
    SAFEST: { label: '🛡️ Safest', color: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.12)' },
    FEWEST_CHANGES: { label: '🔄 Fewest Changes', color: '#22d3ee', bg: 'rgba(34, 211, 238, 0.12)' },
  };
  return map[tag] || { label: tag, color: '#94a3b8', bg: 'rgba(148, 163, 184, 0.12)' };
}

/**
 * Get train type styling.
 */
export function getTrainTypeInfo(type) {
  const map = {
    RAJDHANI: { label: 'Rajdhani', color: '#ef4444', priority: 1 },
    VANDE_BHARAT: { label: 'Vande Bharat', color: '#f97316', priority: 2 },
    SHATABDI: { label: 'Shatabdi', color: '#eab308', priority: 3 },
    DURONTO: { label: 'Duronto', color: '#8b5cf6', priority: 4 },
    SUPERFAST: { label: 'Superfast', color: '#3b82f6', priority: 5 },
    EXPRESS: { label: 'Express', color: '#6366f1', priority: 6 },
    MAIL: { label: 'Mail', color: '#64748b', priority: 7 },
    PASSENGER: { label: 'Passenger', color: '#94a3b8', priority: 8 },
  };
  return map[type] || { label: type, color: '#94a3b8', priority: 9 };
}

/**
 * Get a default date for search (tomorrow).
 */
export function getDefaultDate() {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return d.toISOString().split('T')[0];
}

/**
 * Debounce function.
 */
export function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}
