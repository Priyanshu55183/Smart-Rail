'use client';

import { useState } from 'react';

/**
 * BookingModal — Realistic IRCTC Passenger Entry & Fare Breakdown Drawer.
 * Generates official 10-digit PNRs and persists booked tickets to localStorage.
 */
export default function BookingModal({
  isOpen,
  onClose,
  journey,
  segment,
  avail,
  quota = 'GN',
  onBookSuccess,
}) {
  const [passengerName, setPassengerName] = useState('');
  const [passengerAge, setPassengerAge] = useState('24');
  const [passengerGender, setPassengerGender] = useState('M');
  const [berthPreference, setBerthPreference] = useState('LB');
  const [irctcId, setIrctcId] = useState('rail_traveler');
  const [mobile, setMobile] = useState('9876543210');
  const [isProcessing, setIsProcessing] = useState(false);
  const [formError, setFormError] = useState('');

  if (!isOpen || !avail) return null;

  // Pricing calculations
  const baseFare = Math.max(120, Math.round((avail.fare || 500) * 0.82));
  const reservationFee = 40;
  const superfastCharge = 45;
  const tatkalCharge = quota === 'TQ' ? 250 : 0;
  const isAC = ['1A', '2A', '3A', '3E', 'CC', 'EC'].includes(avail.travel_class);
  const gst = isAC ? Math.round((baseFare + reservationFee + superfastCharge + tatkalCharge) * 0.05) : 0;
  const totalFare = baseFare + reservationFee + superfastCharge + tatkalCharge + gst;

  // Train and route metadata
  const trainNumber = segment?.train_number || journey?.segments?.[0]?.train_number || '12627';
  const trainName = segment?.train_name || journey?.segments?.[0]?.train_name || 'Superfast Express';
  const fromCode = segment?.from_station_code || journey?.from_station || 'SBC';
  const fromName = segment?.from_station_name || journey?.from_station_name || 'Bengaluru';
  const toCode = segment?.to_station_code || journey?.to_station || 'NDLS';
  const toName = segment?.to_station_name || journey?.to_station_name || 'New Delhi';
  const depTime = segment?.departure_time || journey?.segments?.[0]?.departure_time || '20:00';
  const arrTime = segment?.arrival_time || journey?.segments?.[journey?.segments?.length - 1]?.arrival_time || '06:30';

  const handleConfirm = (e) => {
    e.preventDefault();
    setFormError('');

    if (!passengerName.trim()) {
      setFormError('Please enter passenger full name');
      return;
    }
    if (!passengerAge || Number(passengerAge) < 1 || Number(passengerAge) > 120) {
      setFormError('Please enter a valid age (1-120)');
      return;
    }
    if (!irctcId.trim()) {
      setFormError('Please provide an IRCTC user ID');
      return;
    }

    setIsProcessing(true);

    setTimeout(() => {
      // Generate authentic 10-digit Indian Railways PNR (e.g. 245-8912341)
      const prefix = Math.floor(100 + Math.random() * 800);
      const suffix = Math.floor(1000000 + Math.random() * 9000000);
      const pnr = `${prefix}-${suffix}`;

      // Assign realistic Coach & Berth
      let coachPrefix = 'S';
      if (avail.travel_class === '3A') coachPrefix = 'B';
      else if (avail.travel_class === '2A') coachPrefix = 'A';
      else if (avail.travel_class === '1A') coachPrefix = 'H';
      else if (avail.travel_class === 'CC') coachPrefix = 'C';
      else if (avail.travel_class === '2S') coachPrefix = 'D';

      const coachNumber = Math.floor(1 + Math.random() * 6);
      const coach = `${coachPrefix}${coachNumber}`;
      const berthNum = Math.floor(1 + Math.random() * 72);

      const berthTypes = {
        LB: 'Lower Berth [LB]',
        MB: 'Middle Berth [MB]',
        UB: 'Upper Berth [UB]',
        SL: 'Side Lower [SL]',
        SU: 'Side Upper [SU]',
        NONE: 'Window Seat [WS]',
      };
      const assignedBerthType = berthTypes[berthPreference] || 'Lower Berth [LB]';

      const isWaitlist = avail.status === 'WAITLIST';
      const bookingStatus = isWaitlist
        ? `WL ${avail.status_display?.replace('WL', '').trim() || '18'} / GNWL`
        : `CNF / ${coach} / ${berthNum}`;
      const currentStatus = isWaitlist
        ? `RAC ${Math.floor(2 + Math.random() * 8)} (Upgraded)`
        : `CNF / ${coach} / ${berthNum} (${assignedBerthType})`;

      const ticket = {
        pnr,
        bookedAt: new Date().toISOString(),
        trainNumber,
        trainName,
        fromCode,
        fromName,
        toCode,
        toName,
        depTime,
        arrTime,
        travelClass: avail.travel_class,
        quota,
        chartStatus: 'CHART PREPARED',
        bookingStatus,
        currentStatus,
        coach: isWaitlist ? 'WL' : coach,
        berth: isWaitlist ? 'WL' : String(berthNum),
        berthType: isWaitlist ? 'Waitlisted' : assignedBerthType,
        totalFare,
        gst,
        reservationFee,
        superfastCharge,
        tatkalCharge,
        baseFare,
        passenger: {
          name: passengerName.trim(),
          age: Number(passengerAge),
          gender: passengerGender,
          berthPreference,
          irctcId: irctcId.trim(),
          mobile: mobile.trim(),
        },
      };

      // Persist to localStorage
      try {
        const stored = JSON.parse(localStorage.getItem('smartrail_booked_tickets') || '[]');
        stored.unshift(ticket);
        localStorage.setItem('smartrail_booked_tickets', JSON.stringify(stored));
      } catch (err) {
        console.error('Failed to store ticket in localStorage:', err);
      }

      setIsProcessing(false);
      onBookSuccess(ticket);
    }, 700);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={{
          padding: '18px 24px',
          background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95))',
          borderBottom: '1px solid rgba(148, 163, 184, 0.15)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '20px' }}>🎟️</span>
              <h2 style={{ fontSize: '18px', fontWeight: 800, color: '#fff' }}>
                IRCTC Passenger Booking
              </h2>
              <span className="station-code-badge" style={{ fontSize: '10px' }}>
                {avail.travel_class} • {quota}
              </span>
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-tertiary)', marginTop: '2px' }}>
              {trainNumber} — {trainName} ({fromCode} ➔ {toCode})
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              fontSize: '20px',
              cursor: 'pointer',
              padding: '4px',
            }}
          >
            ✕
          </button>
        </div>

        {/* Content Body */}
        <form onSubmit={handleConfirm} style={{ padding: '24px' }}>
          {formError && (
            <div style={{
              padding: '10px 14px',
              background: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid var(--danger)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--danger-light)',
              fontSize: '13px',
              marginBottom: '16px',
            }}>
              ⚠️ {formError}
            </div>
          )}

          {/* Passenger Details Grid */}
          <div style={{
            background: 'rgba(15, 23, 42, 0.6)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '16px',
            marginBottom: '20px',
          }}>
            <h3 style={{ fontSize: '13px', fontWeight: 700, color: 'var(--accent-cyan)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              👤 Passenger 1 (Primary)
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px', fontWeight: 600 }}>
                  Full Name (as per Govt ID) *
                </label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g. Rahul Sharma"
                  value={passengerName}
                  onChange={(e) => setPassengerName(e.target.value)}
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px', fontWeight: 600 }}>
                  Age *
                </label>
                <input
                  type="number"
                  className="input"
                  min="1"
                  max="120"
                  value={passengerAge}
                  onChange={(e) => setPassengerAge(e.target.value)}
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px', fontWeight: 600 }}>
                  Gender *
                </label>
                <select
                  className="input"
                  value={passengerGender}
                  onChange={(e) => setPassengerGender(e.target.value)}
                >
                  <option value="M">Male (M)</option>
                  <option value="F">Female (F)</option>
                  <option value="T">Transgender (T)</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px', fontWeight: 600 }}>
                  Berth Preference
                </label>
                <select
                  className="input"
                  value={berthPreference}
                  onChange={(e) => setBerthPreference(e.target.value)}
                >
                  <option value="LB">Lower Berth [LB]</option>
                  <option value="MB">Middle Berth [MB]</option>
                  <option value="UB">Upper Berth [UB]</option>
                  <option value="SL">Side Lower [SL]</option>
                  <option value="SU">Side Upper [SU]</option>
                  <option value="NONE">No Preference</option>
                </select>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '12px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px', fontWeight: 600 }}>
                  IRCTC User ID *
                </label>
                <input
                  type="text"
                  className="input"
                  value={irctcId}
                  onChange={(e) => setIrctcId(e.target.value)}
                  placeholder="IRCTC username"
                  required
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px', fontWeight: 600 }}>
                  Mobile (For SMS & Live Status)
                </label>
                <input
                  type="tel"
                  className="input"
                  value={mobile}
                  onChange={(e) => setMobile(e.target.value)}
                  placeholder="10-digit mobile"
                />
              </div>
            </div>
          </div>

          {/* Fare Breakdown Card */}
          <div style={{
            background: 'rgba(30, 41, 59, 0.4)',
            border: '1px solid rgba(148, 163, 184, 0.1)',
            borderRadius: 'var(--radius-md)',
            padding: '16px',
            marginBottom: '20px',
          }}>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '10px', textTransform: 'uppercase' }}>
              🧾 Official Fare Breakdown
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                <span>Base Fare ({avail.travel_class})</span>
                <span>₹{baseFare}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                <span>Reservation Charge</span>
                <span>₹{reservationFee}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                <span>Superfast Surcharge</span>
                <span>₹{superfastCharge}</span>
              </div>
              {quota === 'TQ' && (
                <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--warning-light)' }}>
                  <span>Tatkal Premium Quota Fee</span>
                  <span>₹{tatkalCharge}</span>
                </div>
              )}
              {isAC && (
                <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                  <span>GST (5% on AC classes)</span>
                  <span>₹{gst}</span>
                </div>
              )}
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                paddingTop: '8px',
                marginTop: '4px',
                borderTop: '1px dashed rgba(148, 163, 184, 0.2)',
                fontSize: '15px',
                fontWeight: 800,
                color: '#fff',
              }}>
                <span>Total Amount</span>
                <span style={{ color: 'var(--accent-cyan)' }}>₹{totalFare}</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <button
              type="button"
              className="btn btn-ghost"
              onClick={onClose}
              disabled={isProcessing}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isProcessing}
              style={{ minWidth: '180px' }}
            >
              {isProcessing ? '⚡ Generating PNR...' : `Book Ticket • ₹${totalFare}`}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
