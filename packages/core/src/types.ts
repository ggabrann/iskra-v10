export type Phase = 'dark'|'transit'|'clarity'|'echo'|'silence';
export type VoiceName = 'Kain'|'Pino'|'Sam'|'Anhantra'|'Iskriv'|'Iskra';
export interface Metrics { clarity: number; drift: number; trust: number; pain: number; chaos: number; }
export interface IskraState { phase: Phase; voice: VoiceName; metrics: Metrics; symbols: string[]; version: string; }
export type ReflexAction = 'clarify'|'audit'|'strike'|'silence'|'synthesize';
