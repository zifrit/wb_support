import { useEffect, useMemo, useState } from 'react'

import { fetchMetaEndpoints } from './api/client'
import EndpointsCatalog from './pages/EndpointsCatalog'
import EndpointRunner from './pages/EndpointRunner'
import LoginPage from './pages/LoginPage'

export default function App() {
  const [username, setUsername] = useState(localStorage.getItem('wb_username') || '')
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

  useEffect(() => {
    localStorage.setItem('wb_username', username)
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

  return (
    <main className="layout">
      <header className="hero">
        <h1>WB API Explorer</h1>
        <p>Login by username, run WB wrappers, inspect raw JSON responses.</p>
      </header>

      <div className="grid">
        <LoginPage
          username={effectiveUsername}
          onUsernameChange={setUsername}
          onAuthSuccess={() => {}}
          debugEnabled={debugEnabled}
          debugUsername={debugUsername}
        />

        {loadingEndpoints ? (
          <section className="card">
            <h2>Endpoints Catalog</h2>
            <p>Loading...</p>
          </section>
        ) : metaError ? (
          <section className="card">
            <h2>Endpoints Catalog</h2>
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
