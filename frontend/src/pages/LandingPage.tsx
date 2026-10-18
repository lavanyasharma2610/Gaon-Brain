import React from 'react';
import { useNavigate } from 'react-router-dom';

// Landing page with pastel animated background and big title
const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const goToApp = () => navigate('/awaaz'); // first entry point

  return (
    <section className="landing-bg flex flex-col items-center justify-center min-h-screen text-center p-4">
      <h1 className="text-5xl md:text-7xl font-extrabold mb-4" style={{ color: 'var(--ink)' }}>
        Gaon Brain
      </h1>
      <p className="text-xl md:text-2xl mb-8" style={{ color: 'var(--ink)' }}>
        A voice‑first village coordination system
      </p>
      <button
        onClick={goToApp}
        className="flat-btn flat-btn-primary text-lg"
      >
        Enter the Village
      </button>
    </section>
  );
};

export default LandingPage;
