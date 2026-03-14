import { useEffect, useMemo, useState } from 'react'

import { fetchMetaEndpoints } from './api/client'
import EndpointsCatalog from './pages/EndpointsCatalog'
import EndpointRunner from './pages/EndpointRunner'
import LoginPage from './pages/LoginPage'

const AUTH_FLAG_KEY = 'wb_auth_granted'
const USERNAME_KEY = 'wb_username'
const LOGIN_ROUTE = '/login'
const APP_ROUTE = '/endpoints'

function getCurrentPath() {
  return window.location.pathname || '/'
}

function navigate(path, replace = false) {
  const method = replace ? 'replaceState' : 'pushState'
  window.history[method]({}, '', path)
  window.dispatchEvent(new PopStateEvent('popstate'))
}

export default function App() {
  const [path, setPath] = useState(getCurrentPath())
  const [username, setUsername] = useState(localStorage.getItem(USERNAME_KEY) || '')
  const [isAuthorized, setIsAuthorized] = useState(localStorage.getItem(AUTH_FLAG_KEY) === 'true')
  const [endpoints, setEndpoints] = useState([])
  const [selectedId, setSelectedId] = useState('')
  const [loadingEndpoints, setLoadingEndpoints] = useState(true)
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
      setPath(getCurrentPath())
    }

    window.addEventListener('popstate', syncPath)
    return () => window.removeEventListener('popstate', syncPath)
  }, [])

  useEffect(() => {
    localStorage.setItem(USERNAME_KEY, username)
  }, [username])

  useEffect(() => {
    async function loadMeta() {
      setLoadingEndpoints(true)
      setMetaError('')
      try {
        const response = await fetchMetaEndpoints()
        setEndpoints(response.data.endpoints || [])
        setSelectedId((response.data.endpoints || [])[0]?.id || '')
        setDebugEnabled(Boolean(response.data.debug))
        setDebugUsername(response.data.defaultUsername || '')
      } catch {
        setMetaError('Failed to load endpoint catalog')
      } finally {
        setLoadingEndpoints(false)
      }
    }
    loadMeta()
  }, [])

  useEffect(() => {
    if (debugEnabled && !username && debugUsername) {
      setUsername(debugUsername)
    }
  }, [debugEnabled, debugUsername, username])

  useEffect(() => {
    if (debugEnabled) {
      setIsAuthorized(true)
      localStorage.setItem(AUTH_FLAG_KEY, 'true')
      if (path === '/' || path === LOGIN_ROUTE) {
        navigate(APP_ROUTE, true)
      }
      return
    }

    if (path === '/') {
      navigate(shouldOpenApp ? APP_ROUTE : LOGIN_ROUTE, true)
      return
    }

    if (!shouldOpenApp && path !== LOGIN_ROUTE) {
      navigate(LOGIN_ROUTE, true)
      return
    }

    if (shouldOpenApp && path === LOGIN_ROUTE) {
      navigate(APP_ROUTE, true)
    }
  }, [debugEnabled, path, shouldOpenApp])

  function handleAuthSuccess(authorizedUser) {
    setUsername(authorizedUser)
    setIsAuthorized(true)
    localStorage.setItem(AUTH_FLAG_KEY, 'true')
    navigate(APP_ROUTE)
  }

  function handleLogout() {
    setIsAuthorized(false)
    if (!debugEnabled) {
      localStorage.removeItem(AUTH_FLAG_KEY)
    }
    navigate(LOGIN_ROUTE)
  }

  if (!shouldOpenApp || path === LOGIN_ROUTE) {
    return (
      <LoginPage
        username={effectiveUsername}
        onUsernameChange={setUsername}
        onAuthSuccess={handleAuthSuccess}
        debugEnabled={debugEnabled}
        debugUsername={debugUsername}
      />
    )
  }

  return (
    <main className="app-shell">
      <section className="app-hero">
        <div>
          <p className="eyebrow">WB wrapper console</p>
          <h1>WB API Explorer</h1>
        </div>

        <div className="hero-panel">
          <div>
            <span className="panel-label">Активный пользователь</span>
            <strong>{effectiveUsername || 'Не определен'}</strong>
          </div>
          <div>
            <span className="panel-label">Режим</span>
            <strong>{debugEnabled ? 'Debug bypass' : 'Protected access'}</strong>
          </div>
          {!debugEnabled && (
            <button type="button" className="ghost-button" onClick={handleLogout}>
              Выйти
            </button>
          )}
        </div>
      </section>

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
      </div>
    </main>
  )
}
