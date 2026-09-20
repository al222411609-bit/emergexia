import { mockApi } from './mockApi.js'

// ── Modo "solo frontend" ─────────────────────────────────────────────────
// Con esto en true, la app no toca la red: todo (login, tablas, estado de
// Spark) se resuelve en el navegador con datos de prueba (ver mockApi.js).
// Cuando el backend (FastAPI + Spark) esté listo, cambia esto a false.
const MOCK_API = true

const TOKEN_KEY = 'emergexia.token'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (t) => localStorage.setItem(TOKEN_KEY, t)
export const clearToken = () => localStorage.removeItem(TOKEN_KEY)

let onUnauthorized = () => {}
export const setUnauthorizedHandler = (fn) => { onUnauthorized = fn }

/**
 * Error "no se pudo hablar con el servidor" (sin red, o el backend no responde).
 * Se distingue de un 401/400/422 normal para no cerrar la sesión por un simple
 * corte de conexión, y para poder mostrar la pantalla completa de reintento.
 */
export class ApiError extends Error {
  constructor(message) {
    super(message)
    this.isConnectionError = true
  }
}

export async function api(path, { method = 'GET', body } = {}) {
  const token = getToken()

  if (MOCK_API) {
    try {
      return await mockApi(path, { method, body }, token)
    } catch (e) {
      if (path !== '/auth/login' && /sesión expiró/i.test(e.message)) onUnauthorized()
      throw e
    }
  }

  const headers = { 'Content-Type': 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`

  let res
  try {
    res = await fetch(`/api${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined })
  } catch {
    throw new ApiError('No se pudo conectar con el servidor. Verifica que el backend esté en marcha.')
  }

  if (res.status === 401 && path !== '/auth/login') onUnauthorized()

  const data = await res.json().catch(() => null)

  if (!res.ok) {
    if (typeof data?.detail === 'string') throw new Error(data.detail)
    if (Array.isArray(data?.detail)) throw new Error('Revisa los datos del formulario.')
    if (data === null && res.status >= 500) {
      // Sin cuerpo JSON y código 5xx: el error lo generó el proxy (Vite/nginx),
      // no el backend con nuestro manejador de errores, así que casi siempre
      // significa que el backend no está corriendo.
      throw new ApiError(
        `No se pudo llegar al backend (código ${res.status}). Revisa que esté corriendo en el puerto 8000: ` +
        'en la carpeta backend ejecuta "python diagnostico.py" y mira la terminal de uvicorn.',
      )
    }
    throw new Error(`Ocurrió un error inesperado (código ${res.status}).`)
  }
  return data ?? {}
}
