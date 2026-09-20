import { useCallback, useEffect, useState } from 'react'
import { Navigate, useParams } from 'react-router-dom'
import { Plus, X } from 'lucide-react'
import { api } from '../lib/api.js'
import { findModule } from '../lib/modules.js'

const slug = (v) => String(v).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, '-')

function emptyForm(fields) {
  return Object.fromEntries(fields.map((f) => [f.key, f.options ? f.options[0] : '']))
}

export default function ModulePage() {
  const { module: key } = useParams()
  const mod = findModule(key)
  if (!mod || mod.custom) return <Navigate to="/" replace />
  return <ModuleView key={key} mod={mod} />
}

function ModuleView({ mod }) {
  const [items, setItems] = useState(null)
  const [error, setError] = useState('')
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState(() => emptyForm(mod.fields))
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState('')

  const load = useCallback(() => {
    setError('')
    api(`/${mod.key}`).then((d) => setItems(d.items)).catch((e) => setError(e.message))
  }, [mod.key])

  useEffect(load, [load])

  const save = async (e) => {
    e.preventDefault()
    setSaving(true)
    setFormError('')
    try {
      const body = { ...form }
      if (body.ambulancia === '') body.ambulancia = null
      await api(`/${mod.key}`, { method: 'POST', body })
      setOpen(false)
      setForm(emptyForm(mod.fields))
      load()
    } catch (err) {
      setFormError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="module-view">
      <header className="view-head">
        <div>
          <h1>{mod.label}</h1>
          <p>{mod.description}</p>
        </div>
        <button className="btn-primary compact" onClick={() => setOpen((v) => !v)}>
          {open ? <X size={16} /> : <Plus size={16} />} {open ? 'Cancelar' : `${mod.nuevo} ${mod.singular}`}
        </button>
      </header>

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

      <div className="panel table-wrap">
        {error && <p className="form-error">{error} <button className="link" onClick={load}>Reintentar</button></p>}
        {!error && items === null && <p className="muted pad">Consultando datos en Spark…</p>}
        {!error && items?.length === 0 && (
          <p className="muted pad">Aún no hay registros. Usa “{mod.nuevo} {mod.singular}” para crear el primero.</p>
        )}
        {items?.length > 0 && (
          <table>
            <thead>
              <tr>{mod.columns.map((c) => <th key={c.key}>{c.label}</th>)}</tr>
            </thead>
            <tbody>
              {items.map((row) => (
                <tr key={row.id}>
                  {mod.columns.map((c) => (
                    <td key={c.key}>
                      {c.badge && row[c.key]
                        ? <span className={`badge b-${slug(row[c.key])}`}>{row[c.key]}</span>
                        : row[c.key] ?? '—'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  )
}
