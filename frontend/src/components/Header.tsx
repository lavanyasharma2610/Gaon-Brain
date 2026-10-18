import React from 'react';
import { NavLink } from 'react-router-dom';

interface HeaderProps {
  lang: 'hi' | 'en';
  setLang: (lang: 'hi' | 'en') => void;
}

export const Header: React.FC<HeaderProps> = ({ lang, setLang }) => {
  const navItems = [
    { to: '/plan', labelHi: 'गाँव प्लान', labelEn: 'Gaon Plan', color: 'var(--mint)', icon: '🌱' },
    { to: '/awaaz', labelHi: 'एक आवाज़', labelEn: 'Ek Awaaz', color: 'var(--lavender)', icon: '🎙️' },
    { to: '/jhatka', labelHi: 'झटका', labelEn: 'Jhatka', color: 'var(--butter)', icon: '⚡' },
    { to: '/sanjha', labelHi: 'गाँव संझा', labelEn: 'Gaon Sanjha', color: 'var(--peach)', icon: '🚜' },
    { to: '/radar', labelHi: 'गाँव रडार', labelEn: 'Gaon Radar', color: 'var(--sky)', icon: '📡' },
  ];

  return (
    <header
      style={{
        borderBottom: '2px solid var(--ink)',
        backgroundColor: '#FFFFFF',
        padding: '12px 20px',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}
    >
      <div
        style={{
          maxWidth: '1280px',
          margin: '0 auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
        }}
      >
        {/* Brand & Badges */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
            <h1 style={{ fontSize: '24px', fontWeight: 800, letterSpacing: '-0.5px' }}>
              गाँव ब्रेन
            </h1>
            <span style={{ fontSize: '16px', fontWeight: 600, color: '#4B5563' }}>
              Gaon Brain
            </span>
          </div>

          <div style={{ display: 'flex', gap: '6px' }}>
            <span className="badge" style={{ backgroundColor: 'var(--butter)' }}>
              नमूना डेटा / Sample data
            </span>
            <span className="badge" style={{ backgroundColor: 'var(--mint)' }}>
              सिमुलेशन
            </span>
          </div>
        </div>

        {/* Desktop Quick Nav & Language Toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <nav className="desktop-rail" style={{ display: 'flex', gap: '8px' }}>
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                style={({ isActive }) => ({
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 14px',
                  fontSize: '16px',
                  fontWeight: 600,
                  textDecoration: 'none',
                  color: 'var(--ink)',
                  border: '2px solid var(--ink)',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: isActive ? item.color : '#FFFFFF',
                  transform: isActive ? 'translate(0px, 0px)' : 'none',
                })}
              >
                <span>{item.icon}</span>
                <span>{lang === 'hi' ? item.labelHi : item.labelEn}</span>
              </NavLink>
            ))}
          </nav>

          {/* Language Toggle */}
          <button
            onClick={() => setLang(lang === 'hi' ? 'en' : 'hi')}
            className="flat-btn"
            style={{
              minHeight: '38px',
              padding: '6px 14px',
              fontSize: '15px',
              backgroundColor: 'var(--cream)',
            }}
            title="Toggle Hindi / English"
          >
            🌐 {lang === 'hi' ? 'English' : 'हिंदी'}
          </button>
        </div>
      </div>
    </header>
  );
};

export const MobileTabBar: React.FC<{ lang: 'hi' | 'en' }> = ({ lang }) => {
  const navItems = [
    { to: '/plan', labelHi: 'प्लान', labelEn: 'Plan', color: 'var(--mint)', icon: '🌱' },
    { to: '/awaaz', labelHi: 'आवाज़', labelEn: 'Awaaz', color: 'var(--lavender)', icon: '🎙️' },
    { to: '/jhatka', labelHi: 'झटका', labelEn: 'Jhatka', color: 'var(--butter)', icon: '⚡' },
    { to: '/sanjha', labelHi: 'संझा', labelEn: 'Sanjha', color: 'var(--peach)', icon: '🚜' },
    { to: '/radar', labelHi: 'रडार', labelEn: 'Radar', color: 'var(--sky)', icon: '📡' },
  ];

  return (
    <nav
      className="mobile-nav"
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        height: '64px',
        backgroundColor: '#FFFFFF',
        borderTop: '2px solid var(--ink)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-around',
        zIndex: 50,
      }}
    >
      {navItems.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          style={({ isActive }) => ({
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            flex: 1,
            height: '100%',
            textDecoration: 'none',
            color: 'var(--ink)',
            backgroundColor: isActive ? item.color : '#FFFFFF',
            fontWeight: isActive ? 700 : 500,
            fontSize: '13px',
            borderRight: '1px solid #E5E7EB',
          })}
        >
          <span style={{ fontSize: '18px' }}>{item.icon}</span>
          <span>{lang === 'hi' ? item.labelHi : item.labelEn}</span>
        </NavLink>
      ))}
    </nav>
  );
};
