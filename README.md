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
