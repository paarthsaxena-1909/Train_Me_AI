import { FormEvent, useEffect, useMemo, useState } from 'react'

type Role = 'admin' | 'agent'
type Session = { email: string; role: Role }

const adminCredentials: Record<string, string> = {
  'hardik.jain@timesinternet.in': 'hardik',
  'paarth.saxena@timesinternet.in': 'paaarth',
  'udbhav.verma@timesinternet.in': 'udbhav',
}

// Separate maps preserve role isolation for the future backend integration.
const agentCredentials: Record<string, string> = { ...adminCredentials }

const navItems = [
  { label: 'Overview', icon: 'grid' },
  { label: 'Playbooks', icon: 'book' },
  { label: 'Conversations', icon: 'chat' },
  { label: 'Team', icon: 'users' },
]

function Icon({ name, size = 20 }: { name: string; size?: number }) {
  const common = { width: size, height: size, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 1.8, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const }
  if (name === 'search') return <svg {...common}><circle cx="11" cy="11" r="6.5" /><path d="m16 16 4.5 4.5" /></svg>
  if (name === 'bell') return <svg {...common}><path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4" /></svg>
  if (name === 'grid') return <svg {...common}><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><rect x="14" y="14" width="7" height="7" rx="1" /></svg>
  if (name === 'book') return <svg {...common}><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21.5zM4 5.5v16M8 7h8M8 11h8" /></svg>
  if (name === 'chat') return <svg {...common}><path d="M20 11.5a7.5 7.5 0 0 1-8 7.5 8.6 8.6 0 0 1-3.5-.8L4 20l1.3-3.5A7.4 7.4 0 0 1 4 11.5 7.5 7.5 0 0 1 12 4a7.5 7.5 0 0 1 8 7.5Z" /><path d="M8 12h.01M12 12h.01M16 12h.01" /></svg>
  if (name === 'users') return <svg {...common}><path d="M16 20v-1.5a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4V20M9.5 10.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7ZM17 11a3 3 0 1 0-1-5.8M21 20v-1.5a4 4 0 0 0-3-3.87" /></svg>
  if (name === 'logout') return <svg {...common}><path d="M10 17l5-5-5-5M15 12H3M21 19V5a2 2 0 0 0-2-2h-5" /></svg>
  if (name === 'arrow') return <svg {...common}><path d="M5 12h14M13 6l6 6-6 6" /></svg>
  return <svg {...common}><circle cx="12" cy="12" r="8" /></svg>
}

function BrandMark({ light = false }: { light?: boolean }) {
  return <div className={`flex items-center gap-2.5 ${light ? 'text-white' : 'text-dark'}`}><span className="grid h-9 w-9 place-items-center rounded-xl bg-orange text-lg font-black text-white">✦</span><span className="text-[17px] font-bold tracking-[-0.04em]">Train Me<span className={light ? 'text-light-purple' : 'text-primary'}>.</span></span></div>
}

function routeRole(pathname: string): Role { return pathname.startsWith('/admin') ? 'admin' : 'agent' }

function getSession(): Session | null {
  const value = window.localStorage.getItem('train-me-session')
  if (!value) return null
  try { return JSON.parse(value) as Session } catch { return null }
}

function LoginPage({ role, onLogin }: { role: Role; onLogin: (session: Session) => void }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const isAdmin = role === 'admin'
  const credentials = isAdmin ? adminCredentials : agentCredentials

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (credentials[email.trim().toLowerCase()] !== password) {
      setError('That email and password do not match. Try one of the prototype accounts below.')
      return
    }
    onLogin({ email: email.trim().toLowerCase(), role })
  }

  return <main className="min-h-screen bg-background lg:grid lg:grid-cols-[minmax(380px,0.82fr)_1.18fr]">
    <section className="relative hidden overflow-hidden bg-dark p-12 text-white lg:flex lg:flex-col lg:justify-between">
      <BrandMark light />
      <div className="relative z-10 max-w-lg pb-8"><div className="mb-7 flex items-center gap-2 text-sm text-light-purple"><span className="h-2 w-2 rounded-full bg-orange" /> {isAdmin ? 'Admin workspace' : 'Agent workspace'}</div><h1 className="max-w-md text-5xl font-semibold leading-[1.04] tracking-[-0.055em]">Make every conversation a little better.</h1><p className="mt-6 max-w-sm text-[15px] leading-7 text-white/55">A calm command center for the people shaping helpful, human customer experiences.</p></div>
      <div className="absolute -right-24 top-1/4 h-80 w-80 rounded-full border-[38px] border-primary/60" /><div className="absolute -bottom-24 -left-20 h-72 w-72 rounded-full bg-primary/25 blur-2xl" /><p className="text-xs text-white/35">Train Me AI · Internal prototype</p>
    </section>
    <section className="flex min-h-screen items-center justify-center px-6 py-12"><div className="page-enter w-full max-w-[430px]">
      <div className="mb-10 lg:hidden"><BrandMark /></div><div className="mb-8"><p className="mb-3 text-sm font-semibold text-primary">{isAdmin ? 'For administrators' : 'For agents'}</p><h2 className="text-4xl font-semibold tracking-[-0.05em] text-main-text">Welcome back<span className="text-primary">.</span></h2><p className="mt-3 text-[15px] leading-6 text-muted-text">Sign in to continue to your {isAdmin ? 'admin' : 'agent'} workspace.</p></div>
      <form className="space-y-5" onSubmit={submit}><label className="block"><span className="mb-2 block text-sm font-medium text-main-text">Work email</span><input autoComplete="email" className="w-full rounded-2xl border border-border bg-surface px-4 py-3.5 text-main-text shadow-sm transition placeholder:text-muted-text/60 focus:border-primary" onChange={(event) => { setEmail(event.target.value); setError('') }} placeholder="you@timesinternet.in" required type="email" value={email} /></label><label className="block"><span className="mb-2 block text-sm font-medium text-main-text">Password</span><input autoComplete="current-password" className="w-full rounded-2xl border border-border bg-surface px-4 py-3.5 text-main-text shadow-sm transition placeholder:text-muted-text/60 focus:border-primary" onChange={(event) => { setPassword(event.target.value); setError('') }} placeholder="Enter your password" required type="password" value={password} /></label>{error && <p className="rounded-xl bg-pink-accent/60 px-4 py-3 text-sm leading-5 text-dark" role="alert">{error}</p>}<button className="group flex w-full items-center justify-center gap-3 rounded-2xl bg-dark px-5 py-4 font-semibold text-white shadow-lg shadow-dark/15 transition hover:bg-primary" type="submit">Enter workspace <span className="transition-transform group-hover:translate-x-1"><Icon name="arrow" size={18} /></span></button></form>
      <div className="mt-8 rounded-2xl border border-border bg-surface p-4"><p className="mb-3 text-xs font-semibold text-muted-text">Prototype access</p><div className="space-y-2 text-xs text-main-text">{Object.keys(credentials).map((account) => <div className="flex items-center justify-between gap-3" key={account}><span className="truncate">{account}</span><code className="rounded-md bg-light-purple px-2 py-1 text-dark">{credentials[account]}</code></div>)}</div></div><p className="mt-6 text-center text-xs text-muted-text">Need access? Contact your workspace administrator.</p>
    </div></section>
  </main>
}

function Dashboard({ session, onLogout }: { session: Session; onLogout: () => void }) {
  const isAdmin = session.role === 'admin'
  const [active, setActive] = useState('Overview')
  const firstName = session.email.split('.')[0]
  const roleLabel = isAdmin ? 'Admin' : 'Agent'
  const stats = isAdmin ? [{ label: 'Active agents', value: '24', change: '+12%' }, { label: 'Playbooks created', value: '86', change: '+8%' }, { label: 'Avg. quality score', value: '92%', change: '+4%' }] : [{ label: 'My conversations', value: '48', change: '+18%' }, { label: 'Playbooks completed', value: '17', change: '+6%' }, { label: 'Quality score', value: '94%', change: '+3%' }]

  return <div className="min-h-screen bg-background text-main-text lg:flex"><aside className="flex w-full flex-col border-b border-border bg-surface px-5 py-5 lg:fixed lg:inset-y-0 lg:w-[245px] lg:border-b-0 lg:border-r lg:px-4"><div className="px-2 pb-10"><BrandMark /></div><p className="mb-3 px-3 text-[11px] font-semibold text-muted-text">WORKSPACE</p><nav className="space-y-1">{navItems.map((item, index) => <button className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm font-medium transition ${active === item.label ? 'bg-light-purple text-dark' : 'text-muted-text hover:bg-background hover:text-main-text'}`} key={item.label} onClick={() => setActive(item.label)} type="button"><Icon name={item.icon} size={18} /><span>{item.label}</span>{index === 0 && <span className="ml-auto h-2 w-2 rounded-full bg-primary" />}</button>)}</nav><div className="mt-auto hidden border-t border-border pt-4 lg:block"><div className="mb-3 flex items-center gap-3 px-2"><div className="grid h-9 w-9 place-items-center rounded-full bg-blue-accent text-sm font-bold text-dark">{firstName[0].toUpperCase()}</div><div className="min-w-0"><p className="truncate text-sm font-semibold">{firstName[0].toUpperCase() + firstName.slice(1)}</p><p className="text-xs text-muted-text">{roleLabel}</p></div></div><button className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-muted-text transition hover:bg-pink-accent/40 hover:text-dark" onClick={onLogout} type="button"><Icon name="logout" size={17} /> Log out</button></div></aside>
    <main className="w-full lg:ml-[245px]"><header className="flex flex-wrap items-center justify-between gap-4 border-b border-border bg-surface px-6 py-4 lg:px-10"><div><p className="text-xs font-medium text-muted-text">{roleLabel} workspace</p><h1 className="mt-1 text-xl font-semibold tracking-[-0.03em]">{active}</h1></div><div className="flex items-center gap-3"><div className="hidden items-center gap-2 rounded-xl border border-border bg-background px-3 py-2 text-sm text-muted-text sm:flex"><Icon name="search" size={17} /><span>Search anything</span><kbd className="ml-8 rounded bg-surface px-1.5 py-0.5 text-[10px] text-muted-text">⌘ K</kbd></div><button aria-label="Notifications" className="relative rounded-xl border border-border bg-surface p-2.5 text-muted-text transition hover:text-primary" type="button"><Icon name="bell" size={18} /><span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-orange" /></button><button aria-label="Log out" className="grid h-10 w-10 place-items-center rounded-full bg-primary text-sm font-bold text-white lg:hidden" onClick={onLogout} type="button">{firstName[0].toUpperCase()}</button></div></header>
      <div className="page-enter mx-auto max-w-[1200px] px-6 py-8 lg:px-10 lg:py-10"><div className="mb-8 flex flex-wrap items-end justify-between gap-4"><div><p className="mb-2 text-sm font-medium text-primary">Good morning, {firstName}.</p><h2 className="text-3xl font-semibold tracking-[-0.05em]">Here’s your signal for today.</h2></div><button className="rounded-xl bg-dark px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-primary" type="button">+ Create playbook</button></div>
        <div className="grid gap-4 md:grid-cols-3">{stats.map((stat, index) => <section className="rounded-2xl border border-border bg-surface p-5" key={stat.label}><div className="mb-5 flex items-center justify-between"><p className="text-sm text-muted-text">{stat.label}</p><span className={`rounded-full px-2 py-1 text-xs font-semibold ${index === 1 ? 'bg-pink-accent text-dark' : 'bg-light-purple text-dark'}`}>{stat.change}</span></div><p className="text-3xl font-semibold tracking-[-0.05em]">{stat.value}</p><div className="mt-5 h-1.5 overflow-hidden rounded-full bg-background"><div className={`h-full rounded-full ${index === 1 ? 'bg-orange' : 'bg-primary'}`} style={{ width: `${70 + index * 9}%` }} /></div></section>)}</div>
        <div className="mt-8 grid gap-5 xl:grid-cols-[1.35fr_0.65fr]"><section className="rounded-2xl border border-border bg-surface p-6"><div className="mb-8 flex items-start justify-between"><div><h3 className="font-semibold">Activity overview</h3><p className="mt-1 text-sm text-muted-text">Workspace performance over the last 7 days</p></div><button className="text-sm font-medium text-primary" type="button">This week⌄</button></div><div className="flex h-48 items-end gap-3 sm:gap-5">{[42, 58, 46, 74, 62, 88, 72].map((height, index) => <div className="flex h-full flex-1 flex-col items-center justify-end gap-3" key={index}><div className={`w-full rounded-t-lg ${index === 5 ? 'bg-primary' : 'bg-light-purple'}`} style={{ height: `${height}%` }} /><span className="text-xs text-muted-text">{['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][index]}</span></div>)}</div></section><section className="rounded-2xl border border-border bg-dark p-6 text-white"><div className="mb-7 flex items-center justify-between"><h3 className="font-semibold">Quick start</h3><span className="rounded-full bg-orange px-2 py-1 text-[10px] font-semibold text-white">{roleLabel.toUpperCase()}</span></div><p className="max-w-[240px] text-2xl font-semibold leading-tight tracking-[-0.04em]">Keep the team moving forward.</p><p className="mt-3 text-sm leading-6 text-white/55">Pick up where you left off or create something new for your workspace.</p><button className="mt-8 flex items-center gap-2 text-sm font-semibold text-light-purple" type="button">Browse playbooks <Icon name="arrow" size={16} /></button></section></div>
        <section className="mt-5 rounded-2xl border border-border bg-surface p-6"><div className="mb-5 flex items-center justify-between"><div><h3 className="font-semibold">Recent activity</h3><p className="mt-1 text-sm text-muted-text">A pulse of what’s happening in your workspace</p></div><button className="text-sm font-medium text-primary" type="button">View all</button></div><div className="grid gap-3 md:grid-cols-3">{[{ title: 'Brand voice playbook', tag: 'Branding', color: 'bg-pink-accent', time: '12 min ago' }, { title: 'New agent onboarding', tag: 'Front-end', color: 'bg-blue-accent', time: '1 hr ago' }, { title: 'Q3 conversation review', tag: 'Review', color: 'bg-light-purple', time: '3 hrs ago' }].map((item) => <div className="flex items-center gap-3 rounded-xl bg-background p-3.5" key={item.title}><span className={`grid h-9 w-9 shrink-0 place-items-center rounded-lg ${item.color} text-dark`}><Icon name="book" size={17} /></span><div className="min-w-0"><p className="truncate text-sm font-medium">{item.title}</p><p className="mt-1 text-xs text-muted-text">{item.tag} · {item.time}</p></div></div>)}</div></section>
      </div>
    </main>
  </div>
}

function App() {
  const [session, setSession] = useState<Session | null>(() => getSession())
  const [path, setPath] = useState(window.location.pathname)
  const role = routeRole(path)
  const isLogin = path === '/admin/login' || path === '/agent/login'
  const expectedDashboard = session ? `/${session.role}` : `/${role}`

  useEffect(() => { const onPopState = () => setPath(window.location.pathname); window.addEventListener('popstate', onPopState); return () => window.removeEventListener('popstate', onPopState) }, [])
  const navigate = (to: string) => { window.history.pushState({}, '', to); setPath(to) }
  const login = (nextSession: Session) => { window.localStorage.setItem('train-me-session', JSON.stringify(nextSession)); setSession(nextSession); navigate(`/${nextSession.role}`) }
  const logout = () => { window.localStorage.removeItem('train-me-session'); setSession(null); navigate(`/${role}/login`) }
  const destination = useMemo(() => { if (path === '/') return session ? `/${session.role}` : '/agent/login'; if (path === '/admin' || path === '/agent') return session && path !== `/${session.role}` ? `/${session.role}` : path; if (isLogin) return session && session.role !== role ? `/${session.role}` : path; return session ? `/${session.role}` : '/agent/login' }, [isLogin, path, role, session])
  useEffect(() => { if (destination !== path) navigate(destination) }, [destination, path])

  if (session && path === expectedDashboard) return <Dashboard onLogout={logout} session={session} />
  if (isLogin && (!session || session.role === role)) return <LoginPage onLogin={login} role={role} />
  if (session) return <Dashboard onLogout={logout} session={session} />
  return <LoginPage onLogin={login} role={routeRole(destination)} />
}

export default App
