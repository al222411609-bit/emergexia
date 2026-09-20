const TOKEN_KEY = 'emergexia.token'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (t) => localStorage.setItem(TOKEN_KEY, t)
export const clearToken = () => localStorage.removeItem(TOKEN_KEY)

let onUnauthorized = () => {}
export const setUnauthorizedHandler = (fn) => { onUnauthorized = fn }

export async function api(path, { method = 'GET', body } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  let res
  try {
    res = await fetch(`/api${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined })
  } catch {
    throw new Error('No se pudo conectar con el servidor. Verifica que el backend esté en marcha.')
  }

  if (res.status === 401 && path !== '/auth/login') onUnauthorized()

  const data = await res.json().catch(() => null)

  if (!res.ok) {
    if (typeof data?.detail === 'string') throw new Error(data.detail)
    if (Array.isArray(data?.detail)) throw new Error('Revisa los datos del formulario.')
    if (res.status >= 500) {
      // Si la respuesta no trae JSON, el error lo generó el proxy (Vite/nginx),
      // no el backend: casi siempre significa que el backend no está en marcha.
      throw new Error(
        `No se pudo llegar al backend (código ${res.status}). Revisa que esté corriendo en el puerto 8000: ` +
        'en la carpeta backend ejecuta "python diagnostico.py" y mira la terminal de uvicorn.',
      )
    }
    throw new Error('Ocurrió un error inesperado.')
  }
  return data ?? {}
}
