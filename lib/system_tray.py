#!/usr/bin/env python3
"""
🔔 System Tray Integration

System tray icon for quick access to clipboard helper functions.
Note: System tray support varies by desktop environment.

Made with ❤️ by Pink Pixel
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import time
from pathlib import Path

# Add lib directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from clipboard_core import ClipboardManager
    from virtual_keyboard import VirtualKeyboard
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)


class SystemTrayIcon:
    """System tray integration for clipboard helper"""

    def __init__(self):
        self.clipboard = ClipboardManager()
        self.keyboard = VirtualKeyboard()
        self.root = None
        self.menu = None
        self.typing_in_progress = False

        # Check if we have tray support
        self.tray_available = self._check_tray_support()

    def _check_tray_support(self):
        """Check if system tray is available"""
        try:
            # Try to import pystray (not installed by default)
            import pystray

            return True
        except ImportError:
            # Fallback: check for notification support
            try:
                subprocess.run(
                    ["notify-send", "--version"],
                    capture_output=True,
                    timeout=2,
                    check=True,
                )
                return True
            except:
                return False

    def show_notification(self, title, message, urgency="normal"):
        """Show desktop notification"""
        try:
            subprocess.run(
                [
                    "notify-send",
                    "--urgency",
                    urgency,
                    "--app-name",
                    "Clipboard Helper",
                    "--icon",
                    "edit-paste",
                    title,
                    message,
                ],
                timeout=5,
            )
        except Exception:
            pass  # Notifications are optional

    def create_simple_menu(self):
        """Create a simple right-click menu window"""
        if self.root and self.root.winfo_exists():
            self.root.destroy()

        self.root = tk.Tk()
        self.root.title("📋 Clipboard Helper")
        self.root.geometry("300x400")
        self.root.resizable(False, False)

        # Set window to stay on top
        self.root.attributes("-topmost", True)

        # Position near system tray (bottom right)
        self.root.update_idletasks()
        x = self.root.winfo_screenwidth() - 320
        y = self.root.winfo_screenheight() - 420
        self.root.geometry(f"+{x}+{y}")

        # Style
        self.root.configure(bg="#2c3e50")

        # Header
        header_frame = tk.Frame(self.root, bg="#34495e", height=50)
        header_frame.pack(fill="x", padx=2, pady=2)
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame,
            text="📋 Clipboard Helper",
            font=("Segoe UI", 12, "bold"),
            fg="white",
            bg="#34495e",
        ).pack(pady=15)

        # Menu items
        menu_frame = tk.Frame(self.root, bg="#2c3e50")
        menu_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Quick actions
        self.create_menu_button(
            menu_frame, "🎹 Type Clipboard (Delayed)", self.type_delayed, "#27ae60"
        )
        self.create_menu_button(
            menu_frame, "⚡ Type Clipboard Now", self.type_now, "#3498db"
        )
        self.create_menu_button(
            menu_frame, "🔄 Show Current Clipboard", self.show_clipboard, "#f39c12"
        )
        self.create_menu_button(
            menu_frame, "🗂️ Show History", self.show_history, "#9b59b6"
        )
        self.create_menu_button(
            menu_frame, "🗑️ Clear Clipboard", self.clear_clipboard, "#e74c3c"
        )

        # Separator
        tk.Frame(menu_frame, height=2, bg="#34495e").pack(fill="x", pady=10)

        # Application actions
        self.create_menu_button(menu_frame, "🖥️ Open Main GUI", self.open_gui, "#16a085")
        self.create_menu_button(
            menu_frame, "📋 Show Status", self.show_status, "#7f8c8d"
        )
        self.create_menu_button(menu_frame, "❌ Close Menu", self.close_menu, "#95a5a6")

        # Status bar
        self.status_label = tk.Label(
            self.root, text="Ready", font=("Segoe UI", 9), fg="#bdc3c7", bg="#2c3e50"
        )
        self.status_label.pack(side="bottom", pady=5)

        # Update keyboard status
        self._update_status()

        # Auto-close after 10 seconds of inactivity
        self.root.after(10000, self.auto_close)

        # Focus and show
        self.root.focus_force()
        self.root.mainloop()

    def create_menu_button(self, parent, text, command, color):
        """Create a styled menu button"""
        btn = tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 10),
            fg="white",
            bg=color,
            activebackground=self._lighten_color(color),
            activeforeground="white",
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=8,
            cursor="hand2",
            command=command,
        )
        btn.pack(fill="x", pady=2)

        # Hover effects
        def on_enter(e):
            btn.config(bg=self._lighten_color(color))

        def on_leave(e):
            btn.config(bg=color)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

    def _lighten_color(self, color):
        """Lighten a hex color"""
        # Simple color lightening
        color_map = {
            "#27ae60": "#2ecc71",
            "#3498db": "#5dade2",
            "#f39c12": "#f5b041",
            "#9b59b6": "#bb8fce",
            "#e74c3c": "#ec7063",
            "#16a085": "#48c9b0",
            "#7f8c8d": "#a6acaf",
            "#95a5a6": "#b2babb",
        }
        return color_map.get(color, color)

    def _update_status(self):
        """Update status display"""
        if self.keyboard.is_available():
            self.status_label.config(text="🎹 Virtual Keyboard Ready", fg="#27ae60")
        else:
            self.status_label.config(
                text="❌ Virtual Keyboard Not Available", fg="#e74c3c"
            )

    def type_delayed(self):
        """Type clipboard with delay"""
        if self.typing_in_progress:
            self.show_notification("In Progress", "Typing operation already running!")
            return

        content = self.clipboard.get()
        if not content:
            self.show_notification(
                "Empty Clipboard", "Nothing to type - clipboard is empty!"
            )
            return

        if not self.keyboard.is_available():
            self.show_notification("Error", "Virtual keyboard not available!")
            return

        self.close_menu()
        self.show_notification(
            "Ready to Type", "Switch to target window - typing in 3 seconds..."
        )

        # Start typing in background
        threading.Thread(
            target=self._type_worker, args=(content, 3), daemon=True
        ).start()

    def type_now(self):
        """Type clipboard immediately"""
        if self.typing_in_progress:
            self.show_notification("In Progress", "Typing operation already running!")
            return

        content = self.clipboard.get()
        if not content:
            self.show_notification(
                "Empty Clipboard", "Nothing to type - clipboard is empty!"
            )
            return

        if not self.keyboard.is_available():
            self.show_notification("Error", "Virtual keyboard not available!")
            return

        self.close_menu()

        # Start typing in background
        threading.Thread(
            target=self._type_worker, args=(content, 0), daemon=True
        ).start()

    def _type_worker(self, content, delay):
        """Background typing worker"""
        self.typing_in_progress = True

        try:
            if delay > 0:
                time.sleep(delay)

            success = self.keyboard.type_text(content, delay=50)

            if success:
                self.show_notification(
                    "Success", f"Typed {len(content)} characters", "low"
                )
            else:
                self.show_notification("Error", "Failed to type content", "critical")

        except Exception as e:
            self.show_notification("Error", f"Typing failed: {str(e)}", "critical")

        finally:
            self.typing_in_progress = False

    def show_clipboard(self):
        """Show current clipboard content"""
        content = self.clipboard.get()

        if not content:
            self.show_notification("Clipboard", "Clipboard is empty")
            return

        # Show in notification (truncated)
        preview = content[:100]
        if len(content) > 100:
            preview += "..."

        self.show_notification("Current Clipboard", f"{len(content)} chars: {preview}")

        # Also show in message box for full content
        if len(content) <= 500:
            messagebox.showinfo("Clipboard Content", content)
        else:
            messagebox.showinfo(
                "Clipboard Content",
                f"Content too long to display fully.\n\n"
                f"Length: {len(content)} characters\n"
                f"Lines: {content.count(chr(10)) + 1}\n"
                f"Words: {len(content.split())}\n\n"
                f"Preview:\n{content[:200]}...",
            )

    def show_history(self):
        """Show clipboard history"""
        history = self.clipboard.get_history()

        if not history:
            self.show_notification("History", "No clipboard history available")
            return

        # Show recent history
        recent = history[-5:] if len(history) > 5 else history
        history_text = f"Last {len(recent)} clipboard entries:\n\n"

        for i, entry in enumerate(reversed(recent), 1):
            timestamp = entry.get("timestamp", "Unknown")[:16]
            preview = entry.get("preview", entry.get("content", ""))[:40]
            history_text += f"{i}. {timestamp} - {preview}\n"

        history_text += f"\nTotal history: {len(history)} entries"

        messagebox.showinfo("Clipboard History", history_text)

    def clear_clipboard(self):
        """Clear clipboard"""
        if self.clipboard.clear():
            self.show_notification("Cleared", "Clipboard has been cleared", "low")
        else:
            self.show_notification("Error", "Failed to clear clipboard", "critical")

    def open_gui(self):
        """Open main GUI"""
        try:
            gui_script = Path(__file__).parent.parent / "bin" / "clipboard-gui"
            subprocess.Popen([str(gui_script)])
            self.show_notification("GUI Opened", "Main interface launched", "low")
            self.close_menu()
        except Exception as e:
            self.show_notification("Error", f"Failed to open GUI: {str(e)}", "critical")

    def show_status(self):
        """Show system status"""
        try:
            cli_script = Path(__file__).parent.parent / "bin" / "clipboard-helper"
            result = subprocess.run(
                [str(cli_script), "--status", "-q"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                messagebox.showinfo("System Status", result.stdout)
            else:
                messagebox.showerror("Status Error", "Failed to get status")

        except Exception as e:
            messagebox.showerror("Status Error", f"Error: {str(e)}")

    def close_menu(self):
        """Close the menu"""
        if self.root and self.root.winfo_exists():
            self.root.quit()
            self.root.destroy()

    def auto_close(self):
        """Auto-close menu after timeout"""
        if self.root and self.root.winfo_exists():
            try:
                self.close_menu()
            except:
                pass

    def create_startup_script(self):
        """Create a startup script for system tray"""
        script_content = f'''#!/bin/bash
# Clipboard Helper System Tray Startup
# Add this to your desktop environment's autostart

cd "{Path(__file__).parent.parent}"
python3 -c "
import sys
sys.path.insert(0, 'lib')
from system_tray import SystemTrayIcon
tray = SystemTrayIcon()
print('📋 Clipboard Helper system tray integration available')
print('🎹 Use notifications and quick menu for clipboard operations')
print('Right-click system tray or run: python3 -c \\"from lib.system_tray import SystemTrayIcon; SystemTrayIcon().create_simple_menu()\\"')
"
'''

        startup_script = Path(__file__).parent.parent / "bin" / "clipboard-tray"
        with open(startup_script, "w") as f:
            f.write(script_content)

        os.chmod(startup_script, 0o755)
        return startup_script


def main():
    """Main entry point for system tray"""
    try:
        tray = SystemTrayIcon()

        if len(sys.argv) > 1 and sys.argv[1] == "--menu":
            # Show menu directly
            tray.create_simple_menu()
        elif len(sys.argv) > 1 and sys.argv[1] == "--setup":
            # Create startup script
            script = tray.create_startup_script()
            print(f"✅ Created startup script: {script}")
            print("💡 Add this to your desktop environment's autostart programs")
        else:
            # Show status and menu option
            print("📋 Clipboard Helper System Tray")
            print("=" * 40)
            print(
                "🎹 Virtual Keyboard:",
                "Available" if tray.keyboard.is_available() else "Not Available",
            )
            print(
                "🔔 Notifications:",
                "Available" if tray._check_tray_support() else "Not Available",
            )
            print()
            print("Usage:")
            print("  python3 lib/system_tray.py --menu     # Show quick menu")
            print("  python3 lib/system_tray.py --setup    # Create startup script")
            print()
            print("Quick access menu:")
            tray.create_simple_menu()

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
