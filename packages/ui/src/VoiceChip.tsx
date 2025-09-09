import React from 'react'; import { tokens } from './tokens';
export const VoiceChip:React.FC<{voice:string}> = ({voice}) => (
  <span style={{display:'inline-block',padding:'6px 10px',borderRadius:999,background:tokens.colors.ok,color:'#111',marginRight:8}}>
    {voice}
  </span>
);
