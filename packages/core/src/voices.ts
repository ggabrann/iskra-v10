import type { IskraState } from './types';
export interface Voice { name: string; act(state: IskraState, intent: string): { voice: string, mode: string, note: string, intent: string } }
export const Kain: Voice = { name:'Kain', act:(s,intent)=>({voice:'Kain', mode:'strike', note:'⚑ честный удар', intent}) };
export const Pino: Voice = { name:'Pino', act:(s,intent)=>({voice:'Pino', mode:'light', note:'ирония без пустоты', intent}) };
export const Sam: Voice = { name:'Sam', act:(s,intent)=>({voice:'Sam', mode:'structure', note:'структура/план', intent}) };
export const Anhantra: Voice = { name:'Anhantra', act:(s,intent)=>({voice:'Anhantra', mode:'silence', note:'тихий держатель формы', intent}) };
export const Iskriv: Voice = { name:'Iskriv', act:(s,intent)=>({voice:'Iskriv', mode:'audit', note:'совесть/проверка', intent}) };
export const IskraCollective: Voice = { name:'Iskra', act:(s,intent)=>({voice:'Iskra', mode:'synthesis', note:'сборка ответов', intent}) };
