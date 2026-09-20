import { RefreshCw } from 'lucide-react'
import Heartbeat from './Heartbeat.jsx'
import { Logo } from './Logo.jsx'
import ambulancePhoto from '../assets/ambulance.jpg'

/**
 * Pantalla completa roja y difuminada, con el pulso animado de fondo: la misma
 * identidad visual del login. Se usa mientras la app carga (sesión, datos) y
 * cuando algo falla de forma inesperada (sin red, error de renderizado, etc.),
 * en vez de una pantalla en blanco o un mensaje seco.
 *
 * `mode`: "loading" (por defecto) o "error".
 * `message`: título corto. `detail`: línea secundaria con más contexto.
 * `onRetry`: si se define, muestra un botón "Reintentar" (solo en modo error).
 */
export default function BrandLoader({ mode = 'loading', message, detail, onRetry }) {
  const isError = mode === 'error'
  const title = message || (isError ? 'Algo salió mal' : 'Cargando…')

  return (
    <div className="brand-loader" role={isError ? 'alert' : 'status'} aria-live="polite">
      <img className="loader-photo" src={ambulancePhoto} alt="" />
      <div className="loader-tint" aria-hidden="true" />
      <Heartbeat className="loader-ecg" color="#fff" />

      <div className="loader-body">
        <Logo size={44} />
        <p className="loader-title">{title}</p>
        {detail && <p className="loader-detail">{detail}</p>}

        {isError ? (
          <button type="button" className="btn-ghost loader-retry" onClick={onRetry || (() => window.location.reload())}>
            <RefreshCw size={15} /> Reintentar
          </button>
        ) : (
          <div className="loader-dots" aria-hidden="true"><span /><span /><span /></div>
        )}
      </div>
    </div>
  )
}
