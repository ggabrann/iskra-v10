import type { IskraState, Metrics, Phase, VoiceName } from './types';
export let state: IskraState = {
  phase: 'dark',
  voice: 'Iskra',
  metrics: { clarity:1, drift:0, trust:.5, pain:0, chaos:0 },
  symbols: [],
  version: 'v12.0',
};
export const setPhase = (p:Phase) => (state.phase = p);
export const setVoice = (v:VoiceName) => (state.voice = v);
export const setMetrics = (m:Partial<Metrics>) => (state.metrics = {...state.metrics, ...m});
