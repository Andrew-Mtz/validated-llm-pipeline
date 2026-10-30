import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from schemas import TechnicalExtraction


load_dotenv(Path(__file__).resolve().parent / ".env")
logger = logging.getLogger(__name__)

prompt = ChatPromptTemplate.from_template(
    """Extrae del texto las tecnologias, el nivel de criticidad (baja, media o alta)
y un resumen tecnico siguiendo estas reglas:

- En tecnologias incluye unicamente tecnologias concretas explicitamente
  mencionadas: lenguajes, frameworks, bases de datos, herramientas, plataformas
  o servicios tecnologicos con nombre propio identificable.
- No inventes tecnologias ni las infieras a partir del contexto o del problema.
- No incluyas terminos genericos como sistema, aplicacion, servicio, servidor
  o software, salvo que formen parte del nombre concreto de una tecnologia
  explicitamente mencionada; en ese caso, usa el nombre concreto completo.
- Si el texto identifica tecnologias concretas y aporta detalles tecnicos
  suficientes para realizar la extraccion, devuelve informacion_suficiente=true,
  extrae solo esas tecnologias, asigna la criticidad segun la evidencia del texto,
  genera un resumen tecnico y devuelve mensaje=null. Si no hay evidencia para
  determinar la criticidad, usa nivel_de_criticidad=null.
- Si no hay tecnologias concretas identificables o faltan detalles tecnicos
  suficientes, devuelve informacion_suficiente=false, tecnologias=[] y
  nivel_de_criticidad=null. Genera un resumen no vacio indicando que el texto
  carece de detalles tecnicos suficientes y completa mensaje con una explicacion
  breve de la informacion que falta. La falta de informacion es un resultado
  valido: no inventes tecnologias ni criticidad para completar los campos.
  Por ejemplo, 'El sistema tiene problemas y a veces no funciona bien.
  No hay mas detalles disponibles.' es un caso de informacion insuficiente.
- Basa la criticidad unicamente en la informacion disponible en el texto.
  No supongas impactos, urgencia ni gravedad que no esten indicados.
- El resumen tecnico debe limitarse a lo expresado en el texto, sin inventar
  causas, componentes, tecnologias ni otros detalles ausentes. Si la informacion
  es insuficiente, indicalo en el resumen.

Texto a analizar:
{text}"""
)

provider = os.getenv("LLM_PROVIDER", "").strip()
if provider not in {"openai", "anthropic", "gemini"}:
    raise ValueError("Configuracion invalida: LLM_PROVIDER debe ser openai, anthropic o gemini.")

model_name = os.getenv("LLM_MODEL", "").strip()
if not model_name:
    raise ValueError("Configuracion incompleta: definir LLM_MODEL para el proveedor elegido.")

# Los reintentos se controlan en la cadena, incluida la validacion de la salida.
if provider == "openai":
    from langchain_openai import ChatOpenAI

    model = ChatOpenAI(model=model_name, temperature=0, max_retries=0)
elif provider == "anthropic":
    from langchain_anthropic import ChatAnthropic

    model = ChatAnthropic(model=model_name, temperature=0, max_retries=0)
else:
    model = ChatGoogleGenerativeAI(model=model_name, temperature=0, max_retries=0)
structured_model = model.with_structured_output(TechnicalExtraction)
chain = (prompt | structured_model).with_retry(stop_after_attempt=2)


async def process_text(text: str) -> TechnicalExtraction:
    logger.info("Comienza el procesamiento del texto")
    try:
        resultado = await chain.ainvoke({"text": text})
    except Exception:
        logger.error("El procesamiento fallo definitivamente tras los reintentos")
        raise

    logger.info("El procesamiento termino correctamente")
    return resultado
