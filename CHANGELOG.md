# 🐾 Changelog

All notable changes to the CopyCat project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planning
- Future enhancements based on user feedback
- Additional template categories
- Performance optimizations

## [1.0.1] - 2025-09-17 🎉 **PUBLISHED TO PyPI**

### 🚀 Major Milestone
- **Successfully published to PyPI** as `copycat-linux`
- Package now available worldwide via `pip install copycat-linux`
- All entry points working: `copycat`, `copycat-gui`, `copycat-tray`

### 🎨 GUI Improvements
- **Fixed emoji compatibility issues** - Removed paw emojis (🐾) causing display problems
- **Improved text layout** - Fixed tagline wrapping and overflow in GUI header
- **Enhanced font compatibility** - Added fallback fonts (Arial/Courier) for systems without Segoe UI/Consolas
- **Better cross-platform support** - Keyboard emoji (🎹) replaced with universal symbol (⌨)
- **Optimized subtitle display** - Multi-line layout prevents text cutoff

### 📦 Package Management
- **Package name changed** from `copycat-clipboard` to `copycat-linux` (original name was taken)
- **Test PyPI validation** - Thoroughly tested installation and functionality
- **Authentication resolved** - Fixed PyPI upload credentials and permissions
- **Quality assurance** - All twine checks passed, proper metadata included

### 🔧 Technical Improvements
- **Font rendering** - Improved cross-distribution compatibility
- **Window sizing** - Better handling of GUI layout on different screen configurations
- **Resource packaging** - All assets properly included in distribution
- **Entry point validation** - Confirmed all CLI/GUI commands work from PyPI installation

## [1.0.0] - 2025-09-15

### Added
- Initial project structure created
- Comprehensive README with feature overview and usage instructions  
- Apache 2.0 license for open source distribution
- Default configuration file with all available settings
- Template system with pre-built templates for:
  - API keys with secure handling
  - JSON schema generation
  - MCP server configuration
  - Email signatures
  - SQL queries
  - HTTP curl requests
- Project directories organized for:
  - `/bin` - Main executables
  - `/copycat` - Python package modules
  - `/config` - Configuration files and templates
  - `/docs` - Documentation
  - `/templates` - User template files

### Features Planned
- Virtual keyboard typing to bypass paste restrictions in web-based UIs
- Enhanced clipboard management with history
- GUI interface with system tray integration
- Smart data type detection and handling
- Desktop integration with keyboard shortcuts
- Secure template system for sensitive data
- Cross-application compatibility focus

### Target Use Cases
- Solving Warp terminal settings paste issues
- Managing API keys and configuration strings
- Quick access to frequently used text snippets
- Professional email signatures and templates
- Development workflow automation

---

*Made with ❤️ by Pink Pixel* ✨
