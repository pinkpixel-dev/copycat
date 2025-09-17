# 🐾 CopyCat - Project Overview

**Version:** 1.0.1  
**Release Date:** September 17, 2025  
**PyPI Publication:** September 17, 2025 🎉  
**Author:** Pink Pixel  
**License:** Apache 2.0  
**Platform:** Linux  
**Installation:** `pip install copycat-linux`

*Made with ❤️ by Pink Pixel - Dream it, Pixel it ✨*

---

## 🎯 Project Purpose

CopyCat is a sophisticated Linux clipboard utility specifically designed to solve paste restrictions in web-based UIs by simulating human-like keystrokes through virtual typing. The primary use case is bypassing JavaScript paste restrictions in applications like Warp terminal settings, where traditional clipboard paste operations are blocked.

### Core Problem Solved
- **Issue:** Many web-based UIs and applications (especially Warp terminal settings) block programmatic clipboard paste operations
- **Solution:** CopyCat bypasses these restrictions by simulating actual human keystrokes using xdotool/ydotool
- **Workflow:** Copy → Run `copycat --type-delayed` → Switch to target app → Focus input field → Automatic typing after countdown

---

## 🏗️ Architecture & Core Components

### **Entry Points (pyproject.toml)**
- `copycat` → `copycat.cli:main` (Command-line interface)
- `copycat-gui` → `copycat.gui:main` (GUI application)
- `copycat-tray` → `copycat.system_tray:main` (System tray integration)

### **Core Modules**

#### 1. **CLI Interface** (`cli.py`)
- **Purpose:** Command-line facade with argparse handling all CLI operations
- **Features:** Banner display, configuration management, all core operations accessible via CLI
- **Key Operations:** Get/set clipboard, virtual typing, history management, template access

#### 2. **Clipboard Manager** (`clipboard_core.py`)
- **Purpose:** Core clipboard operations with robust fallback mechanisms
- **Methods:** 
  - Primary: `xclip` with clipboard and primary selections
  - Fallbacks: `xsel`, `pbpaste`/`pbcopy` (macOS compatibility)
- **Features:** History tracking, sensitive data detection, content analysis

#### 3. **Virtual Keyboard** (`virtual_keyboard.py`)
- **Purpose:** Virtual typing simulation to bypass paste restrictions
- **Methods:**
  - X11: `xdotool` (primary method)
  - Wayland: `ydotool` (automatic fallback)
- **Features:** Human-like typing patterns, burst typing, variable delays, special character handling

#### 4. **GUI Application** (`gui.py`)
- **Purpose:** Full-featured Tkinter GUI with modern theming
- **Architecture:** Tabbed interface (Clipboard, History, Templates, Settings)
- **Features:** Light/dark themes, modern styled buttons with hover effects, theme-aware widgets

#### 5. **Template System** (`template_manager.py`)
- **Purpose:** Advanced template management with analytics
- **Features:**
  - Placeholder extraction using regex patterns
  - Usage analytics and statistics
  - Import/export functionality
  - Automatic backup creation
  - Content-based template suggestions

#### 6. **Data Handlers** (`data_handlers.py`)
- **Purpose:** Content analysis and smart data type detection
- **Capabilities:** Detects API keys, JSON, XML, URLs, emails, phone numbers, code patterns, credit cards, IP addresses
- **Security:** Automatic sensitive data identification and masking

### **Design Patterns**

1. **Fallback Chain Pattern**
   - Multiple methods for clipboard access: xclip → xsel → platform alternatives
   - Graceful degradation when primary tools unavailable

2. **Display Server Detection**
   - Automatic detection of X11 vs Wayland environment
   - Dynamic method selection (xdotool vs ydotool)

3. **Human-like Typing Simulation**
   - Configurable burst patterns (3-8 characters per burst)
   - Variable delays between keystrokes (50-300ms)
   - Punctuation pause simulation for realism

4. **Secure Content Handling**
   - Sensitive data pattern recognition
   - Automatic exclusion from history logs
   - Content masking for display purposes

---

## ✨ Key Features & Capabilities

### **Core Features**
- **Virtual Keyboard Typing:** Bypass paste restrictions using keystroke simulation
- **Clipboard Control:** Complete read/write/clear operations with fallback methods
- **Multi-Format Support:** Intelligent handling of text, JSON, URLs, API keys, code
- **Cross-Interface Access:** CLI, GUI, and system tray interfaces

### **Advanced Features**
- **Clipboard History:** Persistent storage up to 100 entries with search functionality
- **Template System:** Reusable snippets with placeholder support and usage analytics  
- **Smart Content Detection:** Automatic data type recognition with confidence scoring
- **Security-First Design:** Sensitive data detection and exclusion from history
- **Desktop Integration:** Global keyboard shortcuts and system tray access
- **Theming Support:** Modern light/dark theme system in GUI

### **Human-like Typing Simulation**
- **Burst Patterns:** 3-8 characters typed in natural bursts
- **Variable Delays:** 100-300ms pauses between bursts
- **Punctuation Awareness:** Extra pauses after punctuation marks
- **Special Characters:** Complete mapping for xdotool special key handling

---

## 🔧 Technical Dependencies

### **System Dependencies**
```bash
# Core clipboard access
xclip                 # Primary clipboard interface
xsel                  # Fallback clipboard method

# Virtual keyboard
xdotool              # X11 virtual typing
ydotool              # Wayland virtual typing

# Desktop integration  
notify-send          # Desktop notifications
python3-tk           # GUI framework (Tkinter)
```

### **Python Requirements**
- **Python:** >=3.9
- **Core Libraries:** Built-in Python modules only (no external PyPI dependencies)
- **Optional:** `pystray>=0.19.5` (for enhanced system tray features)

---

## ⚙️ Configuration System

### **Hierarchical Loading**
1. **Built-in Defaults:** `copycat/resources/default.conf`
2. **User Overrides:** `~/.config/copycat/config.conf`

### **Configuration Sections**
```ini
[general]
typing_delay = 50
max_history = 100
auto_detect_types = true

[gui]
show_tray_icon = true
start_minimized = false
theme = light

[typing]
initial_delay = 3.0
human_like = true
burst_length_min = 3
burst_length_max = 8

[security]
exclude_sensitive = true
mask_sensitive_in_logs = true

[shortcuts]
type_clipboard = Ctrl+Alt+T
show_history = Ctrl+Alt+H
open_gui = Ctrl+Alt+V
```

### **Data Storage Locations**
- **Configuration:** `~/.config/copycat/config.conf`
- **Clipboard History:** `~/.local/share/copycat/history.json`
- **Templates:** `~/.copycat/templates.json`
- **Template Backups:** `~/.copycat/template_backups/`

---

## 🛠️ Development Workflow

### **Installation Methods**

#### **PyPI Installation (Recommended) 🎉**
```bash
# One-command installation from PyPI
pip install copycat-linux
```

#### **Development Installation**
```bash
# Clone repository for development
git clone https://github.com/pinkpixel-dev/copycat.git
cd copycat
pip install -e .     # Editable installation
```

#### **Guided Setup (Alternative)**
```bash
# Interactive setup with virtual environment
./scripts/setup_copycat.sh
```

### **Development Commands**
```bash
# Launch interfaces
copycat --help                   # CLI help
copycat-gui                     # GUI interface
copycat-tray                    # System tray

# Development testing
copycat --status                # System dependency check
copycat --setup                 # Create user configuration
python -m copycat.gui          # Direct module execution
```

### **Resource Management**
- **Assets:** `copycat/assets/` (icon.png, logo.png)
- **Resources:** `copycat/resources/` (default.conf, templates.json)
- **Package Data:** Included via `pyproject.toml` configuration
- **Cross-platform:** Uses `importlib.resources` for reliable resource access

---

## 📋 Usage Examples

### **CLI Operations**
```bash
# Basic clipboard operations
copycat --get                    # Display current clipboard
copycat --set "Hello World"      # Set clipboard content
copycat --clear                  # Clear clipboard

# Virtual typing (main feature)
copycat --type                   # Type immediately
copycat --type-delayed           # Type after 3-second delay

# Advanced features
copycat --history                # Show clipboard history
copycat --templates              # List available templates
copycat --gui                    # Launch GUI interface
```

### **Typical Warp Settings Workflow**
1. Copy your API key or configuration string
2. Run `copycat --type-delayed` 
3. Quickly switch to Warp settings page
4. Focus the input field where you want to paste
5. Watch CopyCat automatically type the content after the countdown

---

## 🔒 Security Features

### **Sensitive Data Detection**
- **API Key Patterns:** OpenAI, Anthropic, GitHub, Google, AWS, Stripe, Slack, Discord, JWT
- **Generic Detection:** Long alphanumeric strings (>20 chars)
- **Auto-Exclusion:** Sensitive content never stored in history
- **Content Masking:** Safe display with partial masking (`sk-****...****`)

### **Data Type Recognition**
- **JSON:** Validation and structure analysis
- **URLs:** HTTP/HTTPS/FTP/SSH protocol detection
- **Emails:** RFC-compliant email pattern matching
- **Phone Numbers:** US and international format support
- **Code:** Multi-language detection (Python, JavaScript, SQL, HTML, CSS, etc.)
- **Hashes:** MD5, SHA patterns
- **Coordinates:** Geographic coordinate detection

---

## 📈 Current Status (v1.0.1) 🎉

### **🚀 MAJOR MILESTONE: PyPI Publication**
✅ **Published to PyPI** as `copycat-linux`  
✅ **Worldwide availability** via `pip install copycat-linux`  
✅ **All entry points working** from PyPI installation  
✅ **GUI improvements** - Fixed emoji compatibility and font rendering  
✅ **Enhanced cross-platform support** - Better Linux distribution compatibility  

### **Completed Features**
✅ Core clipboard operations with fallback methods  
✅ Virtual keyboard typing with human-like simulation  
✅ GUI application with modern theming  
✅ CLI interface with comprehensive operations  
✅ System tray integration  
✅ Clipboard history with persistent storage  
✅ Template system with placeholders and analytics  
✅ Smart content detection and data type recognition  
✅ Security features for sensitive data handling  
✅ Cross-platform compatibility (X11/Wayland)  
✅ Desktop integration with keyboard shortcuts

### **Documentation Status**
✅ README.md - Comprehensive user guide  
✅ CHANGELOG.md - Version history and release notes  
✅ LICENSE - Apache 2.0 license  
✅ WARP.md - Development guidance and architecture details  
✅ OVERVIEW.md - This architectural overview  

---

## 🚀 Future Roadmap

Based on CHANGELOG.md planning notes:

### **Potential Enhancements**
- **Enhanced GUI Features:** More advanced clipboard management UI
- **Plugin System:** Extensible architecture for custom data handlers
- **Cloud Integration:** Optional cloud sync for templates and history
- **Advanced Automation:** Macro recording and playback
- **Multi-language Support:** Internationalization for GUI
- **Performance Optimizations:** Faster clipboard operations and typing simulation
- **Enhanced Security:** Encryption for sensitive data storage
- **Cross-desktop Integration:** Better desktop environment integration

### **Platform Expansion**
- **Windows Support:** Potential Windows clipboard and typing support
- **macOS Integration:** Enhanced macOS compatibility
- **Container Support:** Docker/Flatpak packaging options

---

## 🤝 Development Notes

### **Code Quality**
- **Type Hints:** Python 3.9+ type annotations throughout
- **Error Handling:** Graceful degradation with "best effort" pattern  
- **Resource Management:** Proper cleanup for subprocess operations
- **Threading:** Background operations for typing and monitoring
- **Path Handling:** `pathlib.Path` for cross-platform compatibility

### **Testing & Validation**
- **System Check:** `copycat --status` validates all dependencies
- **Dependency Detection:** Runtime availability checking
- **Fallback Testing:** Multiple method validation
- **Configuration Testing:** Setup and validation workflows

---

## 📞 Support & Contributing

### **Getting Help**
- **System Status:** Run `copycat --status` to check dependencies
- **Configuration:** Use `copycat --setup` to initialize user config
- **Debugging:** Check logs and test with `--type-delayed` for troubleshooting

### **Contributing**
- **Bug Reports:** Submit issues with system information and steps to reproduce
- **Feature Requests:** Describe use cases and expected behavior
- **Pull Requests:** Follow existing code patterns and include tests
- **Documentation:** Help improve user guides and technical documentation

---

*This overview was updated on September 17, 2025, documenting CopyCat v1.0.1 - now available on PyPI! 🎉*
