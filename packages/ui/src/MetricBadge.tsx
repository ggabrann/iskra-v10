import React from 'react'; import { tokens } from './tokens';
export const MetricBadge:React.FC<{name:string;value:number}> = ({name,value}) => (
  <span style={{display:'inline-block',padding:'4px 8px',borderRadius:999,background:'rgba(255,255,255,.08)',color:tokens.colors.text,marginRight:8}}>
    {name}: {value.toFixed(2)}
  </span>
);
