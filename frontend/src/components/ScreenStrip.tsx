import React from 'react';
import { Strip3Line } from './Strip3Line';

/**
 * Simple wrapper that places a 3‑line strip (Problem / Answer / Impact)
 * at the top of a screen. The caller decides the text.
 */
export const ScreenStrip: React.FC<{ samasya: string; jawab: string; asar: string; accentColor?: string }> = ({ samasya, jawab, asar, accentColor }) => {
  return (
    <Strip3Line
      samasya={samasya}
      jawab={jawab}
      asar={asar}
      accentColor={accentColor ?? '#FFEDA8'}
    />
  );
};

export default ScreenStrip;
