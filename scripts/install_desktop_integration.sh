#!/bin/bash

# 🐾 CopyCat Desktop Integration Installer
# Made with ❤️ by Pink Pixel - Dream it, Pixel it ✨

set -euo pipefail

# Colors for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Banner
print_banner() {
    echo -e "${PURPLE}"
    echo "  ╔════════════════════════════════════════════════════════╗"
    echo "  ║                                                        ║"
    echo "  ║        🐾 CopyCat Desktop Integration Setup 🎯         ║"
    echo "  ║                                                        ║"
    echo "  ║            Made with ❤️ by Pink Pixel                   ║"
    echo "  ║               Dream it, Pixel it ✨                    ║"
    echo "  ║                                                        ║"
    echo "  ╚════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
}

print_step() {
    echo -e "${CYAN}➤${NC} ${WHITE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Desktop integration paths
DESKTOP_FILES_DIR="$PROJECT_DIR/desktop"
LOCAL_APPLICATIONS_DIR="$HOME/.local/share/applications"
LOCAL_ICONS_DIR="$HOME/.local/share/icons/hicolor"
SYSTEM_APPLICATIONS_DIR="/usr/share/applications"
SYSTEM_ICONS_DIR="/usr/share/icons/hicolor"

# Create local directories if they don't exist
create_directories() {
    print_step "Creating necessary directories..."
    
    mkdir -p "$LOCAL_APPLICATIONS_DIR"
    mkdir -p "$LOCAL_ICONS_DIR/48x48/apps"
    mkdir -p "$LOCAL_ICONS_DIR/64x64/apps"
    mkdir -p "$LOCAL_ICONS_DIR/128x128/apps"
    mkdir -p "$LOCAL_ICONS_DIR/256x256/apps"
    mkdir -p "$LOCAL_ICONS_DIR/scalable/apps"
    
    print_success "Directories created"
}

# Copy icon files
install_icons() {
    print_step "Installing CopyCat icons..."
    
    # Use the existing icon from the package
    local icon_source="$PROJECT_DIR/copycat/assets/icon.png"
    
    if [[ -f "$icon_source" ]]; then
        # Install icon at multiple sizes
        cp "$icon_source" "$LOCAL_ICONS_DIR/48x48/apps/copycat.png"
        cp "$icon_source" "$LOCAL_ICONS_DIR/64x64/apps/copycat.png"
        cp "$icon_source" "$LOCAL_ICONS_DIR/128x128/apps/copycat.png"
        cp "$icon_source" "$LOCAL_ICONS_DIR/256x256/apps/copycat.png"
        
        print_success "Icons installed to $LOCAL_ICONS_DIR"
    else
        print_warning "Icon file not found at $icon_source"
        print_info "Creating placeholder icon..."
        
        # Create a simple placeholder if imagemagick is available
        if command -v convert >/dev/null 2>&1; then
            convert -size 64x64 xc:blue -font Arial -pointsize 20 -fill white -gravity center \
                    -annotate +0+0 "CC" "$LOCAL_ICONS_DIR/64x64/apps/copycat.png"
            print_success "Placeholder icon created"
        else
            print_warning "ImageMagick not found, skipping icon creation"
        fi
    fi
}

# Install desktop files
install_desktop_files() {
    print_step "Installing desktop entry files..."
    
    if [[ -f "$DESKTOP_FILES_DIR/copycat.desktop" ]]; then
        cp "$DESKTOP_FILES_DIR/copycat.desktop" "$LOCAL_APPLICATIONS_DIR/"
        chmod +x "$LOCAL_APPLICATIONS_DIR/copycat.desktop"
        print_success "CopyCat GUI desktop entry installed"
    else
        print_error "Desktop file not found: $DESKTOP_FILES_DIR/copycat.desktop"
    fi
    
    if [[ -f "$DESKTOP_FILES_DIR/copycat-tray.desktop" ]]; then
        cp "$DESKTOP_FILES_DIR/copycat-tray.desktop" "$LOCAL_APPLICATIONS_DIR/"
        chmod +x "$LOCAL_APPLICATIONS_DIR/copycat-tray.desktop"
        print_success "CopyCat Tray desktop entry installed"
    else
        print_error "Desktop file not found: $DESKTOP_FILES_DIR/copycat-tray.desktop"
    fi
}

# Update desktop database
update_desktop_database() {
    print_step "Updating desktop database..."
    
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "$LOCAL_APPLICATIONS_DIR" 2>/dev/null || true
        print_success "Desktop database updated"
    else
        print_warning "update-desktop-database not found, skipping"
    fi
    
    # Update icon cache
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -t "$LOCAL_ICONS_DIR" 2>/dev/null || true
        print_success "Icon cache updated"
    else
        print_warning "gtk-update-icon-cache not found, skipping"
    fi
}

# Install autostart entry
install_autostart() {
    local autostart_dir="$HOME/.config/autostart"
    
    print_step "Setting up autostart (optional)..."
    
    read -p "Do you want CopyCat to start with your desktop? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p "$autostart_dir"
        cp "$DESKTOP_FILES_DIR/copycat-tray.desktop" "$autostart_dir/"
        print_success "Autostart enabled - CopyCat will start with your desktop"
    else
        print_info "Autostart skipped"
    fi
}

# Create desktop shortcuts
create_desktop_shortcuts() {
    print_step "Creating desktop shortcuts (optional)..."
    
    read -p "Do you want shortcuts on your desktop? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "$DESKTOP_FILES_DIR/copycat.desktop" "$HOME/Desktop/" 2>/dev/null || {
            print_warning "Could not copy to Desktop (directory may not exist)"
        }
        
        if [[ -f "$HOME/Desktop/copycat.desktop" ]]; then
            chmod +x "$HOME/Desktop/copycat.desktop"
            print_success "Desktop shortcut created"
        fi
    else
        print_info "Desktop shortcuts skipped"
    fi
}

# Create keyboard shortcuts setup
setup_keyboard_shortcuts() {
    print_step "Setting up global keyboard shortcuts..."
    
    cat << EOF

${YELLOW}⌨️  Keyboard Shortcuts Setup${NC}

To set up global keyboard shortcuts, you'll need to configure them manually
in your desktop environment:

${CYAN}Recommended shortcuts:${NC}
  Ctrl+Alt+V    → Open CopyCat GUI     → Command: copycat-gui
  Ctrl+Alt+T    → Type clipboard       → Command: copycat --type-delayed
  Ctrl+Alt+H    → Show history         → Command: copycat --history

${CYAN}Setup instructions by desktop environment:${NC}

${WHITE}GNOME/Ubuntu:${NC}
  1. Open Settings → Keyboard Shortcuts
  2. Add custom shortcuts with the commands above

${WHITE}KDE/Plasma:${NC}
  1. System Settings → Shortcuts → Custom Shortcuts
  2. Add new shortcuts with the commands above

${WHITE}XFCE:${NC}
  1. Settings → Keyboard → Application Shortcuts
  2. Add shortcuts with the commands above

${WHITE}Cinnamon:${NC}
  1. Settings → Keyboard → Custom Shortcuts
  2. Add shortcuts with the commands above

EOF

    read -p "Press Enter to continue..." -r
}

# Verify installation
verify_installation() {
    print_step "Verifying installation..."
    
    local success=true
    
    # Check if commands are available
    if command -v copycat >/dev/null 2>&1; then
        print_success "copycat command available"
    else
        print_error "copycat command not found"
        success=false
    fi
    
    if command -v copycat-gui >/dev/null 2>&1; then
        print_success "copycat-gui command available"
    else
        print_error "copycat-gui command not found"
        success=false
    fi
    
    if command -v copycat-tray >/dev/null 2>&1; then
        print_success "copycat-tray command available"
    else
        print_error "copycat-tray command not found"
        success=false
    fi
    
    # Check desktop files
    if [[ -f "$LOCAL_APPLICATIONS_DIR/copycat.desktop" ]]; then
        print_success "GUI desktop entry installed"
    else
        print_error "GUI desktop entry missing"
        success=false
    fi
    
    if [[ -f "$LOCAL_APPLICATIONS_DIR/copycat-tray.desktop" ]]; then
        print_success "Tray desktop entry installed"
    else
        print_error "Tray desktop entry missing"
        success=false
    fi
    
    if $success; then
        print_success "Installation verification passed!"
    else
        print_error "Some components are missing"
        return 1
    fi
}

# Show completion message
show_completion() {
    echo
    echo -e "${GREEN}"
    echo "  ╔═══════════════════════════════════════════════════════════╗"
    echo "  ║                                                           ║"
    echo "  ║            🎉 Desktop Integration Complete! 🎯             ║"
    echo "  ║                                                           ║"
    echo "  ╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
    echo -e "${CYAN}📱 CopyCat is now available in your applications menu!${NC}"
    echo
    echo -e "${WHITE}Next steps:${NC}"
    echo -e "  • Look for ${CYAN}CopyCat${NC} in your applications menu"
    echo -e "  • Right-click taskbar to ${CYAN}pin to taskbar${NC} (varies by DE)"
    echo -e "  • Set up ${CYAN}keyboard shortcuts${NC} as shown above"
    echo -e "  • Try: ${CYAN}copycat --gui${NC} or just ${CYAN}copycat-gui${NC}"
    echo
    echo -e "${PURPLE}Made with ❤️ by Pink Pixel - Dream it, Pixel it ✨${NC}"
}

# Main execution
main() {
    print_banner
    
    # Check if CopyCat is installed
    if ! command -v copycat >/dev/null 2>&1; then
        print_error "CopyCat is not installed or not in PATH"
        print_info "Please install CopyCat first:"
        print_info "  pip install copycat-clipboard"
        exit 1
    fi
    
    # Check if desktop files exist
    if [[ ! -d "$DESKTOP_FILES_DIR" ]]; then
        print_error "Desktop files directory not found: $DESKTOP_FILES_DIR"
        exit 1
    fi
    
    print_info "Installing desktop integration for CopyCat..."
    echo
    
    create_directories
    install_icons
    install_desktop_files
    update_desktop_database
    install_autostart
    create_desktop_shortcuts
    setup_keyboard_shortcuts
    
    echo
    verify_installation
    
    show_completion
}

# Error handling
trap 'print_error "Installation failed at line $LINENO"' ERR

# Run main function
main "$@"