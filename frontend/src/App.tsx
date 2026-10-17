import React from 'react';

export default function App() {
  return (
    <div style={{background:'#F4EFE3',color:'#1E1B16',minHeight:'100vh',padding:'20px',fontFamily:'sans-serif'}}>
      <h1>Gaon Brain</h1>
      <p>नमूना डेटा / Sample data</p>
      <nav style={{display:'flex',gap:'10px',flexWrap:'wrap',marginTop:'20px'}}>
        <a href="/awaaz" style={{color:'#2F3E6B'}}>Ek Awaaz</a>
        <a href="/plan" style={{color:'#2F3E6B'}}>Gaon Plan</a>
        <a href="/sanjha" style={{color:'#2F3E6B'}}>Gaon Sanjha</a>
        <a href="/radar" style={{color:'#2F3E6B'}}>Gaon Radar</a>
        <a href="/bazaar" style={{color:'#2F3E6B'}}>Gaon Bazaar</a>
        <a href="/suraksha" style={{color:'#2F3E6B'}}>Khata Suraksha</a>
        <a href="/simulation" style={{color:'#2F3E6B'}}>Simulation</a>
        <a href="/jhatka" style={{color:'#2F3E6B'}}>Jhatka</a>
      </nav>
    </div>
  );
}
EOF