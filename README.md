# 🎬 Descargador de Videos de Vimeo y Loom con Transcripción y Formateo Inteligente

## 📋 Descripción

Script completo de Python que permite extraer y descargar videos de **Vimeo** y **Loom** desde archivos HTML, **extraer el audio**, **transcribirlos automáticamente** usando la API de Replicate con el modelo Whisper de OpenAI, y **generar 4 formatos legibles** diferentes para una lectura óptima.

### ✨ Características principales

- 🎥 **Descarga videos** de Vimeo y Loom desde URLs o archivos HTML
- 🎵 **Extrae audio** con FFmpeg mostrando progreso en tiempo real
- 🎤 **Transcribe con Whisper Large V3** usando polling robusto (sin timeouts)
- 📝 **Genera automáticamente 4 formatos legibles**:
  - **LEGIBLE**: Transcripción por minutos con timestamps claros
  - **CONVERSACION**: Formato continuo agrupado por párrafos
  - **TEMAS**: Análisis automático por bloques temáticos de 5 minutos
  - **INDICE**: Índice buscable con palabras clave más frecuentes
- 🔄 **Progreso visible** en todas las operaciones
- 📁 **Organización automática** de archivos por plataforma
- 🆔 **Formateo de transcripciones existentes** (nueva funcionalidad)

## 🛠️ Requisitos Previos

### Dependencias de Python
```bash
pip install yt-dlp replicate python-dotenv
```

### FFmpeg (para extracción de audio)

**Windows:**
1. Descarga FFmpeg desde [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extrae el archivo y añade la carpeta `bin` al PATH del sistema

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

### Configuración de Replicate API

1. **Regístrate** en [Replicate.com](https://replicate.com)
2. **Obtén tu API token** desde tu dashboard
3. **Configura la variable de entorno** creando un archivo `.env`:

```bash
# Crear archivo .env
echo "REPLICATE_API_TOKEN=r8_tu_token_aqui" > .env
```

**O configurar temporalmente:**
```bash
# Windows (PowerShell)
$env:REPLICATE_API_TOKEN="r8_tu_token_aqui"

# Windows (CMD)
set REPLICATE_API_TOKEN=r8_tu_token_aqui

# macOS/Linux
export REPLICATE_API_TOKEN=r8_tu_token_aqui
```

### Verificar instalación
```bash
yt-dlp --version
ffmpeg -version
python -c "import replicate; print('Replicate OK')"
```

## 📖 Guía Paso a Paso para Descargar Videos

### 🔐 **PASO 1: Iniciar Sesión en la Plataforma**
1. Abre tu navegador web (Chrome, Firefox, Safari, etc.)
2. Ve a la plataforma donde está alojado el video (sitio web de tu curso, LMS, etc.)
3. **Inicia sesión** con tus credenciales
4. Asegúrate de tener acceso al video que quieres descargar

### 🎯 **PASO 2: Navegar al Video**
1. Busca y accede al video específico que deseas descargar
2. Asegúrate de que el video se esté reproduciendo correctamente
3. Verifica que tengas permisos para ver el contenido

### 🖥️ **PASO 3: Maximizar el Video**
1. Haz clic en el botón de **pantalla completa** del reproductor de video
2. O simplemente asegúrate de que el video esté completamente cargado y visible
3. El video debe estar reproduciéndose o listo para reproducir

### 🔧 **PASO 4: Abrir las Herramientas de Desarrollador**
1. **Presiona `F12`** en tu teclado
   - **Alternativa Windows/Linux**: `Ctrl + Shift + I`
   - **Alternativa Mac**: `Cmd + Option + I`
   - **Alternativa**: Clic derecho en la página → "Inspeccionar elemento"

2. Se abrirá un panel con herramientas de desarrollador (generalmente en el lado derecho o inferior)

### 📄 **PASO 5: Copiar el Código HTML**
1. En las herramientas de desarrollador, busca la pestaña **"Elements"** o **"Elementos"**
2. En la parte superior del código HTML, verás una línea que comienza con `<html>`
3. **Haz clic derecho** sobre la etiqueta `<html>` (la línea que dice `<html lang="es">` o similar)
4. En el menú contextual selecciona:
   - **Copy** → **Copy element** (en inglés)
   - **Copiar** → **Copiar elemento** (en español)

### 💾 **PASO 6: Guardar el Código HTML**
1. Abre un editor de texto (Notepad, VS Code, Sublime Text, etc.)
2. **Pega** el contenido copiado (`Ctrl + V` o `Cmd + V`)
3. **Guarda el archivo** como `1.html` en la carpeta raíz del proyecto (donde está el script)

```
📁 Proyecto/
├── video_downloader.py    ← Script principal
├── 1.html                ← Archivo HTML con el código copiado
├── .env                  ← Token de Replicate
└── downloads/            ← Carpeta donde se guardarán los videos
    ├── vimeo/           ← Videos de Vimeo
    └── loom/            ← Videos de Loom
```

## 🚀 Uso del Script

### Ejecutar el Programa
```bash
python video_downloader.py
```

### 📋 Menú de Opciones

Al ejecutar el script, verás:

```
🎬 Descargador de Videos de Vimeo y Loom con Transcripción y Formateo
======================================================================

🔧 VERIFICANDO CONFIGURACIÓN:
   yt-dlp: ✅ 2023.12.30
   ffmpeg: ✅ 6.0
   Replicate API: ✅ Token configurado (...RO389YxY)
   Archivo .env: ✅ Encontrado

¿Qué quieres hacer?
1. Descargar una URL específica (Vimeo o Loom)
2. Procesar archivo HTML/TXT (busca Vimeo y Loom)
3. Debug: Analizar archivo detalladamente
4. Procesar video ya descargado (extraer audio + transcribir)
5. Formatear transcripción existente (generar versiones legibles)
6. Salir
```

### **Opción 1: Descargar URL Específica**
- **Cuándo usar**: Si ya tienes la URL directa del video
- **Qué hace**: Descarga un video individual de Vimeo o Loom
- **Ejemplos de URL**:
  - Vimeo: `https://player.vimeo.com/video/123456789`
  - Loom: `https://www.loom.com/embed/abcd1234-5678-90ab-cdef-123456789abc`

**Proceso:**
1. Selecciona opción `1`
2. Pega la URL del video
3. Especifica carpeta de descarga (opcional)
4. Elige si extraer audio (`s/N`)
5. Si extraes audio, elige si transcribir (`s/N`)

### **Opción 2: Procesar Archivo HTML** ⭐ (MÁS COMÚN)
- **Cuándo usar**: Cuando hayas guardado el código HTML de la página (siguiendo los pasos anteriores)
- **Qué hace**: Busca automáticamente todos los videos de Vimeo y Loom en el archivo HTML

**Proceso:**
1. Selecciona opción `2`
2. Escribe la ruta del archivo: `1.html`
3. Especifica carpeta de descarga (opcional)
4. Elige si extraer audio de todos los videos
5. Elige si transcribir todos los audios
6. El script procesará todos los videos automáticamente

### **Opción 3: Modo Debug**
- **Cuándo usar**: Si no se encuentran videos o quieres analizar qué contiene el HTML
- **Qué hace**: Muestra información detallada sobre el contenido del archivo

**Información que proporciona:**
- Número de menciones de 'vimeo' y 'loom'
- Patrones encontrados con cada expresión regular
- Contextos donde aparecen las plataformas
- Fragmentos de código relevantes

### **Opción 4: Procesar Video Existente**
- **Cuándo usar**: Cuando ya tienes un video descargado y quieres procesarlo
- **Qué hace**: Extrae audio y/o transcribe un video ya descargado

**Proceso:**
1. Selecciona opción `4`
2. Proporciona la ruta del video
3. Elige si extraer audio
4. Elige si transcribir

### **Opción 5: Formatear Transcripción Existente** 🆕
- **Cuándo usar**: Cuando ya tienes una transcripción y quieres generar formatos legibles
- **Qué hace**: Procesa transcripciones en formato JSON, TXT o SRT y genera 4 versiones legibles

**Formatos de entrada soportados:**
- JSON con estructura `transcription_output.transcription`
- Archivos TXT con JSON embebido
- Archivos SRT directos

### **Opción 6: Salir**
- Termina el programa

## 📁 Estructura de Archivos Generados

Los archivos se organizan automáticamente por plataforma:

```
📁 downloads/
├── 📁 vimeo/
│   ├── 🎬 Video_Title.mp4                    ← Video original
│   ├── 🎵 Video_Title.mp3                    ← Audio extraído
│   ├── 🎬 Video_Title_transcription.srt      ← Subtítulos con timestamps
│   ├── 📋 Video_Title_transcription.json     ← Metadatos completos
│   ├── 📖 Video_Title_LEGIBLE.txt           ← Formato por minutos ⭐
│   ├── 💬 Video_Title_CONVERSACION.txt      ← Formato continuo ⭐
│   ├── 📋 Video_Title_TEMAS.txt             ← Análisis por temas ⭐
│   └── 🔍 Video_Title_INDICE.txt            ← Índice buscable ⭐
└── 📁 loom/
    ├── 🎬 Loom_Video_Title.mp4
    ├── 🎵 Loom_Video_Title.mp3
    ├── 🎬 Loom_Video_Title_transcription.srt
    ├── 📋 Loom_Video_Title_transcription.json
    ├── 📖 Loom_Video_Title_LEGIBLE.txt
    ├── 💬 Loom_Video_Title_CONVERSACION.txt
    ├── 📋 Loom_Video_Title_TEMAS.txt
    └── 🔍 Loom_Video_Title_INDICE.txt
```

## 🎤 Transcripción con Polling Robusto

### Características de la Transcripción

- **Modelo**: Whisper Large V3 (el más preciso disponible)
- **Método**: `predictions.create()` + polling (sin timeouts)
- **Formato**: SRT con timestamps precisos
- **Idioma**: Detección automática
- **Progreso**: Actualización cada 30 segundos
- **Robustez**: Maneja archivos de cualquier tamaño

### Progreso en Tiempo Real

```
🔄 MONITOREANDO PROGRESO DE TRANSCRIPCIÓN
==================================================
🆔 Prediction ID: abc123...

⏰ Tiempo transcurrido: 5.2 minutos
📊 Estado: processing
📝 Nuevos logs:
   📈 Progreso: 15% - Audio duration: 4996.0 sec
   📈 Progreso: 28% - Detected language: Spanish
   📈 Progreso: 45% - Processing frames...
```

### Estimaciones de Tiempo

| Tamaño Audio | Duración Video | Tiempo Transcripción |
|--------------|----------------|---------------------|
| 10 MB        | ~15 minutos    | 3-5 minutos         |
| 50 MB        | ~60 minutos    | 15-20 minutos       |
| 90 MB        | ~90 minutos    | 30-45 minutos       |
| 150 MB       | ~150 minutos   | 45-60 minutos       |

## 📝 Formatos de Transcripción Generados

### 1. 📖 **Formato LEGIBLE** (`*_LEGIBLE.txt`)
Transcripción organizada por minutos con separadores visuales:

```
================================================================================
TRANSCRIPCIÓN COMPLETA - FORMATO LEGIBLE
================================================================================
Total de segmentos: 1583
Duración total: 01:23:16
Generado el: 2025-06-02 20:45:30
================================================================================

📍 MINUTO 00
----------------------------------------
[00:05] Vamos a dejar unos minutillos para que entre todo el mundo y también
[00:08] y también Jaime.
[00:25] ¿Cómo vais chavales?
[00:30] Luis, ¿qué pasa tío? ¿Cómo vas?

📍 MINUTO 01
----------------------------------------
[01:00] Estas clases sirven mucho porque también aparte te hacen cambiar el chip
[01:04] y ver la generación de negocio de otra forma.
```

### 2. 💬 **Formato CONVERSACION** (`*_CONVERSACION.txt`)
Texto continuo agrupado por pausas naturales:

```
================================================================================
TRANSCRIPCIÓN - FORMATO CONVERSACIÓN
================================================================================
Duración: 01:23:16
Fecha: 2025-06-02 20:45:30
================================================================================

[00:05] Vamos a dejar unos minutillos para que entre todo el mundo y también y también Jaime.

[00:25] ¿Cómo vais chavales? Luis, ¿qué pasa tío? ¿Cómo vas? Qué tal? Muy bien, muy bien, muy bien. Currando mucho y bien, consiguiendo cositas, poco a poco.

[00:50] Después de la charla que tuvimos con Jaime aquel día, apretándole mucho a las ventas y dándole caña. Ahí está.
```

### 3. 📋 **Formato TEMAS** (`*_TEMAS.txt`)
Análisis automático por bloques temáticos de 5 minutos:

```
================================================================================
TRANSCRIPCIÓN - ORGANIZADA POR TEMAS
================================================================================
Análisis automático de temas en la conversación
Duración total: 01:23:16
================================================================================

🕒 BLOQUE 1: Minutos 00:00 - 05:00
--------------------------------------------------
📋 Temas detectados: inicio, ventas, estrategia
💬 Contenido:
   [00:05] Vamos a dejar unos minutillos para que entre todo el mundo y también
   [00:25] ¿Cómo vais chavales?
   [01:00] Estas clases sirven mucho porque también aparte te hacen cambiar el chip

🕒 BLOQUE 2: Minutos 05:00 - 10:00
--------------------------------------------------
📋 Temas detectados: ventas, cliente, estrategia
💬 Contenido:
   [05:15] Hablando del cliente y cómo abordar las ventas...
```

### 4. 🔍 **Formato INDICE** (`*_INDICE.txt`)
Índice buscable con palabras clave más frecuentes:

```
================================================================================
ÍNDICE BUSCABLE DE LA TRANSCRIPCIÓN
================================================================================

🔤 PALABRAS MÁS FRECUENTES:
------------------------------
ventas: 45 veces
cliente: 32 veces
estrategia: 28 veces
negocio: 24 veces
clases: 22 veces

📚 ÍNDICE COMPLETO (A-Z):
------------------------------

🔍 CLIENTE (32 veces):
   [05:30] hablando con el cliente sobre las necesidades...
   [12:45] el cliente me preguntó sobre los precios...
   [28:10] conseguir que el cliente confíe en nosotros...

🔍 VENTAS (45 veces):
   [02:15] las ventas son fundamentales para...
   [15:20] técnicas de ventas que realmente funcionan...
   [35:40] aumentar las ventas de manera sostenible...
```

## ⚠️ Solución de Problemas

### ❌ "No se encontraron videos"
**Problema**: El script no detecta videos en el HTML
**Solución**: 
1. Verifica que copiaste TODO el elemento `<html>`
2. Asegúrate de que el video esté completamente cargado antes de copiar
3. Usa la opción `3` (Debug) para analizar el contenido
4. Verifica que sea una página con videos de Vimeo o Loom

### ❌ "yt-dlp no está instalado"
**Problema**: Falta la dependencia principal
**Solución**: 
```bash
pip install yt-dlp
# O actualizar si ya está instalado
pip install --upgrade yt-dlp
```

### ❌ "ffmpeg no está instalado"
**Problema**: Falta FFmpeg para extraer audio
**Solución**: Instalar FFmpeg según tu sistema operativo (ver sección de instalación)

### ❌ "REPLICATE_API_TOKEN no está configurado"
**Problema**: Falta configurar la API de Replicate
**Solución**: 
1. Obtener token en [replicate.com](https://replicate.com/account/api-tokens)
2. Crear archivo `.env` con: `REPLICATE_API_TOKEN=r8_tu_token_aqui`
3. Reiniciar terminal/comando

### ❌ "Server disconnected without sending a response"
**Problema**: Timeout en transcripción (archivos muy grandes)
**Solución**: ✅ **Ya solucionado** - El script usa polling robusto que evita timeouts

### ❌ Error de transcripción con Replicate
**Problema**: Falla la transcripción con Replicate
**Solución**:
1. Verificar conexión a internet
2. Verificar que el token de Replicate sea válido
3. Verificar saldo en tu cuenta de Replicate
4. El archivo de audio debe ser válido (MP3, WAV, etc.)

### ❌ Video protegido/privado
**Problema**: Videos con restricciones de acceso
**Solución**: 
1. Asegúrate de estar logueado en la plataforma
2. Copia el HTML mientras estás autenticado
3. Algunos videos institucionales pueden tener protecciones adicionales

### ❌ "No se pudieron extraer segmentos válidos"
**Problema**: El formateador no puede procesar la transcripción
**Solución**:
1. Verifica que el archivo contenga contenido SRT válido
2. Usa la opción 5 para procesar transcripciones existentes
3. Revisa que el formato del archivo sea correcto

## 🎯 Consejos y Mejores Prácticas

### ✅ **Para Mejores Resultados:**
1. **Siempre** inicia sesión antes de copiar el HTML
2. **Reproduce** el video al menos unos segundos antes de copiar
3. **Copia el HTML completo** desde la etiqueta `<html>` principal
4. **Usa navegadores actualizados** (Chrome, Firefox últimas versiones)
5. **Verifica tu conexión** a internet antes de transcripciones largas

### ⚡ **Optimización:**
- Si tienes muchos videos en una página, la opción 2 los procesará todos automáticamente
- Los archivos JSON contienen metadatos completos para análisis posterior
- Las transcripciones incluyen timestamps precisos para navegación
- El audio se extrae en formato MP3 para máxima compatibilidad
- Los 4 formatos legibles se generan automáticamente sin intervención

### 💡 **Casos de Uso:**
- **Estudiantes**: Descargar y transcribir clases online con formatos legibles
- **Profesionales**: Procesar reuniones grabadas en Loom con análisis temático
- **Investigadores**: Analizar contenido de video con índices buscables
- **Creadores**: Obtener transcripciones formateadas para subtítulos y contenido
- **Empresas**: Procesar webinars y presentaciones con análisis automático

### 🔄 **Flujo de Trabajo Recomendado:**
1. **Preparación**: Configurar .env con token de Replicate
2. **Extracción**: Copiar HTML de la página con videos
3. **Descarga**: Usar opción 2 para procesar todos los videos
4. **Revisión**: Verificar los formatos legibles generados
5. **Análisis**: Usar el índice buscable para encontrar temas específicos

## 💰 Costos de Replicate

- **Whisper Large V3**: ~$0.0045 por minuto de audio
- **Ejemplos de costo**:
  - 15 minutos de audio: ~$0.07 USD
  - 60 minutos de audio: ~$0.27 USD
  - 90 minutos de audio: ~$0.41 USD
- **Facturación**: Solo pagas por lo que usas
- **Límites**: Dependen de tu plan en Replicate

Revisa precios actuales en [replicate.com/pricing](https://replicate.com/pricing)

## 📊 Especificaciones Técnicas

### Plataformas Soportadas
- **Vimeo**: URLs de `player.vimeo.com` y `vimeo.com`
- **Loom**: URLs de `loom.com/embed` y `loom.com/share`

### Formatos de Video Soportados
- MP4, WebM, MKV, AVI, MOV (según soporte de yt-dlp)

### Formatos de Audio Generados
- MP3 (alta calidad, compatible universalmente)

### Formatos de Transcripción
- SRT (subtítulos con timestamps)
- JSON (metadatos completos y estructurados)
- TXT (4 formatos legibles diferentes)

### Requisitos del Sistema
- **Python**: 3.7 o superior
- **Memoria**: 512 MB mínimo (recomendado 2 GB para archivos grandes)
- **Espacio**: Depende del tamaño de videos (calcular ~1.5x el tamaño original)
- **Internet**: Conexión estable para descarga y transcripción

## 🆘 Soporte y Troubleshooting

### Logs y Debug
- Usa la **opción 3** (Debug) para analizar archivos HTML problemáticos
- Todos los errores incluyen sugerencias específicas de solución
- Los spinners y barras de progreso muestran el estado en tiempo real

### Archivos de Respaldo
- El script crea automáticamente archivos JSON con metadatos completos
- Cada transcripción incluye timestamp y ID de predicción para seguimiento
- Los formatos legibles son regenerables usando la opción 5

### Interrupción y Reanudación
- **Ctrl+C** durante transcripción: El proceso continúa en Replicate
- **URL de seguimiento**: Siempre se proporciona para monitoreo manual
- **Polling robusto**: Reintenta automáticamente en caso de errores de red

### Limitaciones Conocidas
- Algunos videos pueden estar protegidos por DRM
- Videos privados requieren autenticación previa
- La precisión de transcripción depende de la calidad del audio
- Los temas detectados son aproximaciones basadas en palabras clave

## ⚖️ Nota Legal y Ética

Este script es para **uso educativo y personal**. Al usarlo:

- ✅ **Asegúrate** de tener permisos para descargar el contenido
- ✅ **Respeta** los términos de servicio de las plataformas
- ✅ **Usa solo** para contenido al que tienes acceso legítimo
- ✅ **No redistribuyas** contenido protegido por derechos de autor
- ✅ **Cumple** con las leyes de propiedad intelectual de tu jurisdicción

### Responsabilidades del Usuario
- El usuario es responsable del uso ético y legal del script
- Verificar permisos antes de descargar contenido de terceros
- Respetar las políticas de privacidad y términos de uso
- Usar las transcripciones de manera responsable y ética

---

## 🎉 ¡Disfruta de tu Descargador Completo!

Con este script tienes una solución integral para:
- 📥 Descargar videos de Vimeo y Loom
- 🎵 Extraer audio con calidad
- 🎤 Transcribir con la mejor IA disponible
- 📝 Generar 4 formatos súper legibles automáticamente
- 🔍 Buscar y analizar contenido fácilmente

**¡Perfecto para estudiantes, profesionales e investigadores que quieren aprovechar al máximo el contenido de video!** 🚀
