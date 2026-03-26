import { useEffect, useMemo, useState } from 'react'

import { fetchMetaConfig, fetchMetaEndpoints } from './api/client'
import EndpointsCatalog from './pages/EndpointsCatalog'
import EndpointRunner from './pages/EndpointRunner'
import LoginPage from './pages/LoginPage'

const AUTH_FLAG_KEY = 'wb_auth_granted'
const AUTH_EXPIRES_AT_KEY = 'wb_auth_expires_at'
const USERNAME_KEY = 'wb_username'
const LOGIN_ROUTE = '/login'
const APP_ROUTE = '/endpoints'
const SESSION_TTL_MS = 3 * 24 * 60 * 60 * 1000

function getCurrentPath() {
  return window.location.pathname || '/'
}

function navigate(path, replace = false) {
  const method = replace ? 'replaceState' : 'pushState'
  window.history[method]({}, '', path)
  window.dispatchEvent(new PopStateEvent('popstate'))
}

function hasValidSession() {
  const authGranted = localStorage.getItem(AUTH_FLAG_KEY) === 'true'
  const expiresAt = Number(localStorage.getItem(AUTH_EXPIRES_AT_KEY) || 0)
  return authGranted && expiresAt > Date.now()
}

function persistSession() {
  localStorage.setItem(AUTH_FLAG_KEY, 'true')
  localStorage.setItem(AUTH_EXPIRES_AT_KEY, String(Date.now() + SESSION_TTL_MS))
}

function clearSessionStorage() {
  localStorage.removeItem(AUTH_FLAG_KEY)
  localStorage.removeItem(AUTH_EXPIRES_AT_KEY)
}

export default function App() {
  const [path, setPath] = useState(getCurrentPath())
  const [username, setUsername] = useState(localStorage.getItem(USERNAME_KEY) || '')
  const [isAuthorized, setIsAuthorized] = useState(hasValidSession())
  const [endpoints, setEndpoints] = useState([])
  const [selectedId, setSelectedId] = useState('')
  const [loadingEndpoints, setLoadingEndpoints] = useState(false)
  const [loadingConfig, setLoadingConfig] = useState(true)
  const [metaError, setMetaError] = useState('')
  const [debugEnabled, setDebugEnabled] = useState(false)
  const [debugUsername, setDebugUsername] = useState('')

  const selectedEndpoint = useMemo(
    () => endpoints.find((endpoint) => endpoint.id === selectedId),
    [endpoints, selectedId]
  )

  const effectiveUsername = debugEnabled ? username || debugUsername : username
  const shouldOpenApp = debugEnabled || isAuthorized

  useEffect(() => {
    function syncPath() {
      if (!debugEnabled && !hasValidSession()) {
        clearSessionStorage()
        setIsAuthorized(false)
        setUsername('')
      }
      setPath(getCurrentPath())
    }

    window.addEventListener('popstate', syncPath)
    return () => window.removeEventListener('popstate', syncPath)
  }, [debugEnabled])

  useEffect(() => {
    localStorage.setItem(USERNAME_KEY, username)
  }, [username])

  useEffect(() => {
    async function loadConfig() {
      setLoadingConfig(true)
      setMetaError('')
      try {
        const response = await fetchMetaConfig()
        setDebugEnabled(Boolean(response.data.debug))
        setDebugUsername(response.data.defaultUsername || '')
      } catch {
        setMetaError('Failed to load app config')
      } finally {
        setLoadingConfig(false)
      }
    }
    loadConfig()
  }, [])

  useEffect(() => {
    if (debugEnabled && !username && debugUsername) {
      setUsername(debugUsername)
    }
  }, [debugEnabled, debugUsername, username])

  useEffect(() => {
    if (loadingConfig) return

    if (!shouldOpenApp) {
      setEndpoints([])
      setSelectedId('')
      setLoadingEndpoints(false)
      return
    }

    async function loadMeta() {
      setLoadingEndpoints(true)
      setMetaError('')
      try {
        const response = await fetchMetaEndpoints()
        const nextEndpoints = response.data.endpoints || []
        setEndpoints(nextEndpoints)
        setSelectedId((currentSelectedId) => {
          if (nextEndpoints.some((endpoint) => endpoint.id === currentSelectedId)) {
            return currentSelectedId
          }
          return nextEndpoints[0]?.id || ''
        })
      } catch {
        setMetaError('Failed to load endpoint catalog')
      } finally {
        setLoadingEndpoints(false)
      }
    }

    loadMeta()
  }, [loadingConfig, shouldOpenApp])

  useEffect(() => {
    if (loadingConfig) return

    if (debugEnabled) {
      setIsAuthorized(true)
      persistSession()
      if (path === '/' || path === LOGIN_ROUTE) {
        navigate(APP_ROUTE, true)
      }
      return
    }

    if (!hasValidSession()) {
      clearSessionStorage()
      if (isAuthorized) {
        setIsAuthorized(false)
        setUsername('')
        setEndpoints([])
        setSelectedId('')
      }
    }

    if (path === '/') {
      navigate(hasValidSession() ? APP_ROUTE : LOGIN_ROUTE, true)
      return
    }

    if (!hasValidSession() && path !== LOGIN_ROUTE) {
      navigate(LOGIN_ROUTE, true)
      return
    }

    if (hasValidSession() && path === LOGIN_ROUTE) {
      navigate(APP_ROUTE, true)
    }
  }, [debugEnabled, isAuthorized, loadingConfig, path, shouldOpenApp])

  function handleAuthSuccess(authorizedUser) {
    setUsername(authorizedUser)
    setIsAuthorized(true)
    persistSession()
    navigate(APP_ROUTE)
  }

  function handleLogout() {
    setIsAuthorized(false)
    setUsername('')
    setMetaError('')
    clearSessionStorage()
    localStorage.removeItem(USERNAME_KEY)
    Object.keys(localStorage)
      .filter((key) => key.startsWith('wb_otp_cooldown_until:'))
      .forEach((key) => localStorage.removeItem(key))
    setEndpoints([])
    setSelectedId('')
    navigate(LOGIN_ROUTE)
  }

  if (loadingConfig) {
    return (
      <main className="auth-layout">
        <section className="auth-card auth-card-minimal">
          <p className="muted">Загружаю настройки приложения...</p>
        </section>
      </main>
    )
  }

  if (!shouldOpenApp || path === LOGIN_ROUTE) {
    return (
      <LoginPage
        username={effectiveUsername}
        onUsernameChange={setUsername}
        onAuthSuccess={handleAuthSuccess}
        debugEnabled={debugEnabled}
        debugUsername={debugUsername}
        authError={metaError}
      />
    )
  }

  return (
    <main className="app-shell">
      <div className="workspace-grid">
        {loadingEndpoints ? (
          <section className="surface-card">
            <h2>Каталог ручек</h2>
            <p className="muted">Загружаю мета-описание эндпоинтов...</p>
          </section>
        ) : metaError ? (
          <section className="surface-card">
            <h2>Каталог ручек</h2>
            <p className="error">{metaError}</p>
          </section>
        ) : (
          <EndpointsCatalog endpoints={endpoints} selectedId={selectedId} onSelect={setSelectedId} />
        )}

        <EndpointRunner endpoint={selectedEndpoint} username={effectiveUsername} debugEnabled={debugEnabled} />

        <aside className="workspace-sidebar">
          <div className="user-panel">
            <div>
              <span className="panel-label">Активный пользователь</span>
              <strong>{effectiveUsername || 'Не определен'}</strong>
            </div>
            {!debugEnabled && (
              <button type="button" className="ghost-button" onClick={handleLogout}>
                Выйти
              </button>
            )}
          </div>
        </aside>
      </div>
    </main>
  )
}
