import { FormEvent, useEffect, useRef, useState } from 'react'
import { LiveAvatarSession, SessionEvent } from '@heygen/liveavatar-web-sdk'
import { ApiError, apiRequest } from '../../lib/api'

type AvatarSession = { session_token: string; session_id: string; api_url: string }
type AvatarReply = { response_text: string }
type PrototypeStatus = 'idle' | 'starting' | 'ready' | 'listening' | 'thinking' | 'speaking'

type BrowserRecognition = {
  continuous: boolean
  interimResults: boolean
  lang: string
  start: () => void
  stop: () => void
  onresult: ((event: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null
  onend: (() => void) | null
  onerror: (() => void) | null
}

type BrowserRecognitionConstructor = new () => BrowserRecognition

function speechRecognitionConstructor(): BrowserRecognitionConstructor | undefined {
  const browser = window as Window & { SpeechRecognition?: BrowserRecognitionConstructor; webkitSpeechRecognition?: BrowserRecognitionConstructor }
  return browser.SpeechRecognition ?? browser.webkitSpeechRecognition
}

export function EvaluationsPage() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const avatarRef = useRef<LiveAvatarSession | null>(null)
  const recognitionRef = useRef<BrowserRecognition | null>(null)
  const [message, setMessage] = useState('')
  const [reply, setReply] = useState('')
  const [status, setStatus] = useState<PrototypeStatus>('idle')
  const [error, setError] = useState<string>()

  const avatarReady = status !== 'idle' && status !== 'starting'
  const statusCopy: Record<PrototypeStatus, string> = {
    idle: 'Start a session to connect your avatar.',
    starting: 'Connecting to your HeyGen avatar…',
    ready: 'Avatar ready. Speak or type a message.',
    listening: 'Listening for your response…',
    thinking: 'Preparing a practice response…',
    speaking: 'Your avatar is responding…',
  }

  useEffect(() => () => {
    recognitionRef.current?.stop()
    if (avatarRef.current) void avatarRef.current.stop()
  }, [])

  async function startAvatar() {
    setStatus('starting')
    setError(undefined)
    console.info('[avatar] session start requested')
    try {
      const sessionData = await apiRequest<AvatarSession>('/api/v1/evaluations/avatar-session', { method: 'POST' })
      console.debug('[avatar] session token received', { sessionId: sessionData.session_id, apiUrl: sessionData.api_url })
      const avatar = new LiveAvatarSession(sessionData.session_token, { apiUrl: sessionData.api_url })
      console.debug('[avatar] SDK session constructed')
      avatar.on(SessionEvent.SESSION_STREAM_READY, () => {
        console.info('[avatar] stream ready')
        if (videoRef.current) avatar.attach(videoRef.current)
      })
      avatar.on(SessionEvent.SESSION_DISCONNECTED, () => {
        console.info('[avatar] session disconnected')
        avatarRef.current = null
        setStatus('idle')
      })
      await avatar.start()
      console.info('[avatar] SDK session started')
      avatarRef.current = avatar
      setStatus('ready')
    } catch (caught) {
      console.error('[avatar] session start failed', caught instanceof ApiError ? { status: caught.status, message: caught.message } : caught)
      setStatus('idle')
      setError(caught instanceof ApiError ? caught.message : 'The avatar session could not be started.')
    }
  }

  async function sendMessage(value = message) {
    const transcript = value.trim()
    if (!transcript || !avatarRef.current) return
    setMessage(transcript)
    setStatus('thinking')
    setError(undefined)
    console.info('[avatar] message request started', { messageLength: transcript.length })
    try {
      const result = await apiRequest<AvatarReply>('/api/v1/evaluations/message', { method: 'POST', body: { message: transcript } })
      console.info('[avatar] message response received', { responseLength: result.response_text.length })
      setReply(result.response_text)
      setStatus('speaking')
      avatarRef.current.repeat(result.response_text)
      setMessage('')
    } catch (caught) {
      console.error('[avatar] message request failed', caught instanceof ApiError ? { status: caught.status, message: caught.message } : caught)
      setStatus('ready')
      setError(caught instanceof ApiError ? caught.message : 'The prototype response could not be generated.')
    }
  }

  function startListening() {
    const Recognition = speechRecognitionConstructor()
    if (!Recognition) {
      setError('Speech recognition is not available in this browser. Type your message below instead.')
      return
    }
    setError(undefined)
    console.debug('[avatar] speech recognition starting')
    const recognition = new Recognition()
    recognition.continuous = false
    recognition.interimResults = false
    recognition.lang = 'en-IN'
    recognition.onresult = (event) => {
      const transcript = event.results[0]?.[0]?.transcript ?? ''
      console.debug('[avatar] speech result received', { transcriptLength: transcript.length })
      if (transcript) void sendMessage(transcript)
    }
    recognition.onend = () => setStatus((current) => current === 'listening' ? 'ready' : current)
    recognition.onerror = () => {
      console.warn('[avatar] speech recognition failed')
      setStatus('ready')
      setError('We could not hear that. Please try again or type your message.')
    }
    recognitionRef.current = recognition
    setStatus('listening')
    recognition.start()
  }

  async function endSession() {
    console.info('[avatar] session end requested')
    recognitionRef.current?.stop()
    if (avatarRef.current) await avatarRef.current.stop()
    avatarRef.current = null
    setReply('')
    setStatus('idle')
    console.info('[avatar] session ended')
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    void sendMessage()
  }

  return <div className="mx-auto max-w-[1160px] px-6 py-8 lg:px-10 lg:py-10">
    <div className="grid gap-8 lg:grid-cols-[minmax(0,1.35fr)_minmax(300px,0.65fr)] lg:items-start">
      <section className="overflow-hidden rounded-3xl border border-border bg-dark shadow-[0_24px_64px_rgba(17,16,37,0.18)]">
        <div className="relative aspect-video bg-[radial-gradient(circle_at_65%_20%,rgba(102,88,220,0.42),transparent_36%),linear-gradient(145deg,#201c43,#111025_56%,#292052)]">
          <video aria-label="HeyGen avatar stream" autoPlay className="h-full w-full object-cover" playsInline ref={videoRef} />
          {status === 'idle' && <div className="absolute inset-0 grid place-items-center p-8 text-center"><div><p className="text-2xl font-semibold tracking-[-0.04em] text-white">Practice with your avatar</p><p className="mx-auto mt-3 max-w-sm text-sm leading-6 text-white/65">Start a secure temporary HeyGen session, then speak naturally and receive a prototype coaching response.</p></div></div>}
          {avatarReady && <div className="absolute left-5 top-5 rounded-full bg-dark/65 px-3 py-1.5 text-xs font-medium text-white backdrop-blur"><span className="mr-2 inline-block h-2 w-2 rounded-full bg-blue-accent" />{statusCopy[status]}</div>}
        </div>
      </section>
      <section className="rounded-3xl border border-border bg-surface p-6">
        <p className="text-sm font-semibold text-primary">Live practice prototype</p>
        <h2 className="mt-2 text-3xl font-semibold tracking-[-0.05em]">Say it. See it. Improve it.</h2>
        <p className="mt-3 text-sm leading-6 text-muted-text">Your spoken words are transcribed in the browser. This prototype returns one of ten coaching responses and lets the avatar say it back.</p>
        <div className="mt-6 rounded-2xl bg-background p-4 text-sm text-muted-text" aria-live="polite">{statusCopy[status]}</div>
        {error && <p className="mt-4 text-sm text-red-700" role="alert">{error}</p>}
        {reply && <div className="mt-4 rounded-2xl border border-light-purple bg-light-purple/40 p-4"><p className="text-sm font-semibold text-primary">Avatar response</p><p className="mt-2 text-sm leading-6 text-main-text">{reply}</p></div>}
        {status === 'idle' ? <button className="mt-6 w-full rounded-xl bg-primary px-4 py-3 font-semibold text-white" onClick={() => void startAvatar()} type="button">Start avatar</button> : <div className="mt-6 grid gap-3"><button className="w-full rounded-xl bg-primary px-4 py-3 font-semibold text-white disabled:opacity-60" disabled={status === 'thinking' || status === 'speaking'} onClick={startListening} type="button">Start listening</button><button className="w-full rounded-xl border border-border px-4 py-3 font-semibold text-main-text" onClick={() => void endSession()} type="button">End session</button></div>}
      </section>
    </div>
    <form aria-label="Avatar message" className="mt-6 rounded-3xl border border-border bg-surface p-5" onSubmit={submit}>
      <label className="grid gap-2 text-sm font-semibold" htmlFor="evaluation-message">Message<span className="font-normal text-muted-text">Use this fallback if your browser does not support speech recognition.</span></label>
      <div className="mt-3 flex flex-col gap-3 sm:flex-row"><input className="min-w-0 flex-1 rounded-xl border border-border px-4 py-3 outline-none focus:border-primary" disabled={!avatarReady || status === 'thinking'} id="evaluation-message" onChange={(event) => setMessage(event.target.value)} placeholder="Type what you would like to practice…" value={message} /><button className="rounded-xl bg-dark px-6 py-3 font-semibold text-white disabled:opacity-60" disabled={!avatarReady || !message.trim() || status === 'thinking'} type="submit">Speak</button></div>
    </form>
  </div>
}
