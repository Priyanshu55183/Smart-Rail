'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import ETicketModal from '../components/ETicketModal';

function PnrContent() {
  const searchParams = useSearchParams();
  const initialPnr = searchParams.get('pnr') || '';

  const [inputPnr, setInputPnr] = useState(initialPnr);
  const [ticketResult, setTicketResult] = useState(null);
  const [recentBookings, setRecentBookings] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [activeETicket, setActiveETicket] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  // Load recent bookings from localStorage on mount
  useEffect(() => {
    try {
      const stored = JSON.parse(localStorage.getItem('smartrail_booked_tickets') || '[]');
      setRecentBookings(stored);

      if (initialPnr) {
        lookupPnr(initialPnr, stored);
      }
    } catch (err) {
      console.error('Error loading stored tickets:', err);
    }
  }, [initialPnr]);

  const lookupPnr = (pnrToSearch, storedTickets = recentBookings) => {
    setErrorMsg('');
    const cleanPnr = pnrToSearch.trim().replace(/\s+/g, '');

    if (!cleanPnr || cleanPnr.length < 9) {
      setErrorMsg('Please enter a valid 10-digit Indian Railways PNR number');
      return;
    }

    setIsSearching(true);

    setTimeout(() => {
      // 1. Look up in stored local tickets
      const found = storedTickets.find(
        (t) => t.pnr.replace('-', '') === cleanPnr.replace('-', '')
      );

      if (found) {
        setTicketResult(found);
      } else {
        // 2. Deterministic simulated IRCTC status for any custom 10-digit PNR
        const pseudoSeed = cleanPnr.split('').reduce((acc, ch) => acc + ch.charCodeAt(0), 0);
        const trains = [
          { no: '12952', name: 'New Delhi Rajdhani Express', from: 'BCT', fromName: 'Mumbai Central', to: 'NDLS', toName: 'New Delhi' },
          { no: '12627', name: 'Karnataka Express', from: 'SBC', fromName: 'KSR Bengaluru', to: 'NDLS', toName: 'New Delhi' },
          { no: '22436', name: 'Vande Bharat Express', from: 'NDLS', fromName: 'New Delhi', to: 'BSB', toName: 'Varanasi' },
          { no: '12137', name: 'Punjab Mail', from: 'CSMT', fromName: 'Mumbai CSMT', to: 'FZR', toName: 'Firozpur' },
        ];
        const train = trains[pseudoSeed % trains.length];
        const coachNo = (pseudoSeed % 5) + 1;
        const berthNo = (pseudoSeed % 64) + 1;
        const berths = ['Lower Berth [LB]', 'Middle Berth [MB]', 'Upper Berth [UB]', 'Side Lower [SL]', 'Side Upper [SU]'];
        const berthType = berths[pseudoSeed % berths.length];

        const simulatedTicket = {
          pnr: cleanPnr.includes('-') ? cleanPnr : `${cleanPnr.slice(0, 3)}-${cleanPnr.slice(3)}`,
          bookedAt: new Date(Date.now() - 86400000 * 2).toISOString(),
          trainNumber: train.no,
          trainName: train.name,
          fromCode: train.from,
          fromName: train.fromName,
          toCode: train.to,
          toName: train.toName,
          depTime: '16:55',
          arrTime: '08:35',
          travelClass: '3A',
          quota: 'General (GN)',
          chartStatus: 'CHART PREPARED',
          bookingStatus: `WL 18 / GNWL`,
          currentStatus: `CNF / B${coachNo} / ${berthNo} (${berthType})`,
          coach: `B${coachNo}`,
          berth: String(berthNo),
          berthType,
          totalFare: 1485,
          passenger: {
            name: 'Confirmed Passenger',
            age: 28,
            gender: 'M',
            irctcId: 'irctc_verified_user',
          },
        };

        setTicketResult(simulatedTicket);
      }

      setIsSearching(false);
    }, 450);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    lookupPnr(inputPnr);
  };

  return (
    <div style={{ padding: '40px 0', minHeight: '80vh' }}>
      <div className="container" style={{ maxWidth: '840px' }}>
        {/* Title Header */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 16px',
            borderRadius: 'var(--radius-full)',
            background: 'rgba(59, 130, 246, 0.1)',
            border: '1px solid rgba(59, 130, 246, 0.25)',
            color: 'var(--accent-blue-light)',
            fontSize: '12px',
            fontWeight: 700,
            marginBottom: '12px',
          }}>
            <span>🎫 IRCTC PASSENGER RESERVATION SYSTEM</span>
          </div>
          <h1 style={{ fontSize: '32px', fontWeight: 900, marginBottom: '8px' }}>
            Live PNR Status Enquiry
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '15px' }}>
            Check real-time chart status, coach & berth allocations, and confirmation probabilities.
          </p>
        </div>

        {/* PNR Search Card */}
        <div className="glass-card" style={{ padding: '24px', marginBottom: '32px' }}>
          <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <div style={{ flex: 1, minWidth: '260px' }}>
              <input
                type="text"
                className="input input-lg"
                placeholder="Enter 10-Digit PNR (e.g. 245-8912341)"
                value={inputPnr}
                onChange={(e) => setInputPnr(e.target.value)}
                maxLength={12}
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '17px',
                  letterSpacing: '1px',
                  fontWeight: 700,
                }}
              />
            </div>
            <button
              type="submit"
              className="btn btn-primary btn-lg"
              disabled={isSearching}
              style={{ minWidth: '160px' }}
            >
              {isSearching ? '⚡ Checking Chart...' : '🔍 Check Status'}
            </button>
          </form>

          {errorMsg && (
            <div style={{ color: 'var(--danger-light)', fontSize: '13px', marginTop: '10px' }}>
              ⚠️ {errorMsg}
            </div>
          )}
        </div>

        {/* PNR Status Result Display */}
        {ticketResult && (
          <div className="glass-card animate-fade-in-up" style={{ padding: '0', overflow: 'hidden', marginBottom: '32px' }}>
            {/* Top Banner */}
            <div style={{
              padding: '18px 24px',
              background: 'linear-gradient(135deg, rgba(30, 58, 138, 0.8), rgba(2, 132, 199, 0.8))',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '12px',
            }}>
              <div>
                <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'rgba(255, 255, 255, 0.8)', fontWeight: 600 }}>
                  PNR Number
                </div>
                <div style={{
                  fontSize: '24px',
                  fontWeight: 900,
                  fontFamily: 'var(--font-mono)',
                  color: '#fff',
                  letterSpacing: '1px',
                }}>
                  {ticketResult.pnr}
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{
                  background: 'rgba(16, 185, 129, 0.25)',
                  color: '#34d399',
                  border: '1px solid rgba(16, 185, 129, 0.4)',
                  padding: '4px 12px',
                  borderRadius: 'var(--radius-full)',
                  fontSize: '12px',
                  fontWeight: 800,
                }}>
                  ● {ticketResult.chartStatus || 'CHART PREPARED'}
                </span>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setActiveETicket(ticketResult)}
                  style={{ fontSize: '12px', padding: '6px 12px' }}
                >
                  🖨️ View Full ERS
                </button>
              </div>
            </div>

            {/* Train & Journey Strip */}
            <div style={{ padding: '24px' }}>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                gap: '16px',
                background: 'rgba(15, 23, 42, 0.5)',
                padding: '16px',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-subtle)',
                marginBottom: '20px',
              }}>
                <div>
                  <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', fontWeight: 600 }}>TRAIN</div>
                  <div style={{ fontSize: '14px', fontWeight: 800, color: '#fff', marginTop: '2px' }}>
                    {ticketResult.trainNumber} • {ticketResult.trainName}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', fontWeight: 600 }}>CLASS & QUOTA</div>
                  <div style={{ fontSize: '14px', fontWeight: 800, color: 'var(--accent-cyan)', marginTop: '2px' }}>
                    {ticketResult.travelClass} ({ticketResult.quota || 'GN'})
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', fontWeight: 600 }}>FROM / DEPARTURE</div>
                  <div style={{ fontSize: '14px', fontWeight: 800, color: '#fff', marginTop: '2px' }}>
                    {ticketResult.fromName} ({ticketResult.fromCode}) • {ticketResult.depTime}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: 'var(--text-tertiary)', fontWeight: 600 }}>TO / ARRIVAL</div>
                  <div style={{ fontSize: '14px', fontWeight: 800, color: '#fff', marginTop: '2px' }}>
                    {ticketResult.toName} ({ticketResult.toCode}) • {ticketResult.arrTime}
                  </div>
                </div>
              </div>

              {/* Passenger Chart Status Table */}
              <div>
                <h3 style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '10px', textTransform: 'uppercase' }}>
                  👥 Passenger Allotment Details
                </h3>

                <div style={{
                  overflowX: 'auto',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
                    <thead>
                      <tr style={{ background: 'rgba(30, 41, 59, 0.7)', color: 'var(--text-secondary)' }}>
                        <th style={{ padding: '10px 14px' }}>#</th>
                        <th style={{ padding: '10px 14px' }}>Passenger Name</th>
                        <th style={{ padding: '10px 14px' }}>Booking Status</th>
                        <th style={{ padding: '10px 14px' }}>Current Status</th>
                        <th style={{ padding: '10px 14px' }}>Coach & Berth</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr style={{ borderTop: '1px solid rgba(148, 163, 184, 0.08)' }}>
                        <td style={{ padding: '12px 14px', color: 'var(--text-tertiary)' }}>1</td>
                        <td style={{ padding: '12px 14px', fontWeight: 800, color: '#fff' }}>
                          {ticketResult.passenger?.name || 'Primary Passenger'}
                        </td>
                        <td style={{ padding: '12px 14px', color: 'var(--text-secondary)' }}>
                          {ticketResult.bookingStatus}
                        </td>
                        <td style={{ padding: '12px 14px', color: '#34d399', fontWeight: 800 }}>
                          {ticketResult.currentStatus}
                        </td>
                        <td style={{ padding: '12px 14px', fontWeight: 800, color: 'var(--accent-cyan)' }}>
                          {ticketResult.coach} - {ticketResult.berth} ({ticketResult.berthType})
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Recent Bookings in this Browser Session */}
        {recentBookings.length > 0 && (
          <div style={{ marginTop: '32px' }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '14px',
            }}>
              <h2 style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)' }}>
                🕒 Your Saved Bookings ({recentBookings.length})
              </h2>
              <button
                type="button"
                onClick={() => {
                  localStorage.removeItem('smartrail_booked_tickets');
                  setRecentBookings([]);
                }}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-muted)',
                  fontSize: '12px',
                  cursor: 'pointer',
                }}
              >
                Clear History
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {recentBookings.map((b) => (
                <div
                  key={b.pnr}
                  onClick={() => {
                    setInputPnr(b.pnr);
                    setTicketResult(b);
                  }}
                  style={{
                    padding: '14px 18px',
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: 'pointer',
                    transition: 'all var(--transition-fast)',
                  }}
                  onMouseOver={(e) => { e.currentTarget.style.borderColor = 'var(--accent-blue)'; }}
                  onMouseOut={(e) => { e.currentTarget.style.borderColor = 'var(--border-subtle)'; }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{
                        fontFamily: 'var(--font-mono)',
                        fontWeight: 800,
                        color: 'var(--accent-cyan)',
                        fontSize: '14px',
                      }}>
                        {b.pnr}
                      </span>
                      <span style={{ fontSize: '13px', fontWeight: 700, color: '#fff' }}>
                        {b.trainNumber} • {b.trainName}
                      </span>
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-tertiary)', marginTop: '2px' }}>
                      {b.fromCode} ➔ {b.toCode} • Passenger: {b.passenger?.name} ({b.travelClass})
                    </div>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '12px', fontWeight: 700, color: '#34d399' }}>
                      {b.coach}-{b.berth}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--accent-blue-light)' }}>
                      Click to check status ➔
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* E-Ticket Modal for view / print */}
        {activeETicket && (
          <ETicketModal
            ticket={activeETicket}
            onClose={() => setActiveETicket(null)}
          />
        )}
      </div>
    </div>
  );
}

export default function PnrPage() {
  return (
    <Suspense fallback={<div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading PNR Enquiry...</div>}>
      <PnrContent />
    </Suspense>
  );
}
