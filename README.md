# Análisis Biomecánico con OpenPose
**Universidad de los Andes · Semillero EMBS**

Sistema de análisis de movimiento humano usando OpenPose para la detección de ángulos articulares en 2D y 3D.

---

## Contenido del proyecto

```
openpose-workdir/
├── README.md                 ← este archivo
├── Dockerfile                ← imagen Docker de OpenPose
├── openpose_core.py          ← motor central de análisis
├── openpose_app.py           ← interfaz gráfica profesional
├── openpose_analisis.ipynb   ← notebook interactivo (VS Code)
├── INPUT/                    ← coloca aquí tus videos
└── OUTPUT/                   ← los resultados se guardan aquí
```

---

## Requisitos previos

### Python
- Python 3.10 o superior
- Descarga en: https://www.python.org/downloads/

### Dependencias Python
Ejecuta este comando en la terminal una sola vez:

```bash
pip install PyQt6 opencv-python pandas openpyxl matplotlib ipywidgets tqdm
```

### Docker Desktop
OpenPose corre dentro de un contenedor Docker para garantizar compatibilidad en cualquier computador.

---

## Instalación de Docker

### macOS

1. Ve a https://www.docker.com/products/docker-desktop/
2. Descarga Docker Desktop para Mac
   - Si tu Mac tiene chip M1/M2/M3/M4 → descarga **Apple Silicon**
   - Si tu Mac es Intel → descarga **Intel Chip**
3. Abre el archivo `.dmg` descargado
4. Arrastra Docker a la carpeta **Aplicaciones**
5. Abre Docker desde Aplicaciones
6. Acepta los permisos que solicite
7. Espera a que el ícono 🐳 en la barra superior deje de moverse

Verifica la instalación en la terminal:
```bash
docker --version
```
Deberías ver algo como: `Docker version 29.x.x`

---

### Windows

**Paso 1 — Habilitar WSL2** (necesario para Docker en Windows):

1. Abre **PowerShell como Administrador** (clic derecho → "Ejecutar como administrador")
2. Ejecuta:
```powershell
wsl --install
```
3. Reinicia el computador

**Paso 2 — Instalar Docker Desktop:**

1. Ve a https://www.docker.com/products/docker-desktop/
2. Descarga Docker Desktop para Windows
3. Ejecuta el instalador `.exe`
4. Durante la instalación, asegúrate de marcar **"Use WSL2 instead of Hyper-V"**
5. Reinicia el computador
6. Abre Docker Desktop desde el menú inicio
7. Espera a que aparezca **"Engine running"** en la esquina inferior izquierda

Verifica la instalación en PowerShell:
```powershell
docker --version
```

---

## Construir la imagen de OpenPose

Este paso solo se hace **una vez**. Tarda entre 30 y 60 minutos.

### macOS
```bash
cd ~/Downloads/openpose-workdir
docker build --platform linux/amd64 -t openpose-local .
```

### Windows (PowerShell)
```powershell
cd $HOME\Downloads\openpose-workdir
docker build --platform linux/amd64 -t openpose-local .
```

Cuando termine verás el mensaje:
```
Successfully built ...
Successfully tagged openpose-local:latest
```

---

## Cómo usar el sistema

### Opción 1 — Interfaz gráfica (recomendada para uso hospitalario)

```bash
# macOS
python3 ~/Downloads/openpose-workdir/openpose_app.py

# Windows (PowerShell)
python $HOME\Downloads\openpose-workdir\openpose_app.py
```

**Flujo de uso:**
1. Selecciona el idioma (Español / English)
2. Agrega uno o varios videos usando el botón o arrastrándolos
3. Presiona **Analizar**
4. La barra de progreso muestra el avance en tiempo real
5. Al terminar, aparece una tarjeta con las rutas de todos los resultados

### Opción 2 — Notebook interactivo (para investigación)

1. Abre VS Code
2. Abre el archivo `openpose_analisis.ipynb`
3. Corre las celdas en orden de arriba hacia abajo
4. La Celda 1 verifica Docker automáticamente
5. La Celda 2 te permite configurar el video y el nombre del ejercicio

---

## Resultados generados

Por cada video analizado, el sistema genera una subcarpeta en `OUTPUT/` con:

| Archivo | Descripción |
|---|---|
| `*_skeleton.mp4` | Video original con el esqueleto de 25 puntos articulares superpuesto |
| `*_angles.xlsx` | Ángulos articulares por frame en Excel (dos hojas: datos y estadísticas) |
| `*_charts.png` | Gráficas de todos los ángulos a lo largo del tiempo |
| `json/` | Carpeta con un archivo `.json` por cada frame del video |

### Articulaciones detectadas (modelo BODY_25)

| Articulación | Puntos usados |
|---|---|
| Codo derecho | Hombro D → Codo D → Muñeca D |
| Codo izquierdo | Hombro I → Codo I → Muñeca I |
| Rodilla derecha | Cadera D → Rodilla D → Tobillo D |
| Rodilla izquierda | Cadera I → Rodilla I → Tobillo I |
| Cadera derecha | Cuello → Cadera D → Rodilla D |
| Cadera izquierda | Cuello → Cadera I → Rodilla I |
| Hombro derecho | Cuello → Hombro D → Codo D |
| Hombro izquierdo | Cuello → Hombro I → Codo I |

---

## Análisis 3D (dos cámaras)

Para ejercicios que involucran rotación o movimiento fuera del plano frontal, el sistema soporta análisis con dos cámaras sincronizadas.

### Requisitos
- 2 cámaras (iPhones, cámaras web, etc.)
- Las cámaras deben estar a **90° entre sí** (una frontal, una lateral)
- Los videos deben estar sincronizados mediante un punto de referencia común (por ejemplo, un aplauso al inicio)

### Pasos
1. Graba ambos videos simultáneamente
2. Procesa cada video por separado con OpenPose (genera dos carpetas de JSON)
3. Usa el script de triangulación incluido en el notebook para calcular coordenadas 3D

### Ejercicios que requieren análisis 3D
- Rotación interna y externa de hombro
- Elevación en plano escapular (scaption)
- Extensión de hombro
- Zancada lateral

---

## Solución de problemas frecuentes

### "Cannot connect to the Docker daemon"
Docker no está abierto. Abre Docker Desktop y espera a que el ícono deje de moverse.

### "No such image: openpose-local"
La imagen no ha sido construida. Ejecuta el comando `docker build` de la sección anterior.

### El video de salida dura menos de 1 segundo o se ve verde
El proceso de Docker fue interrumpido antes de terminar. Vuelve a correr el análisis sin interrumpir.

### El archivo Excel no tiene datos de ángulos
Verifica que los archivos JSON en `OUTPUT/nombre_video/json/` existan y no estén vacíos.

### "zsh: command not found: code" (macOS)
Abre VS Code, presiona `Cmd+Shift+P`, busca **"Shell Command: Install 'code' command in PATH"** y ejecútalo.

---

## Estructura del código

```
openpose_core.py
│
├── check_docker()              → verifica que Docker esté corriendo
├── check_openpose_image()      → verifica que la imagen exista
├── get_frame_count()           → obtiene frames y FPS de un video
├── run_openpose()              → ejecuta OpenPose en Docker con progreso
├── json_to_dataframe()         → convierte JSON de OpenPose a DataFrame
├── dataframe_to_excel()        → exporta DataFrame a Excel formateado
├── make_angle_charts()         → genera gráficas PNG de los ángulos
└── open_path()                 → abre carpeta en Finder/Explorador
```

---

## Información del proyecto

- **Institución:** Universidad de los Andes, Bogotá, Colombia
- **Semillero:** EMBS — Engineering in Medicine and Biology Society
- **Herramienta base:** OpenPose (Carnegie Mellon University)
- **Modelo de detección:** BODY_25 (25 puntos articulares)
- **Modo de ejecución:** CPU (compatible con cualquier computador)

---

*Para soporte técnico o preguntas sobre el proyecto, contactar al semillero EMBS.*
