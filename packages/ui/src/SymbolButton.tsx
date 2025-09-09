import React from 'react'; import { tokens } from './tokens';
export const SymbolButton:React.FC<{label:string;val:string;onClick?:()=>void}> = ({label,val,onClick}) =>
(<button onClick={onClick} style={{borderRadius:tokens.radius,padding:12,background:tokens.colors.accent,color:'#111',border:'none',cursor:'pointer'}}>
  <span style={{fontSize:20,marginRight:8}}>{val}</span>{label}
</button>);
