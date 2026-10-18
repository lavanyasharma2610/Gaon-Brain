import React from 'react';

interface StripProps {
  samasya: string;
  jawab: string;
  asar: string;
  accentColor?: string; // e.g. '#BDE5CC' | '#D5CBF0' | '#FFD3B5' | '#BFE0F5'
}

export const Strip3Line: React.FC<StripProps> = ({ samasya, jawab, asar, accentColor = '#FFEDA8' }) => {
  return (
    <div
      style={{
        border: '2px solid var(--ink)',
        borderRadius: 'var(--radius-sm)',
        backgroundColor: accentColor,
        padding: '14px 18px',
        marginBottom: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        fontSize: '16px'
      }}
    >
      <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
        <span
          style={{
            fontWeight: 700,
            color: '#991B1B',
            minWidth: '85px',
            fontSize: '15px',
            textTransform: 'uppercase'
          }}
        >
          समस्या:
        </span>
        <span style={{ color: 'var(--ink)' }}>{samasya}</span>
      </div>

      <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
        <span
          style={{
            fontWeight: 700,
            color: '#166534',
            minWidth: '85px',
            fontSize: '15px',
            textTransform: 'uppercase'
          }}
        >
          हमारा जवाब:
        </span>
        <span style={{ color: 'var(--ink)' }}>{jawab}</span>
      </div>

      <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
        <span
          style={{
            fontWeight: 700,
            color: '#1E40AF',
            minWidth: '85px',
            fontSize: '15px',
            textTransform: 'uppercase'
          }}
        >
          आज का असर:
        </span>
        <span style={{ fontWeight: 600, color: 'var(--ink)' }}>{asar}</span>
      </div>
    </div>
  );
};
