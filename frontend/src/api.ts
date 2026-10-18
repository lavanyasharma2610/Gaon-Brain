const BASE = '';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const fullUrl = url.startsWith('/api') ? url : `/api${url}`;
  try {
    const res = await fetch(fullUrl, options);
    if (!res.ok) {
      // Fallback without /api if running against bare local backend
      if (url.startsWith('/api')) {
        const fallbackUrl = url.replace('/api', '');
        const res2 = await fetch(fallbackUrl, options);
        if (res2.ok) return await res2.json();
      }
      throw new Error(`API Error: ${res.status} ${res.statusText}`);
    }
    return await res.json();
  } catch (err) {
    // If relative path fails in direct vite dev, try localhost:8000
    if (window.location.port === '5173') {
      try {
        const directUrl = `http://127.0.0.1:8000${fullUrl}`;
        const res3 = await fetch(directUrl, options);
        if (res3.ok) return await res3.json();
      } catch (err2) {
        // pass through original error
      }
    }
    throw err;
  }
}

export const api = {
  // Plan
  getGlutState: () => fetchJson<any>('/api/glut/state'),
  runPlan: (payload?: any) => fetchJson<any>('/api/glut/plan', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload || {})
  }),
  applyPlan: (payload?: any) => fetchJson<any>('/api/glut/apply', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload || {})
  }),

  // Voice & Logbook
  parseVoice: (text: string) => fetchJson<any>('/api/voice/parse', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  }),
  confirmVoice: (sessionId: string, answer: string) => fetchJson<any>('/api/voice/confirm', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, answer })
  }),
  getLogbook: () => fetchJson<any[]>('/api/logbook'),

  // Simulation
  getCobweb: (crop: string = 'potato', seasons: number = 6) => fetchJson<any>('/api/sim/cobweb', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ crop, seasons })
  }),
  getAdoptionSweep: () => fetchJson<any[]>('/api/sim/adoption'),

  // Sanjha
  getTractorSchedule: () => fetchJson<any>('/api/tractor/schedule'),
  getPowerWindow: () => fetchJson<any>('/api/power/window'),
  getWaterSlots: () => fetchJson<any[]>('/api/water/slots'),

  // Radar
  getRadarAlerts: () => fetchJson<any[]>('/api/radar/alerts'),
  getRadarHeatmap: () => fetchJson<any[]>('/api/radar/heatmap'),
  submitReport: (payload: any) => fetchJson<any>('/api/radar/report', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  }),
  analyzeDoctor: (condition: string, confidence: number) => fetchJson<any>('/api/doctor/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ condition, confidence })
  }),

  // Shock
  runShock: (type: string, plotIds: number[] = [1, 2, 3]) => fetchJson<any>('/api/shock', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type, plot_ids: plotIds, magnitude: 1.0 })
  })
};
