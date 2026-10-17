import React from 'react';
import { Routes, Route, NavLink } from 'react-router-dom';
import './index.css';

const PageLayout: React.FC<{title?: string; children: React.ReactNode}> = ({title: _title, children}) => (
  <div style={{minHeight:'100vh',padding:'20px',fontFamily:'sans-serif'}}>
    <header style={{marginBottom:'20px',borderBottom:'1px solid var(--river)',paddingBottom:'10px'}}>
      <h1>Gaon Brain</h1>
      <p style={{fontSize:'14px',color:'var(--river)'}}>नमूना डेटा / Sample data · सिमुलेशन</p>
      <nav style={{display:'flex',gap:'10px',flexWrap:'wrap',marginTop:'10px'}}>
        <NavLink to="/awaaz" style={{color:'var(--indigo)'}}>Ek Awaaz</NavLink>
        <NavLink to="/plan" style={{color:'var(--indigo)'}}>Gaon Plan</NavLink>
        <NavLink to="/sanjha" style={{color:'var(--indigo)'}}>Gaon Sanjha</NavLink>
        <NavLink to="/radar" style={{color:'var(--indigo)'}}>Gaon Radar</NavLink>
        <NavLink to="/bazaar" style={{color:'var(--indigo)'}}>Gaon Bazaar</NavLink>
        <NavLink to="/suraksha" style={{color:'var(--indigo)'}}>Khata Suraksha</NavLink>
        <NavLink to="/simulation" style={{color:'var(--indigo)'}}>Simulation</NavLink>
        <NavLink to="/jhatka" style={{color:'var(--indigo)'}}>Jhatka</NavLink>
      </nav>
    </header>
    <main>{children}</main>
  </div>
);

const Awaaz = () => {
  const [transcript, setTranscript] = React.useState('Bolo...');
  const [confirming, setConfirming] = React.useState(false);
  const [sessionId, setSessionId] = React.useState<string|null>(null);
  const [typed, setTyped] = React.useState('');
  const recognitionRef = React.useRef<any>(null);

  React.useEffect(() => {
    if ('webkitSpeechRecognition' in window) {
      recognitionRef.current = new (window as any).webkitSpeechRecognition();
      recognitionRef.current.lang = 'hi-IN';
      recognitionRef.current.onresult = (e: any) => {
        const text = e.results[0][0].transcript;
        setTranscript(text);
        send(text);
      };
    }
  }, []);

  const send = async (text: string) => {
    const r = await fetch('http://127.0.0.1:8000/voice/parse', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text})
    });
    const d = await r.json();
    setTranscript(JSON.stringify(d.parsed, null, 2));
    if (d.status === 'confirm') {
      setConfirming(true);
      setSessionId(d.session_id);
    }
  };

  const confirm = async (ans: string) => {
    if (!sessionId) return;
    const r = await fetch('http://127.0.0.1:8000/voice/confirm', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({session_id: sessionId, answer: ans})
    });
    const d = await r.json();
    setTranscript(d.status);
    setConfirming(false);
    setSessionId(null);
    loadLogbook();
  };

  const loadLogbook = async () => {
    const r = await fetch('http://127.0.0.1:8000/logbook');
    const d = await r.json();
    setTranscript(t => t + '\n\nLogbook entries: ' + d.length);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && typed.trim()) {
      send(typed);
      setTyped('');
    }
  };

  return (
    <PageLayout title="Ek Awaaz">
      <div style={{maxWidth:'600px'}}>
        <button 
          onClick={() => recognitionRef.current?.start()}
          style={{width:120,height:120,borderRadius:'50%',background:'var(--terracotta)',color:'#fff',fontSize:40,border:'none',cursor:'pointer',marginBottom:'20px'}}
        >🎤</button>
        <input
          value={typed}
          onChange={e => setTyped(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ya yahan type karo"
          style={{padding:10,fontSize:16,width:'80%',marginBottom:'10px',display:'block'}}
        />
        <pre style={{background:'#fff',padding:10,border:'1px solid var(--river)',minHeight:100,whiteSpace:'pre-wrap',textAlign:'left'}}>{transcript}</pre>
        {confirming && (
          <div style={{marginTop:10}}>
            <button onClick={() => confirm('haan')} style={{marginRight:10,minHeight:48,padding:'10px 16px',fontSize:18}}>Haan</button>
            <button onClick={() => confirm('nahi')} style={{minHeight:48,padding:'10px 16px',fontSize:18}}>Nahi</button>
          </div>
        )}
      </div>
    </PageLayout>
  );
};

const Plan = () => {
  const [result, setResult] = React.useState<string>('');
  const [showKyun, setShowKyun] = React.useState(false);

  const runPlan = async () => {
    const r = await fetch('http://127.0.0.1:8000/glut/plan', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        plots: [{id: 1, area: 1, crop: 'wheat', week: 0, moved_last: false}],
        crop_params: {wheat: {P0: 2000, yield: 10, cost: 500, weeks: [0,1], demand: 50}}
      })
    });
    const d = await r.json();
    setResult(JSON.stringify(d, null, 2));
    setShowKyun(true);
  };

  return (
    <PageLayout title="Gaon Plan">
      <svg width="600" height="400" style={{border:'1px solid var(--river)',marginBottom:'10px'}}>
        {[[10,10,100,80],[120,20,90,70],[50,100,120,90]].map((p,i) => (
          <g key={i}>
            <rect x={p[0]} y={p[1]} width={p[2]} height={p[3]} fill="#3F5E3A" stroke="#1E1B16" />
            <text x={p[0]+5} y={p[1]+15} fill="#fff">Plot {i+1}</text>
          </g>
        ))}
      </svg>
      <button onClick={runPlan} style={{minHeight:48,padding:'10px 16px',fontSize:18,marginRight:10}}>Run Plan</button>
      <button onClick={() => setShowKyun(true)} style={{minHeight:48,padding:'10px 16px',fontSize:18}}>Kyun?</button>
      {showKyun && (
        <div style={{marginTop:10,border:'1px solid var(--river)',padding:10,whiteSpace:'pre-wrap',background:'#fff'}}>{result}</div>
      )}
    </PageLayout>
  );
};

const Sanjha = () => {
  const [tractor, setTractor] = React.useState<string>('');

  const loadTractor = async () => {
    const r = await fetch('http://127.0.0.1:8000/tractor/schedule', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({requests: [{prev_served_count: 1, want_date: '2026-10-20'}, {prev_served_count: 0, want_date: '2026-10-19'}]})
    });
    const d = await r.json();
    setTractor(JSON.stringify(d, null, 2));
  };

  return (
    <PageLayout title="Gaon Sanjha">
      <h2>Tractor Calendar</h2>
      <button onClick={loadTractor} style={{minHeight:48,padding:'10px 16px',fontSize:18,marginBottom:'10px'}}>Load</button>
      <pre style={{background:'#fff',padding:10,border:'1px solid var(--river)',whiteSpace:'pre-wrap'}}>{tractor}</pre>
      <h2 style={{marginTop:'20px'}}>Bijli Window</h2>
      <p>Best 3-hour window.</p>
      <h2 style={{marginTop:'20px'}}>Sinchai Card</h2>
      <p>Plot: irrigate / wait / skip.</p>
    </PageLayout>
  );
};

const Radar = () => {
  const [result, setResult] = React.useState<string>('');

  const analyze = async () => {
    const r = await fetch('http://127.0.0.1:8000/doctor/analyze', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({condition: 'blight', confidence: 0.8})
    });
    const d = await r.json();
    setResult(JSON.stringify(d, null, 2));
  };

  return (
    <PageLayout title="Gaon Radar">
      <h2>Fasal Doctor</h2>
      <input type="file" accept="image/*" style={{marginBottom:'10px',display:'block'}} />
      <select style={{marginBottom:'10px',padding:'5px',fontSize:16}}>
        <option>Demo: blight</option>
        <option>Demo: rust</option>
      </select>
      <button onClick={analyze} style={{minHeight:48,padding:'10px 16px',fontSize:18}}>Analyze</button>
      <p style={{marginTop:'10px',color:'var(--terracotta)'}}>expert se poochho if confidence {'<'} 0.7</p>
      <h2 style={{marginTop:'20px'}}>Alerts</h2>
      <pre style={{background:'#fff',padding:10,border:'1px solid var(--river)',whiteSpace:'pre-wrap'}}>{result || 'No alerts.'}</pre>
    </PageLayout>
  );
};

const Bazaar = () => {
  const [lots, setLots] = React.useState<string>('');

  const loadLots = async () => {
    const r = await fetch('http://127.0.0.1:8000/bazaar/lots');
    const d = await r.json();
    setLots(JSON.stringify(d, null, 2));
  };

  return (
    <PageLayout title="Gaon Bazaar">
      <h2>Lots</h2>
      <button onClick={loadLots} style={{minHeight:48,padding:'10px 16px',fontSize:18,marginBottom:'10px'}}>Load Lots</button>
      <pre style={{background:'#fff',padding:10,border:'1px solid var(--river)',whiteSpace:'pre-wrap'}}>{lots || 'Bulk lots from staggered harvest.'}</pre>
      <h2 style={{marginTop:'20px'}}>Commitments</h2>
      <p>Buyer commitments.</p>
      <h2 style={{marginTop:'20px'}}>Payments</h2>
      <p>Overdue flags.</p>
      <h2 style={{marginTop:'20px'}}>Buyer Trust</h2>
      <p>Score (n shown, hide if n{'<'}3).</p>
      <h2 style={{marginTop:'20px'}}>Productivity Benchmark</h2>
      <p>Anonymous benchmark (groups {'>='}5).</p>
      <h2 style={{marginTop:'20px'}}>Season Report</h2>
      <p>Per-farmer yield/cost/revenue/profit.</p>
    </PageLayout>
  );
};

const Suraksha = () => {
  const [sinchai, setSinchai] = React.useState<string>('');
  const [pdfStatus, setPdfStatus] = React.useState<string>('');

  const loadSinchai = async () => {
    const r = await fetch('http://127.0.0.1:8000/suraksha/sinchai', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({plot: {}, weather: {rain_mm_48h: 0, prob: 0.2}, crop_interval: 5, days_since: 6, health: 1.0})
    });
    const d = await r.json();
    setSinchai(d.result);
  };

  const generatePdf = async () => {
    setPdfStatus('Generating PDF...');
    const payload = {
      farmer: "राम कुमार",
      policy_no: "PMFBY-2026-001234",
      survey_no: "SRV-5678",
      crop: "गेहूं / Wheat",
      area: 2.5,
      event_type: "अतिवृष्टि / Excess Rainfall",
      event_at: "2026-09-15",
      policy_status: "active (स्वयं-रिपोर्टेड)",
      sowing_record: {sown_on: "2026-06-20", crop: "Wheat", area_acre: 2.5, plot_id: 12},
      photos: [
        {sha256: "a1b2c3d4e5f6...".repeat(4), lat: 28.6139, lon: 77.2090, ts: "2026-09-15T10:30:00Z", weather: {rain_mm_48h: 45, prob: 0.85}},
      ],
      weather_snapshot: {rain_mm_48h: 45, prob: 0.85, temp: 28, humidity: 78},
      purchases: [
        {product: "यूरिया / Urea", mrp: 500, paid: 520, bill_received: false, dealer: "Sharma Agro"},
      ],
      dossier_hash: "deadbeef...".repeat(8),
    };
    try {
      const r = await fetch('http://127.0.0.1:8000/suraksha/claim/pdf', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      if (r.ok) {
        const blob = await r.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'claim_kit.pdf';
        a.click();
        window.URL.revokeObjectURL(url);
        setPdfStatus('PDF downloaded successfully!');
      } else {
        setPdfStatus('Error generating PDF');
      }
    } catch (e: unknown) {
      setPdfStatus('Error: ' + (e as Error).message);
    }
  };

  return (
    <PageLayout title="Khata Suraksha">
      <h2>Bhav Tulna</h2>
      <p>Modal price vs sold rate.</p>
      <h2>Sinchai Card</h2>
      <button onClick={loadSinchai} style={{minHeight:48,padding:'10px 16px',fontSize:18,marginBottom:'10px'}}>Load Sinchai</button>
      <pre style={{background:'#fff',padding:10,border:'1px solid var(--river)',whiteSpace:'pre-wrap'}}>{sinchai || 'Plot: irrigate / wait / skip.'}</pre>
      <h2 style={{marginTop:'20px'}}>Claim Kit</h2>
      <p>72-hour countdown, photos GPS+SHA256, PDF dossier.</p>
      <button onClick={generatePdf} style={{minHeight:48,padding:'10px 16px',fontSize:18,marginBottom:'10px',background:'var(--indigo)'}}>Generate Claim Kit PDF</button>
      {pdfStatus && <p style={{color:'var(--field)',marginTop:'10px'}}>{pdfStatus}</p>}
      <h2 style={{marginTop:'20px'}}>Kharid Check</h2>
      <p>Overcharge, missing bill, complaint draft.</p>
      <h2 style={{marginTop:'20px'}}>Village Mitra</h2>
      <p>4-digit consent code, 24h, audit.</p>
    </PageLayout>
  );
};

const Simulation = () => {
  return (
    <PageLayout title="Simulation">
      <label style={{display:'block',marginBottom:'20px',fontSize:18}}>
        Adoption: 
        <input type="range" min="0" max="100" value="60" style={{marginLeft:'10px',width:'200px'}} /> 
        <span>60%</span>
      </label>
      <canvas width="500" height="200" style={{border:'1px solid var(--river)',background:'#fff'}}></canvas>
    </PageLayout>
  );
};

const Jhatka = () => {
  const [chain, setChain] = React.useState<string>('Radar > Yield > Bazaar > Glut re-plan > Sanjha rebalance');

  const runShock = async (type: string) => {
    setChain('Running ' + type + '...');
    const r = await fetch('http://127.0.0.1:8000/shock', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({type, plot_ids: [1,2,3], magnitude: 1})
    });
    const d = await r.json();
    setChain(d.effects.join(' > '));
  };

  return (
    <PageLayout title="Jhatka Panel">
      <button onClick={() => runShock('disease')} style={{minHeight:48,padding:'10px 16px',fontSize:18,marginRight:10,marginBottom:10}}>Blight on 3 plots</button>
      <button onClick={() => runShock('rain')} style={{minHeight:48,padding:'10px 16px',fontSize:18,marginRight:10,marginBottom:10}}>Heavy rain</button>
      <button onClick={() => runShock('price_drop')} style={{minHeight:48,padding:'10px 16px',fontSize:18,marginBottom:10}}>Price drop</button>
      <div style={{marginTop:'20px',padding:'10px',border:'1px solid var(--river)',background:'#fff',whiteSpace:'pre-wrap'}}>{chain}</div>
    </PageLayout>
  );
};

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/awaaz" replace />} />
      <Route path="/awaaz" element={<Awaaz />} />
      <Route path="/plan" element={<Plan />} />
      <Route path="/sanjha" element={<Sanjha />} />
      <Route path="/radar" element={<Radar />} />
      <Route path="/bazaar" element={<Bazaar />} />
      <Route path="/suraksha" element={<Suraksha />} />
      <Route path="/simulation" element={<Simulation />} />
      <Route path="/jhatka" element={<Jhatka />} />
    </Routes>
  );
}

import { Navigate } from 'react-router-dom';

export default App;