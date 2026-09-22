import { Clock } from 'lucide-react'
import { useNow } from '../lib/useNow.js'

export default function ClockWidget() {
  const now = useNow()
  const date = new Intl.DateTimeFormat('es-MX', { day: 'numeric', month: 'long', year: 'numeric' }).format(now)
  const time = new Intl.DateTimeFormat('es-MX', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true }).format(now)

  return (
    <div className="clock-widget" role="status" aria-label="Fecha y hora actual">
      <span className="clock-widget-icon"><Clock size={15} /></span>
      <span className="clock-widget-text">
        <strong>{time}</strong>
        <small>{date}</small>
      </span>
    </div>
  )
}
