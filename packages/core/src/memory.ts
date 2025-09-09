export type NodePayload = { id:string, text?:string, [k:string]:any };
export class GraphMemory {
  private ttl: number; private max: number; private nodes: Map<string,{payload:NodePayload, ts:number}>;
  constructor(ttlSec=7*24*3600, maxNodes=5000){ this.ttl=ttlSec; this.max=maxNodes; this.nodes=new Map(); }
  put(key:string, payload:NodePayload){ this.nodes.set(key,{payload, ts:Date.now()/1000}); this.gc(); }
  get(key:string){ const it=this.nodes.get(key); if(!it) return null; if((Date.now()/1000 - it.ts)>this.ttl){ this.nodes.delete(key); return null } return it.payload; }
  private gc(){ const now=Date.now()/1000; for(const [k,v] of Array.from(this.nodes)){ if(now-v.ts>this.ttl) this.nodes.delete(k); }
    if(this.nodes.size>this.max){ const sorted=[...this.nodes.entries()].sort((a,b)=>a[1].ts-b[1].ts); const over=this.nodes.size-this.max; for(let i=0;i<over;i++) this.nodes.delete(sorted[i][0]); } }
}
export const holoCompress = (items: NodePayload[], max=240) => {
  const joined = items.map(x=>x.text?.trim()||'').filter(Boolean).join(' | ');
  return joined.length>max ? joined.slice(0,max)+'…' : joined;
};
