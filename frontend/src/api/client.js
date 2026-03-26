const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function clearFrontendSession() {
  localStorage.removeItem('wb_auth_granted')
  localStorage.removeItem('wb_auth_expires_at')
  localStorage.removeItem('wb_username')
  Object.keys(localStorage)
    .filter((key) => key.startsWith('wb_otp_cooldown_until:'))
    .forEach((key) => localStorage.removeItem(key))
}

function redirectToLogin() {
  clearFrontendSession()
  window.history.replaceState({}, '', '/login')
  window.dispatchEvent(new PopStateEvent('popstate'))
}

function isAuthFailure(error) {
  return error?.status === 401 || error?.status === 403
}

async function parseResponse(response) {
  const text = await response.text()
  const json = text ? safeJson(text) : null
  if (!response.ok) {
    const error = json || { message: text || 'Request failed' }
    throw { status: response.status, data: error }
  }
  return { status: response.status, data: json }
}

function safeJson(text) {
  try {
    return JSON.parse(text)
  } catch {
    return { raw: text }
  }
}

export async function authLogin(username) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username })
  })
  return parseResponse(response)
}

export async function authVerify(username, code) {
  const response = await fetch(`${API_BASE_URL}/auth/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, code })
  })
  return parseResponse(response)
}

export async function authCheck(username) {
  const response = await fetch(`${API_BASE_URL}/auth/check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username })
  })
  return parseResponse(response)
}

export async function fetchMetaConfig() {
  const response = await fetch(`${API_BASE_URL}/meta/config`)
  return parseResponse(response)
}

export async function fetchMetaEndpoints() {
  const response = await fetch(`${API_BASE_URL}/meta/endpoints`)
  return parseResponse(response)
}

export async function runEndpoint({ method, path, username, body = null }) {
  try {
    const authResponse = await authCheck(username)
    if (!authResponse.data?.valid) {
      redirectToLogin()
      throw { status: 401, data: { message: 'Authentication required' } }
    }
  } catch (error) {
    if (isAuthFailure(error)) {
      redirectToLogin()
    }
    throw error
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      'X-Username': username
    },
    body: JSON.stringify(body ?? {})
  })
  return parseResponse(response)
}
