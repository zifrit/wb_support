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
        setMessage(`Debug mode enabled. Auth checks are disabled. Active user: ${username || debugUsername}`)
        onAuthSuccess()
        return
      }
      if (username.trim().toLowerCase() === 'admin') {
        setMessage('Admin mode enabled. Token request skipped.')
        onAuthSuccess()
        return
      }
      await authLogin(username)
      const verify = await authVerify(username)
      setMessage(verify.data?.valid ? 'Token saved and verified' : 'Token saved but not verified')
      onAuthSuccess()
    } catch (error) {
      setMessage(error?.data?.error?.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="card">
      <h2>Token Setup</h2>
      {debugEnabled && (
        <p className="status">Debug mode is active. Login is optional and access checks are disabled.</p>
      )}
      <form onSubmit={handleLogin} className="stack">
        <label>
          Username
          <input
            value={username}
            onChange={(e) => onUsernameChange(e.target.value)}
            placeholder={debugEnabled ? debugUsername || 'debug' : 'alice'}
            required={!debugEnabled}
          />
        </label>
        <button disabled={loading}>{loading ? 'Processing...' : debugEnabled ? 'Use debug mode' : 'Войти'}</button>
      </form>
      {message && <p className="status">{message}</p>}
    </section>
  )
}
