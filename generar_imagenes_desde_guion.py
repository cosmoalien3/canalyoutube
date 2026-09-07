#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_imagenes_desde_guion.py

Lee un archivo de guion completo (narración), lo divide en frases/oraciones
cortas siguiendo el ritmo natural de la narración, genera automáticamente
(usando un modelo de OpenAI) un prompt de imagen en inglés para cada frase
-manteniendo siempre el mismo personaje (un muñeco estilo stickman animado)
y el mismo estilo visual (animación plana tipo vector, ilustración 2D, sin
intento de realismo fotográfico)- y envía cada prompt a la API de imágenes
de OpenAI (gpt-image-1) para generar y descargar las imágenes.

Las imágenes se guardan en la carpeta `imagenes_generadas/`, nombradas
en orden como frase_01.png, frase_02.png, etc.

Uso:
    python generar_imagenes_desde_guion.py "C:\\Users\\tuUsuario\\Downloads\\narracion_sacudida-hipnica-final.md"

Si no se indica la ruta, el script intenta encontrar automáticamente el
archivo en la carpeta de Descargas (buscando variantes con/sin acentos
del nombre "narración_sacudida-hípnica-final.md").

Requisitos:
    - pip install openai
    - Variable de entorno OPENAI_API_KEY configurada con tu API key.
"""

from __future__ import annotations

import argparse
import base64
import glob
import os
import re
import sys
import unicodedata

from openai import OpenAI

CARPETA_SALIDA_DEFAULT = "imagenes_generadas"
MODELO_TEXTO_DEFAULT = "gpt-4o-mini"
MODELO_IMAGEN = "gpt-image-1"

# Descripción fija del personaje y el estilo visual que debe mantenerse
# en TODAS las imágenes generadas.
ESTILO_Y_PERSONAJE = (
    "The main character is always the SAME simple animated stickman doll "
    "(a minimalist stick-figure character with basic round head and thin "
    "limbs, expressive but simple). The visual style is always flat vector "
    "animation, 2D illustration, clean flat shapes, bold simple colors, "
    "minimalistic modern flat design, no photorealism, no 3D rendering, "
    "no photographic textures, no text or letters in the image."
)

SYSTEM_PROMPT_GENERADOR = f"""You are an assistant that writes short, vivid English prompts for an AI \
image generator (gpt-image-1), used to illustrate a narration video scene by scene.

{ESTILO_Y_PERSONAJE}

Given ONE short phrase (in Spanish) from the narration script, write a single \
English prompt (1 to 3 sentences) that describes a clear, concrete visual \
scene representing what that phrase is saying, ALWAYS featuring the same \
stickman character and the same flat 2D vector style described above.

Rules:
- Output ONLY the prompt text, nothing else (no quotes, no labels, no explanations).
- Keep it concise and visually specific (composition, pose, simple background, mood).
- Never break character or style, even if the phrase is abstract - find a concrete visual metaphor.
"""


def normalizar(texto: str) -> str:
    """Quita acentos y pasa a minúsculas, para comparar nombres de archivo."""
    sin_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return sin_acentos.lower()


def encontrar_carpeta_descargas() -> str:
    """Intenta ubicar la carpeta de Descargas del usuario (Windows/Linux/Mac)."""
    perfil = os.environ.get("USERPROFILE") or os.path.expanduser("~")
    candidata = os.path.join(perfil, "Downloads")
    if os.path.isdir(candidata):
        return candidata
    return perfil


def encontrar_archivo_guion(ruta_dada: str | None) -> str:
    """
    Devuelve la ruta al archivo de guion.
    Si se dio una ruta explícita y existe, se usa esa.
    Si no, busca en la carpeta de Descargas variantes del nombre
    "narración_sacudida-hípnica-final.md" (con o sin acentos).
    """
    if ruta_dada:
        if os.path.isfile(ruta_dada):
            return ruta_dada
        raise FileNotFoundError(f"No se encontró el archivo indicado: '{ruta_dada}'")

    carpeta = encontrar_carpeta_descargas()
    patrones = [
        "narracion_sacudida-hipnica-final.md",
        "narración_sacudida-hípnica-final.md",
        "narracion*sacudida*hipnica*final*.md",
    ]

    for patron in patrones:
        for ruta in glob.glob(os.path.join(carpeta, patron)):
            if os.path.isfile(ruta):
                return ruta

    # Búsqueda flexible: cualquier .md en Descargas cuyo nombre normalizado
    # contenga "narracion", "sacudida", "hipnica" y "final".
    claves = ["narracion", "sacudida", "hipnica", "final"]
    for ruta in glob.glob(os.path.join(carpeta, "*.md")):
        nombre_normalizado = normalizar(os.path.basename(ruta))
        if all(clave in nombre_normalizado for clave in claves):
            return ruta

    raise FileNotFoundError(
        "No se pudo encontrar el archivo del guion en la carpeta de Descargas "
        f"('{carpeta}'). Indica la ruta manualmente, por ejemplo:\n"
        '  python generar_imagenes_desde_guion.py "C:\\Users\\tuUsuario\\Downloads\\narracion_sacudida-hipnica-final.md"'
    )


def dividir_en_frases(texto: str) -> list[str]:
    """
    Divide el guion completo en frases/oraciones cortas, siguiendo el ritmo
    natural de la narración: primero por líneas (muchos guiones ya vienen
    escritos una frase por línea) y luego, dentro de cada línea, por los
    signos de puntuación que cierran una oración (. ! ? …).
    """
    frases: list[str] = []

    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea:
            continue
        # Ignorar encabezados markdown, líneas de metadatos o separadores.
        if linea.startswith("#") or linea.startswith("---") or linea.startswith("==="):
            continue

        # Quitar marcadores simples de lista ("- ", "* ", "1. ", etc.)
        linea = re.sub(r"^[\-\*\u2022]\s+", "", linea)
        linea = re.sub(r"^\d+[\.\)]\s+", "", linea)

        partes = re.split(r"(?<=[.!?\u2026])\s+", linea)
        for parte in partes:
            parte = parte.strip(" \"'“”‘’")
            if parte:
                frases.append(parte)

    if not frases:
        raise ValueError("No se encontraron frases en el archivo del guion.")

    return frases


def generar_prompt_imagen(client: OpenAI, frase: str, modelo_texto: str) -> str:
    """Usa un modelo de chat de OpenAI para convertir la frase en un prompt de imagen en inglés."""
    respuesta = client.chat.completions.create(
        model=modelo_texto,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_GENERADOR},
            {"role": "user", "content": frase},
        ],
        temperature=0.7,
    )
    prompt = respuesta.choices[0].message.content.strip()
    return prompt


def generar_imagen(client: OpenAI, prompt: str, ruta_salida: str, size: str = "1024x1024"):
    """Genera una imagen con gpt-image-1 a partir del prompt y la guarda en ruta_salida."""
    respuesta = client.images.generate(
        model=MODELO_IMAGEN,
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
        description=(
            "Divide un guion en frases, genera un prompt de imagen en inglés por frase "
            "(mismo personaje stickman y estilo flat vector 2D) y genera las imágenes con gpt-image-1."
        )
    )
    parser.add_argument(
        "archivo_guion",
        nargs="?",
        default=None,
        help=(
            "Ruta al archivo .md del guion completo. Si se omite, se busca "
            "automáticamente en la carpeta de Descargas."
        ),
    )
    parser.add_argument(
        "--carpeta-salida",
        default=CARPETA_SALIDA_DEFAULT,
        help=f"Carpeta donde se guardarán las imágenes (default: {CARPETA_SALIDA_DEFAULT})",
    )
    parser.add_argument(
        "--modelo-texto",
        default=MODELO_TEXTO_DEFAULT,
        help=f"Modelo de OpenAI usado para redactar los prompts de imagen (default: {MODELO_TEXTO_DEFAULT})",
    )
    parser.add_argument(
        "--size",
        default="1024x1024",
        help="Tamaño de la imagen (default: 1024x1024)",
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=None,
        help="Procesar solo las primeras N frases (útil para pruebas).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo muestra las frases y los prompts generados, sin llamar a la API de imágenes.",
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

    try:
        ruta_guion = encontrar_archivo_guion(args.archivo_guion)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Usando archivo de guion: {ruta_guion}")

    with open(ruta_guion, "r", encoding="utf-8") as f:
        texto = f.read()

    frases = dividir_en_frases(texto)
    if args.limite:
        frases = frases[: args.limite]

    print(f"Se detectaron {len(frases)} frases en el guion.\n")

    os.makedirs(args.carpeta_salida, exist_ok=True)
    client = OpenAI()

    imagenes_generadas = 0

    for i, frase in enumerate(frases, start=1):
        etiqueta = f"frase_{i:02d}"
        print(f"[{etiqueta}] Frase: {frase}")

        try:
            prompt_ingles = generar_prompt_imagen(client, frase, args.modelo_texto)
        except Exception as e:
            print(f"  ✘ Error generando el prompt de imagen: {e}", file=sys.stderr)
            continue

        print(f"  Prompt: {prompt_ingles}")

        if args.dry_run:
            continue

        ruta_salida = os.path.join(args.carpeta_salida, f"{etiqueta}.png")
        try:
            generar_imagen(client, prompt_ingles, ruta_salida, size=args.size)
            imagenes_generadas += 1
            print(f"  ✔ Guardada en: {ruta_salida}")
        except Exception as e:
            print(f"  ✘ Error generando la imagen: {e}", file=sys.stderr)

    print("\nProceso terminado.")
    if args.dry_run:
        print(f"Modo prueba (--dry-run): se generaron 0 imágenes de {len(frases)} frases procesadas.")
    else:
        print(f"Total de imágenes generadas: {imagenes_generadas} de {len(frases)} frases procesadas.")


if __name__ == "__main__":
    main()
