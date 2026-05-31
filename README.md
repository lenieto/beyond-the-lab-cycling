# Beyond the Motion Lab: Low-Cost Fatigue Monitoring in Cycling

Universidad de los Andes, Departamento de Ingeniería Biomédica.

Este repositorio contiene el código y los notebooks asociados al artículo *Beyond the Motion Lab: Low-Cost Fatigue Monitoring in Cycling via Deep Learning*. El proyecto propone una alternativa de bajo costo y sin marcadores para detectar fatiga en ciclistas a partir de video del plano sagital, combinando OpenPose para estimación de pose con un pipeline de clasificación supervisada (LSTM, LSTM con atención y XGBoost).

Todo el análisis es bidimensional y está enfocado en el plano sagital izquierdo. No se incluye análisis 3D en esta versión.

## Contenido del repositorio

Cuando descargas el repositorio desde GitHub como ZIP, la carpeta se llama `beyond-the-lab-cycling-main`. Su contenido es el siguiente:

```
beyond-the-lab-cycling-main/
├── docker/                   configuración para construir la imagen de OpenPose
├── notebooks/                cuadernos de análisis y entrenamiento de modelos
├── src/                      scripts de Python para el pipeline de procesamiento
├── .gitignore
└── README.md
```

Las carpetas `data/` y `outputs/` no están versionadas porque contienen videos y resultados de los participantes del estudio. El usuario debe crearlas manualmente al usar el sistema con sus propios datos, como se explica más adelante.

### Estructura recomendada al trabajar localmente

Una vez descomprimido el ZIP, conviene crear las carpetas de trabajo dentro del proyecto:

```
beyond-the-lab-cycling-main/
├── docker/
├── notebooks/
├── src/
├── data/
│   └── raw/                  aquí van los videos en .MOV o .MP4
├── outputs/                  aquí se guardan los resultados por sujeto
│   ├── figures/
│   ├── metrics/
│   └── models/
├── .gitignore
└── README.md
```

En macOS o Linux:

```bash
cd beyond-the-lab-cycling-main
mkdir -p data/raw outputs/figures outputs/metrics outputs/models
```

En Windows (PowerShell):

```powershell
cd beyond-the-lab-cycling-main
mkdir data\raw, outputs\figures, outputs\metrics, outputs\models
```

## Requisitos previos

Para correr el pipeline completo se necesitan tres cosas: una versión reciente de Python, las dependencias de Python listadas más abajo, y Docker Desktop con la imagen de OpenPose construida localmente.

### Python

Se requiere Python 3.10 o superior. Si no lo tienes instalado, puedes descargarlo desde [python.org](https://www.python.org/downloads/).

### Dependencias de Python

Desde la raíz del proyecto, instala los paquetes necesarios:

```bash
pip install PyQt6 opencv-python pandas openpyxl matplotlib ipywidgets tqdm numpy scipy scikit-learn torch xgboost tsfel
```

`torch` y `xgboost` son necesarios para los notebooks de entrenamiento. `tsfel` se usa para la extracción de características en el pipeline de XGBoost.

### Docker Desktop

OpenPose se ejecuta dentro de un contenedor Docker para evitar problemas de compatibilidad entre sistemas operativos.

#### Instalación en macOS

1. Entra a [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) y descarga Docker Desktop para Mac. Si tu equipo tiene chip Apple Silicon (M1, M2, M3, M4), elige esa versión. Si es Intel, descarga la versión correspondiente.
2. Abre el `.dmg` y arrastra Docker a la carpeta Aplicaciones.
3. Abre Docker desde Aplicaciones y acepta los permisos que solicita.
4. Espera a que el ícono de la barra superior se quede estático, lo que indica que el motor de Docker está corriendo.

Para verificar que la instalación fue exitosa, en una terminal:

```bash
docker --version
```

#### Instalación en Windows

Primero hay que habilitar WSL2. En una PowerShell con permisos de administrador, ejecuta:

```powershell
wsl --install
```

Reinicia el computador después de que termine la instalación. Luego descarga Docker Desktop desde la misma página, ejecuta el instalador `.exe` y, durante la instalación, deja marcada la opción "Use WSL2 instead of Hyper-V". Reinicia de nuevo y abre Docker Desktop. Espera a que aparezca el mensaje "Engine running" en la esquina inferior izquierda.

Verifica la instalación:

```powershell
docker --version
```

## Construcción de la imagen de OpenPose

Este paso se realiza una sola vez y puede tardar entre 30 y 60 minutos dependiendo de la conexión y del equipo. Posiciónate en la carpeta del proyecto antes de ejecutar el comando.

En macOS o Linux:

```bash
cd beyond-the-lab-cycling-main
docker build --platform linux/amd64 -t openpose-local ./docker
```

En Windows (PowerShell):

```powershell
cd beyond-the-lab-cycling-main
docker build --platform linux/amd64 -t openpose-local .\docker
```

Cuando termine, deberías ver una línea similar a:

```
Successfully tagged openpose-local:latest
```

## Cómo usar el sistema

El flujo de trabajo tiene dos etapas claramente separadas. La primera convierte videos en series de ángulos articulares filtrados. La segunda toma esas series como entrada para entrenar y comparar los clasificadores de fatiga.

### Etapa 1: procesamiento de video con OpenPose

Coloca los videos en `data/raw/` siguiendo la convención `Sujeto_Condicion.MOV` (por ejemplo, `P1_Inicial.MOV` y `P1_Fatiga.MOV`). Los videos deben grabarse del lado izquierdo del ciclista, en plano sagital.

Hay dos formas de procesarlos:

#### Opción A: interfaz gráfica

```bash
python3 src/openpose_app.py
```

En Windows:

```powershell
python src\openpose_app.py
```

La interfaz permite cargar uno o varios videos arrastrándolos, identificar el sujeto y la condición, y lanzar el análisis. Una barra de progreso muestra el avance frame a frame. Al terminar, cada video genera una subcarpeta en `outputs/` con el video con esqueleto sobrepuesto, un Excel de ángulos y la carpeta con los JSON de OpenPose.

#### Opción B: script directo desde Python

Si prefieres procesar los videos sin GUI, puedes importar las funciones de `src/openpose_core.py` desde un notebook o script propio. Las funciones expuestas se documentan al final del archivo.

### Etapa 2: análisis de ángulos y entrenamiento de modelos

Los notebooks en `notebooks/` toman como entrada las carpetas generadas por la etapa anterior y producen las figuras y tablas del paper. El orden recomendado es el siguiente.

| Notebook | Propósito |
|---|---|
| `openpose_analisis.ipynb` | Carga los JSON de cada sujeto, calcula los cuatro ángulos articulares (rodilla, cadera, tobillo, tronco), aplica el filtro Butterworth de paso bajo (6 Hz, orden 4, fase cero) y genera las series por ciclo de pedaleo. |
| `tsfel_features_extraction.ipynb` | Extrae características estadísticas y espectrales de las series de ángulos usando TSFEL, para alimentar a XGBoost. |
| `xgboost_training.ipynb` | Entrena el clasificador XGBoost bajo el esquema de validación leave-one-subject-out. |
| `dl_fatiga_lstm.ipynb` | Entrena las dos variantes de LSTM (con y sin atención) bajo el mismo esquema de validación. |
| `lstm_vs_xgboost_comparison.ipynb` | Compara las tres aproximaciones y genera las tablas comparativas y la matriz de confusión reportadas en el paper. |

En todos los notebooks los sujetos se referencian con códigos anónimos (P1 a P5). Si quieres analizar tus propios datos, basta con que las carpetas en `outputs/` sigan la nomenclatura `Sujeto_Condicion`.

## Resultados generados

Por cada video procesado, el sistema crea una subcarpeta en `outputs/` con los siguientes archivos:

| Archivo | Descripción |
|---|---|
| `*_skeleton.mp4` | Video original con el esqueleto BODY_25 sobrepuesto. |
| `*_angles.xlsx` | Excel con dos hojas: una con los ángulos por frame y otra con estadísticas descriptivas. |
| `*_charts.png` | Gráficas de los ángulos a lo largo del tiempo o del ciclo de pedaleo. |
| `json/` | Una carpeta con un archivo JSON por frame, en el formato nativo de OpenPose. |

Los notebooks de análisis agregan en `outputs/figures/`, `outputs/metrics/` y `outputs/models/` las figuras finales, las tablas con métricas de rendimiento y los pesos entrenados de los modelos.

## Articulaciones analizadas

El estudio se restringe al plano sagital izquierdo. Los ángulos calculados a partir del modelo BODY_25 de OpenPose son los siguientes:

| Articulación | Keypoints utilizados |
|---|---|
| Rodilla izquierda | KP12, KP13, KP14 |
| Cadera izquierda | KP1, KP12, KP13 |
| Tobillo izquierdo | KP13, KP14, KP19 |
| Tronco | Segmento KP5 a KP12 medido contra la vertical |

## Solución de problemas frecuentes

**El sistema dice "Cannot connect to the Docker daemon".** Docker Desktop no está abierto. Ábrelo y espera a que el motor termine de iniciar antes de volver a correr el análisis.

**El sistema dice "No such image: openpose-local".** La imagen no se ha construido todavía. Vuelve a la sección de construcción de la imagen y ejecuta el comando `docker build`.

**El video de salida dura menos de un segundo o se ve verde.** El contenedor de Docker fue interrumpido antes de terminar de procesar. Asegúrate de no cerrar la terminal ni Docker Desktop durante el procesamiento.

**El Excel sale vacío o sin columnas de ángulos.** Confirma que los archivos JSON en `outputs/Sujeto_Condicion/json/` se generaron correctamente y no están vacíos. Si lo están, el contenedor de OpenPose no terminó.

**En macOS aparece "zsh: command not found: code".** Abre VS Code, presiona Cmd+Shift+P, busca "Shell Command: Install 'code' command in PATH" y ejecútalo.

## Autores

Luis Esteban Nieto Marquez (le.nieto@uniandes.edu.co), Gabriela Osorio Garzón (g.osoriog@uniandes.edu.co), Christian Cifuentes-De la Portilla, Nathalia Ortega, y Luis Felipe Giraldo.

Para preguntas, problemas de instalación o colaboraciones, escribir a Luis Esteban Nieto Marquez o a Gabriela Osorio Garzón.

## Cita

Si usas este código o construyes sobre este trabajo, por favor cita el artículo asociado:

```
L. E. Nieto Marquez, G. Osorio Garzón, C. Cifuentes-De la Portilla,
N. Ortega y L. F. Giraldo, "Beyond the Motion Lab: Low-Cost Fatigue
Monitoring in Cycling via Deep Learning," IEEE Colombian Conference
on Applications of Computational Intelligence (ColCACI), 2026.
```
