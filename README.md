# HOI4 Mod Launcher

A lightweight alternative mod launcher for **Hearts of Iron IV**. Manage your mods with a clean, dark-themed interface without relying on the official Paradox launcher.

## Features

- **Mod Detection** - Automatically scans your HOI4 `mod/` folder and displays all installed mods with their thumbnails.
- **Enable/Disable Mods** - Toggle mods on or off with checkboxes. Click the name, thumbnail, or row to toggle.
- **Mod Details** - Click any mod to view its version, supported game version, tags, and replace paths.
- **Save Configuration** - Writes the selected mods to `dlc_load.json` so the game loads them on startup.
- **Launch Game** - Launch HOI4 directly from the launcher (auto-detects Steam paths or configure manually).
- **Bilingual UI** - Switch between Spanish and English from the Settings menu.
- **Resizable Layout** - Split-screen design with a draggable divider between the mod list and details panel.
- **Persistent Settings** - Remembers your game path, documents path, and language between sessions.

## Requirements

- **Python 3.8+** with tkinter (included by default)
- **Pillow** - For mod thumbnail rendering

Install Pillow if you don't have it:

```
pip install Pillow
```

## How to Run

### Option 1: Double-click `launch.bat`

Just double-click the `launch.bat` file in the `custom launcher` folder.

### Option 2: Run from terminal

```
python hoi4_launcher.py
```

## Setup

1. Run the launcher.
2. Click **Settings** (top-right corner).
3. Set the **HOI4 Documents path** (default: `Documents/Paradox Interactive/Hearts of Iron IV`).
4. Set the **Game path** - either the folder containing `hoi4.exe` or the full path to the executable.
5. Select your preferred language.
6. Click **Apply**.

## How It Works

The launcher reads `.mod` files from your HOI4 `mod/` directory and displays them in a list. When you enable mods and click **Save**, it writes the configuration to `dlc_load.json`:

```json
{
  "enabled_mods": [
    "mod/The Fire Rises.mod",
    "mod/Another Mod.mod"
  ],
  "disabled_dlcs": []
}
```

This is the same file the game reads to determine which mods to load.

## File Structure

```
custom launcher/
├── hoi4_launcher.py   # Main application
├── launch.bat         # Quick launch script
├── config.json        # Saved settings (auto-generated)
└── README.md
```

## License

Free to use and modify.
