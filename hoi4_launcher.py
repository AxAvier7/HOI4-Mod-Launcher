#!/usr/bin/env python3
"""HOI4 Mod Launcher - Alternativo"""

import json
import os
import subprocess
import sys
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"

DEFAULT_DOCS = Path.home() / "Documents" / "Paradox Interactive" / "Hearts of Iron IV"
MOD_DIR_NAME = "mod"
JSON_NAME = "dlc_load.json"

THUMB_SIZE = 48
BIG_THUMB_SIZE = 96

LOCALES = {
    "es": {
        "settings": "Configuracion",
        "save": "Guardar",
        "refresh": "Actualizar",
        "launch_game": "Lanzar Juego",
        "mods_enabled": "Mods habilitados",
        "saved_title": "Guardado",
        "saved_msg": "Configuracion guardada.\n{0} mod(s) habilitado(s).",
        "error_title": "Error",
        "save_error": "No se pudo guardar:\n{0}",
        "launch_error": "No se pudo lanzar el juego:\n{0}",
        "game_not_found_title": "Juego no encontrado",
        "game_not_found_msg": "No se encontro hoi4.exe.\nConfigura la ruta del juego en Configuracion.",
        "docs_path_label": "Ruta documentos HOI4:",
        "game_path_label": "Ruta del juego (carpeta o exe):",
        "browse": "Examinar...",
        "browse_docs_title": "Seleccionar carpeta de documentos HOI4",
        "browse_game_title": "Seleccionar carpeta del juego HOI4",
        "apply": "Aplicar",
        "language": "Idioma:",
        "version": "Version",
        "supported": "Soportado",
        "replace_paths": "Reemplaza rutas",
        "tags": "Tags",
        "select_hint": "Selecciona un mod",
        "no_mods": "No se encontraron mods en la carpeta mod.",
        "no_mods_detail": "Haz clic en Actualizar despues de anyadir mods.",
        "tab_mods": "Mods",
        "tab_played": "Jugados",
        "no_played": "Aun no has jugado ningun mod.",
        "no_played_detail": "Los mods que habilites y guardes apareceran aqui.",
        "played_at": "Jugado",
        "clear_history": "Limpiar historial",
    },
    "en": {
        "settings": "Settings",
        "save": "Save",
        "refresh": "Refresh",
        "launch_game": "Launch Game",
        "mods_enabled": "Mods enabled",
        "saved_title": "Saved",
        "saved_msg": "Configuration saved.\n{0} mod(s) enabled.",
        "error_title": "Error",
        "save_error": "Could not save:\n{0}",
        "launch_error": "Could not launch the game:\n{0}",
        "game_not_found_title": "Game not found",
        "game_not_found_msg": "hoi4.exe not found.\nConfigure the game path in Settings.",
        "docs_path_label": "HOI4 Documents path:",
        "game_path_label": "Game path (folder or exe):",
        "browse": "Browse...",
        "browse_docs_title": "Select HOI4 documents folder",
        "browse_game_title": "Select HOI4 game folder",
        "apply": "Apply",
        "language": "Language:",
        "version": "Version",
        "supported": "Supported",
        "replace_paths": "Replace paths",
        "tags": "Tags",
        "select_hint": "Select a mod",
        "no_mods": "No mods found in mod folder.",
        "no_mods_detail": "Click Refresh after adding mods.",
        "tab_mods": "Mods",
        "tab_played": "Played",
        "no_played": "You haven't played any mod yet.",
        "no_played_detail": "Mods you enable and save will appear here.",
        "played_at": "Played",
        "clear_history": "Clear history",
    },
}


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def clean_path(p):
    """Strip quotes and whitespace from a path string."""
    return p.strip().strip('"').strip("'")


def parse_mod_file(filepath):
    info = {
        "name": filepath.stem,
        "version": "",
        "supported_version": "",
        "path": "",
        "tags": [],
        "replace_paths": [],
        "filepath": str(filepath),
    }
    try:
        text = filepath.read_text(encoding="utf-8-sig")
    except Exception:
        return info

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        if line.startswith("tags") and "=" in line:
            tag_lines = []
            if "{" in line:
                content = line.split("{", 1)[1]
                if "}" in content:
                    content = content.split("}")[0]
                    for t in content.split('"'):
                        t = t.strip()
                        if t:
                            tag_lines.append(t)
                else:
                    i += 1
                    while i < len(lines):
                        tl = lines[i].strip()
                        if "}" in tl:
                            content = tl.split("}")[0]
                            for t in content.split('"'):
                                t = t.strip()
                                if t:
                                    tag_lines.append(t)
                            break
                        for t in tl.split('"'):
                            t = t.strip()
                            if t:
                                tag_lines.append(t)
                        i += 1
            info["tags"] = tag_lines
            i += 1
            continue

        if "=" in line:
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"')
            if key.startswith("replace_path"):
                info["replace_paths"].append(val)
            elif key in ("name", "version", "supported_version", "path"):
                info[key] = val
        i += 1

    return info


def scan_mods(mod_dir):
    mods = []
    if not mod_dir.exists():
        return mods
    for f in sorted(mod_dir.glob("*.mod")):
        info = parse_mod_file(f)
        info["thumbnail"] = _find_thumbnail(mod_dir, info)
        mods.append(info)
    return mods


def _find_thumbnail(mod_dir, info):
    mod_folder = info.get("path", "").rstrip("/")
    if not mod_folder:
        mod_folder = f"mod/{info['name']}"
    for ext in ("thumbnail.png", "thumbnail.jpg", "thumbnail.gif"):
        p = mod_dir.parent / mod_folder / ext
        if p.exists():
            return str(p)
    return None


def _format_time(ts):
    try:
        return time.strftime("%Y-%m-%d %H:%M", time.localtime(float(ts)))
    except Exception:
        return ""


def _on_wheel(event):
    if event.num == 4:
        return -1
    if event.num == 5:
        return 1
    delta = event.delta
    if abs(delta) >= 120:
        return int(-1 * (delta / 120))
    return -1 if delta > 0 else 1


class ModLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("HOI4 Mod Launcher")
        self.root.geometry("1000x600")
        self.root.minsize(750, 480)
        self.root.configure(bg="#1a1a2e")

        self.config = load_config()
        self.lang = self.config.get("language", "es")
        self.docs_path = Path(self.config.get("docs_path", str(DEFAULT_DOCS)))
        self.game_path = self.config.get("game_path", "")
        self.mod_dir = self.docs_path / MOD_DIR_NAME
        self.dlc_path = self.docs_path / JSON_NAME

        self.mods = []
        self.enabled_vars = {}
        self.current_detail_idx = None
        self.thumb_refs = []
        self._list_canvases = []

        self.played_items = []
        self.played_thumb_refs = []
        self.current_played_idx = None
        self._played_loaded = False

        self.config_window = None

        self._build_ui()
        self._load_mods()

    def t(self, key):
        return LOCALES.get(self.lang, LOCALES["es"]).get(key, key)

    def _on_wheel(self, event):
        widget = self.root.winfo_containing(event.x_root, event.y_root)
        while widget is not None:
            if isinstance(widget, tk.Canvas) and widget in self._list_canvases:
                if widget.winfo_ismapped():
                    widget.yview_scroll(_on_wheel(event), "units")
                return "break"
            try:
                widget = widget.master
            except Exception:
                return None
        return None

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")

        BG = "#1a1a2e"
        FG = "#e0e0e0"
        ACCENT = "#16213e"
        BTN_BG = "#0f3460"
        BTN_FG = "#e0e0e0"

        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=FG, font=("Segoe UI", 10))
        style.configure("TButton", background=BTN_BG, foreground=BTN_FG,
                         font=("Segoe UI", 10, "bold"), padding=6)
        style.map("TButton",
                   background=[("active", "#1a4a8a")],
                   foreground=[("active", "#ffffff")])
        style.configure("Header.TLabel", background=BG, foreground="#e94560",
                         font=("Segoe UI", 14, "bold"))
        style.configure("Status.TLabel", background=BG, foreground="#888",
                         font=("Segoe UI", 9))
        style.configure("Config.TButton", background=BG, foreground="#888",
                         font=("Segoe UI", 9), padding=2)
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=ACCENT, foreground=FG,
                         font=("Segoe UI", 10, "bold"), padding=(14, 8))
        style.map("TNotebook.Tab",
                   background=[("selected", BTN_BG)],
                   foreground=[("selected", "#ffffff")])

        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=10, pady=(10, 5))
        ttk.Label(header, text="HOI4 Mod Launcher", style="Header.TLabel").pack(side="left")
        self.btn_settings = ttk.Button(header, text=self.t("settings"), style="Config.TButton",
                                       command=self._open_config)
        self.btn_settings.pack(side="right")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.mods_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.mods_tab, text=self.t("tab_mods"))

        self.played_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.played_tab, text=self.t("tab_played"))

        self._build_main_list(self.mods_tab)
        self._build_played_list(self.played_tab)

        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.root.bind_all(seq, self._on_wheel, add="+")

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=10, pady=(5, 10))

        btn_frame = ttk.Frame(bottom)
        btn_frame.pack(fill="x")

        self.btn_save = ttk.Button(btn_frame, text=self.t("save"), command=self._save)
        self.btn_save.pack(side="left", padx=(0, 5))
        self.btn_refresh = ttk.Button(btn_frame, text=self.t("refresh"), command=self._load_mods)
        self.btn_refresh.pack(side="left", padx=5)
        self.btn_launch = ttk.Button(btn_frame, text=self.t("launch_game"), command=self._launch_game)
        self.btn_launch.pack(side="left", padx=5)

        self.status_var = tk.StringVar(value=f"{self.t('mods_enabled')}: 0 / 0")
        ttk.Label(bottom, textvariable=self.status_var, style="Status.TLabel").pack(
            side="right", pady=(8, 0))

    def _build_panels(self, parent):
        """Builds a shared list+detail paned layout and returns a namespace-like dict."""
        paned = ttk.PanedWindow(parent, orient="horizontal")
        paned.pack(fill="both", expand=True)

        left = ttk.Frame(paned)
        paned.add(left, weight=1)

        canvas = tk.Canvas(left, bg="#1a1a2e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(left, orient="vertical", command=canvas.yview)
        mod_frame = ttk.Frame(canvas)

        def _on_configure(e, canvas=canvas, mod_frame=mod_frame):
            canvas.configure(scrollregion=canvas.bbox("all"))

        mod_frame.bind("<Configure>", _on_configure)
        canvas_window = canvas.create_window((0, 0), window=mod_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e, c=canvas, cw=canvas_window: c.itemconfig(cw, width=e.width))
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        right = ttk.Frame(paned, style="TFrame")
        paned.add(right, weight=1)

        detail_frame = tk.Frame(right, bg="#16213e", bd=0)
        detail_frame.pack(fill="both", expand=True)

        detail_title = tk.Label(detail_frame, text=self.t("select_hint"),
                                bg="#16213e", fg="#e94560",
                                font=("Segoe UI", 14, "bold"),
                                anchor="nw", padx=12, pady=12)
        detail_title.pack(fill="x")

        sep = tk.Frame(detail_frame, bg="#0f3460", height=1)
        sep.pack(fill="x", padx=12, pady=(0, 8))

        detail_info = tk.Label(detail_frame, text="", bg="#16213e", fg="#e0e0e0",
                               font=("Segoe UI", 10), anchor="nw",
                               justify="left", padx=12, pady=4, wraplength=300)
        detail_info.pack(fill="both", expand=True, anchor="nw")

        detail_tags = tk.Label(detail_frame, text="", bg="#16213e", fg="#aaa",
                               font=("Segoe UI", 9), anchor="nw",
                               justify="left", padx=12, pady=4)
        detail_tags.pack(fill="x", anchor="nw")

        detail_frame.bind("<Configure>", lambda e, l=detail_info: l.config(wraplength=max(e.width - 24, 50)))

        self._list_canvases.append(canvas)

        return {
            "paned": paned,
            "canvas": canvas,
            "mod_frame": mod_frame,
            "detail_title": detail_title,
            "detail_info": detail_info,
            "detail_tags": detail_tags,
        }

    def _build_main_list(self, parent):
        self.main_panel = self._build_panels(parent)

    def _build_played_list(self, parent):
        played_top = ttk.Frame(parent)
        played_top.pack(fill="x", pady=(6, 2), padx=8)
        self.btn_clear_history = ttk.Button(played_top, text=self.t("clear_history"),
                                            command=self._clear_history)
        self.btn_clear_history.pack(side="left")

        self.played_panel = self._build_panels(parent)

    def _on_tab_changed(self, event):
        if self.notebook.index(self.notebook.select()) == 1 and not self._played_loaded:
            self._load_played()
            self._played_loaded = True

    def _update_ui_texts(self):
        self.btn_settings.config(text=self.t("settings"))
        self.btn_save.config(text=self.t("save"))
        self.btn_refresh.config(text=self.t("refresh"))
        self.btn_launch.config(text=self.t("launch_game"))
        self.btn_clear_history.config(text=self.t("clear_history"))
        self.notebook.tab(0, text=self.t("tab_mods"))
        self.notebook.tab(1, text=self.t("tab_played"))
        for panel in (self.main_panel, self.played_panel):
            panel["detail_title"].config(text=self.t("select_hint"))
        self._update_status()
        if self.current_detail_idx is not None:
            self._select_mod(self.current_detail_idx)
        if self.current_played_idx is not None:
            self._select_played(self.current_played_idx)

    def _load_mods(self):
        for w in self.main_panel["mod_frame"].winfo_children():
            w.destroy()
        self.enabled_vars.clear()
        self.thumb_refs.clear()
        self.current_detail_idx = None

        self.mods = scan_mods(self.mod_dir)

        enabled_mods = self._read_enabled()

        if not self.mods:
            self.main_panel["detail_title"].config(text=self.t("no_mods"))
            self.main_panel["detail_info"].config(text=self.t("no_mods_detail"))
            self.main_panel["detail_tags"].config(text="")
            self._update_status()
            return

        for idx, mod in enumerate(self.mods):
            mod_key = "mod/" + os.path.basename(mod["filepath"])
            var = tk.BooleanVar(value=mod_key in enabled_mods)
            self.enabled_vars[idx] = var

            row = tk.Frame(self.main_panel["mod_frame"], bg="#1a1a2e", pady=4)
            row.pack(fill="x", padx=4)

            cb = tk.Checkbutton(row, variable=var, bg="#1a1a2e", fg="#e0e0e0",
                                selectcolor="#0f3460", activebackground="#1a1a2e",
                                activeforeground="#e94560", width=2,
                                command=self._update_status)
            cb.pack(side="left", padx=(0, 6))

            thumb_path = mod.get("thumbnail")
            if thumb_path:
                try:
                    img = Image.open(thumb_path)
                    img = img.resize((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.thumb_refs.append(photo)
                    lbl = tk.Label(row, image=photo, bg="#1a1a2e", cursor="hand2")
                    lbl.pack(side="left", padx=(0, 8))
                except Exception:
                    pass

            name_lbl = tk.Label(row, text=mod["name"], bg="#1a1a2e", fg="#e0e0e0",
                                font=("Segoe UI", 12, "bold"), anchor="w", cursor="hand2")
            name_lbl.pack(side="left", fill="x", expand=True)

            def toggle_and_select(event, i=idx):
                self.enabled_vars[i].set(not self.enabled_vars[i].get())
                self._update_status()
                self._select_mod(i)

            if thumb_path:
                lbl.bind("<Button-1>", toggle_and_select)
            row.bind("<Button-1>", toggle_and_select)
            name_lbl.bind("<Button-1>", toggle_and_select)

        self._update_status()

    def _read_enabled(self):
        if self.dlc_path.exists():
            try:
                with open(self.dlc_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return set(data.get("enabled_mods", []))
            except Exception:
                pass
        return set()

    def _select_mod(self, idx):
        if idx < len(self.mods):
            self.current_detail_idx = idx
            mod = self.mods[idx]

            self.main_panel["detail_title"].config(text=mod["name"])

            detail_lines = []
            if mod["version"]:
                detail_lines.append(f"{self.t('version')}: {mod['version']}")
            if mod["supported_version"]:
                detail_lines.append(f"{self.t('supported')}: {mod['supported_version']}")
            if mod["replace_paths"]:
                detail_lines.append(f"\n{self.t('replace_paths')} ({len(mod['replace_paths'])}):")
                for rp in mod["replace_paths"][:15]:
                    detail_lines.append(f"  {rp}")
                if len(mod["replace_paths"]) > 15:
                    detail_lines.append(f"  ...+{len(mod['replace_paths'])-15} more")
            self.main_panel["detail_info"].config(text="\n".join(detail_lines))

            if mod["tags"]:
                self.main_panel["detail_tags"].config(text=f"{self.t('tags')}: " + ", ".join(mod["tags"]))
            else:
                self.main_panel["detail_tags"].config(text="")

    def _update_status(self):
        total = len(self.mods)
        enabled = sum(1 for v in self.enabled_vars.values() if v.get())
        self.status_var.set(f"{self.t('mods_enabled')}: {enabled} / {total}")

    def _save(self):
        enabled_mods = []
        for idx, var in self.enabled_vars.items():
            if var.get():
                mod = self.mods[idx]
                enabled_mods.append("mod/" + os.path.basename(mod["filepath"]))
                self._record_played(mod)

        data = {
            "enabled_mods": enabled_mods,
            "disabled_dlcs": []
        }

        try:
            with open(self.dlc_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            save_config(self.config)
            self._played_loaded = False
            messagebox.showinfo(self.t("saved_title"),
                                self.t("saved_msg").format(len(enabled_mods)))
        except Exception as e:
            messagebox.showerror(self.t("error_title"), self.t("save_error").format(e))

    def _history(self):
        return self.config.setdefault("play_history", [])

    def _record_played(self, mod):
        now = time.time()
        hist = self._history()
        entry_key = os.path.basename(mod["filepath"])
        for e in hist:
            if e.get("key") == entry_key:
                e["timestamp"] = now
                e["name"] = mod["name"]
                return
        hist.append({
            "key": entry_key,
            "name": mod["name"],
            "timestamp": now,
        })

    def _clear_history(self):
        if messagebox.askyesno(self.t("clear_history"),
                               self.t("no_played_detail")):
            self.config["play_history"] = []
            save_config(self.config)
            self._played_loaded = False
            self._load_played()

    def _load_played(self):
        panel = self.played_panel
        for w in panel["mod_frame"].winfo_children():
            w.destroy()
        self.played_thumb_refs.clear()
        self.current_played_idx = None

        hist = [e for e in self._history() if e.get("key")]

        mods_by_key = {}
        for mod in scan_mods(self.mod_dir):
            mods_by_key.setdefault(os.path.basename(mod["filepath"]), mod)

        self.played_items = []
        for e in reversed(sorted(hist, key=lambda x: x.get("timestamp", 0))):
            mod = mods_by_key.get(e.get("key"))
            self.played_items.append((e, mod))

        if not self.played_items:
            panel["detail_title"].config(text=self.t("no_played"))
            panel["detail_info"].config(text=self.t("no_played_detail"))
            panel["detail_tags"].config(text="")
            return

        for idx, (entry, mod) in enumerate(self.played_items):
            row = tk.Frame(panel["mod_frame"], bg="#1a1a2e", pady=4)
            row.pack(fill="x", padx=4)

            thumb_path = mod.get("thumbnail") if mod else None
            if thumb_path:
                try:
                    img = Image.open(thumb_path)
                    img = img.resize((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.played_thumb_refs.append(photo)
                    lbl = tk.Label(row, image=photo, bg="#1a1a2e", cursor="hand2")
                    lbl.pack(side="left", padx=(0, 8))
                except Exception:
                    lbl = None
            else:
                lbl = None

            name = entry.get("name") or os.path.splitext(entry["key"])[0]
            sub = f"{self.t('played_at')}: {_format_time(entry.get('timestamp'))}"
            text_frame = tk.Frame(row, bg="#1a1a2e")
            text_frame.pack(side="left", fill="x", expand=True)
            name_lbl = tk.Label(text_frame, text=name, bg="#1a1a2e", fg="#e0e0e0",
                                font=("Segoe UI", 12, "bold"), anchor="w", cursor="hand2")
            name_lbl.pack(fill="x")
            sub_lbl = tk.Label(text_frame, text=sub, bg="#1a1a2e", fg="#888",
                               font=("Segoe UI", 9), anchor="w")
            sub_lbl.pack(fill="x")

            def select(event, i=idx):
                self._select_played(i)

            if lbl:
                lbl.bind("<Button-1>", select)
            row.bind("<Button-1>", select)
            name_lbl.bind("<Button-1>", select)

    def _select_played(self, idx):
        if idx < len(self.played_items):
            self.current_played_idx = idx
            entry, mod = self.played_items[idx]
            panel = self.played_panel

            name = entry.get("name") or os.path.splitext(entry["key"])[0]
            panel["detail_title"].config(text=name)

            lines = [f"{self.t('played_at')}: {_format_time(entry.get('timestamp'))}"]
            if mod:
                if mod["version"]:
                    lines.append(f"{self.t('version')}: {mod['version']}")
                if mod["supported_version"]:
                    lines.append(f"{self.t('supported')}: {mod['supported_version']}")
                if mod["replace_paths"]:
                    lines.append(f"\n{self.t('replace_paths')} ({len(mod['replace_paths'])}):")
                    for rp in mod["replace_paths"][:15]:
                        lines.append(f"  {rp}")
                    if len(mod["replace_paths"]) > 15:
                        lines.append(f"  ...+{len(mod['replace_paths'])-15} more")
                if mod["tags"]:
                    panel["detail_tags"].config(text=f"{self.t('tags')}: " + ", ".join(mod["tags"]))
                else:
                    panel["detail_tags"].config(text="")
            else:
                lines.append(f"({os.path.basename(entry['key'])})")
                panel["detail_tags"].config(text="")

            panel["detail_info"].config(text="\n".join(lines))

    def _launch_game(self):
        exe = self._find_game_exe()
        if exe:
            try:
                subprocess.Popen([str(exe)], cwd=str(exe.parent))
            except Exception as e:
                messagebox.showerror(self.t("error_title"), self.t("launch_error").format(e))
        else:
            messagebox.showwarning(self.t("game_not_found_title"), self.t("game_not_found_msg"))

    def _find_game_exe(self):
        raw = clean_path(self.game_path) if self.game_path else ""
        if raw:
            p = Path(raw)
            if p.is_file() and p.suffix.lower() == ".exe":
                if p.exists():
                    return p
            elif p.is_dir():
                exe = p / "hoi4.exe"
                if exe.exists():
                    return exe

        candidates = [
            Path("C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV/hoi4.exe"),
            Path("D:/SteamLibrary/steamapps/common/Hearts of Iron IV/hoi4.exe"),
            Path("D:/Steam/steamapps/common/Hearts of Iron IV/hoi4.exe"),
            Path("E:/SteamLibrary/steamapps/common/Hearts of Iron IV/hoi4.exe"),
            Path("C:/Program Files/Steam/steamapps/common/Hearts of Iron IV/hoi4.exe"),
        ]
        for c in candidates:
            if c.exists():
                return c
        return None

    def _open_config(self):
        if self.config_window is not None and self.config_window.winfo_exists():
            self.config_window.lift()
            self.config_window.focus_force()
            return

        cfg = tk.Toplevel(self.root)
        self.config_window = cfg
        cfg.title(self.t("settings"))
        cfg.geometry("480x280")
        cfg.configure(bg="#1a1a2e")
        cfg.resizable(False, False)

        tk.Label(cfg, text=self.t("language"), bg="#1a1a2e", fg="#e0e0e0",
                 font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=(10, 0))

        lang_var = tk.StringVar(value=self.lang)
        lang_frame = tk.Frame(cfg, bg="#1a1a2e")
        lang_frame.pack(anchor="w", padx=10, pady=2)
        tk.Radiobutton(lang_frame, text="Espanol", variable=lang_var, value="es",
                        bg="#1a1a2e", fg="#e0e0e0", selectcolor="#0f3460",
                        activebackground="#1a1a2e", activeforeground="#e94560",
                        font=("Segoe UI", 10)).pack(side="left", padx=(0, 15))
        tk.Radiobutton(lang_frame, text="English", variable=lang_var, value="en",
                        bg="#1a1a2e", fg="#e0e0e0", selectcolor="#0f3460",
                        activebackground="#1a1a2e", activeforeground="#e94560",
                        font=("Segoe UI", 10)).pack(side="left")

        tk.Label(cfg, text=self.t("docs_path_label"), bg="#1a1a2e", fg="#e0e0e0",
                 font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=(10, 0))

        docs_var = tk.StringVar(value=str(self.docs_path))
        tk.Entry(cfg, textvariable=docs_var, bg="#16213e", fg="#e0e0e0",
                 insertbackground="#e0e0e0", font=("Segoe UI", 9), width=48).pack(padx=10, pady=2)

        def browse_docs():
            d = filedialog.askdirectory(title=self.t("browse_docs_title"))
            if d:
                docs_var.set(d)

        tk.Button(cfg, text=self.t("browse"), command=browse_docs,
                  bg="#0f3460", fg="#e0e0e0", font=("Segoe UI", 9)).pack(padx=10, anchor="w")

        tk.Label(cfg, text=self.t("game_path_label"), bg="#1a1a2e", fg="#e0e0e0",
                 font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=(10, 0))

        game_var = tk.StringVar(value=str(self.game_path))
        tk.Entry(cfg, textvariable=game_var, bg="#16213e", fg="#e0e0e0",
                 insertbackground="#e0e0e0", font=("Segoe UI", 9), width=48).pack(padx=10, pady=2)

        def browse_game():
            d = filedialog.askdirectory(title=self.t("browse_game_title"))
            if d:
                game_var.set(d)

        tk.Button(cfg, text=self.t("browse"), command=browse_game,
                  bg="#0f3460", fg="#e0e0e0", font=("Segoe UI", 9)).pack(padx=10, anchor="w")

        def apply_cfg():
            new_lang = lang_var.get()
            self.docs_path = Path(clean_path(docs_var.get()))
            self.game_path = clean_path(game_var.get())
            self.mod_dir = self.docs_path / MOD_DIR_NAME
            self.dlc_path = self.docs_path / JSON_NAME
            self.config["docs_path"] = str(self.docs_path)
            self.config["game_path"] = self.game_path
            self.config["language"] = new_lang
            save_config(self.config)
            self.lang = new_lang
            self._update_ui_texts()
            self._load_mods()
            self._played_loaded = False
            cfg.destroy()
            self.config_window = None

        tk.Button(cfg, text=self.t("apply"), command=apply_cfg,
                  bg="#e94560", fg="#ffffff", font=("Segoe UI", 10, "bold"),
                  padx=15, pady=4).pack(pady=10)

        cfg.protocol("WM_DELETE_WINDOW", lambda: (cfg.destroy(), setattr(self, "config_window", None)))


def main():
    root = tk.Tk()
    root.withdraw()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    app = ModLauncher(root)
    root.deiconify()
    root.mainloop()


if __name__ == "__main__":
    main()
