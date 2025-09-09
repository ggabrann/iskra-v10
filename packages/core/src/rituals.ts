export const srez4 = (text:string) => text.toLowerCase().includes('в целом')
  ? ['srez4', text.toLowerCase().replace('в целом','конкретно:')] as const
  : ['srez4', text] as const;

export const srez5 = (token:string) => token.trim().toLowerCase()==='потом'
  ? ['srez5', 'Укажи дату/время или скажи «нет»'] as const
  : ['srez5', token] as const;

export const srez6 = (text:string) => text.toLowerCase().includes('нормально')
  ? ['srez6', text.toLowerCase().replace('нормально','меня устраивает / не устраивает')] as const
  : ['srez6', text] as const;

export const srez7 = (text:string) => text.toLowerCase().includes('не идеально')
  ? ['srez7', 'не идеально. я оставляю шероховатость намеренно.'] as const
  : ['srez7', text] as const;

export const gravitasHold = () => '≈ (молчание как действие: держу форму)';
export const ironicFirstStrike = () => 'Очевидно неверно: поставить сердечко на всё и забыть. (ирония)';
export const rule21 = (messages: any[], n=100)=> messages.slice(-n);
