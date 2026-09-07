# canalyoutube

## Generador de imágenes con OpenAI (`generar_imagenes.py`)

Script para generar imágenes con el modelo `gpt-image-1` de OpenAI a partir de
un archivo `.md` con prompts, uno por escena.

### Formato del archivo de prompts

```
## Escena 1 — Título de la escena
"texto del prompt en inglés"

## Escena 2 — Otro título
"otro prompt en inglés"
```

### Requisitos

- Python 3.8+
- `pip install openai`
- Variable de entorno `OPENAI_API_KEY` configurada con tu API key.

En PowerShell, si aún no la tienes en tu sesión actual:

```powershell
$env:OPENAI_API_KEY = "tu-api-key"
```

### Uso

```powershell
python generar_imagenes.py "C:\Users\tuUsuario\Downloads\prompts-imagenes-sacudida-hipnica.md"
```

Esto:

1. Lee el archivo `.md` y extrae cada prompt con su número de escena.
2. Envía cada prompt a la API de imágenes de OpenAI (`gpt-image-1`).
3. Descarga cada imagen en la carpeta `imagenes_generadas/`, nombrada como
   `escena_01.png`, `escena_02.png`, etc.

Opciones adicionales:

```powershell
python generar_imagenes.py "ruta\al\archivo.md" --carpeta-salida otra_carpeta --size 1024x1536
```

## Generador de imágenes desde el guion completo (`generar_imagenes_desde_guion.py`)

Script que parte de la narración/guion completo de un video (no de prompts ya
escritos), lo divide automáticamente en frases cortas, redacta un prompt de
imagen en inglés por cada frase (usando un modelo de chat de OpenAI) y genera
las imágenes con `gpt-image-1`.

Todas las imágenes mantienen siempre:

- El **mismo personaje**: un muñeco estilo *stickman* animado.
- El **mismo estilo visual**: animación plana tipo vector, ilustración 2D,
  sin intento de realismo fotográfico.

### Requisitos

- Python 3.8+
- `pip install openai`
- Variable de entorno `OPENAI_API_KEY` configurada con tu API key.

### Uso

```powershell
python generar_imagenes_desde_guion.py "C:\Users\tuUsuario\Downloads\narracion_sacudida-hipnica-final.md"
```

Si no le pasas la ruta del archivo, el script intenta encontrarlo
automáticamente en tu carpeta de Descargas (busca variantes del nombre
`narración_sacudida-hípnica-final.md`, con o sin acentos).

Esto:

1. Lee el guion completo y lo divide en frases/oraciones cortas siguiendo el
   ritmo natural de la narración (respeta saltos de línea y signos `. ! ? …`).
2. Para cada frase, genera automáticamente (con un modelo de chat de OpenAI)
   un prompt de imagen en inglés que describe una escena visual representando
   esa frase, manteniendo siempre el mismo personaje stickman y el mismo
   estilo flat vector 2D.
3. Envía cada prompt a la API de imágenes de OpenAI (`gpt-image-1`) y
   descarga cada imagen en la carpeta `imagenes_generadas/`, nombradas en
   orden: `frase_01.png`, `frase_02.png`, etc.
4. Al final muestra cuántas imágenes se generaron en total.

Opciones adicionales:

```powershell
# Probar solo las primeras 3 frases
python generar_imagenes_desde_guion.py "ruta\al\guion.md" --limite 3

# Ver las frases y los prompts generados SIN gastar en generación de imágenes
python generar_imagenes_desde_guion.py "ruta\al\guion.md" --dry-run

# Cambiar el modelo usado para redactar los prompts, el tamaño de imagen o la carpeta de salida
python generar_imagenes_desde_guion.py "ruta\al\guion.md" --modelo-texto gpt-4o-mini --size 1024x1536 --carpeta-salida otra_carpeta
```
