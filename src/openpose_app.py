"""
openpose_app.py
Universidad de los Andes · Semillero EMBS
Proyecto: Análisis biomecánico en ciclismo con OpenPose
"""
import os, sys, platform
from pathlib import Path
 
APP_DIR = Path(__file__).parent.resolve()
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
 
try:
    import openpose_core as core
except ImportError:
    print(f"ERROR: No se encontró openpose_core.py en {APP_DIR}")
    sys.exit(1)
 
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QFileDialog, QListWidget,
    QListWidgetItem, QFrame, QScrollArea, QComboBox, QMessageBox,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPalette, QIcon, QPixmap
 
# ── Paleta de colores ────────────────────────────────────────────────────────
C = {
    "bg":        "#0a0f14",
    "surface":   "#0d1520",
    "surface2":  "#112030",
    "surface3":  "#163050",
    "border":    "#1a3a5c",
    "border2":   "#1e4a6e",
    "accent":    "#00a3e0",
    "accent2":   "#0099cc",
    "accent3":   "#78be20",
    "warn":      "#f5a623",
    "error":     "#cc2244",
    "success":   "#78be20",
    "text":      "#F0F2F5",
    "text2":     "#8892A4",
    "text3":     "#4A5568",
    "blue":      "#00629b",
    "purple":    "#772583",
}
 
STYLE = f"""
/* ── Base ── */
QMainWindow, QWidget {{
    background-color: {C['bg']};
    color: {C['text']};
    font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
}}
QLabel {{
    color: {C['text']};
    background: transparent;
}}
 
/* ── Botón primario ── */
QPushButton {{
    background-color: {C['accent']};
    color: {C['bg']};
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 12px;
    font-weight: 700;
    font-family: 'SF Mono', 'Fira Code', monospace;
    letter-spacing: 0.5px;
}}
QPushButton:hover {{
    background-color: #33DDFF;
}}
QPushButton:pressed {{
    background-color: {C['accent2']};
}}
QPushButton:disabled {{
    background-color: {C['surface3']};
    color: {C['text3']};
}}
 
/* ── Botón secundario ── */
QPushButton#secondary {{
    background-color: transparent;
    color: {C['text2']};
    border: 1px solid {C['border2']};
}}
QPushButton#secondary:hover {{
    background-color: {C['surface3']};
    color: {C['text']};
    border-color: {C['text3']};
}}
 
/* ── Botón abrir ── */
QPushButton#open_btn {{
    background-color: transparent;
    color: {C['accent']};
    border: 1px solid {C['accent2']};
    padding: 4px 10px;
    font-size: 10px;
    border-radius: 4px;
    letter-spacing: 0.3px;
}}
QPushButton#open_btn:hover {{
    background-color: {C['accent']};
    color: {C['bg']};
}}
 
/* ── Barra de progreso ── */
QProgressBar {{
    background-color: {C['surface3']};
    border: none;
    border-radius: 3px;
    height: 6px;
    text-align: center;
    font-size: 0px;
}}
QProgressBar::chunk {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {C['accent']},
        stop:1 {C['accent3']}
    );
    border-radius: 3px;
}}
 
/* ── Lista de videos ── */
QListWidget {{
    background-color: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 4px;
    outline: none;
}}
QListWidget::item {{
    background-color: {C['surface2']};
    border: 1px solid {C['border']};
    border-radius: 5px;
    padding: 8px 12px;
    margin: 2px 1px;
    color: {C['text2']};
    font-size: 11px;
}}
QListWidget::item:selected {{
    background-color: {C['surface3']};
    border-color: {C['accent']};
    color: {C['text']};
}}
QListWidget::item:hover {{
    border-color: {C['border2']};
    color: {C['text']};
}}
 
/* ── Combo ── */
QComboBox {{
    background-color: {C['surface2']};
    border: 1px solid {C['border2']};
    border-radius: 5px;
    padding: 5px 10px;
    color: {C['text2']};
    font-size: 11px;
}}
QComboBox QAbstractItemView {{
    background-color: {C['surface2']};
    border: 1px solid {C['border2']};
    selection-background-color: {C['surface3']};
    color: {C['text']};
    outline: none;
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
 
/* ── Scrollbar ── */
QScrollBar:vertical {{
    background: transparent;
    width: 4px;
    border-radius: 2px;
}}
QScrollBar::handle:vertical {{
    background: {C['border2']};
    border-radius: 2px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
 
/* ── Cards ── */
QFrame#card {{
    background-color: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 10px;
}}
QFrame#card_success {{
    background-color: {C['surface']};
    border: 1px solid #1A3A2A;
    border-radius: 10px;
}}
QFrame#divider {{
    background-color: {C['border']};
    max-height: 1px;
}}
QFrame#sidebar {{
    background-color: {C['surface']};
    border-right: 1px solid {C['border']};
}}
"""
 
LANGS = {
    "ES": {
        "app_title":      "Análisis Biomecánico - Ciclismo",
        "subtitle":       "OpenPose - Universidad de los Andes",
        "authors":        "Luis Nieto & Gabriela Osorio",
        "lang_label":     "Idioma",
        "add_videos":     "Agregar Videos",
        "clear_list":     "Limpiar",
        "analyze":        "Iniciar Análisis",
        "select_hint":    "Arrastra videos aquí o usa el botón",
        "results_title":  "Resultados",
        "video_result":   "Video con esqueleto",
        "excel_result":   "Ángulos articulares",
        "chart_result":   "Gráficas",
        "json_result":    "JSON por frame",
        "open_btn":       "Abrir",
        "status_ready":   "Listo",
        "status_running": "Procesando…",
        "status_done":    "Análisis completado",
        "status_error":   "Error en el análisis",
        "frames_label":   "frames",
        "queue_label":    "Cola",
        "progress_label": "Progreso",
        "no_videos":      "No hay videos en la lista",
        "docker_error":   "Docker no disponible",
        "check_docker":   "Verificando Docker…",
        "folder_label":   "Carpeta",
        "empty_hint":     "Los resultados aparecerán aquí",
    },
    "EN": {
        "app_title":      "Biomechanical Analysis · Cycling",
        "subtitle":       "OpenPose · Universidad de los Andes",
        "authors":        "Luis Nieto — Gabriela Osorio",
        "lang_label":     "Language",
        "add_videos":     "Add Videos",
        "clear_list":     "Clear",
        "analyze":        "Start Analysis",
        "select_hint":    "Drag videos here or use the button",
        "results_title":  "Results",
        "video_result":   "Skeleton video",
        "excel_result":   "Joint angles",
        "chart_result":   "Charts",
        "json_result":    "JSON per frame",
        "open_btn":       "Open",
        "status_ready":   "Ready",
        "status_running": "Processing…",
        "status_done":    "Analysis complete",
        "status_error":   "Analysis error",
        "frames_label":   "frames",
        "queue_label":    "Queue",
        "progress_label": "Progress",
        "no_videos":      "No videos in queue",
        "docker_error":   "Docker not available",
        "check_docker":   "Checking Docker…",
        "folder_label":   "Folder",
        "empty_hint":     "Results will appear here",
    }
}
 
 
# ── Worker ───────────────────────────────────────────────────────────────────
class AnalysisWorker(QThread):
    progress      = pyqtSignal(int, int)
    status_update = pyqtSignal(str)
    video_done    = pyqtSignal(dict)
    all_done      = pyqtSignal()
    error         = pyqtSignal(str)
 
    def __init__(self, paths):
        super().__init__()
        self.video_paths = paths
 
    def run(self):
        for path in self.video_paths:
            result = core.run_openpose(
                video_path=Path(path),
                output_dir=core.OUTPUT_DIR,
                progress_callback=lambda c, t: self.progress.emit(c, t),
                status_callback=lambda s: self.status_update.emit(s),
            )
            if "error" in result:
                self.error.emit(result["error"])
            else:
                self.video_done.emit(result)
        self.all_done.emit()
 
 
# ── Drop list ────────────────────────────────────────────────────────────────
class DropList(QListWidget):
    files_dropped = pyqtSignal(list)
 
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDropMode.DropOnly)
 
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
 
    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
 
    def dropEvent(self, e):
        paths = [
            u.toLocalFile() for u in e.mimeData().urls()
            if u.toLocalFile().lower().endswith((".mp4", ".mov", ".avi", ".mkv", ".m4v"))
        ]
        if paths:
            self.files_dropped.emit(paths)
 
 
# ── Etiqueta de estado con punto de color ────────────────────────────────────
class StatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        self.dot = QLabel("●")
        self.dot.setFixedWidth(12)
        self.dot.setStyleSheet(f"color: {C['text3']}; font-size: 8px;")
        self.label = QLabel("Listo")
        self.label.setStyleSheet(f"color: {C['text3']}; font-size: 11px;")
        lay.addWidget(self.dot)
        lay.addWidget(self.label)
        lay.addStretch()
 
    def set(self, text, color):
        self.dot.setStyleSheet(f"color: {color}; font-size: 8px;")
        self.label.setStyleSheet(f"color: {color}; font-size: 11px;")
        self.label.setText(text)
 
 
# ── Card de resultado ────────────────────────────────────────────────────────
class ResultCard(QFrame):
    def __init__(self, result, lang="ES", parent=None):
        super().__init__(parent)
        self.setObjectName("card_success")
        t = LANGS[lang]
 
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(10)
 
        # Header
        hdr = QHBoxLayout()
        tag = QLabel("✓")
        tag.setFixedSize(20, 20)
        tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tag.setStyleSheet(f"""
            background-color: #0D2818;
            color: {C['success']};
            border-radius: 10px;
            font-size: 10px;
            font-weight: 700;
        """)
        name_lbl = QLabel(result["name"])
        name_lbl.setStyleSheet(f"color: {C['text']}; font-size: 13px; font-weight: 600;")
        frames_lbl = QLabel(f"{result['frames']} {t['frames_label']}")
        frames_lbl.setStyleSheet(f"color: {C['text3']}; font-size: 10px;")
        hdr.addWidget(tag)
        hdr.addSpacing(6)
        hdr.addWidget(name_lbl)
        hdr.addStretch()
        hdr.addWidget(frames_lbl)
        lay.addLayout(hdr)
 
        # Divider
        div = QFrame()
        div.setObjectName("divider")
        div.setFixedHeight(1)
        lay.addWidget(div)
 
        # Filas de resultados
        items = [
            ("▶", t["video_result"],  result.get("mp4", "")),
            ("⊞", t["excel_result"],  result.get("excel", "")),
            ("∿", t["chart_result"],  result.get("charts", "")),
            ("{ }", t["json_result"], result.get("json", "")),
            ("⊡", t["folder_label"],  result.get("folder", "")),
        ]
        for icon, label, path in items:
            if not path:
                continue
            row = QHBoxLayout()
            row.setSpacing(8)
 
            icon_lbl = QLabel(icon)
            icon_lbl.setFixedWidth(20)
            icon_lbl.setStyleSheet(f"color: {C['accent']}; font-size: 10px;")
 
            label_lbl = QLabel(label)
            label_lbl.setStyleSheet(f"color: {C['text2']}; font-size: 11px;")
            label_lbl.setFixedWidth(130)
 
            path_lbl = QLabel(Path(path).name if Path(path).is_file() else "...")
            path_lbl.setStyleSheet(f"color: {C['text3']}; font-size: 10px;")
            path_lbl.setMaximumWidth(180)
            path_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
 
            btn = QPushButton(t["open_btn"])
            btn.setObjectName("open_btn")
            btn.setFixedWidth(52)
            btn.setFixedHeight(22)
            btn.clicked.connect(lambda _, p=path: core.open_path(p))
 
            row.addWidget(icon_lbl)
            row.addWidget(label_lbl)
            row.addWidget(path_lbl)
            row.addStretch()
            row.addWidget(btn)
            lay.addLayout(row)
 
 
# ── Ventana principal ────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang   = "ES"
        self.worker = None
        self._build()
        self._retranslate()
 
    def _build(self):
        self.setMinimumSize(1080, 700)
        self.setStyleSheet(STYLE)
 
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
 
        # ── Sidebar izquierdo ─────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(360)
        sv = QVBoxLayout(sidebar)
        sv.setContentsMargins(24, 28, 24, 24)
        sv.setSpacing(0)
 
        # Logo / título
        logo_row = QHBoxLayout()
        dot1 = QLabel("◆")
        dot1.setStyleSheet(f"color: {C['accent']}; font-size: 14px;")
        self.title_lbl = QLabel()
        self.title_lbl.setStyleSheet(
            f"color: {C['text']}; font-size: 15px; font-weight: 700; letter-spacing: -0.3px;"
        )
        logo_row.addWidget(dot1)
        logo_row.addSpacing(8)
        logo_row.addWidget(self.title_lbl)
        logo_row.addStretch()
        sv.addLayout(logo_row)
        sv.addSpacing(4)
 
        self.subtitle_lbl = QLabel()
        self.subtitle_lbl.setStyleSheet(
            f"color: {C['text3']}; font-size: 10px; letter-spacing: 0.5px; padding-left: 22px;"
        )
        sv.addWidget(self.subtitle_lbl)
        sv.addSpacing(20)
 
        # Divider
        sv.addWidget(self._divider())
        sv.addSpacing(18)
 
        # Idioma
        lang_row = QHBoxLayout()
        self.lang_lbl = QLabel()
        self.lang_lbl.setStyleSheet(f"color: {C['text3']}; font-size: 10px; letter-spacing: 0.8px;")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Español", "English"])
        self.lang_combo.setFixedWidth(110)
        self.lang_combo.currentIndexChanged.connect(self._on_lang)
        lang_row.addWidget(self.lang_lbl)
        lang_row.addStretch()
        lang_row.addWidget(self.lang_combo)
        sv.addLayout(lang_row)
        sv.addSpacing(18)
 
        # Cola label
        self.queue_lbl = QLabel()
        self.queue_lbl.setStyleSheet(
            f"color: {C['text3']}; font-size: 9px; font-weight: 700; letter-spacing: 1.5px;"
        )
        sv.addWidget(self.queue_lbl)
        sv.addSpacing(6)
 
        # Lista de videos
        self.video_list = DropList()
        self.video_list.files_dropped.connect(self._add_paths)
        self.video_list.setMinimumHeight(150)
        sv.addWidget(self.video_list)
        sv.addSpacing(6)
 
        self.hint_lbl = QLabel()
        self.hint_lbl.setStyleSheet(f"color: {C['text3']}; font-size: 10px;")
        self.hint_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_lbl.setWordWrap(True)
        sv.addWidget(self.hint_lbl)
        sv.addSpacing(10)
 
        # Botones agregar / limpiar
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.add_btn = QPushButton()
        self.add_btn.clicked.connect(self._on_add)
        self.clear_btn = QPushButton()
        self.clear_btn.setObjectName("secondary")
        self.clear_btn.setFixedWidth(90)
        self.clear_btn.clicked.connect(self._on_clear)
        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.clear_btn)
        sv.addLayout(btn_row)
        sv.addSpacing(22)
 
        sv.addWidget(self._divider())
        sv.addSpacing(18)
 
        # Progreso
        self.progress_lbl = QLabel()
        self.progress_lbl.setStyleSheet(
            f"color: {C['text3']}; font-size: 9px; font-weight: 700; letter-spacing: 1.5px;"
        )
        sv.addWidget(self.progress_lbl)
        sv.addSpacing(8)
 
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6)
        sv.addWidget(self.progress_bar)
        sv.addSpacing(6)
 
        self.progress_detail = QLabel("— / — frames")
        self.progress_detail.setStyleSheet(f"color: {C['text3']}; font-size: 10px;")
        sv.addWidget(self.progress_detail)
        sv.addSpacing(14)
 
        # Status
        self.status_bar = StatusBar()
        sv.addWidget(self.status_bar)
        sv.addSpacing(18)
 
        # Botón analizar
        self.analyze_btn = QPushButton()
        self.analyze_btn.setFixedHeight(44)
        self.analyze_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C['accent']},
                    stop:1 {C['accent3']}
                );
                color: {C['bg']};
                border: none;
                border-radius: 7px;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #33DDFF,
                    stop:1 #33FFB8
                );
            }}
            QPushButton:disabled {{
                background: {C['surface3']};
                color: {C['text3']};
            }}
        """)
        self.analyze_btn.clicked.connect(self._on_analyze)
        sv.addWidget(self.analyze_btn)
        sv.addStretch()
 
        # Footer
        self.authors_lbl = QLabel()
        self.authors_lbl.setStyleSheet(f"color: {C['text3']}; font-size: 9px;")
        self.authors_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sv.addWidget(self.authors_lbl)
 
        root.addWidget(sidebar)
 
        # ── Panel derecho ─────────────────────────────────────────────────
        right = QWidget()
        right.setStyleSheet(f"background-color: {C['bg']};")
        rv = QVBoxLayout(right)
        rv.setContentsMargins(28, 28, 28, 28)
        rv.setSpacing(14)
 
        # Header panel derecho
        rh = QHBoxLayout()
        self.results_title = QLabel()
        self.results_title.setStyleSheet(
            f"color: {C['text']}; font-size: 13px; font-weight: 700; letter-spacing: 0.3px;"
        )
        rh.addWidget(self.results_title)
        rh.addStretch()
 
        # Contador de resultados
        self.results_count = QLabel("0")
        self.results_count.setStyleSheet(f"""
            color: {C['accent']};
            background-color: {C['surface2']};
            border: 1px solid {C['border']};
            border-radius: 10px;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 8px;
        """)
        rh.addWidget(self.results_count)
        rv.addLayout(rh)
 
        rv.addWidget(self._divider())
 
        # Scroll area para cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
 
        self.cards_widget = QWidget()
        self.cards_widget.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.cards_layout.setContentsMargins(0, 0, 6, 0)
        self.cards_layout.setSpacing(10)
 
        # Placeholder cuando no hay resultados
        self.empty_lbl = QLabel()
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_lbl.setStyleSheet(f"color: {C['text3']}; font-size: 12px;")
        self.cards_layout.addWidget(self.empty_lbl)
        self.cards_layout.addStretch()
 
        scroll.setWidget(self.cards_widget)
        rv.addWidget(scroll)
 
        root.addWidget(right, 1)
 
        self._result_count = 0
 
    def _divider(self):
        d = QFrame()
        d.setObjectName("divider")
        d.setFixedHeight(1)
        return d
 
    def _retranslate(self):
        t = LANGS[self.lang]
        self.setWindowTitle(t["app_title"])
        self.title_lbl.setText(t["app_title"])
        self.subtitle_lbl.setText(t["subtitle"])
        self.authors_lbl.setText(t["authors"])
        self.lang_lbl.setText(t["lang_label"].upper())
        self.queue_lbl.setText(t["queue_label"].upper())
        self.hint_lbl.setText(t["select_hint"])
        self.add_btn.setText(t["add_videos"])
        self.clear_btn.setText(t["clear_list"])
        self.analyze_btn.setText(t["analyze"])
        self.progress_lbl.setText(t["progress_label"].upper())
        self.results_title.setText(t["results_title"].upper())
        self.empty_lbl.setText(t["empty_hint"])
        self.status_bar.set(t["status_ready"], C["text3"])
 
    def _on_lang(self, idx):
        self.lang = "ES" if idx == 0 else "EN"
        self._retranslate()
 
    def _on_add(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Seleccionar videos", str(Path.home()),
            "Videos (*.mp4 *.mov *.avi *.mkv *.m4v)"
        )
        self._add_paths(paths)
 
    def _add_paths(self, paths):
        existing = [
            self.video_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.video_list.count())
        ]
        for p in paths:
            if p not in existing:
                item = QListWidgetItem(f"  ▶  {Path(p).name}")
                item.setData(Qt.ItemDataRole.UserRole, p)
                self.video_list.addItem(item)
 
    def _on_clear(self):
        self.video_list.clear()
        self.progress_bar.setValue(0)
        self.progress_detail.setText("— / — frames")
 
    def _on_analyze(self):
        t = LANGS[self.lang]
        if self.video_list.count() == 0:
            QMessageBox.warning(self, "Sin videos", t["no_videos"])
            return
 
        self.status_bar.set(t["check_docker"], C["warn"])
        ok, msg = core.check_docker()
        if not ok:
            QMessageBox.critical(self, t["docker_error"], msg)
            self.status_bar.set(t["status_error"], C["error"])
            return
 
        ok2, msg2 = core.check_openpose_image()
        if not ok2:
            QMessageBox.critical(self, "OpenPose", msg2)
            self.status_bar.set(t["status_error"], C["error"])
            return
 
        paths = [
            self.video_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.video_list.count())
        ]
 
        self.analyze_btn.setEnabled(False)
        self.add_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_bar.set(t["status_running"], C["warn"])
 
        # Ocultar placeholder
        self.empty_lbl.hide()
 
        self.worker = AnalysisWorker(paths)
        self.worker.progress.connect(self._on_progress)
        self.worker.status_update.connect(lambda s: self.status_bar.set(s, C["warn"]))
        self.worker.video_done.connect(self._on_video_done)
        self.worker.all_done.connect(self._on_all_done)
        self.worker.error.connect(self._on_error)
        self.worker.start()
 
    def _on_progress(self, c, total):
        self.progress_bar.setMaximum(max(total, 1))
        self.progress_bar.setValue(c)
        self.progress_detail.setText(f"{c} / {total} frames")
 
    def _on_video_done(self, result):
        card = ResultCard(result, lang=self.lang)
        idx  = self.cards_layout.count() - 1
        self.cards_layout.insertWidget(idx, card)
        self._result_count += 1
        self.results_count.setText(str(self._result_count))
 
    def _on_all_done(self):
        t = LANGS[self.lang]
        self.status_bar.set(t["status_done"], C["success"])
        self.analyze_btn.setEnabled(True)
        self.add_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self.progress_bar.setValue(self.progress_bar.maximum())
 
    def _on_error(self, msg):
        t = LANGS[self.lang]
        self.status_bar.set(t["status_error"], C["error"])
        self.analyze_btn.setEnabled(True)
        self.add_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        # Mostrar error de forma limpia, sin stack trace
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Error")
        dialog.setText("Ocurrió un error durante el análisis.")
        dialog.setInformativeText(msg[:300] if len(msg) > 300 else msg)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.exec()
 
 
# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("OpenPose Biomechanics · Ciclismo")
 
    # Fuente base
    font = QFont("SF Mono", 11)
    app.setFont(font)
 
    win = MainWindow()
    win.show()
    sys.exit(app.exec())