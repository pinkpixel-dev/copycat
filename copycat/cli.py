"""CopyCat command-line interface."""

from __future__ import annotations

import argparse
import configparser
import json
import os
import subprocess
import sys
import time
from importlib import resources
from pathlib import Path
from typing import Optional

from .clipboard_core import ClipboardManager
from .virtual_keyboard import VirtualKeyboard
from .data_handlers import DataHandler
from . import __version__

RESOURCE_PACKAGE = "copycat.resources"
CONFIG_DIR = Path.home() / ".config" / "copycat"
USER_CONFIG_FILE = CONFIG_DIR / "config.conf"


class CopyCatCLI:
    """Command-line application facade for CopyCat."""

    def __init__(self) -> None:
        self.version = __version__
        self.config_dir = CONFIG_DIR
        self.config_file = USER_CONFIG_FILE
        self.default_config_name = "default.conf"
        self.templates_resource = "templates.json"

        self.clipboard = ClipboardManager()
        self.keyboard = VirtualKeyboard()
        self.data_handler = DataHandler()

        self.config = self._load_config()

    # ------------------------------------------------------------------
    def _load_config(self) -> configparser.ConfigParser:
        """Load configuration from default and user sources."""
        config = configparser.ConfigParser()

        try:
            with resources.files(RESOURCE_PACKAGE).joinpath(self.default_config_name).open(
                "r", encoding="utf-8"
            ) as handle:
                config.read_file(handle)
        except FileNotFoundError:
            pass

        if self.config_file.exists():
            config.read(self.config_file)

        return config

    # ------------------------------------------------------------------
    def setup_user_config(self) -> None:
        """Ensure the CopyCat config directory and file exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

        if not self.config_file.exists():
            try:
                template = resources.files(RESOURCE_PACKAGE).joinpath(self.default_config_name)
                with template.open("r", encoding="utf-8") as handle:
                    self.config_file.write_text(handle.read(), encoding="utf-8")
                print(f"✅ Created user configuration at {self.config_file}")
            except FileNotFoundError:
                print("⚠️ Default configuration template is missing from CopyCat.")

    # ------------------------------------------------------------------
    def get_clipboard(self) -> bool:
        """Print current clipboard contents."""
        try:
            content = self.clipboard.get()
            if content:
                print(content, end="")
                return True

            print("📋 Clipboard is empty", file=sys.stderr)
            return False
        except Exception as exc:  # pragma: no cover - best effort logging
            print(f"❌ Error reading clipboard: {exc}", file=sys.stderr)
            return False

    # ------------------------------------------------------------------
    def set_clipboard(self, text: str) -> bool:
        """Set clipboard contents."""
        try:
            if self.clipboard.set(text):
                print(f"✅ Clipboard updated with {len(text)} characters")
                return True

            print("❌ Failed to set clipboard", file=sys.stderr)
            return False
        except Exception as exc:  # pragma: no cover - best effort logging
            print(f"❌ Error setting clipboard: {exc}", file=sys.stderr)
            return False

    # ------------------------------------------------------------------
    def type_clipboard(self, delay: Optional[float] = None) -> bool:
        """Type clipboard contents using the virtual keyboard."""
        try:
            content = self.clipboard.get()
            if not content:
                print("📋 Clipboard is empty - nothing to type", file=sys.stderr)
                return False

            if delay:
                print(f"⏱️  Starting to type in {delay} seconds...")
                for seconds in range(int(delay), 0, -1):
                    print(f"⏳ {seconds}...", end=" ")
                    sys.stdout.flush()
                    time.sleep(1)
                print("\n🎹 Typing now!")

            typing_delay = self.config.getint("general", "typing_delay", fallback=50)
            if self.keyboard.type_text(content, delay=typing_delay):
                print(f"✅ Successfully typed {len(content)} characters")
                return True

            print("❌ Failed to type text", file=sys.stderr)
            return False
        except Exception as exc:  # pragma: no cover - best effort logging
            print(f"❌ Error typing clipboard content: {exc}", file=sys.stderr)
            return False

    # ------------------------------------------------------------------
    def show_history(self) -> None:
        """Display clipboard history."""
        try:
            history = self.clipboard.get_history()
            if not history:
                print("📋 No clipboard history available")
                return

            print("📜 CopyCat Clipboard History:")
            print("=" * 50)
            for index, entry in enumerate(history[-10:], 1):
                preview = entry["content"][:50]
                if len(entry["content"]) > 50:
                    preview += "..."
                print(f"{index:2d}. {entry['timestamp']} - {preview}")
        except Exception as exc:  # pragma: no cover - best effort logging
            print(f"❌ Error retrieving history: {exc}", file=sys.stderr)

    # ------------------------------------------------------------------
    def show_templates(self) -> None:
        """Display available template metadata."""
        try:
            with resources.files(RESOURCE_PACKAGE).joinpath(self.templates_resource).open(
                "r", encoding="utf-8"
            ) as handle:
                data = json.load(handle)

            print("📝 Available Templates:")
            print("=" * 50)
            for template in data.get("templates", []):
                print(f"🏷️  {template['name']} ({template['category']})")
                print(f"   {template['description']}")
                print()
        except Exception as exc:  # pragma: no cover - best effort logging
            print(f"❌ Error loading templates: {exc}", file=sys.stderr)

    # ------------------------------------------------------------------
    def clear_clipboard(self) -> bool:
        """Clear clipboard contents."""
        try:
            if self.clipboard.clear():
                print("✅ Clipboard cleared")
                return True

            print("❌ Failed to clear clipboard", file=sys.stderr)
            return False
        except Exception as exc:  # pragma: no cover - best effort logging
            print(f"❌ Error clearing clipboard: {exc}", file=sys.stderr)
            return False

    # ------------------------------------------------------------------
    def show_status(self) -> None:
        """Print CopyCat status summary."""
        print("🐾 CopyCat Status")
        print("=" * 30)
        print(f"Version: {self.version}")
        print(f"Config Dir: {self.config_dir}")
        print("Dependencies:")

        dependencies = [
            ("xclip", "Clipboard access"),
            ("xdotool", "Virtual keyboard"),
            ("notify-send", "Notifications"),
        ]

        for command, description in dependencies:
            try:
                subprocess.run(
                    [command, "--version"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True,
                )
                print(f"  ✅ {command} - {description}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"  ❌ {command} - {description} (NOT FOUND)")

        content = self.clipboard.get()
        if content:
            preview = content[:50]
            if len(content) > 50:
                preview += "..."
            print(f"\nCurrent Clipboard: {preview}")
        else:
            print("\nCurrent Clipboard: (empty)")

    # ------------------------------------------------------------------
    def launch_gui(self) -> bool:
        """Launch the CopyCat GUI."""
        try:
            subprocess.Popen([sys.executable, "-m", "copycat.gui"])
            print("🖥️  GUI launched")
            return True
        except Exception as exc:  # pragma: no cover - best effort logging
            print(f"❌ Error launching GUI: {exc}", file=sys.stderr)
            return False


# ----------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    description = "Linux clipboard utility for solving copy-paste issues in web-based UIs"
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  copycat --get                    # Get clipboard content
  copycat --set "Hello World"      # Set clipboard content  
  copycat --type                   # Type clipboard content
  copycat --type-delayed           # Type after 3-second delay
  copycat --history                # Show clipboard history
  copycat --templates              # Show available templates
  copycat --gui                    # Launch GUI interface

For Warp Settings Issue:
  1. Copy your API key/config
  2. Run: copycat --type-delayed
  3. Quickly switch to Warp settings
  4. Focus the input field
  5. Watch it type automatically! 🎉
        """,
    )

    parser.add_argument("--get", action="store_true", help="Get clipboard content")
    parser.add_argument("--set", metavar="TEXT", help="Set clipboard content")
    parser.add_argument("--type", action="store_true", help="Type clipboard content immediately")
    parser.add_argument(
        "--type-delayed", action="store_true", help="Type clipboard content after delay"
    )
    parser.add_argument("--clear", action="store_true", help="Clear clipboard")
    parser.add_argument("--history", action="store_true", help="Show clipboard history")
    parser.add_argument("--templates", action="store_true", help="Show available templates")
    parser.add_argument("--gui", action="store_true", help="Launch GUI interface")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--setup", action="store_true", help="Create user configuration")
    parser.add_argument("--install-desktop", action="store_true", help="Install desktop integration")
    parser.add_argument("--uninstall-desktop", action="store_true", help="Remove desktop integration")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress banner output")
    parser.add_argument(
        "--version",
        action="version",
        version=f"CopyCat {__version__}",
    )

    return parser


BANNER_LINES = [
    "  ██████╗ ██████╗ ██████╗ ██╗   ██╗ ██████╗ █████╗ ████████╗",
    " ██╔════╝██╔═══██╗██╔══██╗╚██╗ ██╔╝██╔════╝██╔══██╗╚══██╔══╝",
    " ██║     ██║   ██║██████╔╝ ╚████╔╝ ██║     ███████║   ██║   ",
    " ██║     ██║   ██║██╔═══╝   ╚██╔╝  ██║     ██╔══██║   ██║   ",
    " ╚██████╗╚██████╔╝██║        ██║   ╚██████╗██║  ██║   ██║   ",
    "  ╚═════╝ ╚═════╝ ╚═╝        ╚═╝    ╚═════╝╚═╝  ╚═╝   ╚═╝   ",
    "",
    "                    🐾 Linux Clipboard Superpower 🐾"
]

BANNER_COLORS = [31, 33, 32, 36, 34, 35]  # Red, Yellow, Green, Cyan, Blue, Magenta


def print_banner() -> None:
    """Print colorful CopyCat banner."""
    print()
    for i, line in enumerate(BANNER_LINES):
        if line == "":
            print()
        else:
            color = BANNER_COLORS[i % len(BANNER_COLORS)]
            print(f"\033[1;{color}m{line}\033[0m")
    print()


# ----------------------------------------------------------------------
def main(argv: Optional[list[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.quiet and not (args.get or args.set):
        print_banner()

    app = CopyCatCLI()

    if args.setup:
        app.setup_user_config()
        return 0

    success = True

    if args.get:
        success = app.get_clipboard()
    elif args.set is not None:
        success = app.set_clipboard(args.set)
    elif args.type:
        success = app.type_clipboard()
    elif args.type_delayed:
        delay = app.config.getfloat("typing", "initial_delay", fallback=3.0)
        success = app.type_clipboard(delay)
    elif args.clear:
        success = app.clear_clipboard()
    elif args.history:
        app.show_history()
    elif args.templates:
        app.show_templates()
    elif args.gui:
        success = app.launch_gui()
    elif args.status:
        app.show_status()
    elif args.install_desktop:
        from .desktop_integration import install_desktop_integration
        success = install_desktop_integration()
    elif args.uninstall_desktop:
        from .desktop_integration import uninstall_desktop_integration
        success = uninstall_desktop_integration()
    else:
        parser.print_help()
        return 0

    return 0 if success else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
