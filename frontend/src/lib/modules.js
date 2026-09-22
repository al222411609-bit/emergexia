import { Ambulance, CircleDot, Headset, Settings, Siren, Stethoscope, UserRound, House } from 'lucide-react'

export const HOME = { path: '/', label: 'Inicio', navIcon: House }

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

const IDIOMAS = ['Español', 'Inglés', 'Lengua de señas', 'Náhuatl', 'Maya', 'Otomí', 'Otro']
const CERTIFICACIONES = [
  'Soporte Vital Básico (BLS)', 'Soporte Vital Avanzado (ACLS)',
  'Despacho de Emergencias / Triage', 'RCP', 'Primeros Auxilios',
]
const EQUIPAMIENTO = ['Desfibrilador', 'Oxigenoterapia', 'Kit de trauma', 'Ventilador', 'Camilla', 'Succión']

/** Campos comunes a Doctores y Operadores (pantalla completa de alta, con foto). */
const PERSON_FIELDS = [
  { key: 'nombres', label: 'Nombre(s)', required: true, autoComplete: 'given-name' },
  { key: 'apellidos', label: 'Apellidos', required: true, autoComplete: 'family-name' },
  { key: 'celular', label: 'Número de celular', required: true, type: 'tel', autoComplete: 'tel', placeholder: '55 1234 5678' },
  {
    key: 'correo', label: 'Correo electrónico', required: true, type: 'email', autoComplete: 'email',
    placeholder: 'nombre@correo.com', pattern: EMAIL_RE, patternError: 'Escribe un correo válido, con "@" (ej. nombre@correo.com).',
  },
]

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
    personForm: true,   // "Nuevo doctor" abre una pantalla completa (con cámara), no un formulario en línea
    columns: [
      { key: 'foto', label: '', photo: true },
      { key: 'nombre', label: 'Nombre' },
      { key: 'especialidad', label: 'Especialidad' },
      { key: 'celular', label: 'Celular' },
      { key: 'correo', label: 'Correo' },
      { key: 'estado', label: 'Estado', badge: true },
    ],
    personFields: [
      ...PERSON_FIELDS,
      { key: 'especialidad', label: 'Especialidad', required: true, placeholder: 'Ej. Cardiología' },
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
      { key: 'numero_unidad', label: 'Unidad' },
      { key: 'placa', label: 'Placa' },
      { key: 'tipo', label: 'Tipo' },
      { key: 'conductor', label: 'Conductor' },
      { key: 'base_asignada', label: 'Base' },
      { key: 'estado', label: 'Estado', badge: true },
    ],
    fields: [
      { key: 'numero_unidad', label: 'Número de unidad / ficha', required: true, placeholder: 'Ej. AMB-01', section: 'Datos del vehículo' },
      { key: 'placa', label: 'Placa', required: true },
      { key: 'modelo', label: 'Modelo / año del vehículo', placeholder: 'Ej. Ford Transit' },
      { key: 'anio', label: 'Año', type: 'number', placeholder: '2022' },
      { key: 'kilometraje', label: 'Kilometraje actual', type: 'number', placeholder: '45000' },
      { key: 'tipo', label: 'Tipo', options: ['Básica', 'Avanzada'] },

      { key: 'equipamiento', label: 'Nivel de equipamiento médico', type: 'checkboxes', options: EQUIPAMIENTO, section: 'Capacidad y equipamiento médico', wide: true },
      { key: 'base_asignada', label: 'Ubicación / base asignada', placeholder: 'Hospital, estación o zona' },

      { key: 'conductor', label: 'Conductor', section: 'Contacto y personal' },
      { key: 'radio', label: 'Teléfono / radio de la unidad' },
      {
        key: 'tripulacion', label: 'Paramédico(s) / tripulación a bordo', type: 'checkboxesAsync', wide: true,
        asyncOptions: { path: '/operadores', valueKey: 'nombre', label: (i) => `${i.nombre} · ${i.turno}`, filter: (i) => i.estado === 'En línea' },
      },

      { key: 'ultimo_mantenimiento', label: 'Fecha de último mantenimiento', type: 'date', section: 'Mantenimiento y disponibilidad' },
      { key: 'motivo_inactividad', label: 'Motivo de inactividad (si aplica)', placeholder: 'Solo si está en mantenimiento / fuera de servicio' },
      { key: 'estado', label: 'Estado', options: ['Disponible', 'En servicio', 'Mantenimiento', 'Fuera de servicio'] },
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
      { key: 'paciente_nombre', label: 'Paciente' },
      { key: 'prioridad', label: 'Prioridad', badge: true },
      { key: 'ambulancia', label: 'Ambulancia' },
      { key: 'operador', label: 'Operador' },
      { key: 'doctor', label: 'Doctor' },
      { key: 'estado', label: 'Estado', badge: true },
      { key: 'despacho', label: 'Salida verificada', dispatch: true },
    ],
    fields: [
      { key: 'descripcion', label: 'Descripción de la emergencia', required: true },
      { key: 'direccion', label: 'Dirección de la emergencia', required: true },
      { key: 'prioridad', label: 'Prioridad / triage', options: ['Crítica / Roja', 'Alta / Amarilla', 'Baja / Verde'] },

      { key: 'paciente_nombre', label: 'Nombre del paciente', placeholder: 'Ej. Juan Pérez o Desconocido / NN', section: 'Datos del paciente' },
      { key: 'paciente_edad', label: 'Edad', type: 'number' },
      { key: 'paciente_genero', label: 'Género', options: ['No especifica', 'Masculino', 'Femenino', 'Otro'] },
      { key: 'hospital_destino', label: 'Hospital de destino' },

      {
        key: 'ambulancia', label: 'Ambulancia disponible', allowEmpty: true, emptyLabel: 'Sin asignar aún', section: 'Asignación',
        asyncOptions: { path: '/ambulancias', valueKey: 'numero_unidad', label: (i) => `${i.numero_unidad || i.placa} · ${i.tipo}`, filter: (i) => i.estado === 'Disponible' },
      },
      {
        key: 'operador', label: 'Operador a cargo', allowEmpty: true, emptyLabel: 'Sin asignar aún',
        asyncOptions: { path: '/operadores', valueKey: 'nombre', label: (i) => `${i.nombre} · ${i.turno}`, filter: (i) => i.estado === 'En línea' },
      },
      {
        key: 'doctor', label: 'Doctor asignado', allowEmpty: true, emptyLabel: 'Sin asignar aún',
        asyncOptions: { path: '/doctores', valueKey: 'nombre', label: (i) => `${i.nombre} · ${i.especialidad}`, filter: (i) => i.estado === 'Activo' || i.estado === 'En guardia' },
      },
      {
        key: 'paramedicos', label: 'Paramédicos que salen en la ambulancia', type: 'checkboxesAsync', wide: true,
        hint: 'Al despachar, se pedirá verificar con Face ID a uno de estos paramédicos antes de que la ambulancia pueda salir.',
        asyncOptions: { path: '/operadores', valueKey: 'nombre', label: (i) => `${i.nombre} · ${i.turno}`, filter: (i) => i.estado === 'En línea' },
      },

      { key: 'estado', label: 'Estado', options: ['Pendiente', 'En camino', 'En sitio', 'Trasladando', 'Atendida', 'Cancelada'], section: 'Estado' },
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
    personForm: true,
    columns: [
      { key: 'foto', label: '', photo: true },
      { key: 'nombre', label: 'Nombre' },
      { key: 'rol', label: 'Rol' },
      { key: 'turno', label: 'Turno' },
      { key: 'celular', label: 'Celular' },
      { key: 'correo', label: 'Correo' },
      { key: 'estado', label: 'Estado', badge: true },
    ],
    personFields: [
      ...PERSON_FIELDS,
      { key: 'curp', label: 'CURP / DNI / Identificación oficial', required: true, section: 'Datos identificativos y de seguridad' },
      { key: 'pin_acceso', label: 'Contraseña temporal / PIN de acceso (opcional)', type: 'password', hint: 'Solo si el operador iniciará sesión con su propia cuenta.' },
      { key: 'rol', label: 'Rol / nivel de permisos', options: ['Operador Jr.', 'Operador Sr.', 'Supervisor de Cabina'] },

      { key: 'centro_control', label: 'Centro de control / base / sucursal', required: true, section: 'Información operativa y de asignación' },
      { key: 'cabina', label: 'Cabina / estación de trabajo', required: true, placeholder: 'Ej. Escritorio 4' },
      { key: 'turno', label: 'Turno', options: ['Matutino', 'Vespertino', 'Nocturno'] },
      { key: 'extension', label: 'Extensión (opcional)', required: false },
      { key: 'idiomas', label: 'Idiomas / lenguas habladas', type: 'checkboxes', options: IDIOMAS, required: true, wide: true },
      { key: 'certificaciones', label: 'Certificaciones / capacitaciones', type: 'checkboxes', options: CERTIFICACIONES, wide: true },

      { key: 'contacto_emergencia_nombre', label: 'Nombre de contacto de emergencia', required: true, section: 'Contacto de emergencia y salud' },
      { key: 'contacto_emergencia_telefono', label: 'Teléfono de contacto de emergencia', required: true, type: 'tel' },
      { key: 'parentesco', label: 'Parentesco', required: true, options: ['Familiar', 'Cónyuge', 'Padre/Madre', 'Hermano/a', 'Amigo', 'Otro'] },
      { key: 'tipo_sangre', label: 'Tipo de sangre (opcional)', options: ['', 'O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'] },
      { key: 'alergias', label: 'Alergias importantes (opcional)' },

      { key: 'estado', label: 'Estado', options: ['En línea', 'Desconectado'], section: 'Estado' },
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
