import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { BrandMark } from '../../components/BrandMark'
import type { AppDispatch, RootState } from '../../app/store'
import { loginUser, signupUser } from './authSlice'
import type { Role } from '../../lib/types'

type AuthPageProps = { role: Role; mode?: 'login' | 'signup' }

export function AuthPage({ role, mode = 'login' }: AuthPageProps) {
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate()
  const location = useLocation()
  const auth = useSelector((state: RootState) => state.auth)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [region, setRegion] = useState('')
  const [pincode, setPincode] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const isSignup = mode === 'signup'
  const roleName = role === 'admin' ? 'administrator' : 'agent'

  useEffect(() => {
    setNotice((location.state as { registered?: boolean } | null)?.registered ? 'Account created. Sign in to continue.' : null)
  }, [location.state])

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)
    if (isSignup && role === 'agent' && !/^\d{6}$/.test(pincode)) {
      setFormError('Pincode must be exactly six digits.')
      return
    }
    if (isSignup) {
      const values = role === 'agent'
        ? { email, password, name, region, pincode }
        : { email, password, name }
      const result = await dispatch(signupUser({ role, values }))
      if (signupUser.fulfilled.match(result)) {
        navigate(`/${role}/login`, { replace: true, state: { registered: true } })
      }
      return
    }
    const result = await dispatch(loginUser({ role, email, password }))
    if (loginUser.fulfilled.match(result)) navigate(`/${result.payload.account.role}`, { replace: true })
  }

  const error = formError ?? auth.error
  const pending = auth.status === 'loading'
  return (
    <main className="min-h-screen bg-background lg:grid lg:grid-cols-[minmax(380px,0.82fr)_1.18fr]">
      <section className="relative hidden overflow-hidden bg-dark p-12 text-white lg:flex lg:flex-col lg:justify-between">
        <BrandMark light />
        <div className="relative z-10 max-w-lg pb-8">
          <div className="mb-7 flex items-center gap-2 text-sm text-light-purple"><span className="h-2 w-2 rounded-full bg-orange" />{role === 'admin' ? 'Admin workspace' : 'Agent workspace'}</div>
          <h1 className="max-w-md text-5xl font-semibold leading-[1.04] tracking-[-0.055em]">Make every conversation a little better.</h1>
          <p className="mt-6 max-w-sm text-[15px] leading-7 text-white/55">A calm command center for the people shaping helpful, human customer experiences.</p>
        </div>
        <p className="text-xs text-white/35">Train Me AI · Internal workspace</p>
      </section>
      <section className="flex min-h-screen items-center justify-center px-6 py-12">
        <div className="w-full max-w-[430px]">
          <div className="mb-10 lg:hidden"><BrandMark /></div>
          <div className="mb-8">
            <p className="mb-3 text-sm font-semibold text-primary">For {role === 'admin' ? 'administrators' : 'agents'}</p>
            <h2 className="text-4xl font-semibold tracking-[-0.05em] text-main-text">{isSignup ? <>Create your account<span className="text-primary">.</span></> : <>Welcome back<span className="text-primary">.</span></>}</h2>
            <p className="mt-3 text-[15px] leading-6 text-muted-text">{isSignup ? `Set up your ${roleName} workspace access.` : `Sign in to continue to your ${role} workspace.`}</p>
          </div>
          {notice && <p className="mb-5 rounded-xl border border-primary/20 bg-light-purple px-4 py-3 text-sm text-dark" role="status">{notice}</p>}
          {error && <p className="mb-5 rounded-xl border border-orange/30 bg-pink-accent/50 px-4 py-3 text-sm text-dark" role="alert">{error}</p>}
          <form className="space-y-5" onSubmit={submit}>
            {isSignup && <label className="block"><span className="mb-2 block text-sm font-medium text-main-text">Full name</span><input autoComplete="name" className="w-full rounded-2xl border border-border bg-surface px-4 py-3.5 text-main-text shadow-sm transition placeholder:text-muted-text/60 focus:border-primary" onChange={(event) => setName(event.target.value)} required value={name} /></label>}
            <label className="block"><span className="mb-2 block text-sm font-medium text-main-text">Work email</span><input autoComplete="email" className="w-full rounded-2xl border border-border bg-surface px-4 py-3.5 text-main-text shadow-sm transition placeholder:text-muted-text/60 focus:border-primary" onChange={(event) => setEmail(event.target.value)} placeholder="you@timesinternet.in" required type="email" value={email} /></label>
            <label className="block"><span className="mb-2 block text-sm font-medium text-main-text">Password</span><input autoComplete={isSignup ? 'new-password' : 'current-password'} className="w-full rounded-2xl border border-border bg-surface px-4 py-3.5 text-main-text shadow-sm transition placeholder:text-muted-text/60 focus:border-primary" minLength={1} onChange={(event) => setPassword(event.target.value)} required type="password" value={password} /></label>
            {isSignup && role === 'agent' && <>
              <label className="block"><span className="mb-2 block text-sm font-medium text-main-text">Region <span className="font-normal text-muted-text">(optional)</span></span><input className="w-full rounded-2xl border border-border bg-surface px-4 py-3.5 text-main-text shadow-sm transition placeholder:text-muted-text/60 focus:border-primary" onChange={(event) => setRegion(event.target.value)} value={region} /></label>
              <label className="block"><span className="mb-2 block text-sm font-medium text-main-text">Six-digit pincode</span><input aria-describedby="pincode-help" className="w-full rounded-2xl border border-border bg-surface px-4 py-3.5 text-main-text shadow-sm transition placeholder:text-muted-text/60 focus:border-primary" inputMode="numeric" maxLength={6} onChange={(event) => setPincode(event.target.value.replace(/\D/g, '').slice(0, 6))} required type="text" value={pincode} /><span className="mt-2 block text-xs text-muted-text" id="pincode-help">Use the six-digit location code for your region.</span></label>
            </>}
            <button className="w-full rounded-2xl bg-dark px-5 py-4 font-semibold text-white shadow-lg transition hover:bg-primary disabled:cursor-wait disabled:opacity-60" disabled={pending} type="submit">{pending ? (isSignup ? 'Creating account…' : 'Signing in…') : (isSignup ? 'Create account' : 'Sign in')}</button>
          </form>
          <p className="mt-6 text-center text-sm text-muted-text">{isSignup ? 'Already have an account?' : 'New to Train Me AI?'} <Link className="font-semibold text-primary hover:text-dark" to={`/${role}/${isSignup ? 'login' : 'signup'}`}>{isSignup ? 'Sign in' : 'Create an account'}</Link></p>
        </div>
      </section>
    </main>
  )
}
