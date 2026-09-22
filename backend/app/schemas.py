from typing import Literal

from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class DoctorIn(BaseModel):
    nombres: str = Field(min_length=2)
    apellidos: str = Field(min_length=2)
    fecha_nacimiento: str = ""
    direccion: str = ""
    celular: str = Field(min_length=2)
    correo: str = ""
    contacto_emergencia: str = ""
    especialidad: str = Field(min_length=2)
    cedula_profesional: str = Field(min_length=2)
    turno: Literal["Matutino", "Vespertino", "Nocturno"] = "Matutino"
    estado: Literal["Activo", "En guardia", "Descanso"] = "Activo"
    # Foto de referencia (igual que en Operadores): se usa para verificar por
    # reconocimiento facial que es el mismo doctor antes de asignarlo a una emergencia.
    foto: str = Field(min_length=1, description="Foto de referencia en base64 (data URL)")


class AmbulanceIn(BaseModel):
    placa: str = Field(min_length=2)
    tipo: Literal["Básica", "Avanzada"] = "Básica"
    conductor: str = ""
    estado: Literal["Disponible", "En servicio", "Mantenimiento"] = "Disponible"


class EmergencyIn(BaseModel):
    # Datos del paciente
    paciente_nombre: str = Field(min_length=2)
    paciente_edad: str = ""
    paciente_sexo: Literal["Masculino", "Femenino", "Otro"] = "Otro"
    paciente_telefono: str = ""
    direccion: str = Field(min_length=3)

    # Datos de la emergencia
    descripcion: str = Field(min_length=3)
    prioridad: Literal["Alta", "Media", "Baja"] = "Media"
    estado: Literal["Pendiente", "Asignada", "En curso", "Cerrada"] = "Pendiente"

    # Asignación (idealmente elegidos de las bases de operadores/ambulancias/doctores)
    operador: str | None = None
    ambulancia: str | None = None
    doctor: str | None = None


class OperatorIn(BaseModel):
    nombre: str = Field(min_length=2)
    turno: Literal["Matutino", "Vespertino", "Nocturno"] = "Matutino"
    extension: str = ""
    estado: Literal["En línea", "Desconectado"] = "En línea"
    # Foto de referencia (imagen en base64, formato data URL) tomada al registrar
    # al operador. Se usa después para verificar por reconocimiento facial que es
    # el mismo operador antes de asignarlo a una emergencia y antes de que salga
    # la ambulancia.
    foto: str = Field(min_length=1, description="Foto de referencia en base64 (data URL)")


class VerificacionIn(BaseModel):
    operador: str = Field(min_length=1)
    contexto: Literal["asignacion", "salida"]
    coincide: bool = True
    distancia: float | None = None
    emergencia_folio: str | None = None
