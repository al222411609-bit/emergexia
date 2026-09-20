import { Ambulance, CircleDot, Headset, Settings, Siren, Stethoscope, UserRound, House } from 'lucide-react'

export const HOME = { path: '/', label: 'Inicio', navIcon: House }

// Cada módulo alimenta: tarjeta de inicio, menú lateral, tabla y formulario.
export const MODULES = [
  {
    key: 'doctores',
    label: 'Doctores',
    description: 'Gestiona el personal médico y sus especialidades',
    icon: Stethoscope,
    navIcon: UserRound,
    singular: 'doctor',
    nuevo: 'Nuevo',
    columns: [
      { key: 'nombre', label: 'Nombre' },
      { key: 'especialidad', label: 'Especialidad' },
      { key: 'telefono', label: 'Teléfono' },
      { key: 'estado', label: 'Estado', badge: true },
    ],
    fields: [
      { key: 'nombre', label: 'Nombre completo', required: true },
      { key: 'especialidad', label: 'Especialidad', required: true },
      { key: 'telefono', label: 'Teléfono' },
      { key: 'estado', label: 'Estado', options: ['Activo', 'En guardia', 'Descanso'] },
    ],
  },
  {
    key: 'ambulancias',
    label: 'Ambulancias',
    description: 'Administra la flota de ambulancias y su disponibilidad',
    icon: Ambulance,
    navIcon: Ambulance,
    singular: 'ambulancia',
    nuevo: 'Nueva',
    columns: [
      { key: 'placa', label: 'Placa' },
      { key: 'tipo', label: 'Tipo' },
      { key: 'conductor', label: 'Conductor' },
      { key: 'estado', label: 'Estado', badge: true },
    ],
    fields: [
      { key: 'placa', label: 'Placa', required: true },
      { key: 'tipo', label: 'Tipo', options: ['Básica', 'Avanzada'] },
      { key: 'conductor', label: 'Conductor' },
      { key: 'estado', label: 'Estado', options: ['Disponible', 'En servicio', 'Mantenimiento'] },
    ],
  },
  {
    key: 'emergencias',
    label: 'Emergencias',
    description: 'Atiende y da seguimiento a las emergencias',
    icon: Siren,
    navIcon: CircleDot,
    singular: 'emergencia',
    nuevo: 'Nueva',
    columns: [
      { key: 'folio', label: 'Folio' },
      { key: 'descripcion', label: 'Descripción' },
      { key: 'prioridad', label: 'Prioridad', badge: true },
      { key: 'ambulancia', label: 'Ambulancia' },
      { key: 'estado', label: 'Estado', badge: true },
    ],
    fields: [
      { key: 'descripcion', label: 'Descripción', required: true },
      { key: 'prioridad', label: 'Prioridad', options: ['Alta', 'Media', 'Baja'] },
      { key: 'ambulancia', label: 'Ambulancia asignada (placa)' },
      { key: 'estado', label: 'Estado', options: ['Pendiente', 'Asignada', 'En curso', 'Cerrada'] },
    ],
  },
  {
    key: 'operadores',
    label: 'Operadores',
    description: 'Gestiona el equipo de operadores y sus turnos',
    icon: Headset,
    navIcon: UserRound,
    singular: 'operador',
    nuevo: 'Nuevo',
    columns: [
      { key: 'nombre', label: 'Nombre' },
      { key: 'turno', label: 'Turno' },
      { key: 'extension', label: 'Extensión' },
      { key: 'estado', label: 'Estado', badge: true },
    ],
    fields: [
      { key: 'nombre', label: 'Nombre completo', required: true },
      { key: 'turno', label: 'Turno', options: ['Matutino', 'Vespertino', 'Nocturno'] },
      { key: 'extension', label: 'Extensión' },
      { key: 'estado', label: 'Estado', options: ['En línea', 'Desconectado'] },
    ],
  },
  {
    key: 'configuracion',
    label: 'Configuración',
    description: 'Ajusta las preferencias del sistema y tu cuenta',
    icon: Settings,
    navIcon: Settings,
    custom: true,
  },
]

export const findModule = (key) => MODULES.find((m) => m.key === key)
