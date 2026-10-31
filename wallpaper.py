

# wallpaper.py

# Python LiveWallpaper - Windows 10/11

# PySide6 + Windows API



import ctypes

from ctypes import wintypes

from pathlib import Path



from PySide6.QtCore import Qt, QUrl

from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication

from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

from PySide6.QtMultimediaWidgets import QVideoWidget





# =========================================================

# Windows API

# =========================================================



user32 = ctypes.WinDLL("user32", use_last_error=True)



HWND = wintypes.HWND

LPARAM = ctypes.c_ssize_t

WPARAM = ctypes.c_size_t

UINT = wintypes.UINT

ULONG_PTR = ctypes.c_size_t



user32.FindWindowW.argtypes = [

    wintypes.LPCWSTR,

    wintypes.LPCWSTR,

]

user32.FindWindowW.restype = HWND



user32.FindWindowExW.argtypes = [

    HWND,

    HWND,

    wintypes.LPCWSTR,

    wintypes.LPCWSTR,

]

user32.FindWindowExW.restype = HWND



user32.EnumWindows.argtypes = [

    ctypes.WINFUNCTYPE(wintypes.BOOL, HWND, LPARAM),

    LPARAM,

]

user32.EnumWindows.restype = wintypes.BOOL



user32.EnumChildWindows.argtypes = [

    HWND,

    ctypes.WINFUNCTYPE(wintypes.BOOL, HWND, LPARAM),

    LPARAM,

]

user32.EnumChildWindows.restype = wintypes.BOOL



user32.GetClassNameW.argtypes = [

    HWND,

    wintypes.LPWSTR,

    ctypes.c_int,

]

user32.GetClassNameW.restype = ctypes.c_int



user32.GetParent.argtypes = [HWND]

user32.GetParent.restype = HWND



user32.SetParent.argtypes = [HWND, HWND]

user32.SetParent.restype = HWND



user32.GetWindowLongW.argtypes = [HWND, ctypes.c_int]

user32.GetWindowLongW.restype = ctypes.c_long



user32.SetWindowLongW.argtypes = [

    HWND,

    ctypes.c_int,

    ctypes.c_long,

]

user32.SetWindowLongW.restype = ctypes.c_long



user32.SetWindowPos.argtypes = [

    HWND,

    HWND,

    ctypes.c_int,

    ctypes.c_int,

    ctypes.c_int,

    ctypes.c_int,

    UINT,

]

user32.SetWindowPos.restype = wintypes.BOOL



user32.SendMessageTimeoutW.argtypes = [

    HWND,

    UINT,

    WPARAM,

    LPARAM,

    UINT,

    UINT,

    ctypes.POINTER(ULONG_PTR),

]

user32.SendMessageTimeoutW.restype = ctypes.c_ssize_t



user32.IsWindow.argtypes = [HWND]

user32.IsWindow.restype = wintypes.BOOL





# Window constants

GWL_STYLE = -16



WS_CHILD = 0x40000000

WS_POPUP = 0x80000000

WS_VISIBLE = 0x10000000



SWP_NOZORDER = 0x0004

SWP_NOACTIVATE = 0x0010

SWP_FRAMECHANGED = 0x0020

SWP_SHOWWINDOW = 0x0040



WM_SPAWN_WORKER = 0x052C

SMTO_ABORTIFHUNG = 0x0002







def hwnd_value(hwnd):

    """Safely convert a Windows handle to an integer."""

    if not hwnd:

        return 0



    if isinstance(hwnd, int):

        return hwnd



    if isinstance(hwnd, (bytes, bytearray)):

        return int.from_bytes(hwnd, byteorder="little")



    if hasattr(hwnd, "value"):

        return int(hwnd.value or 0)



    return int(hwnd)





def get_class_name(hwnd):

    """Return a window's class name."""

    buffer = ctypes.create_unicode_buffer(256)



    if user32.GetClassNameW(hwnd, buffer, len(buffer)):

        return buffer.value



    return ""





def find_desktop_worker():

    """

    Search for a plausible WorkerW window.



    Returns an HWND integer, or None if no candidate is found.

    The selected window must still be verified on the user's

    Windows configuration.

    """



    progman = user32.FindWindowW("Progman", None)



    if not progman:

        print("ERROR: Progman was not found.")

        return None



    print(f"Progman: {hwnd_value(progman)}")



    # Ask Windows Explorer to create/refresh its desktop layout.

    # 0x052C is an undocumented shell message.

    for wparam, lparam in [

        (0, 0),

        (0x0D, 0),

        (0x0D, 1),

        (0x0D, 2),

    ]:

        result = ULONG_PTR()



        ctypes.set_last_error(0)



        user32.SendMessageTimeoutW(

            progman,

            WM_SPAWN_WORKER,

            wparam,

            lparam,

            SMTO_ABORTIFHUNG,

            1000,

            ctypes.byref(result),

        )



    # Collect top-level windows in their current Z-order.

    top_windows = []



    @ctypes.WINFUNCTYPE(wintypes.BOOL, HWND, LPARAM)

    def enum_top(hwnd, _):

        top_windows.append(hwnd)

        return True



    user32.EnumWindows(enum_top, 0)



    # Locate the window containing the desktop icon view.

    desktop_hosts = []

    host_index = {}



    for index, hwnd in enumerate(top_windows):

        shell_view = user32.FindWindowExW(

            hwnd,

            None,

            "SHELLDLL_DefView",

            None,

        )



        if shell_view:

            desktop_hosts.append(hwnd)

            host_index[hwnd_value(hwnd)] = index



            print(

                f"Desktop host: {hwnd_value(hwnd)} | "

                f"SHELLDLL_DefView: {hwnd_value(shell_view)}"

            )



    if not desktop_hosts:

        print("ERROR: SHELLDLL_DefView was not found.")

        return None



    # Gather all WorkerW windows, including child windows.

    worker_records = []

    seen = set()



    def add_worker(hwnd, parent, location):

        value = hwnd_value(hwnd)



        if not value or value in seen:

            return



        if get_class_name(hwnd) != "WorkerW":

            return



        seen.add(value)



        record = {

            "hwnd": hwnd,

            "parent": parent,

            "location": location,

        }

        worker_records.append(record)



        print(

            f"WorkerW candidate: {value} | "

            f"parent={hwnd_value(parent)} | "

            f"location={location}"

        )



    # First: top-level WorkerW windows.

    for index, hwnd in enumerate(top_windows):

        if get_class_name(hwnd) == "WorkerW":

            add_worker(hwnd, user32.GetParent(hwnd), "top-level")



            # Record whether it appears after a desktop host.

            for host in desktop_hosts:

                host_pos = host_index.get(hwnd_value(host), -1)



                if index > host_pos >= 0:

                    print(

                        f"WorkerW {hwnd_value(hwnd)} appears "

                        f"after desktop host {hwnd_value(host)}"

                    )



    # Second: child WorkerW windows under Progman and desktop hosts.

    parents_to_check = [progman] + desktop_hosts



    for parent in parents_to_check:

        children = []



        @ctypes.WINFUNCTYPE(wintypes.BOOL, HWND, LPARAM)

        def enum_child(hwnd, _):

            children.append(hwnd)

            return True



        user32.EnumChildWindows(parent, enum_child, 0)



        for child in children:

            add_worker(

                child,

                user32.GetParent(child),

                f"child of {hwnd_value(parent)}",

            )



    if not worker_records:

        print("ERROR: Windows did not expose a WorkerW candidate.")

        return None



    # Prefer a WorkerW that follows a desktop host in top-level

    # Z-order. If absent, prefer a WorkerW directly parented to

    # Progman. Otherwise report the available candidate.

    for host in desktop_hosts:

        host_pos = host_index.get(hwnd_value(host), -1)



        for index, hwnd in enumerate(top_windows):

            if (

                index > host_pos >= 0

                and get_class_name(hwnd) == "WorkerW"

            ):

                print(

                    f"Selected top-level WorkerW: "

                    f"{hwnd_value(hwnd)}"

                )

                return hwnd_value(hwnd)



    for record in worker_records:

        if hwnd_value(record["parent"]) == hwnd_value(progman):

            print(

                f"Selected Progman child WorkerW: "

                f"{hwnd_value(record['hwnd'])}"

            )

            return hwnd_value(record["hwnd"])



    chosen = worker_records[0]["hwnd"]



    print(

        f"Selected fallback WorkerW: {hwnd_value(chosen)}"

    )

    return hwnd_value(chosen)





# =========================================================

# Wallpaper window

# =========================================================



class WallpaperWindow(QWidget):



    def __init__(self, parent=None):

        super().__init__(parent)



        self.setWindowTitle("Python LiveWallpaper")



        self.setWindowFlags(

            Qt.WindowType.FramelessWindowHint

            | Qt.WindowType.Tool

        )



        self.setAttribute(

            Qt.WidgetAttribute.WA_NativeWindow,

            True,

        )



        self.attached = False

        self.video_path = None

        self.desktop_hwnd = None



        # Video output

        self.video = QVideoWidget(self)



        layout = QVBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)

        layout.setSpacing(0)

        layout.addWidget(self.video)



        # Player

        self.player = QMediaPlayer(self)

        self.audio = QAudioOutput(self)



        self.player.setVideoOutput(self.video)

        self.player.setAudioOutput(self.audio)



        # Infinite playback

        self.player.setLoops(QMediaPlayer.Loops.Infinite)



        # Default: muted

        self.audio.setVolume(0.0)



        # Diagnostics

        self.player.mediaStatusChanged.connect(

            self._on_media_status

        )

        self.player.playbackStateChanged.connect(

            self._on_playback_state

        )

        self.player.errorOccurred.connect(

            self._on_player_error

        )



    # -----------------------------------------------------

    # Load a video

    # -----------------------------------------------------



    def set_video(self, path):

        """Load a local video file."""



        if not path:

            print("ERROR: No video path provided.")

            return False



        path = str(Path(path).expanduser().resolve())



        if not Path(path).is_file():

            print(f"ERROR: Video file does not exist: {path}")

            return False



        self.video_path = path

        self.player.setSource(QUrl.fromLocalFile(path))



        print(f"Video selected: {path}")

        return True



    # Alias for code that uses setVideo(...)

    def setVideo(self, path):

        return self.set_video(path)



    # -----------------------------------------------------

    # Attach window to desktop

    # -----------------------------------------------------



    def attach_to_desktop(self):

        """Attach the video window to a desktop WorkerW."""



        if not self.video_path:

            print("ERROR: Select a video before attaching.")

            return False



        worker_value = find_desktop_worker()



        if not worker_value:

            print("ATTACH FAILED: no WorkerW candidate.")

            return False



        worker = HWND(worker_value)



        if not user32.IsWindow(worker):

            print("ATTACH FAILED: WorkerW handle is invalid.")

            return False



        # Create the native window handle.

        hwnd_value_self = int(self.winId())

        hwnd = HWND(hwnd_value_self)



        # Show the native window before changing its parent.

        # This also ensures Windows has created the HWND.

        self.show()

        QApplication.processEvents()



        # Change the native window style from top-level popup

        # to a child window.

        style = user32.GetWindowLongW(hwnd, GWL_STYLE)

        style = (style & ~WS_POPUP) | WS_CHILD | WS_VISIBLE



        user32.SetWindowLongW(hwnd, GWL_STYLE, style)



        ctypes.set_last_error(0)

        previous_parent = user32.SetParent(hwnd, worker)

        parent_error = ctypes.get_last_error()



        actual_parent = user32.GetParent(hwnd)



        print(f"Wallpaper HWND: {hwnd_value(hwnd)}")

        print(f"Target WorkerW: {hwnd_value(worker)}")

        print(f"Previous parent: {hwnd_value(previous_parent)}")

        print(f"SetParent last error: {parent_error}")

        print(f"Actual parent: {hwnd_value(actual_parent)}")

        print(f"Expected parent: {hwnd_value(worker)}")



        if hwnd_value(actual_parent) != hwnd_value(worker):

            print("ATTACH FAILED: Windows rejected the parent change.")

            self.attached = False

            return False



        # Size to the primary monitor.
        screen = QApplication.primaryScreen()

        if screen:
            geometry = screen.geometry()
            logical_width = geometry.width()
            logical_height = geometry.height()
            dpr = screen.devicePixelRatio()
            physical_width = round(logical_width * dpr)
            physical_height = round(logical_height * dpr)
        else:
            logical_width = physical_width = 1920
            logical_height = physical_height = 1080
            dpr = 1.0

        # Native Win32 window dimensions use physical pixels.
        ok = user32.SetWindowPos(
            hwnd,
            HWND(0),
            0,
            0,
            physical_width,
            physical_height,
            SWP_NOZORDER
            | SWP_NOACTIVATE
            | SWP_FRAMECHANGED
            | SWP_SHOWWINDOW,
        )

        # Qt widget geometry uses logical pixels.
        self.setGeometry(0, 0, logical_width, logical_height)
        self.video.setGeometry(0, 0, logical_width, logical_height)

        # Fill the screen; crop the edges if aspect ratios differ.
        self.video.setAspectRatioMode(
            Qt.AspectRatioMode.KeepAspectRatioByExpanding
        )

        print(f"Display scaling factor: {dpr}")
        print(f"Logical size: {logical_width}x{logical_height}")
        print(f"Physical size: {physical_width}x{physical_height}")
        print(f"SetWindowPos result: {bool(ok)}")

        self.video.show()

        self.show()

        QApplication.processEvents()



        self.desktop_hwnd = worker_value

        self.attached = True



        self.player.play()



        print("ATTACH COMPLETED; verify desktop visibility.")

        return True



    # Alias for alternate button handlers

    def set_wallpaper(self):

        return self.attach_to_desktop()



    # -----------------------------------------------------

    # Playback controls

    # -----------------------------------------------------



    def pause_wallpaper(self):

        self.player.pause()



    def resume_wallpaper(self):

        if self.video_path:

            self.player.play()



    def stop_wallpaper(self):

        self.player.stop()

        self.hide()

        self.attached = False

        print("Wallpaper stopped.")



    def set_volume(self, value):

        """

        Accept either 0.0-1.0 or 0-100.

        Example: set_volume(50) means 50%.

        """

        value = float(value)



        if value > 1.0:

            value = value / 100.0



        value = max(0.0, min(1.0, value))

        self.audio.setVolume(value)



    # -----------------------------------------------------

    # Player diagnostics

    # -----------------------------------------------------



    def _on_media_status(self, status):

        print(f"MEDIA STATUS: {status}")



    def _on_playback_state(self, state):

        print(f"PLAYBACK STATE: {state}")



    def _on_player_error(self, error, error_string):

        print(f"PLAYER ERROR: {error}")

        print(f"PLAYER ERROR DETAILS: {error_string}")
