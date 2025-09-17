# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

CopyCat is a Linux clipboard utility that solves paste restrictions in web-based UIs using virtual keyboard typing. It's designed specifically to bypass copy-paste limitations in applications like Warp terminal settings by simulating keystrokes through xdotool/ydotool.

## Architecture

### Core Components

- **CLI Interface** (`cli.py`): Command-line facade with argparse handling all CLI operations
- **Clipboard Manager** (`clipboard_core.py`): Core clipboard operations using xclip/xsel with fallbacks
- **Virtual Keyboard** (`virtual_keyboard.py`): Typing simulation using xdotool (X11) or ydotool (Wayland)
- **GUI Application** (`gui.py`): Full-featured Tkinter GUI with tabbed interface and theming
- **Template System** (`template_manager.py`): Advanced template management with usage analytics
- **Data Handlers** (`data_handlers.py`): Content analysis and smart data type detection

### Key Design Patterns

- **Fallback Chain**: Multiple methods for clipboard access (xclip → xsel → alternatives)
- **Display Server Detection**: Automatic switching between xdotool (X11) and ydotool (Wayland)
- **Human-like Typing**: Configurable burst patterns and delays to simulate natural typing
- **Secure Content Handling**: Sensitive data detection and masking for history/logs

## Development Commands

### Installation & Setup
```bash
# Interactive setup wizard with multiple package managers
./scripts/setup_copycat.sh

# Manual pip installation
pip install .

# Development installation
pip install -e .

# Using the virtual environment
source .venv/bin/activate
```

### Running the Application
```bash
# CLI interface
copycat --help
copycat --get                    # Get clipboard
copycat --set "text"             # Set clipboard  
copycat --type-delayed           # Type with 3s delay
copycat --gui                    # Launch GUI

# Direct module execution
python -m copycat --status
python -m copycat.gui           # Launch GUI directly
python -m copycat.system_tray   # Launch system tray
```

### Configuration
```bash
# Setup user configuration
copycat --setup

# Configuration files:
# ~/.config/copycat/config.conf       - User settings
# ~/.local/share/copycat/history.json - Clipboard history
# ~/.copycat/templates.json           - Template definitions
```

## Project Structure Insights

### Entry Points (pyproject.toml)
- `copycat` → `copycat.cli:main` (CLI interface)
- `copycat-gui` → `copycat.gui:main` (GUI application) 
- `copycat-tray` → `copycat.system_tray:main` (System tray)

### Resource Management
Resources are packaged using `importlib.resources` for cross-platform compatibility:
- `copycat/resources/default.conf` - Default configuration template
- `copycat/resources/templates.json` - Built-in templates
- `copycat/assets/` - Icons and logos

### Virtual Keyboard Implementation
The virtual keyboard has sophisticated human-like typing patterns:
- Burst typing (3-8 characters at once)
- Variable delays between keystrokes  
- Special character mapping for xdotool
- Automatic method detection (xdotool vs ydotool)

### Template System Architecture
Advanced template management with:
- Placeholder extraction using regex patterns
- Usage analytics and statistics
- Import/export functionality
- Automatic backup creation
- Content-based template suggestions

## System Dependencies

CopyCat requires these Linux system tools:
- `xclip` - Primary clipboard access
- `xdotool` - Virtual typing (X11)
- `ydotool` - Virtual typing (Wayland)
- `notify-send` - Desktop notifications
- `python3-tk` - GUI framework (Tkinter)

Check system status: `copycat --status`

## Configuration System

The configuration uses Python's `configparser` with a hierarchical loading system:
1. Built-in defaults from `resources/default.conf`
2. User overrides from `~/.config/copycat/config.conf`

Key configuration sections:
- `[general]` - Basic behavior settings
- `[gui]` - Interface preferences and theming
- `[typing]` - Virtual keyboard behavior
- `[security]` - Data handling and privacy
- `[shortcuts]` - Global keyboard shortcuts

## GUI Architecture

The GUI uses a sophisticated theming system with:
- Light/dark theme support
- Dynamic color scheme application
- Theme-aware widget registration
- Modern styled buttons with hover effects
- Tabbed interface (Clipboard, History, Templates, Settings)

The GUI maintains references to themable widgets for dynamic updates and uses `after()` for thread-safe UI updates from background operations.

## Primary Use Case

CopyCat was specifically designed to solve paste restrictions in web-based UIs like Warp terminal settings. The typical workflow:

1. Copy API key/configuration
2. Run `copycat --type-delayed` 
3. Switch to target application
4. Focus input field
5. CopyCat types content automatically after 3-second countdown

This bypasses JavaScript paste restrictions by simulating actual keystrokes rather than programmatic clipboard insertion.

## Development Notes

- All file paths use `pathlib.Path` for cross-platform compatibility
- Error handling follows "best effort" pattern with graceful degradation
- Threading used for background operations (typing, clipboard monitoring)
- Security-conscious: sensitive data detection and exclusion from history
- Resource cleanup handled properly for subprocess operations
- Configuration changes require restart for some settings