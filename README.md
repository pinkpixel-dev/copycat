# 🐾 CopyCat – Linux Copy-Paste Superpower

<p align="center">
  <img src="copycat/assets/logo.png" alt="CopyCat logo" width="350" />
</p>

*Crafted with ❤️ by Pink Pixel*

## 🚀 What Is CopyCat?

CopyCat is your all-in-one clipboard utility for Linux. It crushes copy-paste headaches in stubborn apps and web UIs. With built-in virtual typing, advanced clipboard tricks, and a clean GUI, CopyCat makes paste restrictions a thing of the past.

## ✨ Features

### 🎯 Core Tools

* **Virtual Keyboard Typing** – Simulate real keystrokes to bypass paste blocks
* **Clipboard Control** – Read, write, and manipulate clipboard content
* **Multi-Format Ready** – Handle text, JSON, URLs, API keys, and more
* **GUI & Tray App** – Simple interface with system tray access

### 🔧 Power Features

* **Clipboard History** – Persistent storage with search & management
* **Text Templates** – Reusable snippets at your fingertips
* **Smart Detection** – Auto-detect and adapt to different data types
* **Desktop Integration** – Global shortcuts and menu entries

## 🛠️ Installation

### Quick Install

```bash
git clone https://github.com/<your-org>/copycat.git
cd copycat
pip install .
```

### Guided Setup

Prefer interactive? Run:

```bash
./scripts/setup_copycat.sh
```

Choose `pip`, `uv`, or `conda`—the script builds a virtual environment, installs dependencies, and registers CopyCat.

### Manual Dependencies (Ubuntu/Mint)

```bash
sudo apt update
sudo apt install xclip xdotool python3-tk libnotify-bin
```

## 📖 Usage

### CLI Basics

```bash
# Core
copycat --get              # Show clipboard
copycat --set "text"       # Set clipboard
copycat --type             # Type clipboard (bypasses restrictions)
copycat --type-delayed     # Type after 3s delay

# Advanced
copycat --history          # Clipboard history
copycat --templates        # Templates list
copycat --gui              # Launch GUI
```

### GUI

* Start from desktop menu, tray icon, or `Ctrl+Alt+V`
* Access history, templates, and one-click “Type Clipboard”

### Usage

1. Copy text, API key, or config
2. Focus input field
3. Use one of these:

   * GUI: click **Type Clipboard**
   * CLI: `copycat --type-delayed` then switch to the designated paste location
   * Shortcut: `Ctrl+Alt+T`

## 🎨 Templates

Custom templates live in `~/.config/copycat/templates/`:

```bash
# API key
copycat --template api-key "sk-your-key-here"

# JSON schema
copycat --template json-schema '{"type": "object", "properties": {...}}'
```

## ⌨️ Keyboard Shortcuts

* `Ctrl+Alt+V` → Open GUI
* `Ctrl+Alt+T` → Type clipboard
* `Ctrl+Alt+H` → Show history
* `Ctrl+Shift+V` → Enhanced paste (when supported)

## 🔧 Config

Edit `~/.config/copycat/config.conf`:

```ini
[general]
typing_delay = 50
max_history = 100
auto_detect_types = true

[gui]
show_tray_icon = true
start_minimized = false

[shortcuts]
type_clipboard = Ctrl+Alt+T
show_history = Ctrl+Alt+H
open_gui = Ctrl+Alt+V
```

## 🐛 Troubleshooting

**Paste still blocked?**

* Try `copycat --type-delayed`
* Confirm `xdotool` is installed
* Ensure input field focus

**GUI not showing?**

* Install `tkinter`: `sudo apt install python3-tk`
* Check desktop environment

**Shortcuts failing?**

* Install `xbindkeys`: `sudo apt install xbindkeys`
* Check system shortcut conflicts

## 🤝 Contributing

Want to help?

1. Fork the repo
2. Create a branch
3. Submit a PR

## 📄 License

Apache 2.0 – see [LICENSE](LICENSE).

## 🏷️ Version

**1.0.0 – Released September 17, 2025**

---

*Made with 🩷 by Pink Pixel*

---
