'use client';

import { useState, useEffect, useCallback, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import SearchForm from '../components/SearchForm';
import JourneyCard from '../components/JourneyCard';
import RecommendationCards from '../components/RecommendationCards';
import SplitTicketCard from '../components/SplitTicketCard';
import DateStrip from '../components/DateStrip';
import BookingModal from '../components/BookingModal';
import ETicketModal from '../components/ETicketModal';
import { LoadingState, ErrorState, EmptyState } from '../components/States';
import { searchJourneys, fetchSplitTickets } from '../lib/api';

function SearchContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [results, setResults] = useState(null);
  const [splitData, setSplitData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState('best');

  // Booking Modal & E-Ticket State
  const [bookingState, setBookingState] = useState({
    isOpen: false,
    journey: null,
    segment: null,
    avail: null,
  });
  const [eTicketState, setETicketState] = useState({
    isOpen: false,
    ticket: null,
  });

  const from = searchParams.get('from');
  const to = searchParams.get('to');
  const date = searchParams.get('date');
  const maxConn = searchParams.get('max_connections') || '2';
  const quota = searchParams.get('quota') || 'GN';

  const handleSelectDate = (newDate) => {
    if (!from || !to) return;
    const params = new URLSearchParams({
      from,
      to,
      date: newDate,
      max_connections: String(maxConn),
      quota,
    });
    router.push(`/search?${params.toString()}`);
  };

  const handleOpenBooking = ({ journey, segment, avail }) => {
    setBookingState({
      isOpen: true,
      journey,
      segment,
      avail,
    });
  };

  const handleBookSuccess = (ticket) => {
    setBookingState((prev) => ({ ...prev, isOpen: false }));
    setETicketState({
      isOpen: true,
      ticket,
    });
  };

  const doSearch = useCallback(async () => {
    if (!from || !to || !date) return;

    setLoading(true);
    setError(null);
    setResults(null);
    setSplitData(null);

    try {
      // Parallel fetch: journey search + split-ticket hacker fare analysis
      const [data, splitRes] = await Promise.all([
        searchJourneys({
          from,
          to,
          date,
          maxConnections: parseInt(maxConn),
          sortBy,
        }),
        fetchSplitTickets({
          from,
          to,
          date,
          travelClass: '3A',
        }).catch((e) => {
          console.warn('Split ticket check skipped:', e);
          return null;
        }),
      ]);

      setResults(data);
      if (splitRes && splitRes.options_count > 0) {
        setSplitData(splitRes);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [from, to, date, maxConn, sortBy]);

  useEffect(() => {
    doSearch();
  }, [doSearch]);

  const hasParams = from && to && date;

  return (
    <div style={{ padding: '32px 0' }}>
      <div className="container">
        {/* Compact Search Form at Top */}
        <div className="glass-card" style={{ padding: '20px', marginBottom: '20px' }}>
          <SearchForm compact />
        </div>

        {/* 7-Day Date Ribbon Carousel */}
        {hasParams && (
          <DateStrip currentDate={date} onSelectDate={handleSelectDate} />
        )}

        {/* No params yet */}
        {!hasParams && (
          <div style={{ textAlign: 'center', padding: '60px 20px' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
            <h2 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '8px' }}>
              Start your search
            </h2>
            <p style={{ color: 'var(--text-tertiary)', fontSize: '14px' }}>
              Select source and destination stations to find the best journeys.
            </p>
          </div>
        )}

        {/* Loading */}
        {loading && <LoadingState />}

        {/* Error */}
        {error && <ErrorState message={error} onRetry={doSearch} />}

        {/* Results */}
        {results && !loading && (
          <>
            {/* Results Header */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '20px',
              flexWrap: 'wrap',
              gap: '12px',
            }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <h1 style={{ fontSize: '22px', fontWeight: 800, margin: 0 }}>
                    {from} → {to}
                  </h1>
                  <span className="station-code-badge" style={{ fontSize: '11px' }}>
                    Quota: {quota}
                  </span>
                </div>
                <p style={{ fontSize: '13px', color: 'var(--text-tertiary)', marginTop: '4px' }}>
                  {date} • {results.direct_trains_count} direct, {results.connecting_journeys_count} connecting •{' '}
                  {results.journeys?.length || 0} total results
                </p>
              </div>

              {/* Sort Options */}
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {['best', 'fastest', 'cheapest', 'safest'].map((option) => (
                  <button
                    key={option}
                    className={sortBy === option ? 'btn btn-primary' : 'btn btn-ghost'}
                    onClick={() => setSortBy(option)}
                    style={{ fontSize: '12px', padding: '6px 14px', textTransform: 'capitalize' }}
                  >
                    {option === 'best' ? '⭐' : option === 'fastest' ? '⚡' : option === 'cheapest' ? '💰' : '🛡️'} {option}
                  </button>
                ))}
              </div>
            </div>

            {/* Split-Ticket / Hacker Fare Discovery */}
            {splitData && (
              <SplitTicketCard data={splitData} travelClass="3A" />
            )}

            {/* Recommendation Cards */}
            {results.journeys?.length > 0 && (
              <RecommendationCards
                recommendations={{
                  best_overall: results.best_overall,
                  fastest: results.fastest,
                  cheapest: results.cheapest,
                  safest: results.safest,
                }}
              />
            )}

            {/* Journey List */}
            {results.journeys?.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {results.journeys.map((journey, idx) => (
                  <JourneyCard
                    key={journey.journey_id}
                    journey={journey}
                    index={idx}
                    onBookTicket={handleOpenBooking}
                  />
                ))}
              </div>
            ) : (
              <EmptyState from={from} to={to} />
            )}
          </>
        )}

        {/* Passenger Booking Drawer Modal */}
        {bookingState.isOpen && (
          <BookingModal
            isOpen={bookingState.isOpen}
            onClose={() => setBookingState((prev) => ({ ...prev, isOpen: false }))}
            journey={bookingState.journey}
            segment={bookingState.segment}
            avail={bookingState.avail}
            quota={quota}
            onBookSuccess={handleBookSuccess}
          />
        )}

        {/* Printable Electronic Reservation Slip (ERS) Modal */}
        {eTicketState.isOpen && (
          <ETicketModal
            ticket={eTicketState.ticket}
            onClose={() => setETicketState({ isOpen: false, ticket: null })}
          />
        )}
      </div>
    </div>
  );
}

export default function SearchClient() {
  return (
    <Suspense fallback={<LoadingState message="Loading search..." />}>
      <SearchContent />
    </Suspense>
  );
}
