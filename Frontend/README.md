# DemandNet Frontend Dashboard

The geospatial intelligence command center and primary healthcare facility community portal for DemandNet.

## Tech Stack
* **Framework:** Vue 3 + TypeScript + Vite
* **Styling:** TailwindCSS + Radix Vue
* **Mapping:** Leaflet & Mapbox GL
* **Charts:** Apache ECharts (`vue-echarts`)
* **State Management:** Pinia
* **Icons:** Lucide Vue Next

## Getting Started

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
```bash
copy .env.example .env    # Windows
# cp .env.example .env    # Linux/macOS
```

Configure `VITE_API_BASE_URL` (default: `http://localhost:8000`) and optional `VITE_MAPBOX_ACCESS_TOKEN`.

### 3. Run Development Server
```bash
npm run dev
```
The application will launch at `http://localhost:5173`.

### 4. Build for Production
```bash
npm run build
```
