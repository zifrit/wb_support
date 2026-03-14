import { useState } from 'react'
import { authLogin, authVerify } from '../api/client'

export default function LoginPage({ username, onUsernameChange, onAuthSuccess, debugEnabled, debugUsername }) {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  async function handleLogin(event) {
    event.preventDefault()
    setLoading(true)
    setMessage('')
    try {
      if (debugEnabled) {
        const activeUser = username || debugUsername
        setMessage(`Debug mode enabled. Active user: ${activeUser}`)
        onAuthSuccess(activeUser)
        return
      }
      const trimmedUsername = username.trim()
      if (trimmedUsername.toLowerCase() === 'admin') {
        setMessage('Admin mode enabled. Token request skipped.')
        onAuthSuccess(trimmedUsername)
        return
      }
      await authLogin(trimmedUsername)
      const verify = await authVerify(trimmedUsername)
      setMessage(verify.data?.valid ? 'Token saved and verified' : 'Token saved but not verified')
      onAuthSuccess(trimmedUsername)
    } catch (error) {
      setMessage(error?.data?.error?.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="auth-layout">
      <section className="auth-card auth-card-minimal">
        <div className="auth-card-head">
          <p className="eyebrow">WB API Explorer</p>
          <h2>{debugEnabled ? 'Debug access' : 'Вход'}</h2>
          <p className="muted">
            {debugEnabled
              ? 'Логин будет пропущен автоматически.'
              : 'Введите username для доступа.'}
          </p>
        </div>

        <form onSubmit={handleLogin} className="auth-form">
          <label className="field">
            <span>Username</span>
            <input
              value={username}
              onChange={(e) => onUsernameChange(e.target.value)}
              placeholder={debugEnabled ? debugUsername || 'debug' : 'alice'}
              required={!debugEnabled}
            />
          </label>

          <button className="primary-button" disabled={loading}>
            {loading ? 'Проверяю доступ...' : debugEnabled ? 'Продолжить в debug' : 'Войти'}
          </button>
        </form>

        {message && <p className="status">{message}</p>}
      </section>
    </main>
  )
}
