import { useEffect, useState } from 'react'
import { authLogin, authVerify } from '../api/client'

function normalizePhoneDigits(value) {
  const digits = value.replace(/\D/g, '')
  if (!digits) return ''
  if (digits.length === 11 && digits.startsWith('8')) {
    return `7${digits.slice(1)}`
  }
  if (digits.length > 11) {
    if (digits.startsWith('8')) {
      return `7${digits.slice(1, 11)}`
    }
    return digits.slice(0, 11)
  }
  return digits
}

function toCanonicalPhone(value) {
  const digits = normalizePhoneDigits(value)
  if (digits.length === 10) {
    return `7${digits}`
  }
  if (digits.length === 11 && digits.startsWith('8')) {
    return `7${digits.slice(1)}`
  }
  return digits
}

function formatPhone(value) {
  const digits = normalizePhoneDigits(value)
  const local = digits.length === 11 && digits.startsWith('7') ? digits.slice(1) : digits
  const parts = [
    local.slice(0, 3),
    local.slice(3, 6),
    local.slice(6, 8),
    local.slice(8, 10)
  ].filter(Boolean)

  if (!parts.length) return ''

  let formatted = '+7'
  if (parts[0]) formatted += ` (${parts[0]}`
  if (parts[0]?.length === 3) formatted += ')'
  if (parts[1]) formatted += ` ${parts[1]}`
  if (parts[2]) formatted += `-${parts[2]}`
  if (parts[3]) formatted += `-${parts[3]}`
  return formatted
}

function isValidRussianPhone(value) {
  return /^7\d{10}$/.test(toCanonicalPhone(value))
}

export default function LoginPage({
  username,
  onUsernameChange,
  onAuthSuccess,
  debugEnabled,
  debugUsername,
  authError
}) {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [code, setCode] = useState('')
  const [awaitingCode, setAwaitingCode] = useState(false)
  const [phoneDraft, setPhoneDraft] = useState(debugEnabled ? username : formatPhone(username))

  const normalizedPhone = toCanonicalPhone(username)
  const phoneError =
    !debugEnabled && username && !isValidRussianPhone(username) ? 'Введите номер в российском формате' : ''

  useEffect(() => {
    setPhoneDraft(debugEnabled ? username : formatPhone(username))
  }, [debugEnabled])

  function handlePhoneChange(value) {
    setPhoneDraft(value)
    onUsernameChange(debugEnabled ? value : normalizePhoneDigits(value))
    if (awaitingCode) {
      setCode('')
      setAwaitingCode(false)
      setMessage('')
    }
  }

  function handlePhoneBlur() {
    if (debugEnabled) return
    setPhoneDraft(formatPhone(username))
  }

  async function handlePhoneSubmit(event) {
    event.preventDefault()
    if (!debugEnabled && !isValidRussianPhone(username)) {
      setMessage('Введите корректный номер телефона')
      return
    }

    setLoading(true)
    setMessage('')
    try {
      if (debugEnabled) {
        const activeUser = username || debugUsername
        setMessage(`Debug mode enabled. Active user: ${activeUser}`)
        onAuthSuccess(activeUser)
        return
      }
      await authLogin(normalizedPhone)
      onUsernameChange(normalizedPhone)
      setAwaitingCode(true)
      setMessage('Код отправлен. Введите его ниже.')
    } catch (error) {
      setMessage(error?.data?.error?.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  async function handleCodeSubmit(event) {
    event.preventDefault()
    if (!code.trim()) {
      setMessage('Введите код подтверждения')
      return
    }

    setLoading(true)
    setMessage('')
    try {
      const verify = await authVerify(normalizedPhone, code.trim())
      setMessage(verify.data?.valid ? 'Номер подтвержден' : 'Код не подтвержден')
      if (verify.data?.valid) {
        onAuthSuccess(normalizedPhone)
      }
    } catch (error) {
      setMessage(error?.data?.error?.message || 'Code verification failed')
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
              : 'Введите номер телефона и код подтверждения.'}
          </p>
        </div>

        <form onSubmit={handlePhoneSubmit} className="auth-form">
          <label className="field">
            <span>Телефон</span>
            <input
              value={debugEnabled ? username : phoneDraft}
              onChange={(e) => handlePhoneChange(e.target.value)}
              onBlur={handlePhoneBlur}
              placeholder={debugEnabled ? debugUsername || 'debug' : '+7 (999) 123-45-67'}
              required={!debugEnabled}
              inputMode={debugEnabled ? 'text' : 'tel'}
            />
            {phoneError && <span className="error">{phoneError}</span>}
          </label>

          <button className="primary-button" disabled={loading}>
            {loading ? 'Отправляю...' : debugEnabled ? 'Продолжить в debug' : awaitingCode ? 'Отправить код повторно' : 'Получить код'}
          </button>
        </form>

        {awaitingCode && !debugEnabled && (
          <form onSubmit={handleCodeSubmit} className="auth-form">
            <label className="field">
              <span>Код подтверждения</span>
              <input value={code} onChange={(e) => setCode(e.target.value)} placeholder="1234" inputMode="numeric" />
            </label>

            <button className="primary-button" disabled={loading}>
              {loading ? 'Проверяю код...' : 'Подтвердить'}
            </button>
          </form>
        )}

        {authError && <p className="error">{authError}</p>}
        {message && <p className="status">{message}</p>}
      </section>
    </main>
  )
}
