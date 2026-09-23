'use client';

import { useRouter } from 'next/navigation';

/**
 * ETicketModal — Authentic Indian Railways Electronic Reservation Slip (ERS).
 * Includes digital boarding pass styling, mock QR code, and print support.
 */
export default function ETicketModal({ ticket, onClose }) {
  const router = useRouter();

  if (!ticket) return null;

  const handlePrint = () => {
    window.print();
  };

  const handleTrackPNR = () => {
    router.push(`/pnr?pnr=${ticket.pnr}`);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-dialog printable-eticket"
        onClick={(e) => e.stopPropagation()}
        style={{ maxWidth: '720px' }}
      >
        {/* Ticket Header */}
        <div style={{
          padding: '20px 24px',
          background: 'linear-gradient(135deg, #1e3a8a, #0284c7)',
          color: '#fff',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '30px' }}>🚂</span>
            <div>
              <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '1px', opacity: 0.9 }}>
                Indian Railways • Electronic Reservation Slip (ERS)
              </div>
              <h2 style={{ fontSize: '20px', fontWeight: 800, margin: 0 }}>
                SmartRail Confirmed E-Ticket
              </h2>
            </div>
          </div>

          <div style={{ textAlign: 'right' }} className="no-print">
            <button
              onClick={onClose}
              style={{
                background: 'rgba(255, 255, 255, 0.2)',
                border: 'none',
                color: '#fff',
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                cursor: 'pointer',
                fontSize: '16px',
              }}
            >
              ✕
            </button>
          </div>
        </div>

        {/* PNR & Barcode Banner */}
        <div style={{
          padding: '16px 24px',
          background: 'rgba(15, 23, 42, 0.9)',
          borderBottom: '1px dashed rgba(148, 163, 184, 0.2)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px',
        }}>
          <div>
            <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600 }}>
              PNR Number (10-Digit)
            </div>
            <div style={{
              fontSize: '24px',
              fontWeight: 900,
              fontFamily: 'var(--font-mono)',
              color: 'var(--accent-cyan)',
              letterSpacing: '1px',
            }}>
              {ticket.pnr}
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {/* Mock QR / Barcode */}
            <div style={{
              background: '#fff',
              padding: '6px 10px',
              borderRadius: 'var(--radius-sm)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}>
              <div style={{
                fontFamily: 'monospace',
                letterSpacing: '2px',
                fontSize: '10px',
                color: '#000',
                fontWeight: 900,
              }}>
                ||| | |||| | ||| |||| |
              </div>
              <span style={{ fontSize: '8px', color: '#333', fontWeight: 700 }}>
                IRCTC SECURE QR
              </span>
            </div>

            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', textTransform: 'uppercase', fontWeight: 600 }}>
                Charting Status
              </div>
              <span style={{
                display: 'inline-block',
                background: 'rgba(16, 185, 129, 0.2)',
                color: '#34d399',
                border: '1px solid rgba(16, 185, 129, 0.4)',
                padding: '2px 8px',
                borderRadius: 'var(--radius-full)',
                fontSize: '11px',
                fontWeight: 800,
              }}>
                {ticket.chartStatus || 'CHART PREPARED'}
              </span>
            </div>
          </div>
        </div>

        {/* Journey Details */}
        <div style={{ padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Train & Route Strip */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '12px',
            background: 'rgba(30, 41, 59, 0.4)',
            padding: '14px',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)',
          }}>
            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>TRAIN NUMBER & NAME</div>
              <div style={{ fontSize: '14px', fontWeight: 700, color: '#fff' }}>
                {ticket.trainNumber} • {ticket.trainName}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>CLASS & QUOTA</div>
              <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--accent-blue-light)' }}>
                {ticket.travelClass} • {ticket.quota || 'General (GN)'}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>BOARDING / DEPARTURE</div>
              <div style={{ fontSize: '14px', fontWeight: 700, color: '#fff' }}>
                {ticket.fromName} ({ticket.fromCode}) • {ticket.depTime}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>DESTINATION / ARRIVAL</div>
              <div style={{ fontSize: '14px', fontWeight: 700, color: '#fff' }}>
                {ticket.toName} ({ticket.toCode}) • {ticket.arrTime}
              </div>
            </div>
          </div>

          {/* Passenger & Berth Allocation Table */}
          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '8px', textTransform: 'uppercase' }}>
              👥 Passenger & Seat Allotment
            </div>

            <div style={{
              overflowX: 'auto',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
            }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: 'rgba(30, 41, 59, 0.6)', color: 'var(--text-secondary)' }}>
                    <th style={{ padding: '8px 12px' }}>#</th>
                    <th style={{ padding: '8px 12px' }}>Name</th>
                    <th style={{ padding: '8px 12px' }}>Age/Sex</th>
                    <th style={{ padding: '8px 12px' }}>Booking Status</th>
                    <th style={{ padding: '8px 12px' }}>Current Status</th>
                    <th style={{ padding: '8px 12px' }}>Coach / Berth</th>
                  </tr>
                </thead>
                <tbody>
                  <tr style={{ borderTop: '1px solid rgba(148, 163, 184, 0.08)' }}>
                    <td style={{ padding: '10px 12px', color: 'var(--text-tertiary)' }}>1</td>
                    <td style={{ padding: '10px 12px', fontWeight: 700, color: '#fff' }}>
                      {ticket.passenger?.name || 'Primary Passenger'}
                    </td>
                    <td style={{ padding: '10px 12px', color: 'var(--text-secondary)' }}>
                      {ticket.passenger?.age} / {ticket.passenger?.gender}
                    </td>
                    <td style={{ padding: '10px 12px', color: 'var(--text-secondary)' }}>
                      {ticket.bookingStatus}
                    </td>
                    <td style={{ padding: '10px 12px', color: '#34d399', fontWeight: 700 }}>
                      {ticket.currentStatus}
                    </td>
                    <td style={{ padding: '10px 12px', fontWeight: 800, color: 'var(--accent-cyan)' }}>
                      {ticket.coach} - {ticket.berth}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Payment & Security Footer */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            background: 'rgba(15, 23, 42, 0.5)',
            padding: '12px 16px',
            borderRadius: 'var(--radius-sm)',
            fontSize: '12px',
            color: 'var(--text-secondary)',
          }}>
            <div>
              <span>IRCTC User ID: </span>
              <strong style={{ color: '#fff' }}>{ticket.passenger?.irctcId}</strong>
              <span style={{ marginLeft: '12px' }}>Booked on: {new Date(ticket.bookedAt).toLocaleDateString()}</span>
            </div>
            <div style={{ fontSize: '14px', fontWeight: 800, color: '#fff' }}>
              Total Paid: <span style={{ color: 'var(--accent-cyan)' }}>₹{ticket.totalFare}</span>
            </div>
          </div>
        </div>

        {/* Modal Buttons */}
        <div style={{
          padding: '16px 24px',
          background: 'rgba(15, 23, 42, 0.95)',
          borderTop: '1px solid var(--border-subtle)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: '12px',
        }} className="no-print">
          <button
            type="button"
            className="btn btn-ghost"
            onClick={handleTrackPNR}
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            🔍 Track in PNR Status
          </button>

          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handlePrint}
              style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              🖨️ Print / Save E-Ticket
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={onClose}
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
