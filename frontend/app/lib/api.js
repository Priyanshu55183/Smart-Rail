/**
 * SmartRail API Client
 * ====================
 * Centralized API calls to the FastAPI backend.
 * Uses the Next.js rewrite proxy in development,
 * falls back to NEXT_PUBLIC_API_URL in production.
 */

function getApiBase() {
  if (typeof window !== 'undefined') {
    // In browser: use relative path to route through Next.js proxy
    return '';
  }
  return process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000';
}

/**
 * Generic fetch wrapper with error handling.
 */
async function apiFetch(endpoint, options = {}) {
  const base = getApiBase();
  const url = `${base}/api${endpoint}`;
  
  try {
    const res = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `API error: ${res.status}`);
    }

    return await res.json();
  } catch (err) {
    if (err.message.includes('fetch failed') || err.message.includes('ECONNREFUSED')) {
      throw new Error('Cannot connect to SmartRail API. Is the backend running?');
    }
    throw err;
  }
}

/**
 * Search stations by name, code, or city.
 * GET /api/stations/search?q=bang&limit=8
 */
export async function searchStations(query, limit = 8) {
  if (!query || query.trim().length < 1) return { stations: [], count: 0 };
  const params = new URLSearchParams({ q: query.trim(), limit: String(limit) });
  return apiFetch(`/stations/search?${params}`);
}

/**
 * Get station details by code.
 * GET /api/stations/{code}
 */
export async function getStation(code) {
  return apiFetch(`/stations/${code}`);
}

/**
 * Search for journeys (the main AI endpoint).
 * GET /api/journeys?from=SBC&to=NDLS&date=2026-09-10&max_connections=2
 */
export async function searchJourneys({
  from, to, date, departureTime, maxConnections = 2,
  minLayover = 30, maxLayover = 360, sortBy = 'best',
}) {
  const params = new URLSearchParams({
    from,
    to,
    date,
    max_connections: String(maxConnections),
    min_layover: String(minLayover),
    max_layover: String(maxLayover),
    sort_by: sortBy,
  });
  if (departureTime) params.set('departure_time', departureTime);
  return apiFetch(`/journeys?${params}`);
}

/**
 * Search direct trains between two stations.
 * GET /api/trains/direct?from=SBC&to=NDLS&date=2026-09-10
 */
export async function searchDirectTrains(from, to, date) {
  const params = new URLSearchParams({ from, to, date });
  return apiFetch(`/trains/direct?${params}`);
}

/**
 * Get train details by number.
 * GET /api/trains/{train_number}
 */
export async function getTrain(trainNumber) {
  return apiFetch(`/trains/${trainNumber}`);
}

/**
 * Get full train schedule (all stops).
 * GET /api/trains/{train_number}/schedule
 */
export async function getTrainSchedule(trainNumber) {
  return apiFetch(`/trains/${trainNumber}/schedule`);
}

/**
 * Check API health.
 * GET /api/health
 */
export async function getHealth() {
  return apiFetch('/health');
}
