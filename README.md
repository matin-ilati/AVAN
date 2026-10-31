# AVAN — Live Wallpaper Manager

**Your Desktop, in Motion.**

AVAN is a Windows desktop application that lets you turn your favorite videos into live wallpapers.

Manage your wallpaper collection, create playlists, control playback, and monitor your system performance through a modern and simple interface.

## Features

- 🎬 Set videos as live desktop wallpapers
- 📚 Manage your wallpaper library
- 📋 Organize wallpapers in a playlist
- 🔊 Control wallpaper audio and volume
- ⏯️ Pause, resume, and stop playback
- 📊 Monitor CPU and RAM usage
- 🖥️ System Tray integration
- 🎨 Modern dark UI with purple accents

## Screenshots

Screenshots coming soon.

## Requirements

- Windows 10 / 11
- Python 3.10 or newer

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/AVAN.git
cd AVAN
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run AVAN:

```bash
python main.py
```

## Building

AVAN can be packaged into a standalone executable using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --noconfirm --clean --windowed --onefile --name "AVAN" --icon "icon.ico" --add-data "icon.ico;." main.py
```

The executable will be generated in the `dist` folder.

## Technologies

- Python
- PySide6
- Qt Multimedia
- PyWin32
- psutil
- PyInstaller

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

**AVAN — Your Desktop, in Motion.**