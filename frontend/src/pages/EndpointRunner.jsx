import { useEffect, useMemo, useState } from 'react'

import { runEndpoint } from '../api/client'
import JsonViewer from '../components/JsonViewer'

const SIMPLE_FORM_ENDPOINTS = new Set(['wb_adverts', 'wb_fullstats', 'wb_stop', 'wb_orders'])

export default function EndpointRunner({ endpoint, username, debugEnabled }) {
  const [fieldState, setFieldState] = useState({})
  const [bodyState, setBodyState] = useState('{}')
  const [result, setResult] = useState(null)
  const [running, setRunning] = useState(false)

  const formFields = endpoint?.query || []
  const simpleFormMode = endpoint ? SIMPLE_FORM_ENDPOINTS.has(endpoint.id) : false

  useEffect(() => {
    setFieldState({})
    setBodyState('{}')
    setResult(null)
  }, [endpoint?.id])

  const bodyError = useMemo(() => {
    if (!endpoint || simpleFormMode || !endpoint.body) return ''
    try {
      JSON.parse(bodyState || '{}')
      return ''
    } catch {
      return 'Body must be valid JSON'
    }
  }, [endpoint, bodyState, simpleFormMode])

  const missingRequiredField = useMemo(() => {
    if (!endpoint) return ''
    for (const field of formFields) {
      if (!field.required) continue
      const value = fieldState[field.name]
      if (value === undefined || value === null || `${value}`.trim() === '') {
        return field.name
      }
    }
    return ''
  }, [endpoint, formFields, fieldState])

  if (!endpoint) {
    return (
      <section className="surface-card runner-panel">
        <h2>Runner</h2>
        <p className="muted">Выберите ручку в каталоге слева.</p>
      </section>
    )
  }

  async function run() {
    if (bodyError || missingRequiredField) return
    setRunning(true)
    try {
      let body
      if (simpleFormMode) {
        body = Object.fromEntries(
          Object.entries(fieldState).filter(([, value]) => value !== undefined && value !== null && `${value}`.trim() !== '')
        )
      } else {
        body = endpoint.body ? JSON.parse(bodyState || '{}') : {}
        if (fieldState.shop_id !== undefined && `${fieldState.shop_id}`.trim() !== '') {
          body.shop_id = Number(fieldState.shop_id)
        }
      }
      const response = await runEndpoint({
        method: endpoint.method,
        path: endpoint.path,
        username,
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
        {formFields.map((field) => (
          <label key={field.name} className="field">
            <span>
              {field.name}
              {field.required ? ' *' : ''}
            </span>
            <input
              placeholder={field.description}
              required={field.required}
              value={fieldState[field.name] || ''}
              onChange={(e) => setFieldState((prev) => ({ ...prev, [field.name]: e.target.value }))}
            />
          </label>
        ))}

        {!simpleFormMode && endpoint.body && (
          <label className="field">
            <span>JSON body</span>
            <textarea rows={10} value={bodyState} onChange={(e) => setBodyState(e.target.value)} />
            {bodyError && <span className="error">{bodyError}</span>}
          </label>
        )}

        {missingRequiredField && <span className="error">Заполните обязательное поле: {missingRequiredField}</span>}

        <button
          className="primary-button"
          disabled={running || (!debugEnabled && !username) || Boolean(bodyError) || Boolean(missingRequiredField)}
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
