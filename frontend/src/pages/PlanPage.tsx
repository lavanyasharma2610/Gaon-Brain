import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { PlanResult, Plot } from '../types';
import { Strip3Line } from '../components/Strip3Line';

const CROP_COLORS: Record<string, { bg: string; border: string; nameHi: string; nameEn: string }> = {
  wheat: { bg: '#FDE047', border: '#CA8A04', nameHi: 'गेहूं (Wheat)', nameEn: 'Wheat' },
  potato: { bg: '#FBCFE8', border: '#DB2777', nameHi: 'आलू (Potato)', nameEn: 'Potato' },
  rice: { bg: '#86EFAC', border: '#16A34A', nameHi: 'धान (Paddy)', nameEn: 'Paddy' },
  mustard: { bg: '#FEF08A', border: '#EAB308', nameHi: 'सरसों (Mustard)', nameEn: 'Mustard' },
  chana: { bg: '#FED7AA', border: '#EA580C', nameHi: 'चना (Gram)', nameEn: 'Gram' },
};

export const PlanPage: React.FC<{ lang: 'hi' | 'en' }> = ({ lang }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [planData, setPlanData] = useState<PlanResult | null>(null);
  const [selectedPlot, setSelectedPlot] = useState<Plot | null>(null);
  const [applying, setApplying] = useState(false);
  const [applySuccess, setApplySuccess] = useState<string | null>(null);

  // Adoption & Cobweb Simulation state
  const [adoptionAlpha, setAdoptionAlpha] = useState(60);
  const [cobwebData, setCobwebData] = useState<any>(null);

  const fetchPlan = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.runPlan();
      setPlanData(data);
      if (data.plots && data.plots.length > 0) {
        setSelectedPlot(data.plots[0]);
      }
      // Load cobweb simulation data
      const cobweb = await api.getCobweb('potato', 6);
      setCobwebData(cobweb);
    } catch (err: any) {
      setError(err.message || 'गाँव प्लान लोड करने में त्रुटि (Failed to load plan)');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlan();
  }, []);

  const handleApply = async () => {
    setApplying(true);
    try {
      const res = await api.applyPlan();
      setApplySuccess(
        lang === 'hi'
          ? 'गाँव योजना सफलतापूर्वक लागू हो गई! सभी खेतों की बुवाई व कटाई हफ़्ते अपडेट हो गए।'
          : 'Village plan successfully applied! All plot sowing & harvest weeks locked.'
      );
      if (res.plan) {
        setPlanData(res.plan);
      }
      setTimeout(() => setApplySuccess(null), 6000);
    } catch (err: any) {
      alert('Error applying plan: ' + err.message);
    } finally {
      setApplying(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-block">
        <div style={{ fontSize: '36px' }}>🌱</div>
        <p>{lang === 'hi' ? 'ग्लट गार्ड योजना की गणना हो रही है...' : 'Calculating Glut Guard optimal plan...'}</p>
      </div>
    );
  }

  if (error || !planData) {
    return (
      <div className="error-banner">
        <h3>{lang === 'hi' ? 'डेटा लोड करने में समस्या' : 'Error loading plan data'}</h3>
        <p>{error}</p>
        <button onClick={fetchPlan} className="flat-btn flat-btn-primary" style={{ width: 'fit-content' }}>
          🔄 {lang === 'hi' ? 'पुनः प्रयास करें (Retry)' : 'Retry'}
        </button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
      {/* 3-Line Strip */}
      <Strip3Line
        accentColor="var(--mint)"
        samasya={
          lang === 'hi'
            ? 'गाँव में हर कोई पिछले साल के भाव देखकर वही फसल बो देता है, जिससे बंपर आवक पर भाव धड़ाम गिर जाते हैं।'
            : 'Every farmer plants based on last year’s prices, triggering village over-supply and price crashes.'
        }
        jawab={
          lang === 'hi'
            ? 'ग्लट गार्ड सभी 30 खेतों की फसलों और कटाई हफ़्तों को ऐसे फैलाता है कि किसी भी किसान का लाभ बेसलाइन से कम न हो।'
            : 'Glut Guard staggers crops and harvest weeks so no farmer is ever worse off than their own baseline.'
        }
        asar={
          lang === 'hi'
            ? `किसानों का नुकसान = 0 | अतिरिक्त गाँव लाभ: +₹${planData.profit_diff.toLocaleString('en-IN')} | अधिकतम फसल निर्भरता 100% से घटकर ${(planData.max_crop_share_after * 100).toFixed(0)}% हुई।`
            : `Farmers worse off = 0 | Extra Village Profit: +₹${planData.profit_diff.toLocaleString('en-IN')} | Max crop dependency dropped to ${(planData.max_crop_share_after * 100).toFixed(0)}%.`
        }
      />

      {/* Success Banner */}
      {applySuccess && (
        <div
          className="flat-panel-mint"
          style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}
        >
          <span style={{ fontSize: '24px' }}>✅</span>
          <span style={{ fontWeight: 700 }}>{applySuccess}</span>
        </div>
      )}

      {/* Key Metrics Strip */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '14px',
          marginBottom: '20px',
        }}
      >
        <div className="flat-panel" style={{ backgroundColor: '#FFFFFF' }}>
          <div style={{ fontSize: '14px', fontWeight: 600, color: '#4B5563' }}>
            {lang === 'hi' ? 'किसानों का नुकसान' : 'Farmers Worse Off'}
          </div>
          <div style={{ fontSize: '32px', fontWeight: 800, color: '#166534' }}>
            {planData.farmers_worse_off}
            <span style={{ fontSize: '16px', fontWeight: 600, marginLeft: '6px' }}>
              ({lang === 'hi' ? 'गारंटीड शून्य' : 'Guaranteed 0'})
            </span>
          </div>
        </div>

        <div className="flat-panel" style={{ backgroundColor: 'var(--mint)' }}>
          <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--ink)' }}>
            {lang === 'hi' ? 'गाँव का कुल लाभ (योजना)' : 'Planned Village Profit'}
          </div>
          <div style={{ fontSize: '28px', fontWeight: 800, color: 'var(--ink)' }}>
            ₹{(planData.village_profit_after / 100000).toFixed(2)} {lang === 'hi' ? 'लाख' : 'Lakh'}
          </div>
          <div style={{ fontSize: '13px', fontWeight: 600, color: '#166534' }}>
            +₹{(planData.profit_diff / 1000).toFixed(0)}k {lang === 'hi' ? 'बेसलाइन से अधिक' : 'above baseline'}
          </div>
        </div>

        <div className="flat-panel" style={{ backgroundColor: 'var(--butter)' }}>
          <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--ink)' }}>
            {lang === 'hi' ? 'अधिकतम फसल हिस्सेदारी' : 'Max Crop Share'}
          </div>
          <div style={{ fontSize: '28px', fontWeight: 800, color: 'var(--ink)' }}>
            {(planData.max_crop_share_after * 100).toFixed(0)}%
          </div>
          <div style={{ fontSize: '13px', fontWeight: 600, color: '#4B5563' }}>
            {lang === 'hi' ? 'पहले' : 'Before'}: {(planData.max_crop_share_before * 100).toFixed(0)}% (
            {lang === 'hi' ? 'संतुलित' : 'Diversified'})
          </div>
        </div>

        <div
          className="flat-panel"
          style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        >
          <button
            onClick={handleApply}
            disabled={applying}
            className="flat-btn flat-btn-mint"
            style={{ width: '100%', height: '100%', minHeight: '52px', fontSize: '18px' }}
          >
            {applying
              ? lang === 'hi'
                ? 'लागू हो रहा है...'
                : 'Applying...'
              : lang === 'hi'
              ? '⚡ प्लान लगाओ (Apply Plan)'
              : '⚡ Apply Plan to Village'}
          </button>
        </div>
      </div>

      {/* Main Grid: SVG Map on Left + Kyun? Drawer on Right */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1.8fr) minmax(0, 1.2fr)',
          gap: '20px',
          marginBottom: '24px',
        }}
      >
        {/* SVG Cadastral Village Map */}
        <div className="flat-panel" style={{ padding: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: 700 }}>
              🗺️ {lang === 'hi' ? 'शिवपुर राजस्व खेत नक्शा (Village Cadastral Map)' : 'Shivpur Revenue Field Map'}
            </h2>
            <span style={{ fontSize: '13px', fontWeight: 600, color: '#6B7280' }}>
              {lang === 'hi' ? 'खेत पर क्लिक करके "क्यों?" देखें' : 'Click plot to view "Kyun?"'}
            </span>
          </div>

          <div style={{ width: '100%', overflowX: 'auto', backgroundColor: '#FAF6EE', border: '1px solid #D1D5DB', borderRadius: '4px' }}>
            <svg viewBox="0 0 600 390" style={{ width: '100%', height: 'auto', display: 'block' }}>
              {planData.plots.map((plot) => {
                const isSelected = selectedPlot?.id === plot.id;
                const cropMeta = CROP_COLORS[plot.planned_crop] || CROP_COLORS['wheat'];
                const pts = Array.isArray(plot.polygon)
                  ? plot.polygon.map((p) => `${p[0]},${p[1]}`).join(' ')
                  : '10,10 90,10 90,70 10,70';

                // Center of plot for label
                const x0 = plot.polygon?.[0]?.[0] || 20;
                const y0 = plot.polygon?.[0]?.[1] || 20;

                return (
                  <g
                    key={plot.id}
                    onClick={() => setSelectedPlot(plot)}
                    style={{ cursor: 'pointer' }}
                  >
                    <polygon
                      points={pts}
                      fill={cropMeta.bg}
                      stroke={isSelected ? '#000000' : 'var(--ink)'}
                      strokeWidth={isSelected ? '3.5' : '1.5'}
                    />
                    <text
                      x={x0 + 6}
                      y={y0 + 18}
                      fontSize="12"
                      fontWeight="700"
                      fill="var(--ink)"
                    >
                      P{plot.id}: {plot.area_acre}ac
                    </text>
                    <text
                      x={x0 + 6}
                      y={y0 + 34}
                      fontSize="11"
                      fontWeight="600"
                      fill="#374151"
                    >
                      {lang === 'hi' ? cropMeta.nameHi.split(' ')[0] : cropMeta.nameEn} (W{plot.week + 1})
                    </text>
                    <text
                      x={x0 + 6}
                      y={y0 + 50}
                      fontSize="10"
                      fill="#4B5563"
                    >
                      {plot.farmer_name.split(' ')[0]}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Map Legend */}
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '12px',
              marginTop: '12px',
              paddingTop: '10px',
              borderTop: '1px solid #E5E7EB',
            }}
          >
            {Object.entries(CROP_COLORS).map(([c, meta]) => (
              <div key={c} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px' }}>
                <span
                  style={{
                    width: '16px',
                    height: '16px',
                    backgroundColor: meta.bg,
                    border: '1px solid var(--ink)',
                    display: 'inline-block',
                  }}
                />
                <span>{lang === 'hi' ? meta.nameHi : meta.nameEn}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Kyun? Drawer for Selected Plot */}
        <div
          className="flat-panel"
          style={{
            backgroundColor: '#FFFFFF',
            border: '2px solid var(--ink)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
          }}
        >
          <div>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'baseline',
                borderBottom: '2px solid var(--ink)',
                paddingBottom: '10px',
                marginBottom: '14px',
              }}
            >
              <h3 style={{ fontSize: '20px', fontWeight: 800 }}>
                💡 {lang === 'hi' ? 'खेत विवरण व "क्यों?"' : 'Plot Detail & "Kyun?"'}
              </h3>
              <span className="badge" style={{ backgroundColor: 'var(--butter)' }}>
                Plot #{selectedPlot?.id}
              </span>
            </div>

            {selectedPlot ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '15px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #E5E7EB', paddingBottom: '6px' }}>
                  <span style={{ color: '#4B5563' }}>{lang === 'hi' ? 'किसान का नाम' : 'Farmer Name'}:</span>
                  <span style={{ fontWeight: 700 }}>{selectedPlot.farmer_name}</span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #E5E7EB', paddingBottom: '6px' }}>
                  <span style={{ color: '#4B5563' }}>{lang === 'hi' ? 'खेत का रकबा' : 'Area'}:</span>
                  <span style={{ fontWeight: 700 }}>{selectedPlot.area_acre} {lang === 'hi' ? 'एकड़' : 'Acres'}</span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #E5E7EB', paddingBottom: '6px' }}>
                  <span style={{ color: '#4B5563' }}>{lang === 'hi' ? 'मूल पसंद (Baseline)' : 'Original Crop'}:</span>
                  <span style={{ fontWeight: 600 }}>{selectedPlot.baseline_crop}</span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #E5E7EB', paddingBottom: '6px' }}>
                  <span style={{ color: '#4B5563' }}>{lang === 'hi' ? 'सुझाई गई फसल (Plan)' : 'Assigned Crop'}:</span>
                  <span
                    style={{
                      fontWeight: 700,
                      backgroundColor: CROP_COLORS[selectedPlot.planned_crop]?.bg,
                      padding: '2px 8px',
                      border: '1px solid var(--ink)',
                      borderRadius: '3px',
                    }}
                  >
                    {selectedPlot.planned_crop} (सप्ताह {selectedPlot.week + 1})
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #E5E7EB', paddingBottom: '6px' }}>
                  <span style={{ color: '#4B5563' }}>{lang === 'hi' ? 'प्रत्याशित लाभ vs बेसलाइन' : 'Profit vs Baseline'}:</span>
                  <span style={{ fontWeight: 700, color: '#166534' }}>
                    ₹{selectedPlot.profit?.toLocaleString('en-IN')} (+₹{selectedPlot.profit_gain?.toLocaleString('en-IN')})
                  </span>
                </div>

                {/* Kyun? Explanation Box */}
                <div
                  className="flat-panel-mint"
                  style={{ marginTop: '10px', padding: '14px', borderRadius: '4px' }}
                >
                  <div style={{ fontWeight: 800, marginBottom: '6px', fontSize: '16px' }}>
                    🤔 {lang === 'hi' ? 'ग्लट गार्ड का "क्यों?"' : 'Why this recommendation?'}
                  </div>
                  <p style={{ fontSize: '15px', lineHeight: 1.4, color: 'var(--ink)' }}>
                    {lang === 'hi' ? selectedPlot.kyun_hi : selectedPlot.kyun_en}
                  </p>
                </div>
              </div>
            ) : (
              <p>{lang === 'hi' ? 'खेत का चयन करें' : 'Select a plot on map'}</p>
            )}
          </div>

          <div style={{ marginTop: '16px', paddingTop: '10px', borderTop: '1px solid #E5E7EB', fontSize: '13px', color: '#6B7280' }}>
            ℹ️ {lang === 'hi' ? 'फ्लोर चेक: बेसलाइन से ₹1 का भी नुकसान वर्जित है।' : 'Floor check: Loss below baseline is mathematically prevented.'}
          </div>
        </div>
      </div>

      {/* Crop Share Bars Before vs After */}
      <div className="flat-panel" style={{ marginBottom: '24px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: 800, marginBottom: '14px' }}>
          📊 {lang === 'hi' ? 'फसल हिस्सेदारी तुलना: पहले vs योजना के बाद' : 'Crop Acreage Share: Before vs After Glut Guard'}
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {Object.entries(planData.crop_distribution_after).map(([crop, afterArea]) => {
            const beforeArea = planData.crop_distribution_before[crop] || 0;
            const totalArea = Object.values(planData.crop_distribution_after).reduce((a, b) => a + b, 0) || 1;
            const beforePct = Math.round((beforeArea / totalArea) * 100);
            const afterPct = Math.round((afterArea / totalArea) * 100);
            const meta = CROP_COLORS[crop] || CROP_COLORS['wheat'];

            return (
              <div key={crop} style={{ fontSize: '15px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 700 }}>{lang === 'hi' ? meta.nameHi : meta.nameEn}</span>
                  <span style={{ color: '#4B5563' }}>
                    {lang === 'hi' ? 'पहले' : 'Before'}: {beforeArea}ac ({beforePct}%) ➔{' '}
                    <strong>
                      {afterArea}ac ({afterPct}%)
                    </strong>
                  </span>
                </div>
                <div style={{ display: 'flex', height: '22px', border: '1.5px solid var(--ink)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div
                    style={{
                      width: `${afterPct}%`,
                      backgroundColor: meta.bg,
                      transition: 'width 300ms ease',
                    }}
                  />
                  <div style={{ width: `${100 - afterPct}%`, backgroundColor: '#F3F4F6' }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Adoption Slider & Interactive Cobweb Boom-Bust Chart */}
      <div className="flat-panel" style={{ backgroundColor: '#FFFFFF', border: '2px solid var(--ink)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '14px' }}>
          <div>
            <h3 style={{ fontSize: '20px', fontWeight: 800 }}>
              📈 {lang === 'hi' ? 'एडॉप्शन प्रभाव व कॉबवेब चक्र (Adoption Slider & Cobweb Oscillation)' : 'Adoption Sweep & Cobweb Chart'}
            </h3>
            <p style={{ fontSize: '14px', color: '#4B5563' }}>
              {lang === 'hi'
                ? 'स्लाइडर हिलाकर देखें: जितने अधिक किसान जुड़ेंगे, बूम-बस्ट मूल्य चक्र उतना ही शांत होगा।'
                : 'Move slider: higher village coordination dampens price shocks and eliminates gluts.'}
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontWeight: 700, fontSize: '18px' }}>
              {lang === 'hi' ? 'गाँव सहभागिता:' : 'Adoption:'} {adoptionAlpha}%
            </span>
            <input
              type="range"
              min="0"
              max="100"
              step="10"
              value={adoptionAlpha}
              onChange={(e) => setAdoptionAlpha(Number(e.target.value))}
              style={{ width: '160px', accentColor: 'var(--ink)' }}
            />
          </div>
        </div>

        {/* SVG Cobweb Chart */}
        {cobwebData && (
          <div style={{ padding: '12px', backgroundColor: '#FAF6EE', border: '1px solid #E5E7EB', borderRadius: '4px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
              <div style={{ display: 'flex', gap: '16px' }}>
                <span style={{ color: '#DC2626' }}>● {lang === 'hi' ? 'बिना योजना (Uncoordinated Boom-Bust)' : 'Without Guard (Boom-Bust)'}</span>
                <span style={{ color: '#16A34A' }}>● {lang === 'hi' ? 'ग्लट गार्ड के साथ (Coordinated Stable)' : 'With Glut Guard (Stable)'}</span>
              </div>
              <span className="badge" style={{ backgroundColor: 'var(--mint)' }}>
                {lang === 'hi' ? 'मूल्य अस्थिरता में' : 'Volatility Reduction'}: {cobwebData.volatility_reduction_pct}% {lang === 'hi' ? 'कमी' : 'Drop'}
              </span>
            </div>

            <svg viewBox="0 0 700 200" style={{ width: '100%', height: 'auto', display: 'block' }}>
              {/* Axes */}
              <line x1="40" y1="20" x2="40" y2="170" stroke="var(--ink)" strokeWidth="1.5" />
              <line x1="40" y1="170" x2="680" y2="170" stroke="var(--ink)" strokeWidth="1.5" />

              {/* Grid lines & labels */}
              {[40, 80, 120, 160].map((y, idx) => (
                <g key={y}>
                  <line x1="40" y1={y} x2="680" y2={y} stroke="#E5E7EB" strokeDasharray="3 3" />
                  <text x="5" y={y + 4} fontSize="10" fill="#6B7280">
                    ₹{20 - idx * 4}
                  </text>
                </g>
              ))}

              {/* Uncoordinated Line (Red zigzag) */}
              <polyline
                fill="none"
                stroke="#DC2626"
                strokeWidth="2.5"
                points={cobwebData.uncoordinated
                  .map((pt: any, i: number) => {
                    const x = 70 + i * 110;
                    const y = 170 - (pt.price / 25) * 140;
                    return `${x},${y}`;
                  })
                  .join(' ')}
              />

              {/* Coordinated Line (Green smooth) */}
              <polyline
                fill="none"
                stroke="#16A34A"
                strokeWidth="2.5"
                points={cobwebData.coordinated
                  .map((pt: any, i: number) => {
                    const x = 70 + i * 110;
                    // Slightly adjust with adoptionAlpha
                    const effectivePrice =
                      pt.price * (adoptionAlpha / 100) +
                      cobwebData.uncoordinated[i].price * (1 - adoptionAlpha / 100);
                    const y = 170 - (effectivePrice / 25) * 140;
                    return `${x},${y}`;
                  })
                  .join(' ')}
              />

              {/* Data Points & Season Labels */}
              {cobwebData.seasons.map((s: number, i: number) => {
                const x = 70 + i * 110;
                const ptU = cobwebData.uncoordinated[i];
                const yU = 170 - (ptU.price / 25) * 140;
                const ptC = cobwebData.coordinated[i];
                const effectivePrice =
                  ptC.price * (adoptionAlpha / 100) +
                  ptU.price * (1 - adoptionAlpha / 100);
                const yC = 170 - (effectivePrice / 25) * 140;

                return (
                  <g key={s}>
                    <circle cx={x} cy={yU} r="4" fill="#DC2626" />
                    <text x={x - 12} y={yU - 8} fontSize="11" fill="#DC2626" fontWeight="700">
                      ₹{ptU.price}
                    </text>

                    <circle cx={x} cy={yC} r="4" fill="#16A34A" />
                    <text x={x - 12} y={yC + 16} fontSize="11" fill="#16A34A" fontWeight="700">
                      ₹{effectivePrice.toFixed(1)}
                    </text>

                    <text x={x - 15} y="186" fontSize="11" fill="var(--ink)" fontWeight="600">
                      {lang === 'hi' ? `सीजन ${s}` : `S${s}`}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>
        )}
      </div>
    </div>
  );
};
