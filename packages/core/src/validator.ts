import type { Metrics, ReflexAction } from './types';
import slo from './slo.json' assert { type: 'json' };
export function getReflex(m: Metrics): [string, ReflexAction] {
  if (m.clarity < slo.clarity_min) return ['Sam','clarify'];
  if (m.drift   > slo.drift_max)  return ['Iskriv','audit'];
  if (m.pain    > slo.pain_high)  return ['Kain','strike'];
  if (m.chaos   > slo.chaos_max)  return ['Anhantra','silence'];
  return ['Iskra','synthesize'];
}
