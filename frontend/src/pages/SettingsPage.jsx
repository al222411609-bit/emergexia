import { useCallback, useEffect, useState } from 'react'
import { RefreshCw } from 'lucide-react'
import { api } from '../lib/api.js'
import { useAuth } from '../lib/auth.jsx'

export default function SettingsPage() {
  const { user } = useAuth()
  const [spark, setSpark] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const check = useCallback(() => {
    setBusy(true)
    setError('')
    api('/spark/status')
      .then(setSpark)
      .catch((e) => { setSpark(null); setError(e.message) })
      .finally(() => setBusy(false))
  }, [])

  useEffect(check, [check])

  return (
    <section className="module-view">
      <header className="view-head">
        <div>
          <h1>Configuración</h1>
          <p>Ajusta las preferencias del sistema y tu cuenta</p>
        </div>
      </header>

      <div className="settings-grid">
        <div className="panel">
          <h2 className="panel-title">Tu cuenta</h2>
          <dl className="kv">
            <dt>Nombre</dt><dd>{user.full_name}</dd>
            <dt>Usuario</dt><dd>{user.username}</dd>
            <dt>Rol</dt><dd>{user.role}</dd>
          </dl>
        </div>

        <div className="panel">
          <div className="panel-title-row">
            <h2 className="panel-title">Conexión con Spark</h2>
            <button className="btn-ghost" onClick={check} disabled={busy}>
              <RefreshCw size={14} className={busy ? 'spin' : ''} /> Verificar
            </button>
          </div>
          {error && <p className="form-error">{error}</p>}
          {spark && (
            <dl className="kv">
              <dt>Estado</dt><dd><span className="badge b-activo">Conectado</span></dd>
              <dt>Master</dt><dd>{spark.master}</dd>
              <dt>Versión</dt><dd>Spark {spark.version}</dd>
              <dt>Aplicación</dt><dd>{spark.app_name}</dd>
              <dt>ID de aplicación</dt><dd>{spark.app_id}</dd>
              <dt>Datos</dt><dd>{spark.data_dir}</dd>
            </dl>
          )}
          {!spark && !error && <p className="muted">Verificando…</p>}
        </div>
      </div>
    </section>
  )
}
