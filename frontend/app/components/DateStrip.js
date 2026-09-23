'use client';

import { useMemo } from 'react';

/**
 * DateStrip — Multi-day horizontal calendar carousel like IRCTC & ConfirmTkt.
 * Displays 7 consecutive days with quick availability chips.
 */
export default function DateStrip({ currentDate, onSelectDate }) {
  const days = useMemo(() => {
    if (!currentDate) return [];

    const baseDate = new Date(currentDate);
    if (isNaN(baseDate.getTime())) return [];

    const result = [];
    const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    // Show 1 day before, and 5 days after (total 7 days)
    for (let offset = -1; offset <= 5; offset++) {
      const d = new Date(baseDate);
      d.setDate(baseDate.getDate() + offset);

      const yyyy = d.getFullYear();
      const mm = String(d.getMonth() + 1).padStart(2, '0');
      const dd = String(d.getDate()).padStart(2, '0');
      const dateStr = `${yyyy}-${mm}-${dd}`;

      // Deterministic availability status simulation for visual preview
      const hash = (d.getDate() * 13 + d.getMonth() * 7) % 10;
      let statusText = 'AVL 24';
      let statusColor = '#34d399';
      let statusBg = 'rgba(16, 185, 129, 0.15)';

      if (hash < 2) {
        statusText = 'WL 14';
        statusColor = '#f87171';
        statusBg = 'rgba(239, 68, 68, 0.15)';
      } else if (hash < 4) {
        statusText = 'RAC 6';
        statusColor = '#fbbf24';
        statusBg = 'rgba(245, 158, 11, 0.15)';
      } else if (hash < 7) {
        statusText = `AVL ${15 + hash * 6}`;
      } else {
        statusText = `AVL ${30 + hash * 4}`;
      }

      result.push({
        dateStr,
        dayName: weekdays[d.getDay()],
        dayNum: d.getDate(),
        monthName: months[d.getMonth()],
        statusText,
        statusColor,
        statusBg,
        isSelected: dateStr === currentDate,
        isToday: new Date().toISOString().slice(0, 10) === dateStr,
      });
    }

    return result;
  }, [currentDate]);

  if (!days.length) return null;

  return (
    <div style={{ marginBottom: '20px' }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '8px',
        padding: '0 4px',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '13px',
          fontWeight: 600,
          color: 'var(--text-secondary)',
        }}>
          <span>📅 Alternate Travel Dates</span>
          <span style={{ fontSize: '11px', color: 'var(--accent-cyan)' }}>
            (Check adjacent days for confirmed seats)
          </span>
        </div>
      </div>

      <div className="date-strip-container">
        {days.map((item) => (
          <div
            key={item.dateStr}
            className={`date-strip-card ${item.isSelected ? 'selected' : ''}`}
            onClick={() => onSelectDate(item.dateStr)}
            title={`Check train journeys for ${item.dayName}, ${item.dayNum} ${item.monthName}`}
          >
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              fontSize: '11px',
              fontWeight: 700,
              color: item.isSelected ? 'var(--accent-cyan)' : 'var(--text-tertiary)',
            }}>
              <span>{item.dayName}</span>
              {item.isToday && (
                <span style={{
                  fontSize: '9px',
                  background: 'var(--accent-blue)',
                  color: '#fff',
                  padding: '1px 4px',
                  borderRadius: '3px',
                }}>
                  Today
                </span>
              )}
            </div>

            <div style={{
              fontSize: '17px',
              fontWeight: 800,
              color: item.isSelected ? '#fff' : 'var(--text-primary)',
            }}>
              {item.dayNum} {item.monthName}
            </div>

            <div style={{
              fontSize: '11px',
              fontWeight: 700,
              color: item.statusColor,
              background: item.statusBg,
              padding: '3px 6px',
              borderRadius: 'var(--radius-sm)',
              marginTop: '2px',
            }}>
              {item.statusText}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
