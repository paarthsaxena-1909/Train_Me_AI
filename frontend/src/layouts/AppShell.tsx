import { type ReactNode, useState } from 'react'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { BrandMark } from '../components/BrandMark'
import { Icon } from '../components/Icon'
import { navigationByRole } from '../lib/navigation'
import { useDispatch, useSelector } from 'react-redux'
import type { AppDispatch, RootState } from '../app/store'
import { clearSession } from '../features/auth/authSlice'
import type { Role } from '../lib/types'

export function AppShell({ role, children }: { role: Role; children?: ReactNode }) {
  const navigate = useNavigate()
  const location = useLocation()
  const dispatch = useDispatch<AppDispatch>()
  const account = useSelector((state: RootState) => state.auth.account)
  const [menuOpen, setMenuOpen] = useState(false)
  const firstName = account?.name ?? role
  const roleLabel = role === 'admin' ? 'Admin' : 'Agent'
  const logout = () => { dispatch(clearSession()); navigate('/' + role + '/login') }
  const navClass = (active: boolean) => 'flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm font-medium transition ' + (active ? 'bg-light-purple text-dark' : 'text-muted-text hover:bg-background hover:text-main-text')

  return <div className="min-h-screen bg-background text-main-text lg:flex">
    <div className={menuOpen ? 'fixed inset-0 z-20 bg-dark/25 lg:hidden' : 'hidden'} aria-hidden="true" onClick={() => setMenuOpen(false)} />
    <aside className={menuOpen ? 'translate-x-0 fixed inset-y-0 left-0 z-30 flex w-[260px] flex-col border-r border-border bg-surface px-4 py-5 transition-transform lg:static lg:z-auto lg:w-[245px] lg:translate-x-0 lg:border-r lg:px-4' : 'hidden fixed inset-y-0 left-0 z-30 w-[260px] flex-col border-r border-border bg-surface px-4 py-5 transition-transform lg:static lg:z-auto lg:flex lg:w-[245px] lg:border-r lg:px-4'}>
      <div className="flex items-center justify-between px-2 pb-10"><BrandMark /><button aria-label="Close navigation" className="rounded-lg p-2 text-muted-text hover:bg-background lg:hidden" onClick={() => setMenuOpen(false)} type="button"><Icon name="close" size={18} /></button></div>
      <p className="mb-3 px-3 text-[11px] font-semibold tracking-[0.08em] text-muted-text">WORKSPACE</p>
      <nav aria-label="Workspace" className="space-y-1" data-menu-visible={menuOpen ? 'true' : 'false'}>{navigationByRole[role].map((item) => { const active = item.to === '/' + role ? location.pathname === item.to : location.pathname.startsWith(item.to); return <Link className={navClass(active)} key={item.to} onClick={() => setMenuOpen(false)} to={item.to}><Icon name={item.icon} size={18} /><span>{item.label}</span>{active && <span className="ml-auto h-2 w-2 rounded-full bg-primary" />}</Link> })}</nav>
      <div className="mt-auto hidden border-t border-border pt-4 lg:block"><div className="mb-3 flex items-center gap-3 px-2"><div className="grid h-9 w-9 place-items-center rounded-full bg-blue-accent text-sm font-bold text-dark">{firstName[0]?.toUpperCase()}</div><div className="min-w-0"><p className="truncate text-sm font-semibold">{firstName[0]?.toUpperCase() + firstName.slice(1)}</p><p className="text-xs text-muted-text">{roleLabel}</p></div></div><button className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-muted-text transition hover:bg-pink-accent/40 hover:text-dark" onClick={logout} type="button"><Icon name="logout" size={17} /> Log out</button></div>
    </aside>
    <main className="w-full lg:min-w-0"><header className="flex items-center justify-between gap-4 border-b border-border bg-surface px-5 py-4 lg:px-10"><div className="flex items-center gap-3"><button aria-label="Open navigation" className="rounded-lg p-2 text-muted-text hover:bg-background lg:hidden" onClick={() => setMenuOpen(true)} type="button"><Icon name="menu" size={20} /></button><div><p className="text-xs font-medium text-muted-text">{roleLabel} workspace</p><h1 className="mt-1 text-xl font-semibold tracking-[-0.03em]">{navigationByRole[role].find((item) => location.pathname === item.to || (item.to !== '/' + role && location.pathname.startsWith(item.to)))?.label ?? 'Overview'}</h1></div></div><div className="flex items-center gap-3"><div className="hidden items-center gap-2 rounded-xl border border-border bg-background px-3 py-2 text-sm text-muted-text sm:flex"><Icon name="search" size={17} /><span>Search anything</span><kbd className="ml-8 rounded bg-surface px-1.5 py-0.5 text-[10px] text-muted-text">⌘ K</kbd></div><button aria-label="Notifications" className="relative rounded-xl border border-border bg-surface p-2.5 text-muted-text transition hover:text-primary" type="button"><Icon name="bell" size={18} /><span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-orange" /></button><button aria-label="Log out" className="grid h-10 w-10 place-items-center rounded-full bg-primary text-sm font-bold text-white lg:hidden" onClick={logout} type="button">{firstName[0]?.toUpperCase()}</button></div></header>{children ?? <Outlet />}</main>
  </div>
}
