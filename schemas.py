from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Criticidad(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


class TechnicalExtraction(BaseModel):
    tecnologias: list[str]
    nivel_de_criticidad: Criticidad | None
    resumen_tecnico: str = Field(min_length=1)
    informacion_suficiente: bool
    mensaje: str | None = None

    @field_validator("tecnologias")
    @classmethod
    def validar_tecnologias(cls, tecnologias: list[str]) -> list[str]:
        tecnologias_limpias = [tecnologia.strip() for tecnologia in tecnologias]

        if any(not tecnologia for tecnologia in tecnologias_limpias):
            raise ValueError("Las tecnologías no pueden contener valores vacíos")

        return tecnologias_limpias

    @field_validator("resumen_tecnico")
    @classmethod
    def validar_resumen(cls, resumen: str) -> str:
        resumen = resumen.strip()

        if not resumen:
            raise ValueError("El resumen técnico no puede estar vacío")

        return resumen
