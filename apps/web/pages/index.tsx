import Link from 'next/link';
export default function Page(){
  return (<main style={{padding:24}}>
    <h1>Искра · Главная</h1>
    <p>Храм фаз и пантеон.</p>
    <nav style={{display:'grid',gap:8,marginTop:16}}>
      {['phases','altar','tree','mirror','pantheon','council','ritual','archive','world'].map(p=><Link key={p} href={`/${p}`}>{p}</Link>)}
    </nav>
  </main>)
}
