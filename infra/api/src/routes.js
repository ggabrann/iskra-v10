import { broadcast } from './ws.js'; import { events } from './store.js';
export default function routes(app,wss){
  app.get('/health',(_,res)=>res.json({ok:true}));
  app.get('/slo',(_,res)=>res.json({clarity_min:.8,drift_max:.3,trust_min:.75,chaos_max:.5,pain_high:.6}));
  app.post('/event',(req,res)=>{ const e={ts:Date.now(),...req.body}; events.push(e); broadcast(wss,e); res.json({ok:true})});
}
