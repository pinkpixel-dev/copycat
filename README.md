# 📋 Clipboard Helper - Linux Copy-Paste Solution

*Made with ❤️ by Pink Pixel*

## 🚀 Overview

A comprehensive clipboard utility designed to solve copy-paste issues in Linux applications, especially web-based UIs like Warp terminal settings. This tool provides alternative input methods including virtual keyboard typing to bypass paste restrictions.

## ✨ Features

### 🎯 Core Features
- **Virtual Keyboard Typing**: Bypasses paste restrictions by simulating keyboard input
- **Enhanced Clipboard Management**: Read, write, and manipulate clipboard content
- **Multi-Format Support**: Handle text, JSON, URLs, API keys, and more
- **GUI Interface**: Easy-to-use graphical interface with system tray integration

### 🔧 Advanced Features
- **Clipboard History**: Persistent history with search and management
- **Text Templates**: Quick access to frequently used text snippets
- **Smart Data Detection**: Automatically detects and handles different data types
- **Desktop Integration**: System shortcuts and menu entries

## 🛠️ Installation

### Quick Install
```bash
cd clipboard-helper
./install.sh
```

### Manual Dependencies (Ubuntu/Mint)
```bash
sudo apt update
sudo apt install xclip xdotool python3-tk libnotify-bin
```

## 📖 Usage

### Command Line Interface
```bash
# Basic clipboard operations
clipboard-helper --get                    # Get clipboard content
clipboard-helper --set "text"            # Set clipboard content
clipboard-helper --type                   # Type clipboard content (bypasses paste restrictions)
clipboard-helper --type-delayed           # Type after 3-second delay

# Advanced operations
clipboard-helper --history               # Show clipboard history
clipboard-helper --templates             # Show available templates
clipboard-helper --gui                   # Launch GUI interface
```

### GUI Interface
- Launch via desktop shortcut or system menu
- Access via system tray icon
- Use keyboard shortcut: `Ctrl+Alt+V`

### Solving Warp Settings Issue
1. Copy your text/API key/config to clipboard
2. Open Warp settings
3. Focus the input field
4. Use one of these methods:
   - Click the "Type Clipboard" button in GUI
   - Run `clipboard-helper --type-delayed` and quickly switch to Warp
   - Use the keyboard shortcut `Ctrl+Alt+T`

## 🎨 Templates

Create custom templates in `~/.config/clipboard-helper/templates/`:
```bash
# API key template
clipboard-helper --template api-key "sk-your-key-here"

# JSON schema template  
clipboard-helper --template json-schema '{"type": "object", "properties": {...}}'
```

## ⌨️ Keyboard Shortcuts

- `Ctrl+Alt+V`: Open GUI
- `Ctrl+Alt+T`: Type clipboard content
- `Ctrl+Alt+H`: Show clipboard history
- `Ctrl+Shift+V`: Enhanced paste (if supported)

## 📁 File Structure

```
clipboard-helper/
├── bin/                    # Main executables
│   ├── clipboard-helper    # Primary CLI tool
│   └── clipboard-gui       # GUI application
├── lib/                    # Library modules
│   ├── clipboard_core.py   # Core clipboard functions
│   ├── virtual_keyboard.py # Virtual keyboard implementation
│   └── data_handlers.py    # Special data type handling
├── config/                 # Configuration files
│   ├── default.conf        # Default configuration
│   └── templates.json      # Template definitions
├── docs/                   # Documentation
└── templates/              # Template files
```

## 🔧 Configuration

Edit `~/.config/clipboard-helper/config.conf`:
```ini
[general]
typing_delay = 50          # Milliseconds between keystrokes
max_history = 100          # Maximum history entries
auto_detect_types = true   # Enable smart data detection

[gui]
show_tray_icon = true      # Show system tray icon
start_minimized = false    # Start GUI minimized

[shortcuts]
type_clipboard = Ctrl+Alt+T
show_history = Ctrl+Alt+H
open_gui = Ctrl+Alt+V
```

## 🐛 Troubleshooting

### Common Issues

**Paste still not working in Warp?**
- Try the delayed typing option: `clipboard-helper --type-delayed`
- Ensure xdotool is installed: `sudo apt install xdotool`
- Check if the input field is properly focused

**GUI not appearing?**
- Install tkinter: `sudo apt install python3-tk`
- Check desktop environment compatibility

**Keyboard shortcuts not working?**
- Verify xbindkeys is installed: `sudo apt install xbindkeys`
- Check for conflicting shortcuts in system settings

## 🤝 Contributing

Found a bug or want to add a feature? Feel free to:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🏷️ Version

Current Version: 1.0.0
Release Date: September 15, 2025

---

*Dream it, Pixel it* ✨