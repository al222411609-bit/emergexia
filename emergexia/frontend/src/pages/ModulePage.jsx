import { useCallback, useEffect, useState } from 'react'
import { Link, Navigate, useLocation, useParams } from 'react-router-dom'
import { Plus, RefreshCw, ShieldCheck, Truck, X } from 'lucide-react'
import { api } from '../lib/api.js'
import { findModule } from '../lib/modules.js'
import FaceIdModal from '../components/FaceIdModal.jsx'

const slug = (v) => String(v).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
  .replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')

const OLD_BACKEND =
  'El servidor no confirmó que guardó en MongoDB: seguramente hay una versión ANTIGUA del backend corriendo en el puerto 8000. ' +
  'Ciérrala (python diagnostico.py te dice cuál) y vuelve a iniciar el backend.'

function emptyForm(fields) {
  return Object.fromEntries(
    fields.map((f) => [f.key, (f.type === 'checkboxes' || f.type === 'checkboxesAsync') ? [] : f.options ? f.options[0] : '']),
  )
}

export default function ModulePage() {
  const { module: key } = useParams()
  const mod = findModule(key)
  if (!mod || mod.custom) return <Navigate to="/" replace />
  return <ModuleView key={key} mod={mod} />
}

/** Carga las opciones de un <select> (o checkboxes) cuyos valores vienen de otro módulo. */
function useAsyncOptions(fields, active) {
  const [options, setOptions] = useState({})

  useEffect(() => {
    if (!active) return
    let cancelled = false
    const asyncFields = fields.filter((f) => f.asyncOptions)
    Promise.all(
      asyncFields.map((f) =>
        api(f.asyncOptions.path)
          .then((d) => (f.asyncOptions.filter ? d.items.filter(f.asyncOptions.filter) : d.items))
          .catch(() => []),
      ),
    ).then((lists) => {
      if (cancelled) return
      setOptions(Object.fromEntries(asyncFields.map((f, i) => [f.key, lists[i]])))
    })
    return () => { cancelled = true }
  }, [fields, active])

  return options
}

function ModuleView({ mod }) {
  const location = useLocation()
  const [items, setItems] = useState(null)
  const [source, setSource] = useState(null)
  const [notice, setNotice] = useState(location.state?.notice ?? null)
  const [error, setError] = useState('')
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState(() => emptyForm(mod.fields ?? []))
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState('')
  const [dispatchRow, setDispatchRow] = useState(null)   // emergencia que se está despachando
  const [dispatchOperador, setDispatchOperador] = useState('')
  const [dispatchStage, setDispatchStage] = useState('pick')  // pick | face
  const [operadoresCache, setOperadoresCache] = useState(null)
  const asyncOptions = useAsyncOptions(mod.fields ?? [], open)

  useEffect(() => {
    if (location.state?.notice) window.history.replaceState({}, '')   // el aviso no reaparece al recargar
  }, [location.state])

  const load = useCallback(() => {
    setError('')
    api(`/${mod.key}`)
      .then((d) => { setItems(d.items); setSource(d.source ?? null) })
      .catch((e) => setError(e.message))
  }, [mod.key])

  useEffect(load, [load])

  const set = (key, value) => setForm((f) => ({ ...f, [key]: value }))

  const toggleCheckbox = (key, option) => {
    setForm((f) => {
      const current = f[key] || []
      const next = current.includes(option) ? current.filter((v) => v !== option) : [...current, option]
      return { ...f, [key]: next }
    })
  }

  const save = async (e) => {
    e.preventDefault()
    setSaving(true)
    setFormError('')
    try {
      const body = Object.fromEntries(Object.entries(form).map(([k, v]) => [k, v === '' ? null : v]))
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

  // ── Despacho con verificación facial (solo módulo Emergencias) ──
  const canDispatch = (row) => mod.key === 'emergencias' && row.ambulancia && (row.paramedicos || []).length > 0
    && !['En camino', 'En sitio', 'Trasladando', 'Atendida', 'Cancelada'].includes(row.estado)

  const startDispatch = async (row) => {
    setDispatchRow(row)
    setDispatchOperador(row.paramedicos[0])
    setDispatchStage('pick')
    if (!operadoresCache) {
      try { setOperadoresCache((await api('/operadores')).items) } catch { setOperadoresCache([]) }
    }
  }

  const closeDispatch = () => { setDispatchRow(null); setDispatchStage('pick') }

  const confirmDispatch = async (distancia) => {
    try {
      await api(`/emergencias/${dispatchRow.id}/despacho`, {
        method: 'PATCH',
        body: { operador: dispatchOperador, verificado: true, distancia },
      })
      setNotice({ kind: 'ok', text: `✓ Salida verificada por Face ID (${dispatchOperador}). La ambulancia ya puede salir.` })
      closeDispatch()
      load()
    } catch (err) {
      setNotice({ kind: 'warn', text: err.message })
      closeDispatch()
    }
  }

  const operadorSeleccionado = operadoresCache?.find((o) => o.nombre === dispatchOperador)

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
          {mod.personForm ? (
            <Link className="btn-primary compact" to={`/${mod.key}/nuevo`} onClick={() => setNotice(null)}>
              <Plus size={16} /> {mod.nuevo} {mod.singular}
            </Link>
          ) : (
            <button className="btn-primary compact" onClick={() => { setNotice(null); setOpen((v) => !v) }}>
              {open ? <X size={16} /> : <Plus size={16} />} {open ? 'Cancelar' : `${mod.nuevo} ${mod.singular}`}
            </button>
          )}
        </div>
      </header>

      {notice && <p className={`notice ${notice.kind}`} role="status">{notice.text}</p>}

      {open && !mod.personForm && (
        <form className="panel form-grid" onSubmit={save}>
          {mod.fields.map((f) => {
            const opts = f.asyncOptions ? asyncOptions[f.key] : null
            return (
              <div key={f.key} className={`field ${f.wide || f.type === 'checkboxesAsync' || f.type === 'checkboxes' ? 'wide' : ''}`}>
                <label htmlFor={f.key}>{f.label}{f.required ? ' *' : ''}</label>
                {f.type === 'checkboxes' ? (
                  <div className="checkbox-group">
                    {f.options.map((o) => (
                      <label key={o} className="checkbox-option">
                        <input type="checkbox" checked={(form[f.key] || []).includes(o)} onChange={() => toggleCheckbox(f.key, o)} />
                        {o}
                      </label>
                    ))}
                  </div>
                ) : f.type === 'checkboxesAsync' ? (
                  <div className="checkbox-group">
                    {opts === null && <span className="muted small">Cargando…</span>}
                    {opts?.length === 0 && <span className="muted small">No hay opciones disponibles</span>}
                    {opts?.map((i) => {
                      const val = i[f.asyncOptions.valueKey]
                      return (
                        <label key={val} className="checkbox-option">
                          <input type="checkbox" checked={(form[f.key] || []).includes(val)} onChange={() => toggleCheckbox(f.key, val)} />
                          {f.asyncOptions.label(i)}
                        </label>
                      )
                    })}
                  </div>
                ) : f.options ? (
                  <select id={f.key} className="input" value={form[f.key]}
                          onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}>
                    {f.options.map((o) => <option key={o} value={o}>{o || '—'}</option>)}
                  </select>
                ) : f.asyncOptions ? (
                  <select id={f.key} className="input" value={form[f.key]}
                          onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}>
                    <option value="">{f.emptyLabel || 'Selecciona una opción'}</option>
                    {opts === null && <option disabled>Cargando…</option>}
                    {opts?.length === 0 && <option disabled>No hay opciones disponibles</option>}
                    {opts?.map((i) => (
                      <option key={i[f.asyncOptions.valueKey]} value={i[f.asyncOptions.valueKey]}>
                        {f.asyncOptions.label(i)}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input id={f.key} className="input" type={f.type || 'text'} value={form[f.key]} required={f.required}
                         onChange={(e) => setForm({ ...form, [f.key]: e.target.value })} />
                )}
                {f.hint && <p className="muted small">{f.hint}</p>}
              </div>
            )
          })}
          {formError && <p className="form-error wide" role="alert">{formError}</p>}
          <div className="wide">
            <button className="btn-primary compact" disabled={saving}>{saving ? 'Guardando…' : `Guardar ${mod.singular}`}</button>
          </div>
        </form>
      )}

      <div className="panel table-wrap">
        {error && <p className="form-error">{error} <button className="link" onClick={load}>Reintentar</button></p>}
        {!error && items === null && <p className="muted pad">Cargando datos…</p>}
        {!error && items?.length === 0 && (
          <p className="muted pad">
            Aún no hay registros.{' '}
            {mod.personForm
              ? <Link className="link" to={`/${mod.key}/nuevo`}>{mod.nuevo} {mod.singular}</Link>
              : <>Usa “{mod.nuevo} {mod.singular}” para crear el primero.</>}
          </p>
        )}
        {items?.length > 0 && (
          <table>
            <thead>
              <tr>
                {mod.columns.map((c) => <th key={c.key}>{c.label}</th>)}
                {mod.key === 'emergencias' && <th></th>}
              </tr>
            </thead>
            <tbody>
              {items.map((row) => (
                <tr key={row.id}>
                  {mod.columns.map((c) => (
                    <td key={c.key}>
                      {c.photo
                        ? (row.foto
                            ? <img className="row-photo" src={row.foto} alt="" />
                            : <span className="row-photo row-photo-empty" aria-hidden="true" />)
                        : c.dispatch
                          ? (row.despacho?.verificado
                              ? <span className="badge b-disponible"><ShieldCheck size={13} /> {row.despacho.operador}</span>
                              : <span className="muted small">—</span>)
                          : c.badge && row[c.key]
                            ? <span className={`badge b-${slug(row[c.key])}`}>{row[c.key]}</span>
                            : Array.isArray(row[c.key]) ? (row[c.key].join(', ') || '—') : (row[c.key] ?? '—')}
                    </td>
                  ))}
                  {mod.key === 'emergencias' && (
                    <td>
                      {canDispatch(row) && (
                        <button type="button" className="btn-ghost" onClick={() => startDispatch(row)}>
                          <Truck size={14} /> Despachar
                        </button>
                      )}
                    </td>
                  )}
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

      {dispatchRow && dispatchStage === 'pick' && (
        <div className="face-modal-backdrop" role="dialog" aria-modal="true">
          <div className="face-modal">
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0 }}>Despachar {dispatchRow.folio}</h3>
              <button type="button" className="btn-ghost" onClick={closeDispatch}><X size={16} /></button>
            </header>
            <p className="muted small">
              Elige al paramédico que va a verificar su identidad con la cámara antes de que la
              ambulancia {dispatchRow.ambulancia} pueda salir.
            </p>
            <div className="field">
              <label>Paramédico</label>
              <select className="input" value={dispatchOperador} onChange={(e) => setDispatchOperador(e.target.value)}>
                {dispatchRow.paramedicos.map((n) => <option key={n} value={n}>{n}</option>)}
              </select>
            </div>
            <div className="form-buttons">
              <button type="button" className="btn-primary compact" disabled={!operadoresCache}
                      onClick={() => setDispatchStage('face')}>
                {operadoresCache ? 'Continuar a Face ID' : 'Cargando…'}
              </button>
              <button type="button" className="btn-ghost compact" onClick={closeDispatch}>Cancelar</button>
            </div>
          </div>
        </div>
      )}

      {dispatchRow && dispatchStage === 'face' && (
        <FaceIdModal operador={operadorSeleccionado} onVerified={confirmDispatch} onCancel={closeDispatch} />
      )}
    </section>
  )
}
