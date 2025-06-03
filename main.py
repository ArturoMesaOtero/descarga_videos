#!/usr/bin/env python3
"""
Descargador de Videos de Vimeo y Loom con Transcripción y Formateo
Convierte URLs con entidades HTML, descarga videos usando yt-dlp,
extrae audio, transcribe usando Replicate Whisper y genera formatos legibles
"""

import re
import html
import subprocess
import sys
import os
import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import replicate
from dotenv import load_dotenv
import threading
import time
from datetime import datetime


class TranscriptionFormatter:
    """
    Formateador de transcripciones integrado para generar versiones legibles
    """

    def __init__(self):
        self.segments = []
        self.total_duration = 0

    def parse_srt_content(self, srt_content):
        """Parsea contenido SRT y extrae segmentos"""
        self.segments = []

        # Limpiar contenido y normalizar saltos de línea
        clean_content = srt_content.strip().replace('\r\n', '\n').replace('\r', '\n')

        # Dividir en bloques por líneas vacías dobles
        blocks = re.split(r'\n\s*\n', clean_content)

        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    # Línea 1: número de segmento
                    segment_num = int(lines[0])

                    # Línea 2: timestamps
                    timestamp_line = lines[1]
                    if '-->' in timestamp_line:
                        start_str, end_str = timestamp_line.split(' --> ')
                        start_seconds = self.timestamp_to_seconds(start_str.strip())
                        end_seconds = self.timestamp_to_seconds(end_str.strip())

                        # Línea 3+: texto
                        text = ' '.join(lines[2:]).strip()

                        # Solo añadir si el texto no está vacío
                        if text:
                            self.segments.append({
                                'number': segment_num,
                                'start': start_seconds,
                                'end': end_seconds,
                                'start_formatted': start_str.strip(),
                                'end_formatted': end_str.strip(),
                                'duration': end_seconds - start_seconds,
                                'text': text
                            })

                except (ValueError, IndexError):
                    continue

        if self.segments:
            self.total_duration = max(seg['end'] for seg in self.segments)

        return len(self.segments)

    def timestamp_to_seconds(self, timestamp):
        """Convierte timestamp SRT (HH:MM:SS,mmm) a segundos"""
        try:
            # Formato: 00:01:23,456
            time_part, ms_part = timestamp.split(',')
            h, m, s = map(int, time_part.split(':'))
            ms = int(ms_part)
            return h * 3600 + m * 60 + s + ms / 1000
        except:
            return 0

    def seconds_to_readable(self, seconds):
        """Convierte segundos a formato legible"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def generate_clean_transcript(self, output_path):
        """Genera transcripción limpia y legible"""
        content = []
        content.append("=" * 80)
        content.append("TRANSCRIPCIÓN COMPLETA - FORMATO LEGIBLE")
        content.append("=" * 80)
        content.append(f"Total de segmentos: {len(self.segments)}")
        content.append(f"Duración total: {self.seconds_to_readable(self.total_duration)}")
        content.append(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("=" * 80)
        content.append("")

        current_minute = -1

        for segment in self.segments:
            # Agregar separador cada minuto
            segment_minute = int(segment['start'] // 60)
            if segment_minute != current_minute:
                if current_minute >= 0:
                    content.append("")
                content.append(f"📍 MINUTO {segment_minute:02d}")
                content.append("-" * 40)
                current_minute = segment_minute

            # Formato: [MM:SS] Texto
            time_mark = self.seconds_to_readable(segment['start'])
            content.append(f"[{time_mark}] {segment['text']}")

        # Guardar archivo
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))

        return output_path

    def generate_conversation_format(self, output_path):
        """Genera formato de conversación continua"""
        content = []
        content.append("=" * 80)
        content.append("TRANSCRIPCIÓN - FORMATO CONVERSACIÓN")
        content.append("=" * 80)
        content.append(f"Duración: {self.seconds_to_readable(self.total_duration)}")
        content.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("=" * 80)
        content.append("")

        # Agrupar texto por párrafos (pausas largas)
        paragraphs = []
        current_paragraph = []
        last_end = 0

        for segment in self.segments:
            # Si hay una pausa larga (>3 segundos), empezar nuevo párrafo
            pause = segment['start'] - last_end

            if pause > 3 and current_paragraph:
                paragraphs.append({
                    'start': current_paragraph[0]['start'],
                    'text': ' '.join([s['text'] for s in current_paragraph])
                })
                current_paragraph = []

            current_paragraph.append(segment)
            last_end = segment['end']

        # Agregar último párrafo
        if current_paragraph:
            paragraphs.append({
                'start': current_paragraph[0]['start'],
                'text': ' '.join([s['text'] for s in current_paragraph])
            })

        # Escribir párrafos
        for i, paragraph in enumerate(paragraphs, 1):
            time_mark = self.seconds_to_readable(paragraph['start'])
            content.append(f"[{time_mark}] {paragraph['text']}")
            content.append("")  # Línea vacía entre párrafos

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))

        return output_path

    def generate_summary_by_topics(self, output_path):
        """Genera resumen organizado por temas"""
        content = []
        content.append("=" * 80)
        content.append("TRANSCRIPCIÓN - ORGANIZADA POR TEMAS")
        content.append("=" * 80)
        content.append(f"Análisis automático de temas en la conversación")
        content.append(f"Duración total: {self.seconds_to_readable(self.total_duration)}")
        content.append("=" * 80)
        content.append("")

        # Palabras clave para detectar cambios de tema
        topic_keywords = {
            'inicio': ['empezar', 'comenzar', 'empezamos', 'vamos a', 'hola', 'buenos'],
            'ventas': ['venta', 'ventas', 'vender', 'cliente', 'clientes', 'dinero', 'facturación'],
            'estrategia': ['estrategia', 'plan', 'objetivo', 'meta', 'planificar', 'metodología'],
            'problema': ['problema', 'error', 'fallo', 'dificultad', 'complicado', 'issue'],
            'solución': ['solución', 'resolver', 'arreglar', 'solucionar', 'fix'],
            'ejemplo': ['ejemplo', 'por ejemplo', 'como por ejemplo', 'caso'],
            'pregunta': ['pregunta', '¿', 'duda', 'consulta', 'cómo'],
            'herramientas': ['herramienta', 'software', 'app', 'aplicación', 'plataforma'],
            'conclusion': ['conclusión', 'resumen', 'final', 'terminar', 'acabar']
        }

        # Detectar temas por bloques de 5 minutos
        time_blocks = {}
        for segment in self.segments:
            block = int(segment['start'] // 300)  # Bloques de 5 minutos
            if block not in time_blocks:
                time_blocks[block] = []
            time_blocks[block].append(segment)

        # Analizar cada bloque
        for block_num in sorted(time_blocks.keys()):
            segments = time_blocks[block_num]
            start_time = block_num * 5
            end_time = min(start_time + 5, self.total_duration / 60)

            content.append(f"🕒 BLOQUE {block_num + 1}: Minutos {start_time:02d}:00 - {end_time:02.0f}:00")
            content.append("-" * 50)

            # Texto completo del bloque
            block_text = ' '.join([seg['text'] for seg in segments])

            # Detectar tema principal
            detected_topics = []
            for topic, keywords in topic_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in block_text.lower():
                        detected_topics.append(topic)
                        break

            if detected_topics:
                content.append(f"📋 Temas detectados: {', '.join(set(detected_topics))}")

            # Mostrar contenido clave del bloque
            content.append(f"💬 Contenido:")
            for segment in segments[:10]:  # Máximo 10 segmentos por bloque
                time_mark = self.seconds_to_readable(segment['start'])
                content.append(f"   [{time_mark}] {segment['text']}")

            if len(segments) > 10:
                content.append(f"   ... y {len(segments) - 10} segmentos más")

            content.append("")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))

        return output_path

    def generate_searchable_index(self, output_path):
        """Genera índice buscable con palabras clave"""
        content = []
        content.append("=" * 80)
        content.append("ÍNDICE BUSCABLE DE LA TRANSCRIPCIÓN")
        content.append("=" * 80)
        content.append("")

        # Crear índice de palabras importantes
        word_index = {}

        for segment in self.segments:
            words = re.findall(r'\b[a-záéíóúñüA-ZÁÉÍÓÚÑÜ]{4,}\b', segment['text'])
            for word in words:
                word_lower = word.lower()
                if word_lower not in word_index:
                    word_index[word_lower] = []
                word_index[word_lower].append({
                    'time': self.seconds_to_readable(segment['start']),
                    'text': segment['text'][:100] + '...' if len(segment['text']) > 100 else segment['text']
                })

        # Mostrar palabras más frecuentes
        word_freq = {word: len(occurrences) for word, occurrences in word_index.items()}
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]

        content.append("🔤 PALABRAS MÁS FRECUENTES:")
        content.append("-" * 30)
        for word, freq in top_words:
            content.append(f"{word}: {freq} veces")
        content.append("")

        # Índice completo
        content.append("📚 ÍNDICE COMPLETO (A-Z):")
        content.append("-" * 30)

        for word in sorted(word_index.keys()):
            occurrences = word_index[word]
            if len(occurrences) > 1:  # Solo palabras que aparecen más de una vez
                content.append(f"\n🔍 {word.upper()} ({len(occurrences)} veces):")
                for occ in occurrences[:3]:  # Mostrar máximo 3 ejemplos
                    content.append(f"   [{occ['time']}] {occ['text']}")
                if len(occurrences) > 3:
                    content.append(f"   ... y {len(occurrences) - 3} más")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))

        return output_path

class VideoDownloader:
    def __init__(self):
        # Cargar variables de entorno desde archivo .env
        load_dotenv()

        # Múltiples patrones para encontrar URLs de Vimeo en diferentes contextos
        self.vimeo_patterns = [
            # Patrón principal: URLs entre comillas dobles
            r'"(https://player\.vimeo\.com/video/\d+[^"]*)"',
            # URLs entre comillas simples
            r"'(https://player\.vimeo\.com/video/\d+[^']*)'",
            # URLs sin comillas pero con parámetros
            r'(https://player\.vimeo\.com/video/\d+(?:\?[^\s<>"\']*)?)',
            # URLs en src de iframe
            r'src=["\']?(https://player\.vimeo\.com/video/\d+[^"\'>\s]*)',
            # URLs en atributos data-*
            r'data-[^=]*=["\']?(https://player\.vimeo\.com/video/\d+[^"\'>\s]*)',
            # URLs simples de vimeo.com
            r'"(https://vimeo\.com/\d+[^"]*)"',
            r"'(https://vimeo\.com/\d+[^']*)'",
            # IDs de video en JavaScript/JSON
            r'video[_/]?id["\']?\s*[:=]\s*["\']?(\d{8,})',
            r'vimeo[_/]?id["\']?\s*[:=]\s*["\']?(\d{8,})',
            # Patrón para encontrar IDs en URLs embedidas
            r'/video/(\d{8,})',
        ]

        # Patrones para Loom
        self.loom_patterns = [
            # URLs completas de Loom embed
            r'"(https://www\.loom\.com/embed/[a-f0-9]{32}[^"]*)"',
            r"'(https://www\.loom\.com/embed/[a-f0-9]{32}[^']*)'",
            r'(https://www\.loom\.com/embed/[a-f0-9]{32})',
            # URLs en src de iframe
            r'src=["\']?(https://www\.loom\.com/embed/[a-f0-9]{32}[^"\'>\s]*)',
            # URLs de loom.com/share
            r'"(https://www\.loom\.com/share/[a-f0-9]{32}[^"]*)"',
            r"'(https://www\.loom\.com/share/[a-f0-9]{32}[^']*)'",
            r'(https://www\.loom\.com/share/[a-f0-9]{32})',
            # IDs de Loom (32 caracteres hexadecimales)
            r'loom[_/]?id["\']?\s*[:=]\s*["\']?([a-f0-9]{32})',
            r'/embed/([a-f0-9]{32})',
            r'/share/([a-f0-9]{32})',
        ]

        # Verificar configuración de Replicate
        self.replicate_token = os.environ.get('REPLICATE_API_TOKEN')
        if not self.replicate_token:
            print("⚠️  Advertencia: REPLICATE_API_TOKEN no está configurado.")
            print("   Crea un archivo .env con: REPLICATE_API_TOKEN=tu_token")
            print("   O ejecuta: export REPLICATE_API_TOKEN=tu_token")

    def show_progress_spinner(self, message, stop_event):
        """
        Muestra un spinner animado mientras se ejecuta una tarea
        """
        spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        i = 0
        while not stop_event.is_set():
            print(f'\r{spinner_chars[i % len(spinner_chars)]} {message}', end='', flush=True)
            time.sleep(0.1)
            i += 1
        print(f'\r✅ {message} - Completado!', flush=True)

    def clean_video_url(self, raw_url, platform):
        """
        Convierte URL con entidades HTML a URL limpia según la plataforma
        """
        # Decodificar entidades HTML (&amp; -> &)
        clean_url = html.unescape(raw_url)

        if platform == 'vimeo':
            # Para Vimeo: eliminar parámetros (hasta el ?)
            if '?' in clean_url:
                clean_url = clean_url.split('?')[0]
        elif platform == 'loom':
            # Para Loom: mantener URL completa pero limpiar
            # Loom necesita la URL embed completa
            pass

        return clean_url

    def extract_audio_from_video(self, video_path, audio_path):
        """
        Extrae audio de un video usando ffmpeg con progreso visible
        """
        print(f"\n🎵 Extrayendo audio de: {Path(video_path).name}")

        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-q:a", "0",  # Mejor calidad de audio
            "-map", "a",  # Solo extraer audio
            "-y",  # Sobrescribir si existe
            "-progress", "pipe:1",  # Mostrar progreso
            str(audio_path)
        ]

        try:
            # Crear evento para detener spinner
            stop_event = threading.Event()

            # Iniciar spinner en hilo separado
            spinner_thread = threading.Thread(
                target=self.show_progress_spinner,
                args=("Extrayendo audio", stop_event)
            )
            spinner_thread.start()

            # Ejecutar ffmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)

            # Detener spinner
            stop_event.set()
            spinner_thread.join()

            if result.returncode == 0:
                print(f"✅ Audio extraído: {Path(audio_path).name}")
                return True
            else:
                print(f"❌ Error extrayendo audio:")
                if result.stderr:
                    # Mostrar solo errores importantes, no warnings
                    error_lines = [line for line in result.stderr.split('\n')
                                   if 'error' in line.lower() and line.strip()]
                    if error_lines:
                        for line in error_lines[:3]:  # Mostrar máximo 3 líneas de error
                            print(f"   {line}")
                return False

        except FileNotFoundError:
            print("❌ Error: ffmpeg no está instalado")
            print("Instálalo desde: https://ffmpeg.org/download.html")
            return False
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
            return False

    def compress_audio_for_transcription(self, audio_path, max_size_mb=45):
        """
        Comprime un archivo de audio si es demasiado grande para Replicate
        """
        audio_path = Path(audio_path)
        current_size_mb = audio_path.stat().st_size / (1024 * 1024)

        if current_size_mb <= max_size_mb:
            print(f"✅ Audio ya es del tamaño adecuado: {current_size_mb:.1f} MB")
            return str(audio_path)

        print(f"📦 Audio demasiado grande: {current_size_mb:.1f} MB")
        print(f"🔄 Comprimiendo para reducir a ~{max_size_mb} MB...")

        # Crear nombre para archivo comprimido
        compressed_path = audio_path.with_stem(f"{audio_path.stem}_compressed")

        # Calcular bitrate necesario para el tamaño objetivo
        # Estimación aproximada: MB = (bitrate * duration_seconds) / 8000
        try:
            # Obtener duración del audio
            probe_cmd = [
                "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                "-of", "csv=p=0", str(audio_path)
            ]
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            duration_seconds = float(result.stdout.strip())

            # Calcular bitrate objetivo (con margen de seguridad)
            target_bitrate = int((max_size_mb * 8000 * 0.9) / duration_seconds)  # 90% del límite
            target_bitrate = max(32, min(128, target_bitrate))  # Entre 32k y 128k

            print(f"   📊 Duración: {duration_seconds / 60:.1f} minutos")
            print(f"   🎚️  Bitrate objetivo: {target_bitrate}k")

        except Exception as e:
            print(f"   ⚠️ No se pudo calcular duración, usando bitrate conservador")
            target_bitrate = 64  # Bitrate conservador por defecto

        # Comando de compresión
        cmd = [
            "ffmpeg",
            "-i", str(audio_path),
            "-acodec", "mp3",  # Codec MP3 eficiente
            "-ab", f"{target_bitrate}k",  # Bitrate específico
            "-ac", "1",  # Mono (reduce tamaño significativamente)
            "-ar", "16000",  # Sample rate reducido (suficiente para voz)
            "-y",  # Sobrescribir si existe
            str(compressed_path)
        ]

        try:
            # Crear evento para spinner
            stop_event = threading.Event()
            spinner_thread = threading.Thread(
                target=self.show_progress_spinner,
                args=("Comprimiendo audio", stop_event)
            )
            spinner_thread.start()

            # Ejecutar compresión
            result = subprocess.run(cmd, capture_output=True, text=True)

            # Detener spinner
            stop_event.set()
            spinner_thread.join()

            if result.returncode == 0 and compressed_path.exists():
                new_size_mb = compressed_path.stat().st_size / (1024 * 1024)
                reduction = ((current_size_mb - new_size_mb) / current_size_mb) * 100

                print(f"✅ Audio comprimido exitosamente:")
                print(f"   📏 Tamaño original: {current_size_mb:.1f} MB")
                print(f"   📏 Tamaño nuevo: {new_size_mb:.1f} MB")
                print(f"   📉 Reducción: {reduction:.1f}%")

                if new_size_mb <= max_size_mb:
                    return str(compressed_path)
                else:
                    print(f"⚠️ Aún demasiado grande, intentando más compresión...")
                    # Intentar compresión más agresiva
                    return self.compress_audio_aggressive(compressed_path, max_size_mb)
            else:
                print(f"❌ Error en compresión:")
                if result.stderr:
                    print(f"   {result.stderr[:200]}...")
                return None

        except Exception as e:
            if 'stop_event' in locals():
                stop_event.set()
            if 'spinner_thread' in locals():
                spinner_thread.join()
            print(f"❌ Error comprimiendo audio: {str(e)}")
            return None

    def compress_audio_aggressive(self, audio_path, max_size_mb=45):
        """
        Compresión más agresiva para archivos muy grandes
        """
        audio_path = Path(audio_path)
        aggressive_path = audio_path.with_stem(f"{audio_path.stem}_ultra")

        print(f"🔥 Aplicando compresión ultra-agresiva...")

        cmd = [
            "ffmpeg",
            "-i", str(audio_path),
            "-acodec", "mp3",
            "-ab", "32k",  # Bitrate muy bajo pero audible
            "-ac", "1",  # Mono
            "-ar", "11025",  # Sample rate muy bajo
            "-af", "highpass=f=100,lowpass=f=3000",  # Filtrar frecuencias innecesarias
            "-y",
            str(aggressive_path)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0 and aggressive_path.exists():
                new_size_mb = aggressive_path.stat().st_size / (1024 * 1024)

                print(f"✅ Compresión ultra-agresiva completada:")
                print(f"   📏 Tamaño final: {new_size_mb:.1f} MB")

                if new_size_mb <= max_size_mb:
                    print(f"   🎉 ¡Archivo listo para transcripción!")
                    return str(aggressive_path)
                else:
                    print(f"   ❌ Aún demasiado grande para Replicate")
                    return None
            else:
                print(f"❌ Falló la compresión agresiva")
                return None

        except Exception as e:
            print(f"❌ Error en compresión agresiva: {str(e)}")
            return None

    def poll_prediction_progress(self, prediction_id):
        """
        Hace polling de la predicción mostrando progreso detallado
        """
        print(f"\n🔄 MONITOREANDO PROGRESO DE TRANSCRIPCIÓN")
        print("=" * 50)
        print(f"🆔 Prediction ID: {prediction_id}")

        start_time = time.time()
        last_log_lines = 0
        check_interval = 30  # Verificar cada 30 segundos

        while True:
            try:
                # Obtener estado actual
                prediction = replicate.predictions.get(prediction_id)
                current_time = time.time()
                elapsed = current_time - start_time

                print(f"\n⏰ Tiempo transcurrido: {elapsed / 60:.1f} minutos")
                print(f"📊 Estado: {prediction.status}")

                # Mostrar logs si hay nuevos
                if prediction.logs:
                    log_lines = prediction.logs.split('\n')
                    new_lines = log_lines[last_log_lines:]

                    if new_lines and any(line.strip() for line in new_lines):
                        print("📝 Nuevos logs:")
                        for line in new_lines:
                            if line.strip():
                                # Formatear líneas de progreso
                                if '%|' in line and 'frames/s' in line:
                                    # Extraer porcentaje si es posible
                                    try:
                                        percent_start = line.find('%|')
                                        if percent_start > 0:
                                            percent_part = line[:percent_start]
                                            percent_num = percent_part.split()[-1]
                                            print(f"   📈 Progreso: {percent_num}% - {line.split(']')[-1].strip()}")
                                        else:
                                            print(f"   📝 {line.strip()}")
                                    except:
                                        print(f"   📝 {line.strip()}")
                                else:
                                    print(f"   📝 {line.strip()}")

                    last_log_lines = len(log_lines)

                # Verificar si terminó
                if prediction.status == "succeeded":
                    total_time = (current_time - start_time) / 60
                    print(f"\n🎉 ¡TRANSCRIPCIÓN COMPLETADA!")
                    print(f"   ⏱️  Tiempo total: {total_time:.1f} minutos")
                    print(f"   📊 Estado final: {prediction.status}")
                    return prediction

                elif prediction.status == "failed":
                    print(f"\n❌ TRANSCRIPCIÓN FALLÓ")
                    print(f"   📊 Estado: {prediction.status}")
                    if prediction.error:
                        print(f"   🚨 Error: {prediction.error}")
                    return prediction

                elif prediction.status == "canceled":
                    print(f"\n⚠️  TRANSCRIPCIÓN CANCELADA")
                    return prediction

                # Si sigue procesando, esperar antes del próximo check
                elif prediction.status in ["starting", "processing"]:
                    print(f"   🔄 Sigue procesando... próxima verificación en {check_interval}s")
                    time.sleep(check_interval)

                else:
                    print(f"   ❓ Estado desconocido: {prediction.status}")
                    time.sleep(check_interval)

            except KeyboardInterrupt:
                print(f"\n⚠️  INTERRUMPIDO POR USUARIO")
                print(f"   La transcripción sigue ejecutándose en: https://replicate.com/p/{prediction_id}")
                print(f"   Puedes reanudar el monitoreo manualmente")
                return None

            except Exception as e:
                print(f"\n❌ Error obteniendo estado: {str(e)}")
                print(f"   Reintentando en {check_interval}s...")
                time.sleep(check_interval)

    def transcribe_audio_with_replicate(self, audio_path):
        """
        Transcribe audio usando Replicate Whisper con POLLING (para archivos grandes)
        """
        if not self.replicate_token:
            print("❌ No se puede transcribir: falta REPLICATE_API_TOKEN en .env")
            return None

        print(f"\n🎤 Transcribiendo audio: {Path(audio_path).name}")

        model_version = "8099696689d249cf8b122d833c36ac3f75505c666a395ca40ef26f68e7d3d16e"

        try:
            # Crear evento para detener spinner durante la subida
            stop_event = threading.Event()

            # Iniciar spinner para subida
            spinner_thread = threading.Thread(
                target=self.show_progress_spinner,
                args=("Subiendo archivo de audio", stop_event)
            )
            spinner_thread.start()

            with open(audio_path, "rb") as audio_file:
                input_data = {
                    "audio": audio_file,
                    "model": "large-v3",  # Modelo más preciso
                    "transcription": "srt",  # Formato SRT con timestamps
                    "language": "auto",  # Detección automática de idioma
                    "translate": False,  # No traducir, mantener idioma original
                    "temperature": 0,  # Más determinístico
                    "suppress_tokens": "-1",  # Tokens a suprimir
                    "condition_on_previous_text": True,  # Usar contexto previo
                    "compression_ratio_threshold": 2.4,
                    "logprob_threshold": -1.0,
                    "no_speech_threshold": 0.6,
                    "temperature_increment_on_fallback": 0.2
                }

                # Detener spinner de subida
                stop_event.set()
                spinner_thread.join()

                print(f"📤 Creando predicción para archivo grande...")
                print(f"⏰ Inicio: {time.strftime('%H:%M:%S')}")

                # ✅ USAR predictions.create EN LUGAR DE run() ✅
                prediction = replicate.predictions.create(
                    version=model_version,
                    input=input_data
                )

                print(f"✅ Predicción creada exitosamente!")
                print(f"   🆔 ID: {prediction.id}")
                print(f"   📊 Estado inicial: {prediction.status}")
                print(f"   🌐 URL: https://replicate.com/p/{prediction.id}")

                # ✅ HACER POLLING EN LUGAR DE ESPERAR ✅
                final_prediction = self.poll_prediction_progress(prediction.id)

                if final_prediction and final_prediction.status == "succeeded":
                    print("✅ Transcripción completada")
                    return final_prediction.output
                else:
                    print("❌ Transcripción falló o fue cancelada")
                    return None

        except Exception as e:
            # Asegurar que se detenga el spinner en caso de error
            if 'stop_event' in locals():
                stop_event.set()
            if 'spinner_thread' in locals():
                spinner_thread.join()

            print(f"❌ Error en transcripción: {str(e)}")

            # Proporcionar ayuda específica según el tipo de error
            if "authentication" in str(e).lower():
                print("   💡 Verifica que tu REPLICATE_API_TOKEN sea correcto en el archivo .env")
            elif "quota" in str(e).lower() or "billing" in str(e).lower():
                print("   💡 Verifica tu saldo en Replicate o métodos de pago")
            elif "network" in str(e).lower() or "connection" in str(e).lower():
                print("   💡 Verifica tu conexión a internet")

            return None

    def transcribe_audio_with_compression_check(self, audio_path, output_base):
        """
        Transcribe audio con verificación y compresión automática si es necesario
        Esta función unifica la lógica para todas las opciones del script
        """
        audio_path = Path(audio_path)

        if not audio_path.exists():
            print(f"❌ Audio no encontrado: {audio_path}")
            return False

        original_size_mb = audio_path.stat().st_size / (1024 * 1024)
        max_size_replicate = 45  # MB

        print(f"📏 Tamaño del audio: {original_size_mb:.1f} MB")

        # Verificar si necesita compresión
        audio_to_transcribe = audio_path
        compressed_file = None

        if original_size_mb > max_size_replicate:
            print(f"\n⚠️ AUDIO DEMASIADO GRANDE PARA REPLICATE")
            print(f"   Límite: ~{max_size_replicate} MB")
            print(f"   Archivo actual: {original_size_mb:.1f} MB")
            print(f"🔄 Comprimiendo automáticamente...")

            compressed_audio = self.compress_audio_for_transcription(audio_path, max_size_replicate)

            if compressed_audio:
                audio_to_transcribe = Path(compressed_audio)
                compressed_file = audio_to_transcribe  # Para limpiar después
                print(f"✅ Usando archivo comprimido para transcripción")
            else:
                print(f"❌ No se pudo comprimir el archivo lo suficiente")
                print(f"💡 El video se descargó correctamente, pero no se pudo transcribir")
                print(f"   Puedes intentar comprimir manualmente el audio a < {max_size_replicate} MB")
                return False

        # Transcribir usando Replicate
        transcription = self.transcribe_audio_with_replicate(audio_to_transcribe)

        # Limpiar archivo comprimido temporal si se creó
        if compressed_file and compressed_file != audio_path and compressed_file.exists():
            try:
                compressed_file.unlink()
                print(f"🗑️ Archivo temporal comprimido eliminado")
            except:
                pass

        if transcription:
            # Guardar transcripción usando el nombre base original
            if self.save_transcription(transcription, output_base):
                print(f"✅ Transcripción completada para: {audio_path.name}")
                return True

        print(f"❌ Falló la transcripción de: {audio_path.name}")
        return False

    def transcribe_audio_file(self, audio_path, output_dir=None):
        """
        Transcribe un archivo de audio existente directamente
        ACTUALIZADA: Usa la función unificada de transcripción
        """
        audio_path = Path(audio_path)

        if not audio_path.exists():
            print(f"❌ Archivo de audio no encontrado: {audio_path}")
            return False

        # Verificar que sea un archivo de audio válido
        valid_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac']
        if audio_path.suffix.lower() not in valid_extensions:
            print(f"❌ Formato de audio no válido: {audio_path.suffix}")
            print(f"   Formatos soportados: {', '.join(valid_extensions)}")
            return False

        print(f"\n🎤 TRANSCRIBIENDO ARCHIVO DE AUDIO")
        print("=" * 50)
        print(f"📁 Archivo: {audio_path.name}")

        # Verificar Replicate API
        if not self.replicate_token:
            print("❌ No se puede transcribir: falta REPLICATE_API_TOKEN en .env")
            return False

        # Definir directorio de salida
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
            output_base = output_dir / audio_path.stem
        else:
            output_base = audio_path.with_suffix('')

        # ✅ USAR LA FUNCIÓN UNIFICADA ✅
        success = self.transcribe_audio_with_compression_check(audio_path, output_base)

        if success:
            print(f"\n✅ TRANSCRIPCIÓN COMPLETADA")
            print(f"   📝 Transcripción SRT: {output_base}_transcription.srt")
            print(f"   📋 Metadatos JSON: {output_base}_transcription.json")
            print(f"   📖 Formatos legibles: {output_base}_*.txt")
            return True

        print("❌ Falló la transcripción del audio")
        return False

    def save_transcription(self, transcription_data, output_path):
        """
        Guarda la transcripción en diferentes formatos y genera versiones legibles
        """
        if not transcription_data:
            return False

        base_path = Path(output_path).with_suffix('')

        try:
            # Guardar como SRT
            srt_path = f"{base_path}_transcription.srt"
            with open(srt_path, 'w', encoding='utf-8') as f:
                if isinstance(transcription_data, str):
                    f.write(transcription_data)
                else:
                    f.write(str(transcription_data))

            # Guardar JSON completo para análisis posterior
            json_path = f"{base_path}_transcription.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(transcription_data, f, ensure_ascii=False, indent=2)

            print(f"📄 Transcripción guardada:")
            print(f"   🎬 SRT: {Path(srt_path).name}")
            print(f"   📋 JSON: {Path(json_path).name}")

            # NUEVA FUNCIONALIDAD: Generar formatos legibles automáticamente
            self.generate_readable_formats(transcription_data, base_path)

            return True

        except Exception as e:
            print(f"❌ Error guardando transcripción: {str(e)}")
            return False

    def generate_readable_formats(self, transcription_data, base_path):
        """
        Genera formatos legibles de la transcripción usando el formateador integrado
        """
        print(f"\n🔄 GENERANDO FORMATOS LEGIBLES...")

        try:
            # Extraer contenido SRT de los datos de transcripción
            srt_content = None

            if isinstance(transcription_data, str):
                srt_content = transcription_data
            elif isinstance(transcription_data, dict):
                # Buscar en diferentes campos posibles
                if 'transcription' in transcription_data:
                    srt_content = transcription_data['transcription']
                elif 'segments' in transcription_data:
                    # Convertir segments a formato SRT
                    srt_lines = []
                    for i, segment in enumerate(transcription_data['segments'], 1):
                        start = segment.get('start', 0)
                        end = segment.get('end', 0)
                        text = segment.get('text', '').strip()

                        # Convertir segundos a formato SRT
                        start_time = f"{int(start // 3600):02d}:{int((start % 3600) // 60):02d}:{int(start % 60):02d},{int((start % 1) * 1000):03d}"
                        end_time = f"{int(end // 3600):02d}:{int((end % 3600) // 60):02d}:{int(end % 60):02d},{int((end % 1) * 1000):03d}"

                        srt_lines.append(f"{i}")
                        srt_lines.append(f"{start_time} --> {end_time}")
                        srt_lines.append(text)
                        srt_lines.append("")

                    srt_content = '\n'.join(srt_lines)

            if not srt_content:
                print("⚠️ No se pudo extraer contenido SRT para formatear")
                return False

            # Procesar con el formateador
            formatter = TranscriptionFormatter()
            segments_count = formatter.parse_srt_content(srt_content)

            if segments_count == 0:
                print("⚠️ No se pudieron procesar segmentos para formatear")
                return False

            print(f"✅ Procesados {segments_count} segmentos")

            # Generar formatos
            base_name = Path(base_path).name
            output_dir = Path(base_path).parent

            formats = [
                ("LEGIBLE", "Transcripción limpia por minutos", formatter.generate_clean_transcript),
                ("CONVERSACION", "Formato de conversación continua", formatter.generate_conversation_format),
                ("TEMAS", "Organizado por bloques temáticos", formatter.generate_summary_by_topics),
                ("INDICE", "Índice buscable por palabras", formatter.generate_searchable_index)
            ]

            generated_files = []
            for format_name, description, method in formats:
                output_path = output_dir / f"{base_name}_{format_name}.txt"
                try:
                    method(output_path)
                    if output_path.exists() and output_path.stat().st_size > 500:
                        size_kb = output_path.stat().st_size / 1024
                        print(f"   ✅ {description}: {output_path.name} ({size_kb:.1f} KB)")
                        generated_files.append(output_path)
                    else:
                        print(f"   ⚠️ {format_name}: Archivo muy pequeño o vacío")
                except Exception as e:
                    print(f"   ❌ Error en {format_name}: {str(e)}")

            if generated_files:
                print(f"🎉 Generados {len(generated_files)} formatos legibles adicionales!")
                print(f"⏱️ Duración total: {formatter.seconds_to_readable(formatter.total_duration)}")

            return len(generated_files) > 0

        except Exception as e:
            print(f"⚠️ Error generando formatos legibles: {str(e)}")
            print("   La transcripción básica sigue disponible")
            return False

    def process_downloaded_video(self, video_path, extract_audio=True, transcribe=True):
        """
        Procesa un video descargado: extrae audio y transcribe
        ACTUALIZADO: Incluye compresión automática para archivos grandes
        """
        video_path = Path(video_path)

        if not video_path.exists():
            print(f"❌ Video no encontrado: {video_path}")
            return False

        print(f"\n🔄 Procesando video: {video_path.name}")

        results = {
            'video_path': str(video_path),
            'audio_extracted': False,
            'transcribed': False,
            'audio_path': None,
            'transcription_path': None
        }

        # Extraer audio si se solicita
        if extract_audio:
            audio_path = video_path.with_suffix('.mp3')

            if self.extract_audio_from_video(video_path, audio_path):
                results['audio_extracted'] = True
                results['audio_path'] = str(audio_path)

                # ✨ NUEVA LÓGICA: Transcribir con compresión automática si es necesario ✨
                if transcribe and self.replicate_token:
                    success = self.transcribe_audio_with_compression_check(audio_path, video_path.with_suffix(''))

                    if success:
                        results['transcribed'] = True
                        results['transcription_path'] = f"{video_path.with_suffix('')}_transcription.srt"

        return results

    def extract_video_urls_from_text(self, text):
        """
        Extrae todas las URLs de video (Vimeo y Loom) de un texto/HTML
        """
        found_videos = []

        print(f"🔍 Analizando texto de {len(text)} caracteres...")

        # === BUSCAR VIDEOS DE VIMEO ===
        print("\n🎬 Buscando videos de VIMEO...")
        found_vimeo_urls = set()
        found_vimeo_ids = set()

        for i, pattern in enumerate(self.vimeo_patterns):
            matches = re.findall(pattern, text, re.IGNORECASE)
            print(f"   Patrón Vimeo {i + 1}: {len(matches)} coincidencias")

            for match in matches:
                if match.startswith('http'):
                    found_vimeo_urls.add(match)
                elif match.isdigit() and len(match) >= 8:
                    found_vimeo_ids.add(match)

        # Procesar URLs de Vimeo
        for raw_url in found_vimeo_urls:
            video_id_match = re.search(r'/video/(\d+)', raw_url)
            if video_id_match:
                video_id = video_id_match.group(1)
                clean_url = self.clean_video_url(raw_url, 'vimeo')

                found_videos.append({
                    'platform': 'vimeo',
                    'original': raw_url,
                    'clean': clean_url,
                    'video_id': video_id,
                    'source': 'URL completa'
                })

        # Procesar IDs sueltos de Vimeo
        for video_id in found_vimeo_ids:
            if not any(v['video_id'] == video_id and v['platform'] == 'vimeo' for v in found_videos):
                clean_url = f"https://player.vimeo.com/video/{video_id}"

                found_videos.append({
                    'platform': 'vimeo',
                    'original': f"ID: {video_id}",
                    'clean': clean_url,
                    'video_id': video_id,
                    'source': 'Solo ID'
                })

        # === BUSCAR VIDEOS DE LOOM ===
        print("\n📹 Buscando videos de LOOM...")
        found_loom_urls = set()
        found_loom_ids = set()

        for i, pattern in enumerate(self.loom_patterns):
            matches = re.findall(pattern, text, re.IGNORECASE)
            print(f"   Patrón Loom {i + 1}: {len(matches)} coincidencias")

            for match in matches:
                if match.startswith('http'):
                    found_loom_urls.add(match)
                elif re.match(r'^[a-f0-9]{32}$', match):  # ID de Loom (32 hex chars)
                    found_loom_ids.add(match)

        # Procesar URLs de Loom
        for raw_url in found_loom_urls:
            loom_id_match = re.search(r'/(?:embed|share)/([a-f0-9]{32})', raw_url)
            if loom_id_match:
                loom_id = loom_id_match.group(1)
                clean_url = self.clean_video_url(raw_url, 'loom')

                found_videos.append({
                    'platform': 'loom',
                    'original': raw_url,
                    'clean': clean_url,
                    'video_id': loom_id,
                    'source': 'URL completa'
                })

        # Procesar IDs sueltos de Loom
        for loom_id in found_loom_ids:
            if not any(v['video_id'] == loom_id and v['platform'] == 'loom' for v in found_videos):
                clean_url = f"https://www.loom.com/embed/{loom_id}"

                found_videos.append({
                    'platform': 'loom',
                    'original': f"ID: {loom_id}",
                    'clean': clean_url,
                    'video_id': loom_id,
                    'source': 'Solo ID'
                })

        return found_videos

    def read_html_file(self, file_path):
        """
        Lee un archivo HTML/TXT
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Intentar con otra codificación
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()

    def download_with_ytdlp(self, url, platform, output_dir="./downloads", referer=None):
        """
        Descarga el video usando yt-dlp según la plataforma con progreso visible
        """
        # Crear directorio de descarga si no existe
        Path(output_dir).mkdir(exist_ok=True)

        # Crear subdirectorio por plataforma
        platform_dir = Path(output_dir) / platform
        platform_dir.mkdir(exist_ok=True)

        # Construir comando base con progreso visible
        cmd = [
            "yt-dlp",
            url,
            "-o", f"{platform_dir}/%(title)s.%(ext)s",
            "--write-description",
            "--write-info-json",
            "--progress",  # Mostrar progreso
            "--no-warnings",  # Reducir ruido
            "--console-title"  # Actualizar título de consola
        ]

        # Configuraciones específicas por plataforma
        if platform == 'loom':
            # Loom a veces necesita configuraciones especiales
            cmd.extend([
                "--user-agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            ])

        # Añadir referer si se proporciona
        if referer:
            cmd.extend(["--referer", referer])

        print(f"🔄 Iniciando descarga de {platform.upper()}")
        print(f"🔗 URL: {url}")
        print(f"📁 Directorio: {platform_dir}")
        print("⏳ Descargando...")
        print("-" * 50)

        try:
            # Ejecutar con salida en tiempo real
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       text=True, universal_newlines=True, bufsize=1)

            # Mostrar progreso en tiempo real
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()

                    # Filtrar y mostrar líneas de progreso importantes
                    if any(keyword in line.lower() for keyword in [
                        'downloading', 'progress', '%', 'eta', 'speed',
                        'fragment', 'merging', 'writing', 'completed'
                    ]):
                        # Limpiar y formatear la línea de progreso
                        if '[download]' in line:
                            # Extraer información de progreso
                            if '%' in line and 'ETA' in line:
                                # Línea típica: [download] 45.2% of 123.45MiB at 1.23MiB/s ETA 00:32
                                parts = line.split()
                                percentage = next((p for p in parts if '%' in p), 'N/A')
                                size_info = ''
                                speed_info = ''
                                eta_info = ''

                                for i, part in enumerate(parts):
                                    if 'of' in part and i + 1 < len(parts):
                                        size_info = f" ({parts[i + 1]})"
                                    elif 'at' in part and i + 1 < len(parts):
                                        speed_info = f" | Velocidad: {parts[i + 1]}"
                                    elif 'ETA' in part and i + 1 < len(parts):
                                        eta_info = f" | ETA: {parts[i + 1]}"

                                print(f"📥 Progreso: {percentage}{size_info}{speed_info}{eta_info}")
                            else:
                                # Otras líneas de descarga importantes
                                if 'downloading' in line.lower():
                                    print(f"📥 {line.replace('[download]', '').strip()}")

                        elif any(word in line.lower() for word in ['merging', 'writing']):
                            print(f"🔄 {line}")

                        elif 'completed' in line.lower():
                            print(f"✅ {line}")

            # Esperar a que termine
            return_code = process.poll()

            print("-" * 50)

            if return_code == 0:
                print("✅ Descarga completada exitosamente")

                # Buscar el archivo descargado más reciente
                video_files = []
                for ext in ['*.mp4', '*.webm', '*.mkv', '*.avi', '*.mov']:
                    video_files.extend(platform_dir.glob(ext))

                if video_files:
                    # Ordenar por fecha de modificación (más reciente primero)
                    latest_video = max(video_files, key=lambda x: x.stat().st_mtime)
                    print(f"📁 Archivo guardado: {latest_video.name}")
                    return str(latest_video)

                return True
            else:
                print(f"❌ Error en la descarga (código: {return_code})")

                # Si falla Loom, intentar con la URL de share
                if platform == 'loom' and '/embed/' in url:
                    print("🔄 Intentando con URL de share de Loom...")
                    share_url = url.replace('/embed/', '/share/')
                    return self.download_with_ytdlp(share_url, platform, output_dir, referer)

                return False

        except FileNotFoundError:
            print("❌ Error: yt-dlp no está instalado o no está en el PATH")
            print("Instálalo con: pip install yt-dlp")
            return False
        except Exception as e:
            print(f"❌ Error inesperado durante la descarga: {str(e)}")
            return False

    def process_single_url(self, raw_url, output_dir="./downloads", referer=None, extract_audio=True, transcribe=True):
        """
        Procesa una URL individual (Vimeo o Loom)
        """
        print(f"🔗 URL Original: {raw_url}")

        # Detectar plataforma
        if 'vimeo.com' in raw_url.lower():
            platform = 'vimeo'
        elif 'loom.com' in raw_url.lower():
            platform = 'loom'
        else:
            print("❌ Error: URL no reconocida. Solo se admiten Vimeo y Loom")
            return False

        clean_url = self.clean_video_url(raw_url, platform)
        print(f"🧹 URL Limpia: {clean_url}")
        print(f"🎬 Plataforma: {platform.upper()}")

        # Descargar video
        downloaded_path = self.download_with_ytdlp(clean_url, platform, output_dir, referer)

        # Si la descarga fue exitosa y tenemos la ruta del archivo
        if downloaded_path and isinstance(downloaded_path, str):
            print(f"\n🎯 Video descargado: {downloaded_path}")

            # Procesar el video (extraer audio y transcribir)
            if extract_audio or transcribe:
                results = self.process_downloaded_video(downloaded_path, extract_audio, transcribe)

                if results['audio_extracted']:
                    print(f"🎵 Audio disponible en: {results['audio_path']}")

                if results['transcribed']:
                    print(f"📝 Transcripción disponible en: {results['transcription_path']}")

                return results

            return {'video_path': downloaded_path}

        return downloaded_path

    def process_html_file(self, file_path, output_dir="./downloads", referer=None, extract_audio=True, transcribe=True):
        """
        Procesa un archivo HTML completo buscando Vimeo y Loom
        """
        print(f"📄 Leyendo archivo: {file_path}")

        if not os.path.exists(file_path):
            print(f"❌ Error: El archivo {file_path} no existe")
            return

        html_content = self.read_html_file(file_path)
        video_urls = self.extract_video_urls_from_text(html_content)

        if not video_urls:
            print("❌ No se encontraron videos (Vimeo/Loom) en el archivo")
            return

        # Agrupar por plataforma
        vimeo_count = len([v for v in video_urls if v['platform'] == 'vimeo'])
        loom_count = len([v for v in video_urls if v['platform'] == 'loom'])

        print(f"\n🎯 Se encontraron {len(video_urls)} video(s) total:")
        print(f"   🎬 Vimeo: {vimeo_count}")
        print(f"   📹 Loom: {loom_count}")

        processed_videos = []

        for i, video_info in enumerate(video_urls, 1):
            print(f"\n📹 Video {i} [{video_info['platform'].upper()}]:")
            print(f"   ID: {video_info['video_id']}")
            print(f"   Fuente: {video_info['source']}")
            print(f"   Original: {video_info['original'][:100]}...")
            print(f"   Limpia: {video_info['clean']}")

            # Descargar
            downloaded_path = self.download_with_ytdlp(
                video_info['clean'],
                video_info['platform'],
                output_dir,
                referer
            )

            if downloaded_path and isinstance(downloaded_path, str):
                print(f"✅ Video {i} descargado: {downloaded_path}")

                # Procesar el video (extraer audio y transcribir)
                if extract_audio or transcribe:
                    results = self.process_downloaded_video(downloaded_path, extract_audio, transcribe)
                    results['video_info'] = video_info
                    processed_videos.append(results)

                    if results['audio_extracted']:
                        print(f"   🎵 Audio: {results['audio_path']}")

                    if results['transcribed']:
                        print(f"   📝 Transcripción: {results['transcription_path']}")
            else:
                print(f"   ⚠️  Falló la descarga del video {i}")

        # Resumen final
        if processed_videos:
            print(f"\n📊 RESUMEN DE PROCESAMIENTO:")
            print(f"   Videos descargados: {len(processed_videos)}")
            audio_count = sum(1 for r in processed_videos if r['audio_extracted'])
            transcript_count = sum(1 for r in processed_videos if r['transcribed'])
            print(f"   Audios extraídos: {audio_count}")
            print(f"   Transcripciones: {transcript_count}")

        return processed_videos

    def debug_search(self, file_path):
        """
        Función de debug para analizar detalladamente un archivo HTML
        """
        if not os.path.exists(file_path):
            print(f"❌ Error: El archivo {file_path} no existe")
            return

        html_content = self.read_html_file(file_path)

        print(f"🔍 ANÁLISIS DETALLADO DE: {file_path}")
        print(f"📏 Tamaño del archivo: {len(html_content)} caracteres")
        print("=" * 60)

        # Buscar palabras clave relacionadas con video platforms
        vimeo_mentions = html_content.lower().count('vimeo')
        loom_mentions = html_content.lower().count('loom')
        player_mentions = html_content.lower().count('player.vimeo')
        embed_mentions = html_content.lower().count('embed')
        video_mentions = html_content.lower().count('video')

        print(f"🔤 Menciones de 'vimeo': {vimeo_mentions}")
        print(f"🔤 Menciones de 'loom': {loom_mentions}")
        print(f"🔤 Menciones de 'player.vimeo': {player_mentions}")
        print(f"🔤 Menciones de 'embed': {embed_mentions}")
        print(f"🔤 Menciones de 'video': {video_mentions}")
        print("-" * 40)

        # Buscar con cada patrón de Vimeo
        print("🎬 PATRONES DE VIMEO:")
        for i, pattern in enumerate(self.vimeo_patterns):
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            print(f"Patrón Vimeo {i + 1}: {pattern}")
            print(f"   Encontrados: {len(matches)}")
            if matches:
                for j, match in enumerate(matches[:2]):  # Mostrar solo primeros 2
                    print(f"     {j + 1}. {match}")
                if len(matches) > 2:
                    print(f"     ... y {len(matches) - 2} más")
            print()

        # Buscar con cada patrón de Loom
        print("📹 PATRONES DE LOOM:")
        for i, pattern in enumerate(self.loom_patterns):
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            print(f"Patrón Loom {i + 1}: {pattern}")
            print(f"   Encontrados: {len(matches)}")
            if matches:
                for j, match in enumerate(matches[:2]):  # Mostrar solo primeros 2
                    print(f"     {j + 1}. {match}")
                if len(matches) > 2:
                    print(f"     ... y {len(matches) - 2} más")
            print()

        # Buscar fragmentos que contengan "vimeo" o "loom"
        print("🔍 FRAGMENTOS QUE CONTIENEN PLATAFORMAS DE VIDEO:")

        # Contextos de Vimeo
        vimeo_contexts = []
        for match in re.finditer(r'.{0,50}vimeo.{0,50}', html_content, re.IGNORECASE):
            context = match.group(0)
            vimeo_contexts.append(context)

        # Contextos de Loom
        loom_contexts = []
        for match in re.finditer(r'.{0,50}loom.{0,50}', html_content, re.IGNORECASE):
            context = match.group(0)
            loom_contexts.append(context)

        # Mostrar algunos contextos únicos de Vimeo
        if vimeo_contexts:
            print("   VIMEO contextos:")
            unique_vimeo = list(set(vimeo_contexts))[:3]
            for i, context in enumerate(unique_vimeo):
                print(f"     {i + 1}. ...{context}...")

        # Mostrar algunos contextos únicos de Loom
        if loom_contexts:
            print("   LOOM contextos:")
            unique_loom = list(set(loom_contexts))[:3]
            for i, context in enumerate(unique_loom):
                print(f"     {i + 1}. ...{context}...")

        print(f"\n💡 Total contextos únicos con 'vimeo': {len(set(vimeo_contexts))}")
        print(f"💡 Total contextos únicos con 'loom': {len(set(loom_contexts))}")

    def format_existing_transcription(self, file_path):
        """
        Formatea una transcripción existente en archivos legibles
        """
        file_path = Path(file_path)

        print(f"🔄 FORMATEANDO TRANSCRIPCIÓN EXISTENTE")
        print("=" * 50)
        print(f"📁 Archivo: {file_path.name}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            print(f"📏 Tamaño del archivo: {len(content):,} caracteres")

            # Extraer contenido SRT
            srt_content = None

            # Caso 1: Archivo TXT con JSON embebido (formato de nuestro script)
            if not content.strip().startswith('{') and '{' in content:
                print("📋 Formato detectado: TXT con JSON embebido")
                json_start = content.find('{')
                if json_start != -1:
                    json_content = content[json_start:]
                    try:
                        data = json.loads(json_content)
                        srt_content = self.extract_srt_from_json_data(data)
                    except json.JSONDecodeError:
                        print("⚠️ Error parseando JSON embebido")

            # Caso 2: JSON puro
            elif content.strip().startswith('{'):
                print("📋 Formato detectado: JSON puro")
                try:
                    data = json.loads(content)
                    srt_content = self.extract_srt_from_json_data(data)
                except json.JSONDecodeError:
                    print("⚠️ Error parseando JSON")

            # Caso 3: SRT directo
            else:
                print("📋 Formato detectado: SRT directo")
                srt_content = content

            if not srt_content:
                print("❌ No se pudo extraer contenido SRT válido")
                return False

            print(f"📏 Contenido SRT extraído: {len(srt_content):,} caracteres")

            # Procesar con el formateador
            formatter = TranscriptionFormatter()
            segments_count = formatter.parse_srt_content(srt_content)

            if segments_count == 0:
                print("❌ No se pudieron procesar segmentos válidos")
                return False

            print(f"✅ Procesados {segments_count} segmentos")
            print(f"⏱️ Duración total: {formatter.seconds_to_readable(formatter.total_duration)}")

            # Generar formatos legibles
            base_name = file_path.stem
            output_dir = file_path.parent

            formats = [
                ("LEGIBLE", "Transcripción limpia por minutos", formatter.generate_clean_transcript),
                ("CONVERSACION", "Formato de conversación continua", formatter.generate_conversation_format),
                ("TEMAS", "Organizado por bloques temáticos", formatter.generate_summary_by_topics),
                ("INDICE", "Índice buscable por palabras", formatter.generate_searchable_index)
            ]

            print(f"\n📝 GENERANDO FORMATOS LEGIBLES:")
            generated_files = []

            for format_name, description, method in formats:
                output_path = output_dir / f"{base_name}_{format_name}.txt"
                try:
                    method(output_path)
                    if output_path.exists() and output_path.stat().st_size > 500:
                        size_kb = output_path.stat().st_size / 1024
                        print(f"   ✅ {description}: {output_path.name} ({size_kb:.1f} KB)")
                        generated_files.append(output_path)
                    else:
                        print(f"   ⚠️ {format_name}: Archivo muy pequeño o vacío")
                except Exception as e:
                    print(f"   ❌ Error en {format_name}: {str(e)}")

            print(f"\n🎉 FORMATEO COMPLETADO")
            print(f"   📁 Archivos generados: {len(generated_files)}")
            for file in generated_files:
                size_kb = file.stat().st_size / 1024
                print(f"      📄 {file.name} ({size_kb:.1f} KB)")

            return len(generated_files) > 0

        except Exception as e:
            print(f"❌ Error formateando transcripción: {str(e)}")
            return False

    def extract_srt_from_json_data(self, data):
        """
        Extrae contenido SRT de diferentes estructuras JSON
        """
        # Buscar en transcription_output.transcription
        if 'transcription_output' in data:
            transcription_output = data['transcription_output']
            if isinstance(transcription_output, dict) and 'transcription' in transcription_output:
                raw_srt = transcription_output['transcription']
                return raw_srt.replace('\\n', '\n').replace('\\r', '\r')

        # Buscar en campo transcription directo
        if 'transcription' in data and isinstance(data['transcription'], str):
            raw_srt = data['transcription']
            return raw_srt.replace('\\n', '\n').replace('\\r', '\r')

        # Buscar en otros campos comunes
        search_fields = ['output', 'text', 'result']
        for field in search_fields:
            if field in data and isinstance(data[field], str) and '-->' in data[field]:
                raw_srt = data[field]
                return raw_srt.replace('\\n', '\n').replace('\\r', '\r')

        # Convertir desde segments si está disponible
        if 'segments' in data and isinstance(data['segments'], list):
            srt_lines = []
            for i, segment in enumerate(data['segments'], 1):
                if 'start' in segment and 'end' in segment and 'text' in segment:
                    start = segment['start']
                    end = segment['end']
                    text = segment['text'].strip()

                    # Convertir segundos a formato SRT
                    start_time = f"{int(start // 3600):02d}:{int((start % 3600) // 60):02d}:{int(start % 60):02d},{int((start % 1) * 1000):03d}"
                    end_time = f"{int(end // 3600):02d}:{int((end % 3600) // 60):02d}:{int(end % 60):02d},{int((end % 1) * 1000):03d}"

                    srt_lines.append(f"{i}")
                    srt_lines.append(f"{start_time} --> {end_time}")
                    srt_lines.append(text)
                    srt_lines.append("")

            if srt_lines:
                return '\n'.join(srt_lines)

        return None


def main():
    downloader = VideoDownloader()

    print("🎬 Descargador de Videos de Vimeo y Loom con Transcripción y Formateo")
    print("=" * 70)

    # Verificar configuración
    print("\n🔧 VERIFICANDO CONFIGURACIÓN:")

    # Verificar yt-dlp
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"   yt-dlp: ✅ {version}")
        else:
            print("   yt-dlp: ❌ Error al verificar versión")
    except FileNotFoundError:
        print("   yt-dlp: ❌ No instalado")

    # Verificar ffmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            version = version_line.split(' ')[2] if len(version_line.split(' ')) > 2 else 'Instalado'
            print(f"   ffmpeg: ✅ {version}")
        else:
            print("   ffmpeg: ❌ Error al verificar versión")
    except FileNotFoundError:
        print("   ffmpeg: ❌ No instalado")

    # Verificar Replicate API
    if downloader.replicate_token:
        print(f"   Replicate API: ✅ Token configurado (...{downloader.replicate_token[-8:]})")
    else:
        print("   Replicate API: ❌ Token no configurado")
        print("                   💡 Crea archivo .env con: REPLICATE_API_TOKEN=tu_token")

    # Verificar archivo .env
    env_file = Path('.env')
    if env_file.exists():
        print(f"   Archivo .env: ✅ Encontrado")
    else:
        print(f"   Archivo .env: ⚠️  No encontrado (recomendado)")

    while True:
        print("\n¿Qué quieres hacer?")
        print("1. Descargar una URL específica (Vimeo o Loom)")
        print("2. Procesar archivo HTML/TXT (busca Vimeo y Loom)")
        print("3. Debug: Analizar archivo detalladamente")
        print("4. Procesar video ya descargado (extraer audio + transcribir)")
        print("5. 🆕 Transcribir archivo de audio existente")  # ← NUEVA OPCIÓN
        print("6. Formatear transcripción existente (generar versiones legibles)")
        print("7. Salir")  # ← Numeración actualizada

        choice = input("\nElige una opción (1-7): ").strip()

        if choice == "1":
            url = input("\n🔗 Pega la URL (Vimeo o Loom): ").strip()
            if url:
                output_dir = input("📁 Directorio de descarga (Enter para './downloads'): ").strip()
                if not output_dir:
                    output_dir = "./downloads"

                referer = input("🌐 Referer (opcional, Enter para omitir): ").strip()
                referer = referer if referer else None

                # Preguntar por procesamiento de audio
                extract_audio = input("🎵 ¿Extraer audio? (s/N): ").strip().lower() in ['s', 'y', 'yes', 'sí']
                transcribe = False

                if extract_audio:
                    transcribe = input("📝 ¿Transcribir audio? (s/N): ").strip().lower() in ['s', 'y', 'yes', 'sí']

                result = downloader.process_single_url(url, output_dir, referer, extract_audio, transcribe)

                if result:
                    print("\n✅ Procesamiento completado")

        elif choice == "2":
            file_path = input("\n📄 Ruta del archivo HTML/TXT: ").strip()
            if file_path:
                output_dir = input("📁 Directorio de descarga (Enter para './downloads'): ").strip()
                if not output_dir:
                    output_dir = "./downloads"

                referer = input("🌐 Referer (opcional, Enter para omitir): ").strip()
                referer = referer if referer else None

                # Preguntar por procesamiento de audio
                extract_audio = input("🎵 ¿Extraer audio de todos los videos? (s/N): ").strip().lower() in ['s', 'y',
                                                                                                           'yes', 'sí']
                transcribe = False

                if extract_audio:
                    transcribe = input("📝 ¿Transcribir todos los audios? (s/N): ").strip().lower() in ['s', 'y', 'yes',
                                                                                                       'sí']

                results = downloader.process_html_file(file_path, output_dir, referer, extract_audio, transcribe)

        elif choice == "3":
            file_path = input("\n🔍 Ruta del archivo para analizar: ").strip()
            if file_path:
                downloader.debug_search(file_path)

        elif choice == "4":
            video_path = input("\n🎬 Ruta del video a procesar: ").strip()
            if video_path:
                if not os.path.exists(video_path):
                    print(f"❌ Error: El archivo {video_path} no existe")
                    continue

                extract_audio = input("🎵 ¿Extraer audio? (S/n): ").strip().lower() not in ['n', 'no']
                transcribe = False

                if extract_audio:
                    transcribe = input("📝 ¿Transcribir audio? (S/n): ").strip().lower() not in ['n', 'no']

                results = downloader.process_downloaded_video(video_path, extract_audio, transcribe)

                if results:
                    print("\n✅ Procesamiento completado:")
                    if results['audio_extracted']:
                        print(f"   🎵 Audio: {results['audio_path']}")
                    if results['transcribed']:
                        print(f"   📝 Transcripción: {results['transcription_path']}")

        elif choice == "5":  # ← NUEVA FUNCIONALIDAD
            audio_path = input("\n🎵 Ruta del archivo de audio (MP3, WAV, M4A, etc.): ").strip()
            if audio_path:
                if not os.path.exists(audio_path):
                    print(f"❌ Error: El archivo {audio_path} no existe")
                    continue

                output_dir = input("📁 Directorio de salida (Enter para misma carpeta): ").strip()
                output_dir = output_dir if output_dir else None

                result = downloader.transcribe_audio_file(audio_path, output_dir)

                if result:
                    print("✅ Transcripción completada exitosamente")
                else:
                    print("❌ Error en la transcripción")

        elif choice == "6":  # Formatear transcripción existente
            file_path = input("\n📄 Ruta del archivo de transcripción (JSON o TXT): ").strip()
            if file_path:
                if not os.path.exists(file_path):
                    print(f"❌ Error: El archivo {file_path} no existe")
                    continue

                result = downloader.format_existing_transcription(file_path)
                if result:
                    print("✅ Formatos legibles generados exitosamente")

        elif choice == "7":  # Salir
            print("👋 ¡Hasta luego!")
            break

        else:
            print("❌ Opción inválida. Elige 1, 2, 3, 4, 5, 6 o 7.")


if __name__ == "__main__":
    main()
