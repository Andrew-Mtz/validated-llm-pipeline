import argparse
import asyncio
import logging

from chain import process_text


async def main():
    parser = argparse.ArgumentParser(description="Ejecuta los casos de extraccion tecnica.")
    parser.add_argument(
        "--case",
        choices=("technical", "ambiguous"),
        help="Ejecuta solo el caso indicado; por defecto ejecuta ambos.",
    )
    args = parser.parse_args()

    text = (
        "El servicio de pagos utiliza Python y PostgreSQL. "
        "Una falla en la base de datos impide procesar todos los pagos "
        "y requiere atencion urgente."
    )
    casos = [
        ("CASO 1 - TEXTO TECNICO", text),
        ("CASO 2 - TEXTO AMBIGUO", "El sistema tiene problemas y a veces no funciona bien. No hay mas detalles disponibles."),
    ]
    if args.case == "technical":
        casos = casos[:1]
    elif args.case == "ambiguous":
        casos = casos[1:]

    for titulo, entrada in casos:
        print(f"\n{'=' * 60}\n{titulo}\n{'=' * 60}", flush=True)
        print(f"Entrada: {entrada}", flush=True)
        try:
            resultado = await process_text(entrada)
        except Exception:
            print("No se pudo procesar el caso por un error tecnico tras agotar los intentos. Intenta nuevamente mas tarde.")
        else:
            print(resultado.model_dump_json(indent=2))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(main())
