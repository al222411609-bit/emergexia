import Heartbeat from './Heartbeat.jsx'
import { LogoMark } from './Logo.jsx'

/** Pantalla de carga a pantalla completa: fondo rojo + el latido (Heartbeat_Lottie_Animation.json). */
export default function LoadingScreen({ text = 'Cargando' }) {
  return (
    <div className="loading-screen" role="status" aria-live="polite">
      <LogoMark size={56} tone="light" />
      <p className="loading-text">{text}…</p>
      <Heartbeat className="loading-ecg" />
    </div>
  )
}
