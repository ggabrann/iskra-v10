export const speak=(text:string)=>{ try{ const u = new SpeechSynthesisUtterance(text); (globalThis as any).speechSynthesis?.speak(u) }catch{} };
