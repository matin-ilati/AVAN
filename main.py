
import os
os.environ["QT_MEDIA_BACKEND"] = "ffmpeg"

import sys
import json
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QAction, QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QStackedWidget, QFileDialog,
    QListWidget, QListWidgetItem, QSlider, QMessageBox, QSystemTrayIcon,
    QMenu, QSizePolicy, QProgressBar
)
from PySide6.QtMultimedia import QMediaPlayer

from wallpaper import WallpaperWindow


# -------------------- CONFIG --------------------

APP_NAME = "AVAN"
APP_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "AVAN"
LIBRARY_FILE = APP_DIR / "library.json"

# Backgrounds & Surfaces
BG = "#0B0E14"
PANEL = "#151A27"
PANEL_2 = "#1E2536"
BORDER = "#252D3D"

# Accent Colors
CYAN = "#00D2FF"
PURPLE = "#7C3AED"

# Typography
TEXT = "#F8FAFC"
MUTED = "#94A3B8"

# System Status
SUCCESS = "#10B981"
WARNING = "#F43F5E"

def resource_path(filename):
    base_path = getattr(
        sys, "_MEIPASS",
        str(Path(__file__).resolve().parent)
    )
    return str(Path(base_path) / filename)

ICON_PATH = resource_path("icon.ico")

# -------------------- STYLE --------------------

STYLE = f"""
QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-family: "Segoe UI";
    font-size: 10pt;
}}
QLabel {{
    background-color: transparent;
}}

QStackedWidget {{
    background-color: transparent;
}}

QScrollArea {{
    background-color: transparent;
    border: none;
}}

QListWidget {{
    background-color: transparent;
}}

QFrame#Sidebar {{
    background-color: {PANEL};
    border-right: 1px solid {BORDER};
}}

QFrame#Panel {{
    background-color: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 14px;
}}

QLabel#Brand {{
    font-size: 23pt;
    font-weight: 800;
    color: #A78BFA;
}}

QLabel#Tagline {{
    color: {MUTED};
    font-size: 9pt;
}}

QLabel#PageTitle {{
    font-size: 23pt;
    font-weight: 700;
}}

QLabel#SectionTitle {{
    font-size: 13pt;
    font-weight: 700;
}}

QLabel#Muted {{
    color: {MUTED};
}}

QPushButton {{
    background-color: #211936;
    border: 1px solid #493078;
    border-radius: 9px;
    padding: 10px 15px;
    color: #EDE5FF;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: #38245F;
    border: 1px solid #9B6BFF;
    color: white;
}}

QPushButton:pressed {{
    background-color: #542DA0;
    border: 1px solid #7C3AED;
    color: white;
}}

QPushButton#Primary {{
    background-color: #7C3AED;
    color: white;
    border: 1px solid #9461F5;
    font-weight: 800;
}}

QPushButton#Primary:hover {{
    background-color: #9461F5;
    border: 1px solid #B69AFF;
}}

QPushButton#Primary:pressed {{
    background-color: #5425A8;
    border: 1px solid #7C3AED;
}}

QPushButton#Nav {{
    text-align: left;
    padding: 13px;
    background: transparent;
    border: none;
    color: #94A3B8;
}}

QPushButton#Nav:hover {{
    background-color: #211936;
    color: #C4B5FD;
}}

QPushButton#NavActive {{
    text-align: left;
    padding: 13px;
    background-color: #30204D;
    color: #C4B5FD;
    border: 1px solid #7C3AED;
}}

QFrame#VideoCard {{
    background-color: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 13px;
}}

QFrame#VideoCard:hover {{
    background-color: #211936;
    border: 1px solid #9461F5;
}}

QListWidget {{
    background-color: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 5px;
}}

QListWidget::item {{
    padding: 12px;
    border-radius: 7px;
}}

QListWidget::item:selected {{
    background-color: #1B2B32;
    color: {CYAN};
}}

QSlider::groove:horizontal {{
    background: {BORDER};
    height: 6px;
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: {PURPLE};
    width: 15px;
    margin: -5px 0;
    border-radius: 7px;
}}

QProgressBar {{
    background-color: {BORDER};
    border: none;
    border-radius: 4px;
    height: 7px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {CYAN};
    border-radius: 4px;
}}
"""


# -------------------- VIDEO CARD --------------------

class VideoCard(QFrame):
    selected = Signal(str)

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.setObjectName("VideoCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(145)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 13, 14, 13)

        icon = QLabel("▶")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("""
            font-size: 26pt;
            color: #A78BFA;
            background: #211936;
            border-radius: 9px;
            padding: 12px;
        """)

        name = QLabel(Path(path).name)
        name.setStyleSheet("font-weight: 700;")
        name.setWordWrap(True)

        folder = QLabel(str(Path(path).parent))
        folder.setObjectName("Muted")
        folder.setWordWrap(True)

        layout.addWidget(icon, 1)
        layout.addWidget(name)
        layout.addWidget(folder)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected.emit(self.path)
        super().mousePressEvent(event)


# -------------------- MAIN WINDOW --------------------

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("AVAN")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.resize(1120, 720)
        self.setMinimumSize(900, 600)

        self.wallpaper = WallpaperWindow()
        self.selected_video = None
        self.library = []
        self.nav_buttons = []

        APP_DIR.mkdir(parents=True, exist_ok=True)
        self.load_library()

        self.build_ui()
        self.create_tray()
        self.refresh_library()
        self.update_stats()

        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(2000)

    # ---------------- UI ----------------

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)

        main_layout = QHBoxLayout(root)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)

        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(18, 25, 18, 20)
        side_layout.setSpacing(10)

        brand = QLabel("AVAN")
        brand.setObjectName("Brand")

        tagline = QLabel("YOUR DESKTOP,\nIN MOTION.")
        tagline.setObjectName("Tagline")

        side_layout.addWidget(brand)
        side_layout.addWidget(tagline)
        side_layout.addSpacing(35)

        self.stack = QStackedWidget()

        pages = [
            ("▦   Library", self.create_library_page()),
            ("☷   Playlist", self.create_playlist_page()),
            ("⚙   Settings", self.create_settings_page())
        ]

        for index, (name, page) in enumerate(pages):
            button = QPushButton(name)
            button.setObjectName("Nav")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda checked=False, i=index: self.change_page(i)
            )
            self.nav_buttons.append(button)
            side_layout.addWidget(button)
            self.stack.addWidget(page)

        side_layout.addStretch()

        exit_button = QPushButton("⏻   Exit AVAN")
        exit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_button.setStyleSheet("""
            QPushButton {
                background-color: #2A1724;
                color: #F43F5E;
                border: 1px solid #5B2639;
                border-radius: 9px;
                padding: 11px;
                font-weight: 700;
                text-align: left;
            }

            QPushButton:hover {
                background-color: #482033;
                border: 1px solid #F43F5E;
                color: white;
            }
        """)
        exit_button.clicked.connect(self.quit_app)

        side_layout.addWidget(exit_button)

        version = QLabel("AVAN DESKTOP\nVersion 1.0")
        version.setObjectName("Muted")
        side_layout.addWidget(version)

        # Main content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 24, 28, 15)
        content_layout.setSpacing(18)

        self.header_title = QLabel("Library")
        self.header_title.setObjectName("PageTitle")

        self.header_subtitle = QLabel("Manage your desktop wallpapers.")
        self.header_subtitle.setObjectName("Muted")

        content_layout.addWidget(self.header_title)
        content_layout.addWidget(self.header_subtitle)
        content_layout.addWidget(self.stack, 1)

        # Performance strip
        performance = QFrame()
        performance.setObjectName("Panel")
        performance.setFixedHeight(72)

        perf_layout = QHBoxLayout(performance)
        perf_layout.setContentsMargins(18, 8, 18, 8)

        self.cpu_label = QLabel("CPU: --")
        self.ram_label = QLabel("RAM: --")
        self.gpu_label = QLabel("GPU: N/A")

        for label in (self.cpu_label, self.ram_label, self.gpu_label):
            label.setStyleSheet(f"color: {MUTED}; font-weight: 600;")
            perf_layout.addWidget(label)
            perf_layout.addStretch()

        content_layout.addWidget(performance)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content, 1)

        self.change_page(0)

    # ---------------- PAGES ----------------

    def create_library_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        banner = QFrame()
        banner.setObjectName("Panel")
        banner_layout = QHBoxLayout(banner)
        banner_layout.setContentsMargins(20, 18, 20, 18)

        text_layout = QVBoxLayout()
        title = QLabel("Make your desktop alive.")
        title.setObjectName("SectionTitle")

        subtitle = QLabel("Choose a video and turn it into a live wallpaper.")
        subtitle.setObjectName("Muted")

        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)

        add_button = QPushButton("+  Add Wallpaper")
        add_button.setObjectName("Primary")
        add_button.clicked.connect(self.add_wallpaper)

        banner_layout.addLayout(text_layout, 1)
        banner_layout.addWidget(add_button)

        layout.addWidget(banner)

        heading = QLabel("YOUR WALLPAPERS")
        heading.setObjectName("Muted")
        layout.addWidget(heading)

        self.library_scroll = QWidget()
        self.library_grid = QGridLayout(self.library_scroll)
        self.library_grid.setContentsMargins(0, 0, 0, 0)
        self.library_grid.setSpacing(13)

        layout.addWidget(self.library_scroll, 1)

        return page

    def create_playlist_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)

        heading = QLabel("Your Playlist")
        heading.setObjectName("SectionTitle")
        layout.addWidget(heading)

        description = QLabel("Select a wallpaper from your saved collection.")
        description.setObjectName("Muted")
        layout.addWidget(description)

        self.playlist = QListWidget()
        self.playlist.itemDoubleClicked.connect(self.play_playlist_item)
        layout.addWidget(self.playlist, 1)

        buttons = QHBoxLayout()

        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self.remove_playlist_item)

        play_button = QPushButton("Apply Selected")
        play_button.setObjectName("Primary")
        play_button.clicked.connect(self.play_playlist_item)

        buttons.addWidget(remove_button)
        buttons.addStretch()
        buttons.addWidget(play_button)

        layout.addLayout(buttons)
        return page

    def create_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(18)

        heading = QLabel("Settings")
        heading.setObjectName("SectionTitle")
        layout.addWidget(heading)

        # Audio panel
        audio_panel = QFrame()
        audio_panel.setObjectName("Panel")
        audio_layout = QVBoxLayout(audio_panel)
        audio_layout.setContentsMargins(20, 18, 20, 18)

        audio_title = QLabel("Wallpaper Audio")
        audio_title.setObjectName("SectionTitle")

        volume_row = QHBoxLayout()


        self.volume_value = QLabel("Volume: 0%")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(0)
        self.volume_slider.valueChanged.connect(self.change_volume)


        volume_row.addWidget(self.volume_slider, 1)
        volume_row.addWidget(self.volume_value)

        audio_layout.addWidget(audio_title)
        audio_layout.addLayout(volume_row)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(0)
        self.volume_slider.valueChanged.connect(self.change_volume)

        audio_layout.addWidget(audio_title)
        audio_layout.addWidget(self.volume_value)
        audio_layout.addWidget(self.volume_slider)

        layout.addWidget(audio_panel)

        # About panel
        about = QFrame()
        about.setObjectName("Panel")
        about_layout = QVBoxLayout(about)
        about_layout.setContentsMargins(20, 18, 20, 18)

        about_title = QLabel("About AVAN")
        about_title.setObjectName("SectionTitle")

        about_text = QLabel(
            "AVAN is your personal live wallpaper manager.\n"
            "Your Desktop, in Motion."
        )
        about_text.setObjectName("Muted")

        about_layout.addWidget(about_title)
        about_layout.addWidget(about_text)

        layout.addWidget(about)
        layout.addStretch()

        return page

    # ---------------- NAVIGATION ----------------

    def change_page(self, index):
        self.stack.setCurrentIndex(index)

        names = ["Library", "Playlist", "Settings"]
        subtitles = [
            "Manage your desktop wallpapers.",
            "Organize and apply your favorite wallpapers.",
            "Customize your AVAN experience."
        ]

        self.header_title.setText(names[index])
        self.header_subtitle.setText(subtitles[index])

        for i, button in enumerate(self.nav_buttons):
            button.setObjectName("NavActive" if i == index else "Nav")
            button.style().unpolish(button)
            button.style().polish(button)

    # ---------------- LIBRARY ----------------

    def load_library(self):
        try:
            if LIBRARY_FILE.exists():
                data = json.loads(LIBRARY_FILE.read_text(encoding="utf-8"))
                self.library = [
                    path for path in data
                    if isinstance(path, str) and os.path.isfile(path)
                ]
        except (OSError, json.JSONDecodeError):
            self.library = []

    def save_library(self):
        try:
            LIBRARY_FILE.write_text(
                json.dumps(self.library, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except OSError as error:
            QMessageBox.warning(self, "AVAN", f"Could not save library:\n{error}")

    def refresh_library(self):
        while self.library_grid.count():
            item = self.library_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.playlist.clear()

        for index, path in enumerate(self.library):
            card = VideoCard(path)
            card.selected.connect(self.select_video)

            row = index // 3
            col = index % 3
            self.library_grid.addWidget(card, row, col)

            item = QListWidgetItem(Path(path).name)
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.playlist.addItem(item)

        self.library_grid.setRowStretch(
            (len(self.library) // 3) + 1, 1
        )

    def add_wallpaper(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Wallpaper Videos",
            "",
            "Video Files (*.mp4 *.mkv *.avi *.mov *.wmv)"
        )

        if not paths:
            return

        for path in paths:
            if path not in self.library:
                self.library.append(path)

        self.save_library()
        self.refresh_library()

    def select_video(self, path):
        self.selected_video = path
        self.apply_wallpaper()

    def remove_playlist_item(self):
        item = self.playlist.currentItem()
        if not item:
            return

        path = item.data(Qt.ItemDataRole.UserRole)

        if path in self.library:
            self.library.remove(path)

        if self.selected_video == path:
            self.selected_video = None

        self.save_library()
        self.refresh_library()

    def play_playlist_item(self, item=None):
        item = item or self.playlist.currentItem()

        if item:
            path = item.data(Qt.ItemDataRole.UserRole)
            self.selected_video = path
            self.apply_wallpaper()

    # ---------------- WALLPAPER CONTROLS ----------------

    def apply_wallpaper(self):
        if not self.selected_video:
            return

        try:
            result = self.wallpaper.set_video(self.selected_video)

            if result is False:
                QMessageBox.warning(
                    self, "AVAN", "Could not load this video."
                )
                return

            attached = self.wallpaper.attach_to_desktop()

            if attached is False:
                QMessageBox.warning(
                    self, "AVAN",
                    "The video loaded, but could not attach to desktop."
                )
                return

            self.statusBar().showMessage(
                f"Now playing: {Path(self.selected_video).name}", 5000
            )

        except Exception as error:
            QMessageBox.critical(
                self, "Wallpaper Error", str(error)
            )

    def pause_wallpaper(self):
        self.wallpaper.pause_wallpaper()

    def resume_wallpaper(self):
        self.wallpaper.resume_wallpaper()

    def toggle_playback(self):
        player = self.wallpaper.player

        if player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.pause_wallpaper()
        else:
            self.resume_wallpaper()

    def stop_wallpaper(self):
        self.wallpaper.stop_wallpaper()

    def change_volume(self, value):
        self.volume_value.setText(f"Volume: {value}%")
        self.wallpaper.set_volume(value)

    # ---------------- PERFORMANCE ----------------

    def update_stats(self):
        try:
            import psutil
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            
            cpu_color = WARNING if cpu >= 80 else SUCCESS
            ram_color = WARNING if ram >= 80 else SUCCESS

            self.cpu_label.setStyleSheet(
                f"color: {cpu_color}; font-weight: 700;"
            )

            self.ram_label.setStyleSheet(
                f"color: {ram_color}; font-weight: 700;"
            )

            self.cpu_label.setText(f"CPU: {cpu:.0f}%")
            self.ram_label.setText(f"RAM: {ram:.0f}%")
        except ImportError:
            self.cpu_label.setText("CPU: N/A")
            self.ram_label.setText("RAM: N/A")

    # ---------------- SYSTEM TRAY ----------------

    def create_tray(self):
        self.tray = None

        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        self.tray = QSystemTrayIcon(self)
        self.tray.setToolTip("AVAN — Live Wallpaper")
        self.tray.setIcon(QIcon(ICON_PATH))

        menu = QMenu()

        open_action = QAction("Open AVAN", self)
        open_action.triggered.connect(self.show_window)

        pause_action = QAction("Pause / Resume", self)
        pause_action.triggered.connect(self.toggle_playback)

        stop_action = QAction("Stop Wallpaper", self)
        stop_action.triggered.connect(self.stop_wallpaper)

        quit_action = QAction("Quit AVAN", self)
        quit_action.triggered.connect(self.quit_app)

        menu.addAction(open_action)
        menu.addSeparator()
        menu.addAction(pause_action)
        menu.addAction(stop_action)
        menu.addSeparator()
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.tray_activated)
        self.tray.show()

    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()

    def show_window(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def quit_app(self):
        self.wallpaper.stop_wallpaper()

        if self.tray:
            self.tray.hide()

        QApplication.quit()

    def closeEvent(self, event):
        if self.tray and self.tray.isVisible():
            self.hide()
            self.tray.showMessage(
                "AVAN",
                "AVAN is still running in the system tray.",
                QSystemTrayIcon.MessageIcon.Information,
                2500
            )
            event.ignore()
        else:
            self.wallpaper.stop_wallpaper()
            event.accept()


# -------------------- START --------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("AVAN")
    app.setQuitOnLastWindowClosed(False)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
