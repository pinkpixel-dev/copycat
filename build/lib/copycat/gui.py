#!/usr/bin/env python3
"""
🖥️ CopyCat GUI - Modern Interface

Beautiful GUI interface for CopyCat with all features accessible through an
intuitive interface.

Made with ❤️ by Pink Pixel
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import subprocess
import threading
import json
from pathlib import Path
import time

from . import __version__
from .clipboard_core import ClipboardManager
from .virtual_keyboard import VirtualKeyboard
from .data_handlers import DataHandler
from .template_manager import AdvancedTemplateManager

class ModernButton(tk.Button):
    """Modern styled button with hover effects"""
    def __init__(self, parent, **kwargs):
        # Default modern styling
        default_style = {
            'font': ('Segoe UI', 10, 'normal'),
            'relief': 'flat',
            'borderwidth': 0,
            'padx': 20,
            'pady': 8,
            'cursor': 'hand2'
        }
        default_style.update(kwargs)
        super().__init__(parent, **default_style)
        
        # Store colors for hover effects
        self.default_bg = default_style.get('bg', '#0078d4')
        self.hover_bg = self._lighten_color(self.default_bg, 0.1)
        
        # Bind hover events
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _lighten_color(self, color, factor):
        """Lighten a hex color by a factor"""
        if color.startswith('#'):
            color = color[1:]
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _on_enter(self, event):
        self.config(bg=self.hover_bg)
    
    def _on_leave(self, event):
        self.config(bg=self.default_bg)

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
ICON_PATH = ASSETS_DIR / "icon.png"
LOGO_PATH = ASSETS_DIR / "logo.png"


class CopyCatGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.themes = {
            'light': {
                'window_bg': '#f8f9fa',
                'card_bg': '#ffffff',
                'accent_bg': '#e9ecef',
                'text_primary': '#212529',
                'text_secondary': '#495057',
                'status_bg': '#e9ecef',
                'status_fg': '#495057',
                'text_bg': '#ffffff',
                'text_fg': '#212529',
                'muted_bg': '#f8f9fa',
            },
            'dark': {
                'window_bg': '#1f1f25',
                'card_bg': '#2b2b35',
                'accent_bg': '#34343f',
                'text_primary': '#f5f6f8',
                'text_secondary': '#c3c7d1',
                'status_bg': '#34343f',
                'status_fg': '#d7dbe5',
                'text_bg': '#1f1f25',
                'text_fg': '#f5f6f8',
                'muted_bg': '#262630',
            },
        }
        self.theme_var = tk.StringVar(value='light')
        self.colors = self.themes[self.theme_var.get()]
        self.themable_widgets = []
        self.themable_text_widgets = []
        self.themable_listboxes = []
        self.clipboard = ClipboardManager()
        self.keyboard = VirtualKeyboard()
        
        # Initialize advanced template manager
        config_dir = os.path.expanduser("~/.copycat")
        self.template_manager = AdvancedTemplateManager(config_dir)
        
        # Initialize data handler with template manager reference
        self.data_handler = DataHandler(template_manager=self.template_manager)
        
        # GUI state
        self.typing_in_progress = False
        self.countdown_active = False
        
        self.setup_window()
        self.create_widgets()
        self.start_clipboard_monitor()

    # ------------------------------------------------------------------
    def set_theme(self, theme_name: str) -> None:
        """Set current theme and apply colors."""
        if theme_name not in self.themes:
            return
        self.colors = self.themes[theme_name]
        self.theme_var.set(theme_name)
        self.apply_theme()

    # ------------------------------------------------------------------
    def register_themable(self, widget, color_key: str, fg_key: str = None,
                           extra_options: dict | None = None) -> None:
        """Track widgets that need theme-aware color updates."""
        self.themable_widgets.append((widget, color_key, fg_key, extra_options or {}))
        config = {'bg': self.colors[color_key]}
        if fg_key:
            config['fg'] = self.colors[fg_key]
        widget.configure(**config)
        for option, key in (extra_options or {}).items():
            try:
                widget.configure(**{option: self.colors[key]})
            except tk.TclError:
                continue

    # ------------------------------------------------------------------
    def register_text_widget(self, widget, bg_key: str, fg_key: str) -> None:
        """Track text widgets for theme-aware foreground/background updates."""
        self.themable_text_widgets.append((widget, bg_key, fg_key))
        widget.configure(
            bg=self.colors[bg_key],
            fg=self.colors[fg_key],
            insertbackground=self.colors[fg_key]
        )

    # ------------------------------------------------------------------
    def register_listbox(self, widget, bg_key: str, fg_key: str) -> None:
        """Track listbox widgets for theme updates."""
        self.themable_listboxes.append((widget, bg_key, fg_key))
        widget.configure(
            bg=self.colors[bg_key],
            fg=self.colors[fg_key],
            selectbackground=self.colors['accent_bg'],
            highlightcolor=self.colors['accent_bg'],
            highlightbackground=self.colors['accent_bg']
        )

    # ------------------------------------------------------------------
    def themed_frame(self, parent, color_key: str = 'card_bg', **kwargs):
        """Convenience helper for creating theme-aware frames."""
        frame = tk.Frame(parent, bg=self.colors[color_key], **kwargs)
        self.register_themable(frame, color_key)
        return frame

    # ------------------------------------------------------------------
    def themed_text(self, *args, bg_key: str = 'text_bg', fg_key: str = 'text_fg', **kwargs):
        """Create a theme-aware text widget."""
        widget = tk.Text(*args, **kwargs)
        self.register_text_widget(widget, bg_key, fg_key)
        return widget

    # ------------------------------------------------------------------
    def themed_scrolled_text(self, *args, bg_key: str = 'text_bg', fg_key: str = 'text_fg', **kwargs):
        """Create a theme-aware scrolled text widget."""
        widget = scrolledtext.ScrolledText(*args, **kwargs)
        self.register_text_widget(widget, bg_key, fg_key)
        return widget

    # ------------------------------------------------------------------
    def apply_theme(self) -> None:
        """Apply theme colors to registered widgets and styles."""
        # Root window background
        self.root.configure(bg=self.colors['window_bg'])

        # Update stored frames and text widgets
        for widget, color_key, fg_key, extras in self.themable_widgets:
            try:
                config = {'bg': self.colors[color_key]}
                if fg_key:
                    config['fg'] = self.colors[fg_key]
                widget.configure(**config)
                for option, key in extras.items():
                    widget.configure(**{option: self.colors[key]})
            except tk.TclError:
                continue

        for widget, bg_key, fg_key in self.themable_text_widgets:
            try:
                widget.configure(
                    bg=self.colors[bg_key],
                    fg=self.colors[fg_key],
                    insertbackground=self.colors[fg_key]
                )
            except tk.TclError:
                continue

        for widget, bg_key, fg_key in self.themable_listboxes:
            try:
                widget.configure(
                    bg=self.colors[bg_key],
                    fg=self.colors[fg_key],
                    selectbackground=self.colors['accent_bg'],
                    highlightcolor=self.colors['accent_bg'],
                    highlightbackground=self.colors['accent_bg']
                )
            except tk.TclError:
                continue

        # Update styles if style system initialized
        if hasattr(self, 'style'):
            self.style.configure(
                'TNotebook',
                background=self.colors['window_bg']
            )
            self.style.configure(
                'TNotebook.Tab',
                background=self.colors['card_bg'],
                foreground=self.colors['text_primary']
            )
            self.style.configure(
                'TLabel',
                background=self.colors['card_bg'],
                foreground=self.colors['text_primary']
            )
            self.style.configure(
                'Title.TLabel',
                foreground=self.colors['text_primary'],
                background=self.colors['window_bg']
            )
            self.style.configure(
                'Subtitle.TLabel',
                foreground=self.colors['text_secondary'],
                background=self.colors['window_bg']
            )
            self.style.configure(
                'Status.TLabel',
                foreground=self.colors['status_fg'],
                background=self.colors['status_bg']
            )

    def setup_window(self):
        """Configure main window"""
        self.root.title("🐾 CopyCat")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        if ICON_PATH.exists():
            try:
                icon_image = tk.PhotoImage(file=str(ICON_PATH))
                self.root.iconphoto(True, icon_image)
                self._icon_image = icon_image  # prevent GC
            except Exception:
                pass
        
        # Modern styling
        self.root.configure(bg=self.colors['window_bg'])
        
        # Center window
        self.center_window()
        
        # Configure styles
        self.setup_styles()

        # Apply theme colors to foundational widgets
        self.apply_theme()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def setup_styles(self):
        """Setup ttk styles"""
        self.style = ttk.Style()
        
        # Configure notebook tabs
        self.style.configure('TNotebook.Tab', padding=[20, 10])
        self.style.configure('TNotebook', tabposition='n')
        self.style.configure(
            'TLabel',
            background=self.colors['card_bg'],
            foreground=self.colors['text_primary']
        )
        
        # Configure other widgets
        self.style.configure(
            'Title.TLabel',
            font=('Segoe UI', 16, 'bold'),
            foreground=self.colors['text_primary'],
            background=self.colors['window_bg']
        )
        self.style.configure(
            'Subtitle.TLabel',
            font=('Segoe UI', 12),
            foreground=self.colors['text_secondary'],
            background=self.colors['window_bg']
        )
        self.style.configure(
            'Status.TLabel',
            font=('Consolas', 9),
            foreground=self.colors['status_fg'],
            background=self.colors['status_bg']
        )
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = self.themed_frame(self.root, color_key='window_bg')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_frame)
        
        # Quick actions section
        self.create_quick_actions(main_frame)
        
        # Main content with tabs
        self.create_main_content(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """Create header section"""
        header_frame = self.themed_frame(parent, color_key='window_bg')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Title / Logo
        content_frame = self.themed_frame(header_frame, color_key='window_bg')
        content_frame.pack(fill='x')

        if LOGO_PATH.exists():
            try:
                logo_image = tk.PhotoImage(file=str(LOGO_PATH))

                # Scale down large logos so they don't dominate the header
                max_dim = 160
                scale = 1
                while (
                    logo_image.width() // scale > max_dim
                    or logo_image.height() // scale > max_dim
                ):
                    scale += 1
                if scale > 1:
                    logo_image = logo_image.subsample(scale, scale)

                self._logo_image = logo_image  # prevent GC
                logo_label = tk.Label(
                    content_frame,
                    image=logo_image,
                    bg=self.colors['window_bg']
                )
                logo_label.pack(side='left', pady=(0, 10), padx=(0, 15))
                self.register_themable(logo_label, 'window_bg')
            except Exception:
                pass

        text_frame = self.themed_frame(content_frame, color_key='window_bg')
        text_frame.pack(side='left', fill='x', expand=True)

        ttk.Label(text_frame, text="🐾 CopyCat", style='Title.TLabel').pack(anchor='w')
        ttk.Label(
            text_frame,
            text="Linux clipboard utility for solving copy-paste issues in web-based UIs",
            style='Subtitle.TLabel'
        ).pack(anchor='w')
    
    def create_quick_actions(self, parent):
        """Create quick action buttons"""
        actions_frame = self.themed_frame(parent, color_key='window_bg')
        actions_frame.pack(fill='x', pady=(0, 20))
        
        qa_label = tk.Label(
            actions_frame,
            text="Quick Actions",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['window_bg'],
            fg=self.colors['text_primary']
        )
        qa_label.pack(anchor='w', pady=(0, 10))
        self.register_themable(qa_label, 'window_bg', 'text_primary')
        
        # Button container
        btn_frame = self.themed_frame(actions_frame, color_key='window_bg')
        btn_frame.pack(fill='x')
        
        # Main action buttons
        self.type_delayed_btn = ModernButton(
            btn_frame,
            text="🎹 Type Clipboard (Delayed)",
            bg='#28a745',
            fg='white',
            font=('Segoe UI', 11, 'bold'),
            command=self.type_delayed
        )
        self.type_delayed_btn.pack(side='left', padx=(0, 10))
        
        self.type_now_btn = ModernButton(
            btn_frame,
            text="⚡ Type Now",
            bg='#17a2b8',
            fg='white',
            command=self.type_now
        )
        self.type_now_btn.pack(side='left', padx=(0, 10))
        
        self.clear_btn = ModernButton(
            btn_frame,
            text="🗑️ Clear",
            bg='#dc3545',
            fg='white',
            command=self.clear_clipboard
        )
        self.clear_btn.pack(side='left', padx=(0, 10))
        
        # Countdown label (hidden by default)
        self.countdown_label = tk.Label(
            btn_frame,
            text="",
            font=('Segoe UI', 12, 'bold'),
            fg='#28a745',
            bg=self.colors['window_bg']
        )
        self.countdown_label.pack(side='right')
        self.register_themable(self.countdown_label, 'window_bg')
    
    def create_main_content(self, parent):
        """Create main tabbed content area"""
        # Notebook for tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill='both', expand=True, pady=(0, 20))
        
        # Create tabs
        self.create_clipboard_tab()
        self.create_history_tab()
        self.create_templates_tab()
        self.create_settings_tab()
    
    def create_clipboard_tab(self):
        """Create clipboard monitoring tab"""
        frame = self.themed_frame(self.notebook, color_key='card_bg')
        self.notebook.add(frame, text="📋 Clipboard")
        
        # Clipboard content area
        content_frame = self.themed_frame(frame, color_key='card_bg')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ccc_label = tk.Label(
            content_frame,
            text="Current Clipboard Content",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        ccc_label.pack(anchor='w', pady=(0, 10))
        self.register_themable(ccc_label, 'card_bg', 'text_primary')
        
        # Clipboard text area
        self.clipboard_text = self.themed_scrolled_text(
            content_frame,
            height=8,
            wrap='word',
            font=('Consolas', 10),
            state='disabled'
        )
        self.clipboard_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # Clipboard actions
        actions_frame = self.themed_frame(content_frame, color_key='card_bg')
        actions_frame.pack(fill='x', pady=(10, 0))
        
        ModernButton(
            actions_frame,
            text="🔄 Refresh",
            bg='#6c757d',
            fg='white',
            command=self.refresh_clipboard
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            actions_frame,
            text="📄 Copy to File",
            bg='#fd7e14',
            fg='white',
            command=self.save_clipboard_to_file
        ).pack(side='left', padx=(0, 10))
        
        self.create_template_btn = ModernButton(
            actions_frame,
            text="🎯 Create Template",
            bg='#6f42c1',
            fg='white',
            command=self.create_template_from_clipboard
        )
        self.create_template_btn.pack(side='left', padx=(0, 10))
        
        # Data analysis area
        analysis_frame = self.themed_frame(content_frame, color_key='card_bg')
        analysis_frame.pack(fill='x', pady=(20, 0))
        
        ca_label = tk.Label(
            analysis_frame,
            text="Content Analysis",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        ca_label.pack(anchor='w', pady=(0, 5))
        self.register_themable(ca_label, 'card_bg', 'text_primary')
        
        self.analysis_text = self.themed_text(
            analysis_frame,
            height=4,
            wrap='word',
            font=('Segoe UI', 9),
            state='disabled',
            bg_key='muted_bg'
        )
        self.analysis_text.pack(fill='x', pady=(0, 10))
    
    def create_history_tab(self):
        """Create clipboard history tab"""
        frame = self.themed_frame(self.notebook, color_key='card_bg')
        self.notebook.add(frame, text="🗂️ History")
        
        content_frame = self.themed_frame(frame, color_key='card_bg')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = self.themed_frame(content_frame, color_key='card_bg')
        header_frame.pack(fill='x', pady=(0, 10))
        
        history_label = tk.Label(
            header_frame,
            text="Clipboard History",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        history_label.pack(side='left')
        self.register_themable(history_label, 'card_bg', 'text_primary')
        
        ModernButton(
            header_frame,
            text="🔄 Refresh",
            bg='#6c757d',
            fg='white',
            command=self.refresh_history
        ).pack(side='right')
        
        # History list
        self.history_frame = self.themed_frame(content_frame, color_key='card_bg')
        self.history_frame.pack(fill='both', expand=True)
        
        # History listbox with scrollbar
        list_frame = self.themed_frame(self.history_frame, color_key='card_bg')
        list_frame.pack(fill='both', expand=True)
        
        self.history_listbox = tk.Listbox(
            list_frame,
            font=('Consolas', 9),
            selectmode='single'
        )
        self.register_listbox(self.history_listbox, 'text_bg', 'text_fg')
        history_scrollbar = tk.Scrollbar(list_frame, orient='vertical', command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_listbox.pack(side='left', fill='both', expand=True)
        history_scrollbar.pack(side='right', fill='y')
        
        # History actions
        history_actions = self.themed_frame(content_frame, color_key='card_bg')
        history_actions.pack(fill='x', pady=(10, 0))
        
        ModernButton(
            history_actions,
            text="📋 Restore Selected",
            bg='#28a745',
            fg='white',
            command=self.restore_from_history
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            history_actions,
            text="🗑️ Clear History",
            bg='#dc3545',
            fg='white',
            command=self.clear_history
        ).pack(side='left')
    
    def create_templates_tab(self):
        """Create advanced templates tab"""
        frame = self.themed_frame(self.notebook, color_key='card_bg')
        self.notebook.add(frame, text="📝 Templates")
        
        # Create template sub-notebook
        template_notebook = ttk.Notebook(frame)
        template_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create template sub-tabs
        self.create_template_browser_tab(template_notebook)
        self.create_template_editor_tab(template_notebook)
        self.create_template_analytics_tab(template_notebook)
    
    def create_template_browser_tab(self, parent):
        """Create template browser tab"""
        frame = self.themed_frame(parent, color_key='card_bg')
        parent.add(frame, text="📋 Browse")
        
        # Header with search and filters
        header_frame = self.themed_frame(frame, color_key='card_bg')
        header_frame.pack(fill='x', padx=20, pady=10)
        
        # Search and filter controls
        search_frame = self.themed_frame(header_frame, color_key='card_bg')
        search_frame.pack(fill='x', pady=(0, 10))
        
        search_label = tk.Label(
            search_frame,
            text="🔍 Search:",
            font=('Segoe UI', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        search_label.pack(side='left')
        self.register_themable(search_label, 'card_bg', 'text_primary')
        self.template_search = tk.Entry(search_frame, font=('Segoe UI', 10), width=20)
        self.template_search.pack(side='left', padx=(5, 10))
        self.template_search.bind('<KeyRelease>', self.filter_templates)
        
        category_label = tk.Label(
            search_frame,
            text="Category:",
            font=('Segoe UI', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        category_label.pack(side='left')
        self.register_themable(category_label, 'card_bg', 'text_primary')
        self.template_category = ttk.Combobox(search_frame, width=15, font=('Segoe UI', 10))
        self.template_category.pack(side='left', padx=(5, 10))
        self.template_category.bind('<<ComboboxSelected>>', self.filter_templates)
        
        ModernButton(
            search_frame,
            text="🔄 Refresh",
            bg='#6c757d',
            fg='white',
            command=self.refresh_templates
        ).pack(side='left', padx=(10, 0))
        
        # Template list
        list_frame = self.themed_frame(frame, color_key='card_bg')
        list_frame.pack(fill='both', expand=True, padx=20)
        
        # Templates listbox with details
        self.templates_listbox = tk.Listbox(
            list_frame,
            font=('Segoe UI', 10),
            selectmode='single',
            height=8
        )
        self.register_listbox(self.templates_listbox, 'text_bg', 'text_fg')
        templates_scrollbar = tk.Scrollbar(list_frame, orient='vertical', command=self.templates_listbox.yview)
        self.templates_listbox.configure(yscrollcommand=templates_scrollbar.set)
        self.templates_listbox.bind('<<ListboxSelect>>', self.on_template_select)
        
        self.templates_listbox.pack(side='left', fill='both', expand=True)
        templates_scrollbar.pack(side='right', fill='y')
        
        # Template preview and actions
        preview_frame = self.themed_frame(frame, color_key='card_bg')
        preview_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Template details
        details_frame = self.themed_frame(preview_frame, color_key='card_bg')
        details_frame.pack(fill='x', pady=(0, 10))
        
        self.template_name_label = tk.Label(
            details_frame,
            text="Select a template...",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        self.template_name_label.pack(anchor='w')
        self.register_themable(self.template_name_label, 'card_bg', 'text_primary')
        
        self.template_desc_label = tk.Label(
            details_frame,
            text="",
            font=('Segoe UI', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        )
        self.template_desc_label.pack(anchor='w')
        self.register_themable(self.template_desc_label, 'card_bg', 'text_secondary')
        
        # Template content preview
        self.template_preview = self.themed_scrolled_text(
            preview_frame,
            height=6,
            wrap='word',
            font=('Consolas', 9),
            state='disabled'
        )
        self.template_preview.pack(fill='both', expand=True, pady=(0, 10))
        
        # Template actions
        actions_frame = self.themed_frame(preview_frame, color_key='card_bg')
        actions_frame.pack(fill='x')
        
        self.use_template_btn = ModernButton(
            actions_frame,
            text="✨ Use Template",
            bg='#28a745',
            fg='white',
            command=self.use_selected_template,
            state='disabled'
        )
        self.use_template_btn.pack(side='left', padx=(0, 10))
        
        self.edit_template_btn = ModernButton(
            actions_frame,
            text="✏️ Edit",
            bg='#17a2b8',
            fg='white',
            command=self.edit_selected_template,
            state='disabled'
        )
        self.edit_template_btn.pack(side='left', padx=(0, 10))
        
        self.delete_template_btn = ModernButton(
            actions_frame,
            text="🗑️ Delete",
            bg='#dc3545',
            fg='white',
            command=self.delete_selected_template,
            state='disabled'
        )
        self.delete_template_btn.pack(side='left')
        
        # Templates will be initialized in run() method
    
    def create_template_editor_tab(self, parent):
        """Create template editor tab"""
        frame = self.themed_frame(parent, color_key='card_bg')
        parent.add(frame, text="✏️ Editor")
        
        content_frame = self.themed_frame(frame, color_key='card_bg')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Editor header
        header_frame = self.themed_frame(content_frame, color_key='card_bg')
        header_frame.pack(fill='x', pady=(0, 10))
        
        editor_label = tk.Label(
            header_frame,
            text="Template Editor",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        editor_label.pack(anchor='w')
        self.register_themable(editor_label, 'card_bg', 'text_primary')
        
        # Template form
        form_frame = self.themed_frame(content_frame, color_key='card_bg')
        form_frame.pack(fill='x', pady=(0, 10))
        
        # Name
        name_label = tk.Label(
            form_frame,
            text="Name:",
            font=('Segoe UI', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        name_label.grid(row=0, column=0, sticky='w', pady=2)
        self.register_themable(name_label, 'card_bg', 'text_primary')
        self.editor_name = tk.Entry(form_frame, font=('Segoe UI', 10), width=30)
        self.editor_name.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=2)
        
        # Description
        desc_label = tk.Label(
            form_frame,
            text="Description:",
            font=('Segoe UI', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        desc_label.grid(row=1, column=0, sticky='w', pady=2)
        self.register_themable(desc_label, 'card_bg', 'text_primary')
        self.editor_description = tk.Entry(form_frame, font=('Segoe UI', 10), width=50)
        self.editor_description.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=2)
        
        # Category
        category_label = tk.Label(
            form_frame,
            text="Category:",
            font=('Segoe UI', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        category_label.grid(row=2, column=0, sticky='w', pady=2)
        self.register_themable(category_label, 'card_bg', 'text_primary')
        self.editor_category = ttk.Combobox(form_frame, font=('Segoe UI', 10), width=20)
        self.editor_category.grid(row=2, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # Tags
        tags_label = tk.Label(
            form_frame,
            text="Tags (comma-separated):",
            font=('Segoe UI', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        tags_label.grid(row=3, column=0, sticky='w', pady=2)
        self.register_themable(tags_label, 'card_bg', 'text_primary')
        self.editor_tags = tk.Entry(form_frame, font=('Segoe UI', 10), width=50)
        self.editor_tags.grid(row=3, column=1, sticky='ew', padx=(10, 0), pady=2)

        form_frame.columnconfigure(1, weight=1)
        
        # Template content
        content_label = tk.Label(
            content_frame,
            text="Template Content (use {{PLACEHOLDER}} for variables):",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        content_label.pack(anchor='w', pady=(10, 5))
        self.register_themable(content_label, 'card_bg', 'text_primary')
        
        self.editor_content = self.themed_scrolled_text(
            content_frame,
            height=10,
            wrap='word',
            font=('Consolas', 10)
        )
        self.editor_content.pack(fill='both', expand=True, pady=(0, 10))

        # Placeholder analysis
        analysis_frame = self.themed_frame(content_frame, color_key='card_bg')
        analysis_frame.pack(fill='x', pady=(0, 10))
        
        detected_label = tk.Label(
            analysis_frame,
            text="Detected Placeholders:",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        detected_label.pack(anchor='w')
        self.register_themable(detected_label, 'card_bg', 'text_primary')
        
        self.placeholders_display = self.themed_text(
            analysis_frame,
            height=3,
            wrap='word',
            font=('Segoe UI', 9),
            state='disabled',
            bg_key='muted_bg'
        )
        self.placeholders_display.pack(fill='x', pady=(5, 0))

        # Bind content change to analyze placeholders
        self.editor_content.bind('<KeyRelease>', self.analyze_template_placeholders)

        # Editor actions
        actions_frame = self.themed_frame(content_frame, color_key='card_bg')
        actions_frame.pack(fill='x')
        
        ModernButton(
            actions_frame,
            text="💾 Save Template",
            bg='#28a745',
            fg='white',
            command=self.save_template
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            actions_frame,
            text="🆕 Clear Form",
            bg='#6c757d',
            fg='white',
            command=self.clear_editor_form
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            actions_frame,
            text="📁 Import Templates",
            bg='#fd7e14',
            fg='white',
            command=self.import_templates
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            actions_frame,
            text="📤 Export Templates",
            bg='#6f42c1',
            fg='white',
            command=self.export_templates
        ).pack(side='left')
        
        # Categories will be loaded in run() method
    
    def create_template_analytics_tab(self, parent):
        """Create template analytics tab"""
        frame = self.themed_frame(parent, color_key='card_bg')
        parent.add(frame, text="📈 Analytics")
        
        content_frame = self.themed_frame(frame, color_key='card_bg')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Analytics header
        analytics_label = tk.Label(
            content_frame,
            text="Template Usage Analytics",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        analytics_label.pack(anchor='w', pady=(0, 10))
        self.register_themable(analytics_label, 'card_bg', 'text_primary')
        
        # Statistics display
        self.analytics_text = self.themed_scrolled_text(
            content_frame,
            height=15,
            wrap='word',
            font=('Consolas', 10),
            state='disabled'
        )
        self.analytics_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # Analytics actions
        actions_frame = self.themed_frame(content_frame, color_key='card_bg')
        actions_frame.pack(fill='x')
        
        ModernButton(
            actions_frame,
            text="🔄 Refresh Analytics",
            bg='#17a2b8',
            fg='white',
            command=self.refresh_analytics
        ).pack(side='left')
        
        # Analytics will be loaded in run() method
    
    def create_settings_tab(self):
        """Create settings tab"""
        frame = self.themed_frame(self.notebook, color_key='card_bg')
        self.notebook.add(frame, text="⚙️ Settings")
        
        content_frame = self.themed_frame(frame, color_key='card_bg')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Theme selection section
        theme_section = self.themed_frame(content_frame, color_key='card_bg')
        theme_section.pack(fill='x', pady=(0, 15))

        theme_label = tk.Label(
            theme_section,
            text="Theme",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        theme_label.pack(anchor='w')
        self.register_themable(theme_label, 'card_bg', 'text_primary')

        toggle_frame = self.themed_frame(theme_section, color_key='card_bg')
        toggle_frame.pack(fill='x', pady=(5, 0))

        light_rb = tk.Radiobutton(
            toggle_frame,
            text="Light",
            variable=self.theme_var,
            value='light',
            command=lambda: self.set_theme('light'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary'],
            selectcolor=self.colors['accent_bg'],
            activebackground=self.colors['card_bg']
        )
        light_rb.pack(side='left', padx=(0, 10))
        self.register_themable(
            light_rb,
            'card_bg',
            'text_primary',
            extra_options={
                'selectcolor': 'accent_bg',
                'activebackground': 'card_bg',
                'activeforeground': 'text_primary'
            }
        )

        dark_rb = tk.Radiobutton(
            toggle_frame,
            text="Dark",
            variable=self.theme_var,
            value='dark',
            command=lambda: self.set_theme('dark'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary'],
            selectcolor=self.colors['accent_bg'],
            activebackground=self.colors['card_bg']
        )
        dark_rb.pack(side='left')
        self.register_themable(
            dark_rb,
            'card_bg',
            'text_primary',
            extra_options={
                'selectcolor': 'accent_bg',
                'activebackground': 'card_bg',
                'activeforeground': 'text_primary'
            }
        )

        divider = tk.Frame(content_frame, height=2, bg=self.colors['accent_bg'])
        divider.pack(fill='x', pady=(0, 15))
        self.register_themable(divider, 'accent_bg')

        status_label = tk.Label(
            content_frame,
            text="System Status",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        status_label.pack(anchor='w', pady=(0, 10))
        self.register_themable(status_label, 'card_bg', 'text_primary')

        # Status display
        self.status_text = self.themed_scrolled_text(
            content_frame,
            height=8,
            wrap='word',
            font=('Consolas', 9),
            state='disabled'
        )
        self.status_text.pack(fill='both', expand=True, pady=(0, 10))

        # Settings actions
        settings_actions = self.themed_frame(content_frame, color_key='card_bg')
        settings_actions.pack(fill='x')

        ModernButton(
            settings_actions,
            text="🔄 Check Status",
            bg='#17a2b8',
            fg='white',
            command=self.update_status
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            settings_actions,
            text="⚙️ Setup Config",
            bg='#ffc107',
            fg='black',
            command=self.setup_config
        ).pack(side='left', padx=(0, 10))
    
    def create_status_bar(self, parent):
        """Create status bar"""
        self.status_bar = self.themed_frame(parent, color_key='status_bg', height=30)
        self.status_bar.pack(fill='x', side='bottom')
        self.status_bar.pack_propagate(False)

        self.status_label = ttk.Label(
            self.status_bar, 
            text="Ready", 
            style='Status.TLabel'
        )
        self.status_label.pack(side='left', padx=10, pady=5)

        # Virtual keyboard status
        self.keyboard_status = ttk.Label(
            self.status_bar,
            text="🎹 Virtual Keyboard: Checking...",
            style='Status.TLabel'
        )
        self.keyboard_status.pack(side='right', padx=10, pady=5)
        
        # Update keyboard status
        self.update_keyboard_status()
    
    def update_keyboard_status(self):
        """Update virtual keyboard status"""
        if self.keyboard.is_available():
            self.keyboard_status.config(text="🎹 Virtual Keyboard: Ready ✅", foreground='#28a745')
        else:
            self.keyboard_status.config(text="🎹 Virtual Keyboard: Not Available ❌", foreground='#dc3545')
    
    def start_clipboard_monitor(self):
        """Start monitoring clipboard changes"""
        self.refresh_clipboard()
        # Schedule next check
        self.root.after(2000, self.start_clipboard_monitor)
    
    def refresh_clipboard(self):
        """Refresh clipboard content display"""
        try:
            content = self.clipboard.get()
            
            # Update clipboard display
            self.clipboard_text.config(state='normal')
            self.clipboard_text.delete(1.0, 'end')
            
            if content:
                self.clipboard_text.insert(1.0, content)
                
                # Analyze content with template suggestions
                analysis = self.data_handler.enhance_content_with_templates(content)
                self.update_analysis_display(analysis)
                
                # Update status
                self.status_label.config(text=f"Clipboard: {len(content)} characters")
            else:
                self.clipboard_text.insert(1.0, "(empty)")
                self.analysis_text.config(state='normal')
                self.analysis_text.delete(1.0, 'end')
                self.analysis_text.config(state='disabled')
                self.status_label.config(text="Clipboard: empty")
            
            self.clipboard_text.config(state='disabled')
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
    
    def update_analysis_display(self, analysis):
        """Update content analysis display with enhanced information"""
        self.analysis_text.config(state='normal')
        self.analysis_text.delete(1.0, 'end')
        
        info_lines = [
            f"Type: {analysis['primary_type'].title()}",
            f"Length: {analysis['original_length']} chars, {analysis['words']} words, {analysis['lines']} lines",
            f"Confidence: {analysis['confidence']:.1%}"
        ]
        
        # Add security level if available
        if analysis.get('security_level'):
            security_emoji = {
                'high': '🔒',
                'medium': '🔓', 
                'low': '🔑',
                'none': '📄'
            }
            security_level = analysis['security_level']
            emoji = security_emoji.get(security_level, '❓')
            info_lines.append(f"Security: {emoji} {security_level.title()}")
        
        # Add metadata information (excluding sensitive fields)
        if analysis.get('metadata'):
            for key, value in analysis['metadata'].items():
                if key not in ['masked', 'service'] and value not in [True, False]:  
                    info_lines.append(f"{key.title()}: {value}")
        
        # Add template suggestions if available
        if analysis.get('suggested_templates'):
            suggestions = analysis['suggested_templates'][:3]  # Show top 3
            if suggestions:
                info_lines.append("")
                info_lines.append("💡 Template Suggestions:")
                for suggestion in suggestions:
                    reason = suggestion.get('suggestion_reason', 'Relevant match')
                    info_lines.append(f"  • {suggestion['name']} - {reason}")
        
        self.analysis_text.insert(1.0, '\n'.join(info_lines))
        self.analysis_text.config(state='disabled')
    
    def type_delayed(self):
        """Type clipboard content after delay"""
        if self.typing_in_progress:
            messagebox.showwarning("In Progress", "Typing operation already in progress!")
            return
        
        content = self.clipboard.get()
        if not content:
            messagebox.showwarning("Empty Clipboard", "Nothing to type - clipboard is empty!")
            return
        
        if not self.keyboard.is_available():
            messagebox.showerror("Virtual Keyboard Error", "Virtual keyboard not available!\nMake sure xdotool is installed.")
            return
        
        # Start countdown
        self.start_countdown()
    
    def start_countdown(self):
        """Start 3-second countdown"""
        self.typing_in_progress = True
        self.countdown_active = True
        
        # Disable buttons
        self.type_delayed_btn.config(state='disabled')
        self.type_now_btn.config(state='disabled')
        
        # Start countdown in separate thread
        threading.Thread(target=self.countdown_worker, daemon=True).start()
    
    def countdown_worker(self):
        """Countdown worker thread"""
        try:
            for i in range(3, 0, -1):
                if not self.countdown_active:  # Check if cancelled
                    return
                
                # Update countdown display
                self.root.after(0, lambda i=i: self.countdown_label.config(text=f"⏳ Typing in {i}..."))
                time.sleep(1)
            
            # Start typing
            self.root.after(0, lambda: self.countdown_label.config(text="🎹 Typing now!"))
            
            content = self.clipboard.get()
            success = self.keyboard.type_text(content, delay=50)
            
            # Update UI
            if success:
                self.root.after(0, lambda: self.status_label.config(text=f"✅ Typed {len(content)} characters"))
            else:
                self.root.after(0, lambda: self.status_label.config(text="❌ Typing failed"))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text=f"❌ Error: {str(e)}"))
        
        finally:
            # Re-enable UI
            self.root.after(0, self.finish_typing)
    
    def finish_typing(self):
        """Clean up after typing operation"""
        self.typing_in_progress = False
        self.countdown_active = False
        
        # Re-enable buttons
        self.type_delayed_btn.config(state='normal')
        self.type_now_btn.config(state='normal')
        
        # Clear countdown
        self.countdown_label.config(text="")
    
    def type_now(self):
        """Type clipboard content immediately"""
        if self.typing_in_progress:
            messagebox.showwarning("In Progress", "Typing operation already in progress!")
            return
        
        content = self.clipboard.get()
        if not content:
            messagebox.showwarning("Empty Clipboard", "Nothing to type - clipboard is empty!")
            return
        
        if not self.keyboard.is_available():
            messagebox.showerror("Virtual Keyboard Error", "Virtual keyboard not available!")
            return
        
        # Type in background thread
        self.typing_in_progress = True
        self.type_now_btn.config(state='disabled')
        
        def type_worker():
            try:
                success = self.keyboard.type_text(content, delay=30)
                if success:
                    self.root.after(0, lambda: self.status_label.config(text=f"✅ Typed {len(content)} characters"))
                else:
                    self.root.after(0, lambda: self.status_label.config(text="❌ Typing failed"))
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(text=f"❌ Error: {str(e)}"))
            finally:
                self.root.after(0, lambda: (
                    setattr(self, 'typing_in_progress', False),
                    self.type_now_btn.config(state='normal')
                ))
        
        threading.Thread(target=type_worker, daemon=True).start()
    
    def clear_clipboard(self):
        """Clear clipboard"""
        if self.clipboard.clear():
            self.status_label.config(text="✅ Clipboard cleared")
            self.refresh_clipboard()
        else:
            self.status_label.config(text="❌ Failed to clear clipboard")
    
    def save_clipboard_to_file(self):
        """Save clipboard content to file"""
        content = self.clipboard.get()
        if not content:
            messagebox.showwarning("Empty Clipboard", "Nothing to save - clipboard is empty!")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Clipboard Content",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_label.config(text=f"✅ Saved to {filename}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save file:\n{str(e)}")
    
    def refresh_history(self):
        """Refresh clipboard history"""
        try:
            history = self.clipboard.get_history()
            
            self.history_listbox.delete(0, 'end')
            
            if not history:
                self.history_listbox.insert(0, "(No history available)")
                return
            
            for i, entry in enumerate(reversed(history[-20:])):  # Show last 20 entries
                timestamp = entry.get('timestamp', 'Unknown')[:19]  # Remove microseconds
                preview = entry.get('preview', entry.get('content', ''))[:60]
                self.history_listbox.insert(0, f"{timestamp} - {preview}")
            
            self.status_label.config(text=f"History: {len(history)} entries")
            
        except Exception as e:
            self.status_label.config(text=f"History error: {str(e)}")
    
    def restore_from_history(self):
        """Restore selected history item to clipboard"""
        selection = self.history_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a history item first!")
            return
        
        try:
            index = selection[0]
            history = self.clipboard.get_history()
            
            if history:
                # Get the actual entry (accounting for reversed display)
                actual_index = len(history) - 1 - index
                if 0 <= actual_index < len(history):
                    content = history[actual_index]['content']
                    if self.clipboard.set(content):
                        self.status_label.config(text="✅ Restored from history")
                        self.refresh_clipboard()
                    else:
                        self.status_label.config(text="❌ Failed to restore")
        except Exception as e:
            messagebox.showerror("Restore Error", f"Failed to restore:\n{str(e)}")
    
    def clear_history(self):
        """Clear clipboard history"""
        if messagebox.askyesno("Clear History", "Are you sure you want to clear all clipboard history?"):
            try:
                self.clipboard.clear_history()
                self.refresh_history()
                self.status_label.config(text="✅ History cleared")
            except Exception as e:
                messagebox.showerror("Clear Error", f"Failed to clear history:\n{str(e)}")
    
    def update_status(self):
        """Update system status display"""
        try:
            self.status_text.config(state='normal')
            self.status_text.delete(1.0, 'end')
            
            status_info = []
            
            # Basic info
            status_info.append("🐾 CopyCat Status")
            status_info.append("=" * 40)
            status_info.append(f"Version: {__version__}")
            status_info.append("")
            
            # Dependencies
            status_info.append("Dependencies:")
            
            # Check xclip
            try:
                result = subprocess.run(['xclip', '-version'], capture_output=True, timeout=5)
                if result.returncode == 0:
                    status_info.append("  ✅ xclip - Clipboard access")
                else:
                    status_info.append("  ❌ xclip - Clipboard access (ERROR)")
            except:
                status_info.append("  ❌ xclip - Clipboard access (NOT FOUND)")
            
            # Check xdotool
            try:
                result = subprocess.run(['xdotool', '--version'], capture_output=True, timeout=5)
                if result.returncode == 0:
                    status_info.append("  ✅ xdotool - Virtual keyboard")
                else:
                    status_info.append("  ❌ xdotool - Virtual keyboard (ERROR)")
            except:
                status_info.append("  ❌ xdotool - Virtual keyboard (NOT FOUND)")
            
            # Check notify-send
            try:
                result = subprocess.run(['notify-send', '--version'], capture_output=True, timeout=5)
                status_info.append("  ✅ notify-send - Notifications")
            except:
                status_info.append("  ❌ notify-send - Notifications (NOT FOUND)")
            
            status_info.append("")
            
            # Virtual keyboard status
            kb_status = self.keyboard.get_status()
            status_info.append("Virtual Keyboard:")
            status_info.append(f"  Available: {'Yes' if kb_status['available'] else 'No'}")
            status_info.append(f"  Display Server: {kb_status['display_server']}")
            status_info.append(f"  Methods: {', '.join([k for k, v in kb_status['methods'].items() if v])}")
            
            status_info.append("")
            
            # Clipboard info
            clipboard_info = self.clipboard.get_clipboard_info()
            status_info.append("Current Clipboard:")
            status_info.append(f"  Has Content: {'Yes' if clipboard_info['has_content'] else 'No'}")
            if clipboard_info['has_content']:
                status_info.append(f"  Length: {clipboard_info['length']} characters")
                status_info.append(f"  Lines: {clipboard_info['lines']}")
                status_info.append(f"  Words: {clipboard_info['words']}")
            
            self.status_text.insert(1.0, '\n'.join(status_info))
            self.status_text.config(state='disabled')
            
        except Exception as e:
            self.status_text.config(state='normal')
            self.status_text.delete(1.0, 'end')
            self.status_text.insert(1.0, f"Error getting status: {str(e)}")
            self.status_text.config(state='disabled')
    
    def setup_config(self):
        """Setup user configuration"""
        try:
            # Run the CLI setup command
            subprocess.run([
                str(Path(__file__).parent / "copycat"),
                "--setup"
            ], check=True)
            
            messagebox.showinfo("Setup Complete", "User configuration has been created!")
            self.status_label.config(text="✅ Configuration setup complete")
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Setup Error", f"Failed to setup configuration:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Setup Error", f"Unexpected error:\n{str(e)}")
    
    # Template Management Methods
    def refresh_templates(self):
        """Refresh template list"""
        try:
            # Get current search and category filters
            search_term = self.template_search.get()
            category = self.template_category.get() if hasattr(self, 'template_category') else None
            
            # Get filtered templates
            if category and category != "All":
                templates = self.template_manager.get_templates(category=category, search=search_term)
            else:
                templates = self.template_manager.get_templates(search=search_term)
            
            # Update listbox
            self.templates_listbox.delete(0, 'end')
            self.current_templates = templates  # Store for reference
            
            for template in templates:
                display_name = f"{template['name']} ({template.get('category', 'uncategorized')})"
                self.templates_listbox.insert('end', display_name)
            
            if not templates:
                self.templates_listbox.insert('end', "No templates found")
            
            # Reset selection
            self.on_template_select(None)
            
            self.status_label.config(text=f"Templates: {len(templates)} found")
            
        except Exception as e:
            self.status_label.config(text=f"Template error: {str(e)}")
    
    def filter_templates(self, event=None):
        """Filter templates based on search and category"""
        self.refresh_templates()
    
    def on_template_select(self, event):
        """Handle template selection"""
        try:
            selection = self.templates_listbox.curselection()
            if not selection or not hasattr(self, 'current_templates'):
                # No selection or no templates
                self.template_name_label.config(text="Select a template...")
                self.template_desc_label.config(text="")
                self.template_preview.config(state='normal')
                self.template_preview.delete(1.0, 'end')
                self.template_preview.config(state='disabled')
                
                # Disable buttons
                self.use_template_btn.config(state='disabled')
                self.edit_template_btn.config(state='disabled')
                self.delete_template_btn.config(state='disabled')
                return
            
            # Get selected template
            index = selection[0]
            if index >= len(self.current_templates):
                return
            
            template = self.current_templates[index]
            
            # Update display
            self.template_name_label.config(text=template['name'])
            self.template_desc_label.config(text=template.get('description', ''))
            
            # Show template content
            self.template_preview.config(state='normal')
            self.template_preview.delete(1.0, 'end')
            
            content_lines = [
                f"Content:",
                template.get('content', ''),
                "",
                "Placeholders:"
            ]
            
            placeholders = template.get('placeholders', [])
            if placeholders:
                for placeholder in placeholders:
                    ph_type = placeholder.get('type', 'text')
                    required = "*" if placeholder.get('required') else ""
                    content_lines.append(f"  • {placeholder['name']}{required} ({ph_type}): {placeholder.get('description', '')}")
            else:
                content_lines.append("  (No placeholders)")
            
            content_lines.extend(["", f"Category: {template.get('category', 'uncategorized')}"])
            
            if template.get('tags'):
                content_lines.append(f"Tags: {', '.join(template['tags'])}")
            
            self.template_preview.insert(1.0, '\n'.join(content_lines))
            self.template_preview.config(state='disabled')
            
            # Enable buttons
            self.use_template_btn.config(state='normal')
            self.edit_template_btn.config(state='normal')
            self.delete_template_btn.config(state='normal')
            
        except Exception as e:
            self.status_label.config(text=f"Selection error: {str(e)}")
    
    def use_selected_template(self):
        """Use the selected template with user input"""
        try:
            selection = self.templates_listbox.curselection()
            if not selection or not hasattr(self, 'current_templates'):
                messagebox.showwarning("No Selection", "Please select a template first!")
                return
            
            template = self.current_templates[selection[0]]
            placeholders = template.get('placeholders', [])
            
            if not placeholders:
                # No placeholders, use template directly
                content = template.get('content', '')
                if self.clipboard.set(content):
                    self.status_label.config(text=f"✅ Template '{template['name']}' copied to clipboard")
                    self.refresh_clipboard()
                else:
                    self.status_label.config(text="❌ Failed to copy template")
                return
            
            # Create input dialog for placeholders
            self.create_template_input_dialog(template)
            
        except Exception as e:
            messagebox.showerror("Template Error", f"Failed to use template:\n{str(e)}")
    
    def create_template_input_dialog(self, template):
        """Create dialog for template placeholder input"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Fill Template: {template['name']}")
        dialog.geometry("500x400")
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Content frame
        content_frame = tk.Frame(dialog)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        tk.Label(content_frame, text=f"Template: {template['name']}", 
                font=('Segoe UI', 14, 'bold')).pack(anchor='w')
        tk.Label(content_frame, text=template.get('description', ''), 
                font=('Segoe UI', 10), fg='#666').pack(anchor='w', pady=(0, 10))
        
        # Placeholder inputs
        tk.Label(content_frame, text="Fill in the placeholders:", 
                font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Create scrollable frame for inputs
        canvas = tk.Canvas(content_frame, height=200)
        scrollbar = tk.Scrollbar(content_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Input fields
        input_vars = {}
        for i, placeholder in enumerate(template.get('placeholders', [])):
            row_frame = tk.Frame(scrollable_frame)
            row_frame.pack(fill='x', pady=5)
            
            # Label
            required_marker = " *" if placeholder.get('required') else ""
            label_text = f"{placeholder['name']}{required_marker}:"
            tk.Label(row_frame, text=label_text, font=('Segoe UI', 10)).pack(anchor='w')
            
            # Description
            if placeholder.get('description'):
                tk.Label(row_frame, text=placeholder['description'], 
                        font=('Segoe UI', 9), fg='#666').pack(anchor='w')
            
            # Input field
            if placeholder.get('type') == 'select':
                var = tk.StringVar()
                combo = ttk.Combobox(row_frame, textvariable=var, 
                                    values=placeholder.get('options', []))
                if placeholder.get('default'):
                    var.set(placeholder['default'])
                combo.pack(fill='x', pady=(2, 0))
            else:
                var = tk.StringVar()
                if placeholder.get('default'):
                    var.set(placeholder['default'])
                
                if placeholder.get('type') == 'sensitive':
                    entry = tk.Entry(row_frame, textvariable=var, show='*')
                else:
                    entry = tk.Entry(row_frame, textvariable=var)
                
                entry.pack(fill='x', pady=(2, 0))
            
            input_vars[placeholder['name']] = var
        
        # Action buttons
        buttons_frame = tk.Frame(content_frame)
        buttons_frame.pack(fill='x', pady=(20, 0))
        
        def apply_template():
            try:
                # Collect values
                values = {name: var.get() for name, var in input_vars.items()}
                
                # Process template
                result, errors = self.template_manager.process_template(template['name'], values)
                
                if errors:
                    messagebox.showerror("Validation Error", "\n".join(errors))
                    return
                
                # Copy to clipboard
                if self.clipboard.set(result):
                    self.status_label.config(text=f"✅ Template '{template['name']}' processed and copied")
                    self.refresh_clipboard()
                    dialog.destroy()
                else:
                    messagebox.showerror("Clipboard Error", "Failed to copy to clipboard")
                    
            except Exception as e:
                messagebox.showerror("Template Error", f"Failed to process template:\n{str(e)}")
        
        ModernButton(
            buttons_frame,
            text="✅ Apply Template",
            bg='#28a745',
            fg='white',
            command=apply_template
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            buttons_frame,
            text="❌ Cancel",
            bg='#6c757d',
            fg='white',
            command=dialog.destroy
        ).pack(side='left')
    
    def edit_selected_template(self):
        """Edit the selected template"""
        try:
            selection = self.templates_listbox.curselection()
            if not selection or not hasattr(self, 'current_templates'):
                messagebox.showwarning("No Selection", "Please select a template first!")
                return
            
            template = self.current_templates[selection[0]]
            
            # Switch to editor tab and populate form
            # Find the template notebook and select editor tab
            for child in self.notebook.winfo_children():
                if isinstance(child, tk.Frame):
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, ttk.Notebook):
                            grandchild.select(1)  # Select editor tab
                            break
            
            # Populate editor form
            self.editor_name.delete(0, 'end')
            self.editor_name.insert(0, template['name'])
            
            self.editor_description.delete(0, 'end')
            self.editor_description.insert(0, template.get('description', ''))
            
            self.editor_category.set(template.get('category', ''))
            
            self.editor_tags.delete(0, 'end')
            if template.get('tags'):
                self.editor_tags.insert(0, ', '.join(template['tags']))
            
            self.editor_content.delete(1.0, 'end')
            self.editor_content.insert(1.0, template.get('content', ''))
            
            # Analyze placeholders
            self.analyze_template_placeholders()
            
            self.status_label.config(text=f"Editing template: {template['name']}")
            
        except Exception as e:
            messagebox.showerror("Edit Error", f"Failed to edit template:\n{str(e)}")
    
    def delete_selected_template(self):
        """Delete the selected template"""
        try:
            selection = self.templates_listbox.curselection()
            if not selection or not hasattr(self, 'current_templates'):
                messagebox.showwarning("No Selection", "Please select a template first!")
                return
            
            template = self.current_templates[selection[0]]
            
            if messagebox.askyesno("Delete Template", f"Are you sure you want to delete '{template['name']}'?"):
                if self.template_manager.delete_template(template['name']):
                    self.status_label.config(text=f"✅ Deleted template: {template['name']}")
                    self.refresh_templates()
                else:
                    messagebox.showerror("Delete Error", "Failed to delete template")
            
        except Exception as e:
            messagebox.showerror("Delete Error", f"Failed to delete template:\n{str(e)}")
    
    def load_template_categories(self):
        """Load template categories for comboboxes"""
        try:
            categories = self.template_manager.get_categories()
            category_names = ['All'] + [cat['name'] for cat in categories]
            
            # Update category comboboxes
            if hasattr(self, 'template_category'):
                self.template_category['values'] = category_names
                self.template_category.set('All')
            
            if hasattr(self, 'editor_category'):
                editor_categories = [cat['name'] for cat in categories]
                self.editor_category['values'] = editor_categories
            
        except Exception as e:
            self.status_label.config(text=f"Category error: {str(e)}")
    
    def analyze_template_placeholders(self, event=None):
        """Analyze template content for placeholders"""
        try:
            content = self.editor_content.get(1.0, 'end-1c')
            placeholders = self.template_manager.extract_placeholders(content)
            
            self.placeholders_display.config(state='normal')
            self.placeholders_display.delete(1.0, 'end')
            
            if placeholders:
                self.placeholders_display.insert(1.0, 
                    f"Found {len(placeholders)} placeholders: {', '.join(placeholders)}")
            else:
                self.placeholders_display.insert(1.0, "No placeholders detected")
            
            self.placeholders_display.config(state='disabled')
            
        except Exception as e:
            pass  # Ignore errors during live analysis
    
    def save_template(self):
        """Save template from editor form"""
        try:
            name = self.editor_name.get().strip()
            description = self.editor_description.get().strip()
            category = self.editor_category.get().strip() or "custom"
            tags_text = self.editor_tags.get().strip()
            content = self.editor_content.get(1.0, 'end-1c').strip()
            
            if not name:
                messagebox.showerror("Validation Error", "Template name is required!")
                return
            
            if not content:
                messagebox.showerror("Validation Error", "Template content is required!")
                return
            
            # Parse tags
            tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()] if tags_text else []
            
            # Check if template exists (for update vs create)
            existing_template = self.template_manager.get_template(name)
            
            if existing_template:
                # Update existing template
                success = self.template_manager.update_template(
                    name,
                    description=description,
                    content=content,
                    category=category,
                    tags=tags
                )
                action = "updated"
            else:
                # Create new template
                success = self.template_manager.create_template(
                    name=name,
                    description=description,
                    content=content,
                    category=category,
                    tags=tags
                )
                action = "created"
            
            if success:
                self.status_label.config(text=f"✅ Template '{name}' {action}")
                self.refresh_templates()
                self.load_template_categories()
                messagebox.showinfo("Success", f"Template '{name}' has been {action}!")
            else:
                messagebox.showerror("Save Error", f"Failed to save template (may already exist)")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save template:\n{str(e)}")
    
    def clear_editor_form(self):
        """Clear the template editor form"""
        self.editor_name.delete(0, 'end')
        self.editor_description.delete(0, 'end')
        self.editor_category.set('')
        self.editor_tags.delete(0, 'end')
        self.editor_content.delete(1.0, 'end')
        
        self.placeholders_display.config(state='normal')
        self.placeholders_display.delete(1.0, 'end')
        self.placeholders_display.config(state='disabled')
        
        self.status_label.config(text="Form cleared")
    
    def import_templates(self):
        """Import templates from file"""
        filename = filedialog.askopenfilename(
            title="Import Templates",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                overwrite = messagebox.askyesno(
                    "Import Options", 
                    "Overwrite existing templates with same names?"
                )
                
                count, errors = self.template_manager.import_templates(filename, overwrite=overwrite)
                
                if errors:
                    error_msg = f"Imported {count} templates with errors:\n" + "\n".join(errors[:5])
                    if len(errors) > 5:
                        error_msg += f"\n... and {len(errors) - 5} more errors"
                    messagebox.showwarning("Import Warnings", error_msg)
                else:
                    messagebox.showinfo("Import Success", f"Successfully imported {count} templates!")
                
                self.refresh_templates()
                self.load_template_categories()
                self.status_label.config(text=f"✅ Imported {count} templates")
                
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import templates:\n{str(e)}")
    
    def export_templates(self):
        """Export templates to file"""
        filename = filedialog.asksaveasfilename(
            title="Export Templates",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Ask if user wants to export specific templates or all
                export_all = messagebox.askyesno(
                    "Export Options", 
                    "Export all templates?\n\nClick 'No' to select specific templates."
                )
                
                if export_all:
                    success = self.template_manager.export_templates(filename)
                    if success:
                        messagebox.showinfo("Export Success", "All templates exported successfully!")
                        self.status_label.config(text=f"✅ Templates exported to {filename}")
                    else:
                        messagebox.showerror("Export Error", "Failed to export templates")
                else:
                    # TODO: Create template selection dialog
                    messagebox.showinfo("Not Implemented", "Selective export not yet implemented. Exporting all templates.")
                    success = self.template_manager.export_templates(filename)
                    if success:
                        messagebox.showinfo("Export Success", "All templates exported successfully!")
                        self.status_label.config(text=f"✅ Templates exported to {filename}")
                    else:
                        messagebox.showerror("Export Error", "Failed to export templates")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export templates:\n{str(e)}")
    
    def refresh_analytics(self):
        """Refresh template usage analytics"""
        try:
            stats = self.template_manager.get_usage_statistics()
            
            self.analytics_text.config(state='normal')
            self.analytics_text.delete(1.0, 'end')
            
            analytics_content = [
                "📊 Template Usage Analytics",
                "=" * 50,
                "",
                "📈 Overview:",
                f"  Total Templates: {stats['total_templates']}",
                f"  Used Templates: {stats['used_templates']}",
                f"  Usage Rate: {stats['usage_rate']:.1f}%",
                "",
                "🏆 Most Used Templates:"
            ]
            
            if stats['most_used']:
                for name, count in stats['most_used']:
                    analytics_content.append(f"  • {name}: {count} uses")
            else:
                analytics_content.append("  (No usage data yet)")
            
            analytics_content.extend([
                "",
                "📂 Category Statistics:"
            ])
            
            for category, cat_stats in stats['category_stats'].items():
                usage_rate = (cat_stats['used'] / cat_stats['total'] * 100) if cat_stats['total'] > 0 else 0
                analytics_content.append(
                    f"  • {category}: {cat_stats['used']}/{cat_stats['total']} used ({usage_rate:.1f}%)"
                )
            
            if stats.get('last_backup'):
                analytics_content.extend([
                    "",
                    f"💾 Last Backup: {stats['last_backup'][:19]}"
                ])
            
            self.analytics_text.insert(1.0, '\n'.join(analytics_content))
            self.analytics_text.config(state='disabled')
            
            self.status_label.config(text="✅ Analytics refreshed")
            
        except Exception as e:
            self.analytics_text.config(state='normal')
            self.analytics_text.delete(1.0, 'end')
            self.analytics_text.insert(1.0, f"Error loading analytics: {str(e)}")
        self.analytics_text.config(state='disabled')
    
    def create_template_from_clipboard(self):
        """Create a template from current clipboard content"""
        try:
            content = self.clipboard.get()
            if not content:
                messagebox.showwarning("Empty Clipboard", "Nothing to create template from - clipboard is empty!")
                return
            
            # Analyze content to suggest template properties
            analysis = self.data_handler.analyze_content(content)
            primary_type = analysis.get('primary_type', 'text')
            
            # Create template creation dialog
            self.create_template_creation_dialog(content, analysis)
            
        except Exception as e:
            messagebox.showerror("Template Creation Error", f"Failed to create template:\n{str(e)}")
    
    def create_template_creation_dialog(self, content, analysis):
        """Create dialog for creating template from clipboard content"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Template from Clipboard")
        dialog.geometry("600x500")
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors['card_bg'])
        self.register_themable(dialog, 'card_bg')
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Content frame
        content_frame = self.themed_frame(dialog, color_key='card_bg')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Header
        header_label = tk.Label(
            content_frame,
            text="Create Template from Clipboard Content",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        header_label.pack(anchor='w')
        self.register_themable(header_label, 'card_bg', 'text_primary')
        detected_label = tk.Label(
            content_frame,
            text=f"Detected type: {analysis['primary_type'].title()}",
            font=('Segoe UI', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        )
        detected_label.pack(anchor='w', pady=(0, 10))
        self.register_themable(detected_label, 'card_bg', 'text_secondary')
        
        # Template form
        form_frame = self.themed_frame(content_frame, color_key='card_bg')
        form_frame.pack(fill='x', pady=(0, 10))
        
        # Name
        name_label = tk.Label(
            form_frame,
            text="Template Name:",
            font=('Segoe UI', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        name_label.grid(row=0, column=0, sticky='w', pady=2)
        self.register_themable(name_label, 'card_bg', 'text_primary')
        name_entry = tk.Entry(form_frame, font=('Segoe UI', 10), width=40)
        name_entry.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=2)
        
        # Suggest name based on content type
        primary_type = analysis.get('primary_type', 'text')
        suggested_name = f"{primary_type}-template-{int(time.time())}"
        name_entry.insert(0, suggested_name)
        
        # Description
        desc_label = tk.Label(
            form_frame,
            text="Description:",
            font=('Segoe UI', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        desc_label.grid(row=1, column=0, sticky='w', pady=2)
        self.register_themable(desc_label, 'card_bg', 'text_primary')
        desc_entry = tk.Entry(form_frame, font=('Segoe UI', 10), width=50)
        desc_entry.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=2)
        
        # Suggest description
        suggested_desc = f"Template created from {primary_type} content"
        if analysis.get('metadata', {}).get('service'):
            suggested_desc += f" ({analysis['metadata']['service']})"
        desc_entry.insert(0, suggested_desc)
        
        # Category
        category_label = tk.Label(
            form_frame,
            text="Category:",
            font=('Segoe UI', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        category_label.grid(row=2, column=0, sticky='w', pady=2)
        self.register_themable(category_label, 'card_bg', 'text_primary')
        category_combo = ttk.Combobox(form_frame, font=('Segoe UI', 10), width=20)
        category_combo.grid(row=2, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # Load categories and set default
        try:
            categories = self.template_manager.get_categories()
            category_names = [cat['name'] for cat in categories]
            category_combo['values'] = category_names
            
            # Suggest category based on content type
            category_mapping = {
                'json': 'development',
                'xml': 'development', 
                'sql': 'database',
                'api_key': 'security',
                'email': 'personal',
                'url': 'development',
                'code': 'development'
            }
            suggested_category = category_mapping.get(primary_type, 'custom')
            if suggested_category in category_names:
                category_combo.set(suggested_category)
            else:
                category_combo.set('custom')
        except:
            category_combo.set('custom')
        
        # Tags
        tags_label = tk.Label(
            form_frame,
            text="Tags (comma-separated):",
            font=('Segoe UI', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        tags_label.grid(row=3, column=0, sticky='w', pady=2)
        self.register_themable(tags_label, 'card_bg', 'text_primary')
        tags_entry = tk.Entry(form_frame, font=('Segoe UI', 10), width=50)
        tags_entry.grid(row=3, column=1, sticky='ew', padx=(10, 0), pady=2)
        
        # Suggest tags
        suggested_tags = [primary_type, 'auto-generated']
        if analysis.get('metadata', {}).get('service'):
            suggested_tags.append(analysis['metadata']['service'])
        tags_entry.insert(0, ', '.join(suggested_tags))
        
        form_frame.columnconfigure(1, weight=1)
        
        # Content preview and editing
        content_label = tk.Label(
            content_frame,
            text="Template Content (you can edit this):",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        content_label.pack(anchor='w', pady=(10, 5))
        self.register_themable(content_label, 'card_bg', 'text_primary')

        content_text = self.themed_scrolled_text(
            content_frame,
            height=10,
            wrap='word',
            font=('Consolas', 9)
        )
        content_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # Insert content (use display_content if available for safety)
        display_content = analysis.get('display_content', content)
        content_text.insert(1.0, display_content)
        
        # Analysis info
        info_frame = self.themed_frame(content_frame, color_key='card_bg')
        info_frame.pack(fill='x', pady=(0, 10))

        info_label = tk.Label(
            info_frame,
            text="Content Analysis:",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_primary']
        )
        info_label.pack(anchor='w')
        self.register_themable(info_label, 'card_bg', 'text_primary')

        analysis_info = self.themed_text(
            info_frame,
            height=3,
            wrap='word',
            font=('Segoe UI', 9),
            state='disabled',
            bg_key='muted_bg'
        )
        analysis_info.pack(fill='x', pady=(5, 0))
        
        # Show analysis info
        analysis_info.config(state='normal')
        info_lines = [
            f"Type: {analysis['primary_type'].title()}, Confidence: {analysis['confidence']:.1%}",
            f"Length: {analysis['original_length']} chars, Security: {analysis.get('security_level', 'none').title()}"
        ]
        if analysis.get('suggested_templates'):
            suggestions = [s['name'] for s in analysis['suggested_templates'][:3]]
            info_lines.append(f"Related templates: {', '.join(suggestions)}")
        analysis_info.insert(1.0, '\n'.join(info_lines))
        analysis_info.config(state='disabled')
        
        # Action buttons
        buttons_frame = self.themed_frame(content_frame, color_key='card_bg')
        buttons_frame.pack(fill='x')
        
        def create_template():
            try:
                name = name_entry.get().strip()
                description = desc_entry.get().strip()
                category = category_combo.get().strip() or "custom"
                tags_text = tags_entry.get().strip()
                template_content = content_text.get(1.0, 'end-1c').strip()
                
                if not name:
                    messagebox.showerror("Validation Error", "Template name is required!")
                    return
                
                if not template_content:
                    messagebox.showerror("Validation Error", "Template content cannot be empty!")
                    return
                
                # Parse tags
                tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()] if tags_text else []
                
                # Create template using data handler method
                success = self.data_handler.create_template_from_content(
                    template_content, name, description
                )
                
                if success:
                    # Update with additional properties
                    self.template_manager.update_template(
                        name,
                        category=category,
                        tags=tags
                    )
                    
                    messagebox.showinfo("Template Created", f"Template '{name}' has been created successfully!")
                    self.refresh_templates()
                    self.load_template_categories()
                    self.status_label.config(text=f"✅ Created template: {name}")
                    dialog.destroy()
                else:
                    messagebox.showerror("Creation Error", "Failed to create template (name may already exist)")
                    
            except Exception as e:
                messagebox.showerror("Creation Error", f"Failed to create template:\n{str(e)}")
        
        ModernButton(
            buttons_frame,
            text="✨ Create Template",
            bg='#28a745',
            fg='white',
            command=create_template
        ).pack(side='left', padx=(0, 10))
        
        ModernButton(
            buttons_frame,
            text="❌ Cancel",
            bg='#6c757d',
            fg='white',
            command=dialog.destroy
        ).pack(side='left')
    
    def on_closing(self):
        """Handle window closing"""
        if self.typing_in_progress:
            if messagebox.askokcancel("Quit", "Typing operation in progress. Really quit?"):
                self.countdown_active = False
                self.root.quit()
        else:
            self.root.quit()
    
    def run(self):
        """Start the GUI"""
        # Load initial data
        self.refresh_history()
        self.update_status()
        
        # Load template system data after GUI is fully initialized
        if hasattr(self, 'template_manager'):
            try:
                self.load_template_categories()
                self.refresh_templates()
                self.refresh_analytics()
                self.status_label.config(text="✅ Advanced templates ready")
            except Exception as e:
                self.status_label.config(text=f"Template warning: {str(e)}")
        
        # Start main loop
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        app = CopyCatGUI()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
