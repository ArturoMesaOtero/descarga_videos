# 🛠️ Requisitos Previos

## Dependencias de Python
```bash
pip install yt-dlp replicate python-dotenv
```

## 🎵 FFmpeg (Instalación Detallada)

FFmpeg es **esencial** para extraer audio de los videos descargados. Aquí tienes las instrucciones paso a paso para cada sistema operativo:

### 🪟 **Windows**

#### **Método 1: Descarga Manual (Recomendado)**
1. **Descarga FFmpeg**:
   - Ve a [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)
   - Descarga la versión "release builds" (archivo .zip)
   - O directamente: [ffmpeg-release-essentials.zip](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip)

2. **Extraer el archivo**:
   - Descomprime el archivo ZIP
   - Copia la carpeta extraída (ej: `ffmpeg-6.0-essentials_build`) a `C:\ffmpeg\`

3. **Añadir al PATH**:
   - Presiona `Win + R`, escribe `sysdm.cpl` y presiona Enter
   - Ve a la pestaña "Opciones avanzadas"
   - Haz clic en "Variables de entorno"
   - En "Variables del sistema", busca "Path" y haz clic en "Editar"
   - Haz clic en "Nuevo" y añade: `C:\ffmpeg\bin`
   - Haz clic en "Aceptar" en todas las ventanas

4. **Verificar instalación**:
   - Abre una nueva ventana de CMD o PowerShell
   - Ejecuta: `ffmpeg -version`
   - Deberías ver información de la versión instalada

#### **Método 2: Usando Chocolatey**
```powershell
# Instalar Chocolatey primero (si no lo tienes)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Instalar FFmpeg
choco install ffmpeg
```

#### **Método 3: Usando winget (Windows 10/11)**
```cmd
winget install Gyan.FFmpeg
```

### 🍎 **macOS**

#### **Método 1: Usando Homebrew (Recomendado)**
```bash
# Instalar Homebrew si no lo tienes
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar FFmpeg
brew install ffmpeg
```

#### **Método 2: Usando MacPorts**
```bash
# Instalar MacPorts primero desde https://www.macports.org/install.php
sudo port install ffmpeg
```

#### **Método 3: Descarga Manual**
1. Descarga desde [https://evermeet.cx/ffmpeg/](https://evermeet.cx/ffmpeg/)
2. Descomprime y mueve el ejecutable a `/usr/local/bin/`
3. Ejecuta: `chmod +x /usr/local/bin/ffmpeg`

### 🐧 **Linux**

#### **Ubuntu/Debian y derivados**
```bash
# Actualizar repositorios
sudo apt update

# Instalar FFmpeg
sudo apt install ffmpeg

# Verificar instalación
ffmpeg -version
```

#### **CentOS/RHEL/Fedora**
```bash
# Para Fedora
sudo dnf install ffmpeg

# Para CentOS/RHEL (necesita repositorio EPEL)
sudo yum install epel-release
sudo yum install ffmpeg
```

#### **Arch Linux**
```bash
sudo pacman -S ffmpeg
```

#### **openSUSE**
```bash
sudo zypper install ffmpeg
```

#### **Compilación desde código fuente (avanzado)**
```bash
# Instalar dependencias de compilación
sudo apt install build-essential yasm cmake libtool libc6 libc6-dev unzip wget libnuma1 libnuma-dev

# Descargar y compilar
wget https://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2
tar xjvf ffmpeg-snapshot.tar.bz2
cd ffmpeg
./configure
make
sudo make install
```

## ✅ Verificación de FFmpeg

Después de la instalación, **reinicia tu terminal/CMD** y ejecuta:

```bash
ffmpeg -version
```

**Salida esperada:**
```
ffmpeg version 6.0 Copyright (c) 2000-2023 the FFmpeg developers
built with gcc 9 (Ubuntu 9.4.0-1ubuntu1~20.04.1)
configuration: --enable-gpl --enable-version3 --enable-sdl2...
...
```

Si ves esta información, ¡FFmpeg está correctamente instalado! 🎉

## 🚨 Solución de Problemas de FFmpeg

### ❌ "ffmpeg no está instalado" o "comando no encontrado"

#### **En Windows:**
1. **Verifica el PATH**: Abre CMD y ejecuta `echo %PATH%` - debería incluir la ruta de FFmpeg
2. **Reinicia el terminal**: Cierra y abre una nueva ventana de CMD/PowerShell
3. **Ruta incorrecta**: Asegúrate de que apuntas a la carpeta `bin` (ej: `C:\ffmpeg\bin`)
4. **Caracteres especiales**: Evita espacios y caracteres especiales en la ruta

#### **En macOS:**
1. **Verificar Homebrew**: `brew --version`
2. **Reinstalar**: `brew uninstall ffmpeg && brew install ffmpeg`
3. **Permisos**: `sudo chown -R $(whoami) /usr/local/bin/ffmpeg`

#### **En Linux:**
1. **Repositorios actualizados**: `sudo apt update`
2. **Permisos**: `which ffmpeg` y verificar que sea ejecutable
3. **Variables de entorno**: `echo $PATH` y verificar `/usr/bin` esté incluido

### ❌ Error: "Permission denied" o "Access denied"

#### **Windows:**
- Ejecuta CMD como **Administrador**
- Verifica que el antivirus no esté bloqueando FFmpeg

#### **macOS/Linux:**
```bash
# Dar permisos de ejecución
chmod +x /usr/local/bin/ffmpeg

# O usar sudo para la instalación
sudo brew install ffmpeg  # macOS
sudo apt install ffmpeg   # Linux
```

### ❌ "FFmpeg no funciona con el script"

1. **Reiniciar terminal**: Siempre después de instalar FFmpeg
2. **Ruta completa**: En el script, usar la ruta completa temporalmente:
   ```python
   # Windows
   ffmpeg_path = "C:\\ffmpeg\\bin\\ffmpeg.exe"
   
   # macOS/Linux
   ffmpeg_path = "/usr/local/bin/ffmpeg"
   ```
3. **Verificar versión**: Algunas versiones muy antiguas pueden tener problemas

## 🎯 FFmpeg para el Script

El script **requiere** FFmpeg para:
- ✅ **Extraer audio** de videos MP4, WebM, MKV
- ✅ **Convertir a MP3** para transcripción
- ✅ **Mostrar progreso** durante la extracción
- ✅ **Mantener calidad** del audio original

**Sin FFmpeg**, el script puede descargar videos pero **NO** podrá extraer audio ni generar transcripciones.

### Configuración de Replicate API

Después de instalar FFmpeg, configura la API de Replicate:

1. **Regístrate** en [Replicate.com](https://replicate.com)
2. **Obtén tu API token** desde tu dashboard
3. **Configura la variable de entorno** creando un archivo `.env`:

```bash
# Crear archivo .env en la carpeta del script
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

### ✅ Verificar instalación completa
```bash
# Verificar Python y dependencias
python --version
pip list | grep yt-dlp
pip list | grep replicate

# Verificar FFmpeg
ffmpeg -version

# Verificar que el script detecta todo
python video_downloader.py
# Debería mostrar ✅ para todas las dependencias
```

**¡Listo!** Con FFmpeg correctamente instalado, el script podrá extraer audio y generar transcripciones automáticamente. 🚀