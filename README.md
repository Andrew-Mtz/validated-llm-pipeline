# Pre-entrega 2: Extracción de Entidades Técnicas

Pipeline asíncrono de extracción de tecnologías, criticidad y resumen técnico con
LangChain y LCEL. La salida estructurada se valida con `TechnicalExtraction` de
Pydantic. Se selecciona un único proveedor, sin fallback.

## Requisitos

Python 3.10 o superior (recomendado: 3.11), conexión a Internet y una API key con
acceso a un modelo compatible con salida estructurada del proveedor elegido.

## Instalación en Windows PowerShell

Desde la raíz del repositorio:

```powershell
cd pre-entrega2
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Si ya existe `.env`, conservarlo y agregar las variables faltantes en lugar de
sobrescribirlo. Si PowerShell bloquea la activación, usar
`.\.venv\Scripts\python.exe` en lugar de `python` sin activar el entorno.

## Configuración

Editar `.env`. `LLM_PROVIDER` es obligatorio y acepta únicamente estos valores:

| Valor | Modelo de LangChain | API key requerida |
| --- | --- | --- |
| openai | ChatOpenAI | OPENAI_API_KEY |
| anthropic | ChatAnthropic | ANTHROPIC_API_KEY |
| gemini | ChatGoogleGenerativeAI | GOOGLE_API_KEY |

Completar únicamente la clave del proveedor elegido; las demás pueden quedar vacías.
`LLM_MODEL` también es obligatorio y debe ser un modelo compatible disponible para
tu cuenta. El ejemplo mantiene la configuración de pruebas actual:
`LLM_PROVIDER=gemini` y `LLM_MODEL=gemini-3.5-flash`.
Al cambiar de proveedor, actualizar también el modelo y su API key.
No subir `.env` a Git.

El código carga el `.env` ubicado junto a `chain.py`. Las variables ya definidas en
el entorno del proceso tienen prioridad. Un proveedor no soportado o un modelo
vacío produce un error de configuración antes de ejecutar la cadena.

## Ejecución

Desde `pre-entrega2/`, con el entorno configurado:

```powershell
python main.py
```

El programa ejecuta dos casos con títulos separados, imprime el texto de entrada y,
si tiene éxito, el objeto Pydantic validado:

1. **Texto técnico:** servicio de pagos con Python y PostgreSQL y una falla urgente.
2. **Texto ambiguo:** problema general sin tecnologías claramente identificadas.

El caso ambiguo puede fallar por información insuficiente; el fallo no está
garantizado porque depende de la respuesta del modelo. Pydantic verifica las
reglas del esquema, pero no garantiza que la respuesta sea fiel al texto.

La cadena utiliza `ChatPromptTemplate`, structured output y LCEL.
`process_text()` ejecuta `.ainvoke()` y registra inicio, éxito y fallo definitivo.
LangChain aplica `.with_retry(stop_after_attempt=2)`: un intento inicial y hasta
un reintento, incluida la validación. Los retries internos del modelo están
desactivados para mantener ese límite.

Si un caso agota los intentos, `process_text()` propaga la excepción y `main.py`
muestra un mensaje controlado y continúa con el siguiente caso. Los errores de
configuración al iniciar deben corregirse antes de ejecutar las pruebas.
