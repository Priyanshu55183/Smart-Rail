# 🚆 SmartRail Frontend

The modern, responsive web application for **SmartRail** — built with [Next.js](https://nextjs.org/) (App Router), React 19, and dark-mode glassmorphism styling.

---

## ✨ Features

- **🔎 Smart Search & Autocomplete**: Debounced station search with IRCTC codes and popular station quick-picks.
- **🗺️ Interactive Journey Cards**: Visual segment timelines showing train numbers, timings, layover durations, and transfer stations.
- **🏷️ Seat Availability & Waitlist Chips**: Color-coded badges displaying real-time class availability (`1A`, `2A`, `3A`, `SL`, `CC`), fares, and waitlist confirmation chances.
- **🛡️ Risk Indicators**: Clear visual indicators (`SAFE`, `MODERATE`, `RISKY`) for connecting transfers.
- **📊 Train Timetables & Schedules**: Dedicated timetable views for individual train routes and intermediate stops.

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Configuration

Create a `.env.local` file in this directory (or rely on the default proxy):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

*Note: Next.js is configured with API rewrites to forward requests from `/api/*` to the FastAPI backend running on port 8000.*

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 📁 Directory Structure

```
frontend/
├── app/
│   ├── components/
│   │   ├── Header.js               # Global navigation bar
│   │   ├── Footer.js               # Application footer
│   │   ├── SearchForm.js           # Station selector & date picker
│   │   ├── StationAutocomplete.js  # Debounced station lookup dropdown
│   │   ├── JourneyCard.js          # Journey result card with timeline & availability
│   │   └── FilterDrawer.js         # Layover time & risk filter panel
│   ├── search/
│   │   └── page.js                 # Search results display page
│   ├── train/[number]/
│   │   └── TrainClient.js          # Individual train timetable page
│   ├── globals.css                 # CSS variables, color tokens, and layout styles
│   ├── layout.js                   # Root HTML structure and font loading
│   └── page.js                     # Homepage landing
├── Dockerfile                      # Production container image build
└── package.json
```
