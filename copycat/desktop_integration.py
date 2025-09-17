"""Desktop integration installer for CopyCat."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from importlib import resources
from pathlib import Path
from typing import Optional


class DesktopIntegrator:
    """Handle desktop integration for CopyCat."""
    
    def __init__(self) -> None:
        self.home = Path.home()
        self.local_apps_dir = self.home / ".local/share/applications"
        self.local_icons_dir = self.home / ".local/share/icons/hicolor"
        self.autostart_dir = self.home / ".config/autostart"
        self.desktop_dir = self.home / "Desktop"
        
    def install(self, autostart: bool = False, desktop_shortcut: bool = False) -> bool:
        """Install desktop integration files."""
        try:
            print("🐾 Installing CopyCat desktop integration...")
            
            # Create directories
            self._create_directories()
            
            # Install icons
            self._install_icons()
            
            # Install desktop files
            self._install_desktop_files()
            
            # Optional installations
            if autostart:
                self._install_autostart()
                
            if desktop_shortcut:
                self._install_desktop_shortcut()
            
            # Update desktop database
            self._update_desktop_database()
            
            print("✅ Desktop integration installed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to install desktop integration: {e}")
            return False
    
    def uninstall(self) -> bool:
        """Remove desktop integration files."""
        try:
            print("🗑️ Removing CopyCat desktop integration...")
            
            # Remove desktop files
            (self.local_apps_dir / "copycat.desktop").unlink(missing_ok=True)
            (self.local_apps_dir / "copycat-tray.desktop").unlink(missing_ok=True)
            
            # Remove icons
            for size in ["48x48", "64x64", "128x128", "256x256"]:
                icon_path = self.local_icons_dir / size / "apps" / "copycat.png"
                icon_path.unlink(missing_ok=True)
            
            # Remove autostart
            (self.autostart_dir / "copycat-tray.desktop").unlink(missing_ok=True)
            
            # Remove desktop shortcut
            (self.desktop_dir / "copycat.desktop").unlink(missing_ok=True)
            
            # Update desktop database
            self._update_desktop_database()
            
            print("✅ Desktop integration removed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to remove desktop integration: {e}")
            return False
    
    def is_installed(self) -> bool:
        """Check if desktop integration is installed."""
        return (self.local_apps_dir / "copycat.desktop").exists()
    
    def _create_directories(self) -> None:
        """Create necessary directories."""
        directories = [
            self.local_apps_dir,
            self.local_icons_dir / "48x48/apps",
            self.local_icons_dir / "64x64/apps", 
            self.local_icons_dir / "128x128/apps",
            self.local_icons_dir / "256x256/apps",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _install_icons(self) -> None:
        """Install application icons."""
        try:
            # Get icon from package assets
            with resources.files("copycat.assets").joinpath("icon.png").open("rb") as icon_file:
                icon_data = icon_file.read()
            
            # Install at different sizes
            for size in ["48x48", "64x64", "128x128", "256x256"]:
                icon_path = self.local_icons_dir / size / "apps" / "copycat.png"
                icon_path.write_bytes(icon_data)
            
        except Exception as e:
            print(f"⚠️ Warning: Could not install icons: {e}")
    
    def _install_desktop_files(self) -> None:
        """Install .desktop files."""
        # Main GUI desktop file
        gui_desktop_content = """[Desktop Entry]
Version=1.0
Type=Application
Name=CopyCat
GenericName=Clipboard Manager
Comment=Advanced Linux clipboard utility that bypasses paste restrictions
Exec=copycat-gui
Icon=copycat
Terminal=false
Categories=Utility;System;Office;
Keywords=clipboard;copy;paste;productivity;automation;virtual-keyboard;
StartupNotify=true
StartupWMClass=CopyCat
MimeType=text/plain;text/x-python;application/json;
X-Desktop-File-Install-Version=0.26
X-AppStream-Ignore=false
"""
        
        # System tray desktop file
        tray_desktop_content = """[Desktop Entry]
Version=1.0
Type=Application
Name=CopyCat Tray
GenericName=Clipboard System Tray
Comment=CopyCat clipboard manager in system tray
Exec=copycat-tray
Icon=copycat
Terminal=false
Categories=Utility;System;
Keywords=clipboard;tray;system;background;
StartupNotify=false
StartupWMClass=CopyCat-Tray
NoDisplay=false
X-GNOME-Autostart-enabled=true
X-Desktop-File-Install-Version=0.26
"""
        
        # Write desktop files
        gui_desktop_file = self.local_apps_dir / "copycat.desktop"
        gui_desktop_file.write_text(gui_desktop_content)
        gui_desktop_file.chmod(0o755)
        
        tray_desktop_file = self.local_apps_dir / "copycat-tray.desktop"
        tray_desktop_file.write_text(tray_desktop_content)
        tray_desktop_file.chmod(0o755)
    
    def _install_autostart(self) -> None:
        """Install autostart entry."""
        self.autostart_dir.mkdir(parents=True, exist_ok=True)
        
        tray_desktop_file = self.local_apps_dir / "copycat-tray.desktop"
        autostart_file = self.autostart_dir / "copycat-tray.desktop"
        
        if tray_desktop_file.exists():
            shutil.copy2(tray_desktop_file, autostart_file)
    
    def _install_desktop_shortcut(self) -> None:
        """Install desktop shortcut."""
        if self.desktop_dir.exists():
            gui_desktop_file = self.local_apps_dir / "copycat.desktop"
            shortcut_file = self.desktop_dir / "copycat.desktop"
            
            if gui_desktop_file.exists():
                shutil.copy2(gui_desktop_file, shortcut_file)
                shortcut_file.chmod(0o755)
    
    def _update_desktop_database(self) -> None:
        """Update desktop database and icon cache."""
        # Update desktop database
        try:
            subprocess.run([
                "update-desktop-database", str(self.local_apps_dir)
            ], check=False, capture_output=True)
        except FileNotFoundError:
            pass  # Command not available
        
        # Update icon cache
        try:
            subprocess.run([
                "gtk-update-icon-cache", "-t", str(self.local_icons_dir)
            ], check=False, capture_output=True)
        except FileNotFoundError:
            pass  # Command not available


def install_desktop_integration(
    autostart: bool = False,
    desktop_shortcut: bool = False,
    quiet: bool = False
) -> bool:
    """Install desktop integration for CopyCat.
    
    Args:
        autostart: Install autostart entry
        desktop_shortcut: Create desktop shortcut
        quiet: Suppress output
    
    Returns:
        True if successful, False otherwise
    """
    if not quiet:
        print("🐾 CopyCat Desktop Integration Installer")
        print("Made with ❤️ by Pink Pixel - Dream it, Pixel it ✨")
        print()
    
    integrator = DesktopIntegrator()
    success = integrator.install(autostart=autostart, desktop_shortcut=desktop_shortcut)
    
    if success and not quiet:
        print()
        print("📱 CopyCat is now available in your applications menu!")
        print("• Look for 'CopyCat' in your applications menu")
        print("• Pin to taskbar by right-clicking the menu item")
        print("• Set up keyboard shortcuts in your DE settings")
    
    return success


def uninstall_desktop_integration(quiet: bool = False) -> bool:
    """Remove desktop integration for CopyCat.
    
    Args:
        quiet: Suppress output
    
    Returns:
        True if successful, False otherwise
    """
    if not quiet:
        print("🗑️ CopyCat Desktop Integration Removal")
        print("Made with ❤️ by Pink Pixel - Dream it, Pixel it ✨")
        print()
    
    integrator = DesktopIntegrator()
    success = integrator.uninstall()
    
    if success and not quiet:
        print()
        print("📱 CopyCat desktop integration has been removed.")
        print("• Commands are still available in terminal")
        print("• To fully remove: pip uninstall copycat-clipboard")
    
    return success


def main(argv: Optional[list[str]] = None) -> None:
    """Command-line interface for desktop integration."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CopyCat Desktop Integration Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m copycat.desktop_integration install
  python -m copycat.desktop_integration install --autostart --desktop
  python -m copycat.desktop_integration uninstall
  python -m copycat.desktop_integration status
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install desktop integration")
    install_parser.add_argument("--autostart", action="store_true",
                               help="Enable autostart")
    install_parser.add_argument("--desktop", action="store_true",
                               help="Create desktop shortcut")
    install_parser.add_argument("--quiet", action="store_true",
                               help="Suppress output")
    
    # Uninstall command  
    uninstall_parser = subparsers.add_parser("uninstall", help="Remove desktop integration")
    uninstall_parser.add_argument("--quiet", action="store_true",
                                 help="Suppress output")
    
    # Status command
    subparsers.add_parser("status", help="Check installation status")
    
    # Parse arguments
    argv = argv or sys.argv[1:]
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    integrator = DesktopIntegrator()
    
    if args.command == "install":
        success = install_desktop_integration(
            autostart=args.autostart,
            desktop_shortcut=args.desktop,
            quiet=args.quiet
        )
        sys.exit(0 if success else 1)
    
    elif args.command == "uninstall":
        success = uninstall_desktop_integration(quiet=args.quiet)
        sys.exit(0 if success else 1)
    
    elif args.command == "status":
        if integrator.is_installed():
            print("✅ Desktop integration is installed")
            
            # Check components
            components = [
                ("GUI desktop entry", integrator.local_apps_dir / "copycat.desktop"),
                ("Tray desktop entry", integrator.local_apps_dir / "copycat-tray.desktop"),
                ("Autostart entry", integrator.autostart_dir / "copycat-tray.desktop"),
                ("Desktop shortcut", integrator.desktop_dir / "copycat.desktop"),
            ]
            
            for name, path in components:
                status = "✅" if path.exists() else "❌"
                print(f"  {status} {name}")
        else:
            print("❌ Desktop integration is not installed")
        
        sys.exit(0)


if __name__ == "__main__":
    main()