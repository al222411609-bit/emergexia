import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

MAX_PHOTO_CHARS = 900_000   # ~650 KB de imagen; de sobra para una foto de perfil comprimida

IDIOMAS_VALIDOS = ["Español", "Inglés", "Lengua de señas", "Náhuatl", "Maya", "Otomí", "Otro"]
CERTIFICACIONES_VALIDAS = [
    "Soporte Vital Básico (BLS)", "Soporte Vital Avanzado (ACLS)",
    "Despacho de Emergencias / Triage", "RCP", "Primeros Auxilios",
]
EQUIPAMIENTO_VALIDO = [
    "Desfibrilador", "Oxigenoterapia", "Kit de trauma", "Ventilador", "Camilla", "Succión",
]


class LoginIn(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


def _valida_telefono(v: str) -> str:
    digits = re.sub(r"[\s()\-+]", "", v)
    if not digits.isdigit() or not (8 <= len(digits) <= 15):
        raise ValueError("El teléfono debe tener solo números (8 a 15 dígitos), puede incluir espacios o guiones.")
    return v.strip()


def _valida_foto(v: str | None) -> str | None:
    if v is None or v == "":
        return None
    if not v.startswith("data:image/"):
        raise ValueError("La fotografía no tiene un formato válido. Vuelve a tomarla o súbela de nuevo.")
    if len(v) > MAX_PHOTO_CHARS:
        raise ValueError("La fotografía es muy pesada. Se comprime automáticamente; intenta tomarla de nuevo.")
    return v


class PersonBase(BaseModel):
    """Campos comunes a doctores y operadores."""
    nombres: str = Field(min_length=2, max_length=80)
    apellidos: str = Field(min_length=2, max_length=80)
    celular: str = Field(min_length=8, max_length=20)
    correo: EmailStr
    foto: str | None = None   # imagen en base64 (data:image/...;base64,...), tomada con la cámara
    # La cámara del navegador ya exige detectar una cara antes de dejar tomar la foto (ver
    # frontend/src/components/PhotoCapture.jsx + faceApi.js); aquí solo revisamos formato/tamaño.
    foto_verificada: bool = False   # true si face-api.js detectó una cara real al capturarla
    estado: str

    @field_validator("celular")
    @classmethod
    def _solo_numero(cls, v: str) -> str:
        return _valida_telefono(v)

    @field_validator("foto")
    @classmethod
    def _foto_valida(cls, v: str | None) -> str | None:
        return _valida_foto(v)


class DoctorIn(PersonBase):
    especialidad: str = Field(min_length=2)
    estado: Literal["Activo", "En guardia", "Descanso"] = "Activo"


class OperatorIn(PersonBase):
    # 1) Datos identificativos y de seguridad
    curp: str = Field(min_length=4, max_length=25, description="CURP / DNI / Identificación oficial")
    pin_acceso: str | None = Field(default=None, min_length=4, max_length=20,
                                    description="Contraseña temporal / PIN, si iniciará sesión con cuenta propia")
    rol: Literal["Operador Jr.", "Operador Sr.", "Supervisor de Cabina"] = "Operador Jr."

    # 2) Información operativa y de asignación
    centro_control: str = Field(min_length=2, max_length=120)
    cabina: str = Field(min_length=1, max_length=20)
    idiomas: list[str] = Field(min_length=1)
    certificaciones: list[str] = Field(default_factory=list)

    # 3) Contacto de emergencia y salud
    contacto_emergencia_nombre: str = Field(min_length=2, max_length=120)
    contacto_emergencia_telefono: str = Field(min_length=8, max_length=20)
    parentesco: str = Field(min_length=2, max_length=40)
    tipo_sangre: Literal["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-", ""] = ""
    alergias: str = ""

    turno: Literal["Matutino", "Vespertino", "Nocturno"] = "Matutino"
    extension: str = ""
    estado: Literal["En línea", "Desconectado"] = "En línea"

    @field_validator("contacto_emergencia_telefono")
    @classmethod
    def _tel_emergencia(cls, v: str) -> str:
        return _valida_telefono(v)

    @field_validator("idiomas", "certificaciones")
    @classmethod
    def _listas_no_vacias(cls, v: list[str]) -> list[str]:
        return [x.strip() for x in v if x and x.strip()]


class AmbulanceIn(BaseModel):
    # 1) Datos del vehículo
    placa: str = Field(min_length=2)
    numero_unidad: str = Field(min_length=1, max_length=20, description="Número económico / ficha, ej. AMB-01")
    modelo: str = Field(default="", max_length=80)
    anio: int | None = Field(default=None, ge=1990, le=2100)
    kilometraje: int | None = Field(default=None, ge=0)

    tipo: Literal["Básica", "Avanzada"] = "Básica"
    conductor: str = ""
    estado: Literal["Disponible", "En servicio", "Mantenimiento", "Fuera de servicio"] = "Disponible"

    # 2) Capacidad y equipamiento médico
    equipamiento: list[str] = Field(default_factory=list)
    base_asignada: str = Field(default="", max_length=120)

    # 3) Contacto y personal
    radio: str = Field(default="", max_length=30, description="Teléfono / radio de la unidad")
    tripulacion: list[str] = Field(default_factory=list, description="Nombres de operadores/paramédicos a bordo")

    # 4) Mantenimiento y disponibilidad
    ultimo_mantenimiento: str = Field(default="", description="Fecha (YYYY-MM-DD)")
    motivo_inactividad: str = Field(default="", max_length=200)

    @field_validator("equipamiento", "tripulacion")
    @classmethod
    def _listas_no_vacias(cls, v: list[str]) -> list[str]:
        return [x.strip() for x in v if x and x.strip()]


class EmergencyIn(BaseModel):
    descripcion: str = Field(min_length=3)
    prioridad: Literal["Crítica / Roja", "Alta / Amarilla", "Baja / Verde"] = "Alta / Amarilla"
    estado: Literal["Pendiente", "En camino", "En sitio", "Trasladando", "Atendida", "Cancelada"] = "Pendiente"

    ambulancia: str | None = None    # placa/número de unidad de la ambulancia asignada
    operador: str | None = None      # nombre del operador a cargo
    doctor: str | None = None        # nombre del doctor asignado
    paramedicos: list[str] = Field(default_factory=list, description="Operadores que salen a bordo de la ambulancia")

    tipo_emergencia: Literal[
        "Médica", "Traumatológica", "Accidente vial", "Cardiaca",
        "Respiratoria", "Obstétrica", "Intoxicación", "Otra",
    ] = "Médica"

    paciente_nombre: str = Field(default="Desconocido / NN", max_length=120)
    paciente_edad: int | None = Field(default=None, ge=0, le=130)
    paciente_genero: Literal["Masculino", "Femenino", "Otro", "No especifica"] = "No especifica"
    paciente_telefono: str = Field(default="", max_length=20)
    sintomas: str = Field(default="", max_length=400, description="Síntomas u observaciones reportadas")

    direccion: str = Field(min_length=3, max_length=250)
    hospital_destino: str = Field(default="", max_length=120)

    @field_validator("paciente_telefono")
    @classmethod
    def _tel_paciente(cls, v: str) -> str:
        return _valida_telefono(v) if v else v

    @field_validator("paramedicos")
    @classmethod
    def _lista_no_vacia(cls, v: list[str]) -> list[str]:
        return [x.strip() for x in v if x and x.strip()]


class DespachoIn(BaseModel):
    """Confirmación de salida de una ambulancia: requiere verificación facial hecha en el navegador
    (face-api.js) contra la foto registrada del paramédico elegido. El backend no vuelve a comparar
    las caras (no hay librería de reconocimiento facial en el servidor); solo registra el resultado
    que ya validó el navegador, junto con la distancia obtenida, para quedar en la bitácora."""
    operador: str = Field(min_length=2, description="Nombre del paramédico verificado con la cámara")
    verificado: bool
    distancia: float | None = Field(default=None, ge=0, le=2)
    verificado_en: datetime | None = None