import { getReflex } from '../dist/validator.js';
console.log('[SMOKE] reflex(sane):', getReflex({clarity:1, drift:0, trust:1, pain:0, chaos:0}));
console.log('[SMOKE] reflex(pain):', getReflex({clarity:1, drift:0, trust:1, pain:.8, chaos:0}));
