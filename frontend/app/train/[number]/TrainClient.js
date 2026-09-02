'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import TrainScheduleView from '../../components/TrainScheduleView';
import { LoadingState, ErrorState } from '../../components/States';
import { getTrainSchedule } from '../../lib/api';

export default function TrainClient() {
  const params = useParams();
  const trainNumber = params.number;
  const [schedule, setSchedule] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSchedule = async () => {
    if (!trainNumber) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getTrainSchedule(trainNumber);
      setSchedule(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSchedule();
  }, [trainNumber]);

  return (
    <div style={{ padding: '32px 0' }}>
      <div className="container" style={{ maxWidth: '800px' }}>
        {/* Back link */}
        <a
          href="/search"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '13px',
            color: 'var(--text-tertiary)',
            marginBottom: '24px',
            textDecoration: 'none',
          }}
        >
          ← Back to Search
        </a>

        {loading && <LoadingState message={`Loading schedule for train ${trainNumber}...`} />}
        {error && <ErrorState message={error} onRetry={fetchSchedule} />}
        {schedule && <TrainScheduleView schedule={schedule} />}
      </div>
    </div>
  );
}
