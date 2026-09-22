import { useCallback, useEffect, useState } from 'react'
<<<<<<< HEAD
import { Navigate, useLocation, useNavigate, useParams } from 'react-router-dom'
import { Plus, RefreshCw } from 'lucide-react'
import { api } from '../lib/api.js'
import { findModule } from '../lib/modules.js'
import { slug } from '../lib/moduleHelpers.js'
=======
import { Navigate, useParams } from 'react-router-dom'
import { Plus, RefreshCw, X } from 'lucide-react'
import { api } from '../lib/api.js'
import { findModule } from '../lib/modules.js'

const slug = (v) => String(v).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, '-')

const OLD_BACKEND =
  'El servidor no confirmó que guardó en MongoDB: seguramente hay una versión ANTIGUA del backend corriendo en el puerto 8000. ' +
  'Ciérrala (python diagnostico.py te dice cuál) y vuelve a iniciar el backend.'

function emptyForm(fields) {
  return Object.fromEntries(fields.map((f) => [f.key, f.options ? f.options[0] : '']))
}
>>>>>>> ecb314e0be1671f363a199180d1176f6feb81edb

export default function ModulePage() {
  const { module: key } = useParams()
  const mod = findModule(key)
  if (!mod || mod.custom) return <Navigate to="/" replace />
  return <ModuleView key={key} mod={mod} />
}

function ModuleView({ mod }) {
<<<<<<< HEAD
  const navigate = useNavigate()
  const location = useLocation()
  const [items, setItems] = useState(null)
  const [source, setSource] = useState(null)
  const [notice, setNotice] = useState(location.state?.notice ?? null)
  const [error, setError] = useState('')

  // El aviso de "guardado con éxito" llega desde la pantalla del formulario a
  // través del estado de navegación; se limpia del historial para que no
  // reaparezca si el usuario recarga o vuelve con el botón "atrás".
  useEffect(() => {
    if (location.state?.notice) {
      navigate(location.pathname, { replace: true, state: {} })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
=======
  const [items, setItems] = useState(null)
  const [source, setSource] = useState(null)
  const [notice, setNotice] = useState(null)
  const [error, setError] = useState('')
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState(() => emptyForm(mod.fields))
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState('')
>>>>>>> ecb314e0be1671f363a199180d1176f6feb81edb

  const load = useCallback(() => {
    setError('')
    api(`/${mod.key}`)
      .then((d) => { setItems(d.items); setSource(d.source ?? null) })
      .catch((e) => setError(e.message))
  }, [mod.key])

  useEffect(load, [load])

<<<<<<< HEAD
  const goToRow = (row) => navigate(`/${mod.key}/${row.id}`)
=======
  const save = async (e) => {
    e.preventDefault()
    setSaving(true)
    setFormError('')
    try {
      const body = { ...form }
      if (body.ambulancia === '') body.ambulancia = null
      const saved = await api(`/${mod.key}`, { method: 'POST', body })
      const done = mod.nuevo === 'Nueva' ? 'guardada' : 'guardado'
      const name = mod.singular.charAt(0).toUpperCase() + mod.singular.slice(1)
      setNotice(
        saved.saved_in
          ? { kind: 'ok', text: `✓ ${name} ${done} en MongoDB (${saved.saved_in}), id ${saved.id}.` }
          : { kind: 'warn', text: OLD_BACKEND },
      )
      setOpen(false)
      setForm(emptyForm(mod.fields))
      load()
    } catch (err) {
      setFormError(err.message)
    } finally {
      setSaving(false)
    }
  }
>>>>>>> ecb314e0be1671f363a199180d1176f6feb81edb

  return (
    <section className="module-view">
      <header className="view-head">
        <div>
          <h1>{mod.label}</h1>
          <p>{mod.description}</p>
        </div>
        <div className="head-actions">
          <button className="btn-ghost tall" onClick={load} title="Volver a leer los datos de MongoDB">
            <RefreshCw size={15} /> Actualizar
          </button>
<<<<<<< HEAD
          <button className="btn-primary compact" onClick={() => navigate(`/${mod.key}/nuevo`)}>
            <Plus size={16} /> {mod.nuevo} {mod.singular}
=======
          <button className="btn-primary compact" onClick={() => { setNotice(null); setOpen((v) => !v) }}>
            {open ? <X size={16} /> : <Plus size={16} />} {open ? 'Cancelar' : `${mod.nuevo} ${mod.singular}`}
>>>>>>> ecb314e0be1671f363a199180d1176f6feb81edb
          </button>
        </div>
      </header>

      {notice && <p className={`notice ${notice.kind}`} role="status">{notice.text}</p>}

<<<<<<< HEAD
=======
      {open && (
        <form className="panel form-grid" onSubmit={save}>
          {mod.fields.map((f) => (
            <div key={f.key} className="field">
              <label htmlFor={f.key}>{f.label}</label>
              {f.options ? (
                <select id={f.key} className="input" value={form[f.key]}
                        onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}>
                  {f.options.map((o) => <option key={o}>{o}</option>)}
                </select>
              ) : (
                <input id={f.key} className="input" value={form[f.key]} required={f.required}
                       onChange={(e) => setForm({ ...form, [f.key]: e.target.value })} />
              )}
            </div>
          ))}
          {formError && <p className="form-error wide" role="alert">{formError}</p>}
          <div className="wide">
            <button className="btn-primary compact" disabled={saving}>{saving ? 'Guardando…' : `Guardar ${mod.singular}`}</button>
          </div>
        </form>
      )}

>>>>>>> ecb314e0be1671f363a199180d1176f6feb81edb
      <div className="panel table-wrap">
        {error && <p className="form-error">{error} <button className="link" onClick={load}>Reintentar</button></p>}
        {!error && items === null && <p className="muted pad">Cargando datos…</p>}
        {!error && items?.length === 0 && (
          <p className="muted pad">Aún no hay registros. Usa “{mod.nuevo} {mod.singular}” para crear el primero.</p>
        )}
        {items?.length > 0 && (
          <table>
            <thead>
<<<<<<< HEAD
              <tr>
                {mod.columns.map((c) => <th key={c.key}>{c.label}</th>)}
                <th aria-hidden="true"></th>
              </tr>
            </thead>
            <tbody>
              {items.map((row) => (
                <tr
                  key={row.id}
                  className="row-link"
                  tabIndex={0}
                  role="link"
                  aria-label={`Ver perfil de ${row[mod.columns[0]?.key] ?? mod.singular}`}
                  onClick={() => goToRow(row)}
                  onKeyDown={(e) => { if (e.key === 'Enter') goToRow(row) }}
                >
=======
              <tr>{mod.columns.map((c) => <th key={c.key}>{c.label}</th>)}</tr>
            </thead>
            <tbody>
              {items.map((row) => (
                <tr key={row.id}>
>>>>>>> ecb314e0be1671f363a199180d1176f6feb81edb
                  {mod.columns.map((c) => (
                    <td key={c.key}>
                      {c.badge && row[c.key]
                        ? <span className={`badge b-${slug(row[c.key])}`}>{row[c.key]}</span>
                        : row[c.key] ?? '—'}
                    </td>
                  ))}
<<<<<<< HEAD
                  <td className="row-link-arrow" aria-hidden="true">›</td>
=======
>>>>>>> ecb314e0be1671f363a199180d1176f6feb81edb
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {items && (
          <p className={`source-note ${source ? '' : 'warn'}`}>
            {source
              ? `${items.length} registro(s) · leído de MongoDB: ${source}`
              : '⚠ Este servidor no reporta MongoDB: probablemente es una versión antigua del backend.'}
          </p>
        )}
      </div>
    </section>
  )
}
