export class ApiError extends Error {
  readonly status: number
  readonly code?: string
  readonly details?: unknown

  constructor(message: string, status: number, code?: string, details?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.details = details
  }
}

export type ApiRequestOptions = Omit<RequestInit, 'body'> & {
  body?: BodyInit | Record<string, unknown> | unknown[]
  token?: string
  authToken?: string
}

function storedToken() {
  if (typeof window === 'undefined') return undefined
  return window.sessionStorage.getItem('train-me-auth-token-v1') ?? undefined
}

function isJsonBody(body: unknown) {
  return body !== undefined && body !== null && typeof body === 'object' && !(body instanceof FormData) && !(body instanceof Blob) && !(body instanceof ArrayBuffer)
}

function parsePayload(value: string): unknown {
  if (!value) return undefined
  try { return JSON.parse(value) as unknown } catch { return value }
}

const defaultApiBaseUrl = 'http://localhost:8000'

function configuredApiBaseUrl() {
  return (import.meta as ImportMeta & { env?: { VITE_API_BASE_URL?: string } }).env?.VITE_API_BASE_URL || defaultApiBaseUrl
}

export function resolveApiUrl(path: string) {
  if (/^https?:\/\//i.test(path)) return path
  const configuredBase = configuredApiBaseUrl()
  return configuredBase.replace(/\/$/, '') + '/' + path.replace(/^\/+/, '')
}

export async function apiRequest<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const { body, token, authToken, headers: providedHeaders, ...requestInit } = options
  const headers = new Headers(providedHeaders)
  headers.set('Accept', 'application/json')
  let requestBody: BodyInit | undefined
  if (isJsonBody(body)) {
    if (!headers.has('Content-Type')) headers.set('Content-Type', 'application/json')
    requestBody = JSON.stringify(body)
  } else {
    requestBody = body as BodyInit | undefined
  }
  const explicitBearer = token ?? authToken
  const requestUrl = resolveApiUrl(path)
  const requestOrigin = new URL(requestUrl, typeof window === 'undefined' ? undefined : window.location.origin).origin
  const configuredOrigin = new URL(configuredApiBaseUrl(), typeof window === 'undefined' ? undefined : window.location.origin).origin
  const bearer = explicitBearer ?? (requestOrigin === configuredOrigin ? storedToken() : undefined)
  if (bearer && !headers.has('Authorization')) headers.set('Authorization', `Bearer ${bearer}`)

  const response = await fetch(requestUrl, { ...requestInit, body: requestBody, headers })
  const text = await response.text()
  const payload = parsePayload(text)
  if (!response.ok) {
    const record = payload && typeof payload === 'object' ? payload as Record<string, unknown> : undefined
    const detailItems = Array.isArray(record?.detail) ? record.detail : []
    const detailMessage = detailItems
      .map((item) => item && typeof item === 'object' && 'msg' in item && typeof item.msg === 'string' ? item.msg : undefined)
      .filter((item): item is string => Boolean(item))
      .join('; ')
    const message = typeof record?.detail === 'string'
      ? record.detail
      : detailMessage
        ? detailMessage
        : typeof record?.message === 'string'
          ? record.message
          : typeof payload === 'string'
            ? payload
            : response.statusText || 'Request failed'
    const code = typeof record?.code === 'string' ? record.code : undefined
    throw new ApiError(message, response.status, code, payload)
  }
  if (response.status === 204 || !text) return undefined as T
  return payload as T
}
