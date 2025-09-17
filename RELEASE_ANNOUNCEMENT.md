# 🎉 CopyCat v1.0.1 - Now Available on PyPI!

**September 17, 2025**

**CopyCat** is now officially published on PyPI 🚀

## 🌟 What is CopyCat?

CopyCat is an advanced Linux clipboard utility that solves paste restrictions in web-based UIs by simulating human-like keystrokes. Perfect for bypassing JavaScript paste restrictions in applications like Warp terminal settings, where traditional clipboard operations are blocked.

## 📦 Easy Installation

Getting started is now easier than ever:

```bash
pip install copycat-linux
```

All commands (`copycat`, `copycat-gui`, `copycat-tray`) are now available system-wide.

## ✨ What's New in v1.0.1

### 🎨 GUI Improvements

### 📦 Package Management
- **Published to PyPI** as `copycat-linux`
- **Worldwide availability** - Anyone can now install with `pip install copycat-linux`
- **Quality assurance** - All twine checks passed, proper metadata included
- **Authentication resolved** - Fixed PyPI upload credentials and permissions

### 🔧 Technical Improvements
- **Enhanced cross-platform support** - Better compatibility across Linux distributions
- **Resource packaging** - All assets properly included in distribution
- **Entry point validation** - Confirmed all CLI/GUI commands work from PyPI installation

## 🚀 Key Features

- **Virtual Keyboard Typing** - Bypass paste restrictions using keystroke simulation
- **Advanced Clipboard Management** - History tracking, templates, smart detection
- **Modern GUI** - Light/dark theme support with intuitive interface
- **CLI Power Tools** - Complete command-line interface for all operations
- **System Integration** - Tray icon, keyboard shortcuts, desktop integration
- **Security-First** - Automatic sensitive data detection and exclusion from history

## 🎯 Perfect For

- **Warp Terminal Users** - Solve paste restrictions in settings and configuration
- **Web Developers** - Bypass JavaScript paste restrictions in web UIs
- **System Administrators** - Manage API keys, configurations, and sensitive data
- **Power Users** - Advanced clipboard operations and automation

## 🛠️ Quick Start

### Installation
```bash
# Install from PyPI (recommended)
pip install copycat-linux

# Install system dependencies (Ubuntu/Mint)
sudo apt update
sudo apt install xclip xdotool python3-tk libnotify-bin
```

### Basic Usage
```bash
# Copy something, then:
copycat --type-delayed    # Type after 3-second delay
copycat --gui            # Launch GUI interface
copycat --history        # View clipboard history
```

### Typical Workflow
1. Copy your API key or configuration
2. Run `copycat --type-delayed`
3. Switch to target application (e.g., Warp settings)
4. Focus input field
5. Watch CopyCat automatically type after countdown

## 📊 Package Details

- **Package Name**: `copycat-linux`
- **Version**: 1.0.1
- **Size**: ~1.3MB (includes GUI assets)
- **Python Support**: 3.8+
- **License**: Apache 2.0
- **Platform**: Linux (X11/Wayland)
- **PyPI URL**: https://pypi.org/project/copycat-linux/

## 🌍 Links

- **PyPI Package**: https://pypi.org/project/copycat-linux/
- **GitHub Repository**: https://github.com/pinkpixel-dev/copycat
- **Documentation**: See README.md in repository
- **Support**: admin@pinkpixel.dev

---

**Made with ❤️ by Pink Pixel** ✨  
*Dream it, Pixel it*

*CopyCat v1.0.1 - Solving copy-paste problems one keystroke at a time! 🐾*