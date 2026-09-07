#!/usr/bin/env python3
"""
generar_imagenes.py

Lee un archivo Markdown con prompts de imagen (uno por escena) y genera
una imagen por cada prompt usando la API de imágenes de OpenAI
(modelo gpt-image-1). Las imágenes se guardan en la carpeta
`imagenes_generadas/` como escena_01.png, escena_02.png, etc.

Formato esperado del archivo .md, un bloque por escena:

    ## Escena 1 — Título de la escena
    "texto del prompt en inglés"

Uso:
    python generar_imagenes.py "C:\\Users\\tuUsuario\\Downloads\\prompts-imagenes-sacudida-hipnica.md"

Requisitos:
    - pip install openai
    - Variable de entorno OPENAI_API_KEY configurada con tu API key.
"""

import argparse
import os
import re
import sys
import base64

from openai import OpenAI

# Patrón para capturar cada escena: número de escena + el prompt entre comillas
# que viene después del encabezado "## Escena N ..."
ESCENA_PATTERN = re.compile(
    r'##\s*Escena\s+(\d+).*?\n\s*"(.*?)"',
    re.DOTALL | re.IGNORECASE,
)


def extraer_prompts(ruta_md: str):
    """Lee el archivo .md y devuelve una lista de tuplas (numero_escena, prompt)."""
    with open(ruta_md, "r", encoding="utf-8") as f:
        contenido = f.read()

    coincidencias = ESCENA_PATTERN.findall(contenido)

    if not coincidencias:
        raise ValueError(
            "No se encontraron prompts en el archivo. "
            "Verifica que el formato sea:\n"
            '## Escena N — Título\n"texto del prompt"'
        )

    escenas = []
    for numero_str, prompt in coincidencias:
        numero = int(numero_str)
        prompt_limpio = " ".join(prompt.split())  # normaliza espacios/saltos de línea
        escenas.append((numero, prompt_limpio))

    escenas.sort(key=lambda x: x[0])
    return escenas


def generar_imagen(client: OpenAI, prompt: str, ruta_salida: str, size: str = "1024x1024"):
    """Genera una imagen con gpt-image-1 y la guarda en ruta_salida."""
    respuesta = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size=size,
        n=1,
    )

    imagen_b64 = respuesta.data[0].b64_json
    imagen_bytes = base64.b64decode(imagen_b64)

    with open(ruta_salida, "wb") as f:
        f.write(imagen_bytes)


def main():
    parser = argparse.ArgumentParser(
        description="Genera imágenes con gpt-image-1 a partir de un archivo .md de prompts."
    )
    parser.add_argument(
        "archivo_md",
        help="Ruta al archivo .md con los prompts (ej: prompts-imagenes-sacudida-hipnica.md)",
    )
    parser.add_argument(
        "--carpeta-salida",
        default="imagenes_generadas",
        help="Carpeta donde se guardarán las imágenes (default: imagenes_generadas)",
    )
    parser.add_argument(
        "--size",
        default="1024x1024",
        help="Tamaño de la imagen (default: 1024x1024)",
    )
    args = parser.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        print(
            "ERROR: no se encontró la variable de entorno OPENAI_API_KEY.\n"
            "Configúrala antes de correr el script, por ejemplo en PowerShell:\n"
            '  $env:OPENAI_API_KEY = "tu-api-key"',
            file=sys.stderr,
        )
        sys.exit(1)

    if not os.path.isfile(args.archivo_md):
        print(f"ERROR: no se encontró el archivo '{args.archivo_md}'.", file=sys.stderr)
        sys.exit(1)

    escenas = extraer_prompts(args.archivo_md)
    print(f"Se encontraron {len(escenas)} escenas/prompts.")

    os.makedirs(args.carpeta_salida, exist_ok=True)

    client = OpenAI()

    for numero, prompt in escenas:
        nombre_archivo = f"escena_{numero:02d}.png"
        ruta_salida = os.path.join(args.carpeta_salida, nombre_archivo)

        print(f"[Escena {numero:02d}] Generando imagen...")
        print(f"  Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")

        try:
            generar_imagen(client, prompt, ruta_salida, size=args.size)
            print(f"  ✔ Guardada en: {ruta_salida}")
        except Exception as e:
            print(f"  ✘ Error generando la escena {numero:02d}: {e}", file=sys.stderr)

    print("\nProceso terminado.")


if __name__ == "__main__":
    main()
