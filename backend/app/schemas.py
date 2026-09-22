from typing import Literal

from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class DoctorIn(BaseModel):
    nombre: str = Field(min_length=2)
    especialidad: str = Field(min_length=2)
    telefono: str = ""
    estado: Literal["Activo", "En guardia", "Descanso"] = "Activo"


class AmbulanceIn(BaseModel):
    placa: str = Field(min_length=2)
    tipo: Literal["Básica", "Avanzada"] = "Básica"
    conductor: str = ""
    estado: Literal["Disponible", "En servicio", "Mantenimiento"] = "Disponible"


class EmergencyIn(BaseModel):
    descripcion: str = Field(min_length=3)
    prioridad: Literal["Alta", "Media", "Baja"] = "Media"
    estado: Literal["Pendiente", "Asignada", "En curso", "Cerrada"] = "Pendiente"
    ambulancia: str | None = None


class OperatorIn(BaseModel):
    nombre: str = Field(min_length=2)
    turno: Literal["Matutino", "Vespertino", "Nocturno"] = "Matutino"
    extension: str = ""
    estado: Literal["En línea", "Desconectado"] = "En línea"
