import { createAsyncThunk, createSlice, type PayloadAction } from '@reduxjs/toolkit'
import { ApiError } from '../../lib/api'
import {
  authTokenKey,
  clearAuthToken,
  getCurrentAccount,
  login,
  readAuthToken,
  signup,
  writeAuthToken,
  type Account,
  type AdminSignupValues,
  type AgentSignupValues,
  type LoginCredentials,
  type TokenResponse,
} from './authApi'
import type { Role } from '../../lib/types'

export type AuthState = {
  token: string | null
  account: Account | null
  status: 'idle' | 'loading' | 'authenticated' | 'error'
  error: string | null
  bootstrapped: boolean
}

const initialToken = readAuthToken()
export const initialState: AuthState = {
  token: initialToken,
  account: null,
  status: initialToken ? 'loading' : 'idle',
  error: null,
  bootstrapped: !initialToken,
}

function errorMessage(error: unknown) {
  if (error instanceof ApiError) return error.message
  return error instanceof Error ? error.message : 'Something went wrong. Try again.'
}

export const loginUser = createAsyncThunk<TokenResponse, { role: Role } & LoginCredentials, { rejectValue: string }>(
  'auth/login',
  async ({ role, email, password }, { rejectWithValue }) => {
    try {
      return await login(role, { email, password })
    } catch (error) {
      return rejectWithValue(errorMessage(error))
    }
  },
)

export const signupUser = createAsyncThunk<Account, { role: Role; values: AgentSignupValues | AdminSignupValues }, { rejectValue: string }>(
  'auth/signup',
  async ({ role, values }, { rejectWithValue }) => {
    try {
      return await signup(role, values)
    } catch (error) {
      return rejectWithValue(errorMessage(error))
    }
  },
)

export const restoreSession = createAsyncThunk<Account, void, { rejectValue: string }>(
  'auth/restore',
  async (_, { rejectWithValue }) => {
    const token = readAuthToken()
    if (!token) return rejectWithValue('No saved session')
    try {
      return await getCurrentAccount(token)
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) clearAuthToken()
      return rejectWithValue(errorMessage(error))
    }
  },
)

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    hydrateToken(state, action: PayloadAction<string>) {
      state.token = action.payload
      state.status = 'loading'
      state.error = null
      state.bootstrapped = false
    },
    setSession(state, action: PayloadAction<{ token: string; account: Account }>) {
      state.token = action.payload.token
      state.account = action.payload.account
      state.status = 'authenticated'
      state.error = null
      state.bootstrapped = true
      writeAuthToken(action.payload.token)
    },
    clearSession(state) {
      state.token = null
      state.account = null
      state.status = 'idle'
      state.error = null
      state.bootstrapped = true
      clearAuthToken()
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginUser.pending, (state) => {
        state.status = 'loading'
        state.error = null
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.token = action.payload.access_token
        state.account = action.payload.account
        state.status = 'authenticated'
        state.error = null
        state.bootstrapped = true
        writeAuthToken(action.payload.access_token)
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.status = 'error'
        state.error = action.payload ?? 'Unable to sign in.'
        state.bootstrapped = true
      })
      .addCase(signupUser.pending, (state) => {
        state.status = 'loading'
        state.error = null
      })
      .addCase(signupUser.fulfilled, (state) => {
        state.status = 'idle'
        state.error = null
      })
      .addCase(signupUser.rejected, (state, action) => {
        state.status = 'error'
        state.error = action.payload ?? 'Unable to create your account.'
        state.bootstrapped = true
      })
      .addCase(restoreSession.pending, (state) => {
        state.status = 'loading'
        state.error = null
        state.bootstrapped = false
      })
      .addCase(restoreSession.fulfilled, (state, action) => {
        state.account = action.payload
        state.token = readAuthToken()
        state.status = 'authenticated'
        state.error = null
        state.bootstrapped = true
      })
      .addCase(restoreSession.rejected, (state, action) => {
        state.account = null
        state.token = readAuthToken()
        state.status = 'idle'
        state.error = action.payload === 'No saved session' ? null : action.payload ?? 'Unable to restore your session.'
        state.bootstrapped = true
      })
  },
})

export const { hydrateToken, setSession, clearSession } = authSlice.actions
export default authSlice.reducer

export { authTokenKey }
