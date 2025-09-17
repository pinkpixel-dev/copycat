#!/bin/bash

# 🐾 CopyCat Desktop Integration Uninstaller
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

print_banner() {
    echo -e "${RED}"
    echo "  ╔════════════════════════════════════════════════════════╗"
    echo "  ║                                                        ║"
    echo "  ║      🗑️  CopyCat Desktop Integration Removal 🐾        ║"
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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Desktop integration paths
LOCAL_APPLICATIONS_DIR="$HOME/.local/share/applications"
LOCAL_ICONS_DIR="$HOME/.local/share/icons/hicolor"
AUTOSTART_DIR="$HOME/.config/autostart"

# Remove desktop files
remove_desktop_files() {
    print_step "Removing desktop entry files..."
    
    local removed=false
    
    if [[ -f "$LOCAL_APPLICATIONS_DIR/copycat.desktop" ]]; then
        rm -f "$LOCAL_APPLICATIONS_DIR/copycat.desktop"
        print_success "Removed CopyCat GUI desktop entry"
        removed=true
    fi
    
    if [[ -f "$LOCAL_APPLICATIONS_DIR/copycat-tray.desktop" ]]; then
        rm -f "$LOCAL_APPLICATIONS_DIR/copycat-tray.desktop"
        print_success "Removed CopyCat Tray desktop entry"
        removed=true
    fi
    
    if ! $removed; then
        print_info "No desktop entries found to remove"
    fi
}

# Remove icons
remove_icons() {
    print_step "Removing CopyCat icons..."
    
    local removed=false
    local icon_dirs=("48x48" "64x64" "128x128" "256x256" "scalable")
    
    for size in "${icon_dirs[@]}"; do
        local icon_path="$LOCAL_ICONS_DIR/$size/apps/copycat.png"
        if [[ -f "$icon_path" ]]; then
            rm -f "$icon_path"
            removed=true
        fi
    done
    
    if $removed; then
        print_success "Removed CopyCat icons"
    else
        print_info "No icons found to remove"
    fi
}

# Remove autostart entries
remove_autostart() {
    print_step "Removing autostart entries..."
    
    local removed=false
    
    if [[ -f "$AUTOSTART_DIR/copycat-tray.desktop" ]]; then
        rm -f "$AUTOSTART_DIR/copycat-tray.desktop"
        print_success "Removed autostart entry"
        removed=true
    fi
    
    if ! $removed; then
        print_info "No autostart entries found"
    fi
}

# Remove desktop shortcuts
remove_desktop_shortcuts() {
    print_step "Removing desktop shortcuts..."
    
    local removed=false
    
    if [[ -f "$HOME/Desktop/copycat.desktop" ]]; then
        rm -f "$HOME/Desktop/copycat.desktop"
        print_success "Removed desktop shortcut"
        removed=true
    fi
    
    if ! $removed; then
        print_info "No desktop shortcuts found"
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

# Show completion message
show_completion() {
    echo
    echo -e "${GREEN}"
    echo "  ╔═══════════════════════════════════════════════════════════╗"
    echo "  ║                                                           ║"
    echo "  ║          🗑️  Desktop Integration Removed! 🐾              ║"
    echo "  ║                                                           ║"
    echo "  ╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
    echo -e "${CYAN}📱 CopyCat desktop integration has been removed.${NC}"
    echo
    echo -e "${WHITE}Note:${NC}"
    echo -e "  • CopyCat commands are still available in terminal"
    echo -e "  • To fully remove CopyCat: ${CYAN}pip uninstall copycat-clipboard${NC}"
    echo
    echo -e "${PURPLE}Made with ❤️ by Pink Pixel - Dream it, Pixel it ✨${NC}"
}

# Main execution
main() {
    print_banner
    
    print_info "Removing CopyCat desktop integration..."
    echo
    
    remove_desktop_files
    remove_icons
    remove_autostart
    remove_desktop_shortcuts
    update_desktop_database
    
    show_completion
}

# Run main function
main "$@"