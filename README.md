# HOI4 Mod Launcher

A lightweight alternative mod launcher for **Hearts of Iron IV**. Enable and
disable your mods from a clean dark-themed interface, without the official
Paradox launcher.

![Downloads](https://img.shields.io/badge/download-latest%20release-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

---

## Download

Grab the latest release from the
[Releases page](../../releases/latest) and download the **`.exe`** in the
Assets section (GitHub saves it as `HOI4.Mod.Launcher.exe`).

You do **not** need to install Python. It is a single self-contained file.

### First launch (Windows SmartScreen)

Windows may show a blue *"Windows protected your PC"* warning because the
executable is not code-signed. This is expected for any unofficial program:

1. Click **More info**
2. Click **Run anyway**

Some antivirus software may quarantine or delete the file outright, since
PyInstaller-packed executables can look like a generic packer. This is a false
positive caused by how the executable is bundled, not a sign of malware. If
your antivirus blocks it, add an exclusion for the file and run it again.

**Where to put it:** place the `.exe` anywhere you have write access — Desktop
or Documents are good. Do **not** put it in `C:\Program Files`, which is
read-only for regular users. The launcher saves its settings in a
`config.json` file next to the executable.

---

## Setup

The launcher works out of the box for most people. To change anything:

1. Open the launcher.
2. Click **Settings** (top-right corner).
3. Set the **HOI4 Documents path**
   (default: `Documents\Paradox Interactive\Hearts of Iron IV`).
4. Set the **Game path** — either the folder containing `hoi4.exe` or the full
   path to the executable. A few common Steam locations are checked
   automatically, so you can skip this if your install is in one of them.
5. Pick your language — English or Spanish.
6. Click **Apply**.

---

## Features

- **Mod detection** — automatically scans your HOI4 `mod` folder and lists every
  installed mod with its thumbnail.
- **Fast toggling** — click the checkbox, thumbnail, or row to enable/disable a
  mod.
- **Mod details** — click any mod to see its version, supported game version,
  tags, and replace paths.
- **Save configuration** — writes your selection to `dlc_load.json` so the game
  loads those mods on startup.
- **Launch the game** — start HOI4 straight from the launcher.
- **Played mods history** — a second tab remembers every mod you have saved,
  with the date you last played it.
- **Bilingual** — English and Spanish, switchable at any time.
- **Resizable layout** — drag the divider between the mod list and the details
  panel.

---

## How it works

The launcher only **reads** your mod list and **writes one config file**. It
never modifies your saves, your game files, or the mods themselves.

1. On startup it scans the `.mod` files in
   `Documents\Paradox Interactive\Hearts of Iron IV\mod\` and shows everything
   it finds.
2. You tick the mods you want.
3. Clicking **Save** writes them to `dlc_load.json`:

```json
{
  "enabled_mods": [
    "mod/The Fire Rises.mod",
    "mod/Another Mod.mod"
  ],
  "disabled_dlcs": []
}
```

`dlc_load.json` is the same file the game itself reads to decide which mods to
load — which is why the mods work exactly as they would if you enabled them
from the official launcher.

If you ever want to undo everything, delete that file and the game falls back to
vanilla.

Your launcher preferences (paths, language) and your played-mods history are
stored separately in a `config.json` next to the executable. Deleting that file
just resets the launcher's own settings; it does not affect the game.

---

## Using with other launchers

Because the launcher writes the standard `dlc_load.json`, you can enable a mod
here, launch the game, and the game picks it up. If you also use the Paradox
launcher, avoid toggling the same mods in both at the same time — the last
program to save wins.

---

## Troubleshooting

**No mods appear.** Check the documents path in Settings, and make sure your
mods are in the `mod` folder. Click **Refresh** after adding new ones.

**"Game not found".** Set the game path manually in Settings to the folder
containing `hoi4.exe`.

**Antivirus deleted the exe.** See the SmartScreen section above.

**Thumbnail missing.** Some mods don't ship a `thumbnail.png`. The launcher
just shows the name without an image in that case.

---

## Building from source

<details>
<summary>For developers</summary>

Requires Python 3.8+ and Pillow:

```
pip install Pillow
```

Run it directly:

```
python hoi4_launcher.py
```

Or build a standalone executable with **`build.bat`** (Windows), which installs
PyInstaller and outputs `dist/HOI4 Mod Launcher.exe`:

```
pyinstaller --onefile --noconsole --name "HOI4 Mod Launcher" \
    --exclude-module unittest --exclude-module email \
    --exclude-module http --exclude-module xml --exclude-module pydoc \
    hoi4_launcher.py
```

When frozen, the app resolves its data directory from the executable's own
location rather than `__file__`, so settings persist between runs.

</details>

---

## Contributing

Issues and pull requests are welcome. If you find a mod that doesn't display
correctly, please include the contents of its `.mod` file.

## License

Free to use and modify.
