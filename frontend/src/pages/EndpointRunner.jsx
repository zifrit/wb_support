import { useMemo, useState } from 'react'

import { runEndpoint } from '../api/client'
import JsonViewer from '../components/JsonViewer'

export default function EndpointRunner({ endpoint, username, debugEnabled }) {
  const [queryState, setQueryState] = useState({})
  const [bodyState, setBodyState] = useState('{}')
  const [result, setResult] = useState(null)
  const [running, setRunning] = useState(false)

  const queryFields = endpoint?.query || []

  const bodyError = useMemo(() => {
    if (!endpoint || endpoint.method === 'GET') return ''
    try {
      JSON.parse(bodyState || '{}')
      return ''
    } catch {
      return 'Body must be valid JSON'
    }
  }, [endpoint, bodyState])

  if (!endpoint) {
    return (
      <section className="surface-card runner-panel">
        <h2>Runner</h2>
        <p className="muted">Выберите ручку в каталоге слева.</p>
      </section>
    )
  }

  async function run() {
    if (bodyError) return
    setRunning(true)
    try {
      const body = endpoint.method === 'GET' ? null : JSON.parse(bodyState || '{}')
      const response = await runEndpoint({
        method: endpoint.method,
        path: endpoint.path,
        username,
        query: queryState,
        body
      })
      setResult({ ok: true, status: response.status, payload: response.data })
    } catch (error) {
      setResult({ ok: false, status: error.status, payload: error.data })
    } finally {
      setRunning(false)
    }
  }

  return (
    <section className="surface-card runner-panel">
      <div className="section-head">
        <div>
          <p className="eyebrow">Runner</p>
          <h2>{endpoint.title}</h2>
        </div>
        <div className="runner-route">
          <strong>{endpoint.method}</strong>
          <span>{endpoint.path}</span>
        </div>
      </div>

      <div className="stack">
        {queryFields.map((field) => (
          <label key={field.name} className="field">
            <span>
              {field.name}
              {field.required ? ' *' : ''}
            </span>
            <input
              placeholder={field.description}
              required={field.required}
              value={queryState[field.name] || ''}
              onChange={(e) => setQueryState((prev) => ({ ...prev, [field.name]: e.target.value }))}
            />
          </label>
        ))}

        {endpoint.method !== 'GET' && (
          <label className="field">
            <span>JSON body</span>
            <textarea rows={10} value={bodyState} onChange={(e) => setBodyState(e.target.value)} />
            {bodyError && <span className="error">{bodyError}</span>}
          </label>
        )}

        <button
          className="primary-button"
          disabled={running || (!debugEnabled && !username) || Boolean(bodyError)}
          onClick={run}
        >
          {running ? 'Выполняю запрос...' : 'Запустить'}
        </button>
      </div>

      {result && (
        <div className={result.ok ? 'result ok' : 'result fail'}>
          <p>
            Status: <strong>{result.status}</strong>
          </p>
          <JsonViewer value={result.payload} />
        </div>
      )}
    </section>
  )
}
