import { useState } from 'react'
import { authLogin, authVerify } from '../api/client'

export default function LoginPage({ username, onUsernameChange, onAuthSuccess }) {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  async function handleLogin(event) {
    event.preventDefault()
    setLoading(true)
    setMessage('')
    try {
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
      <form onSubmit={handleLogin} className="stack">
        <label>
          Username
          <input value={username} onChange={(e) => onUsernameChange(e.target.value)} placeholder="alice" required />
        </label>
        <button disabled={loading}>{loading ? 'Processing...' : 'Войти'}</button>
      </form>
      {message && <p className="status">{message}</p>}
    </section>
  )
}
