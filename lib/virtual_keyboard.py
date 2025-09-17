#!/usr/bin/env python3
"""
🎹 Virtual Keyboard Module

Virtual keyboard implementation using xdotool to simulate typing and bypass 
paste restrictions in web-based UIs like Warp settings.

Made with ❤️ by Pink Pixel
"""

import subprocess
import time
import re
import random
from typing import Optional, Dict, List

class VirtualKeyboard:
    """Handles virtual keyboard operations to bypass paste restrictions"""
    
    def __init__(self):
        self.typing_method = 'xdotool'  # Default method
        self.available_methods = self._detect_methods()
        
        # Special character mappings for xdotool
        self.special_chars = {
            '\n': 'Return',
            '\t': 'Tab',
            ' ': 'space',
            '!': 'exclam',
            '@': 'at',
            '#': 'numbersign',
            '$': 'dollar',
            '%': 'percent',
            '^': 'asciicircum',
            '&': 'ampersand',
            '*': 'asterisk',
            '(': 'parenleft',
            ')': 'parenright',
            '-': 'minus',
            '_': 'underscore',
            '=': 'equal',
            '+': 'plus',
            '[': 'bracketleft',
            ']': 'bracketright',
            '{': 'braceleft',
            '}': 'braceright',
            '\\': 'backslash',
            '|': 'bar',
            ';': 'semicolon',
            ':': 'colon',
            "'": 'apostrophe',
            '"': 'quotedbl',
            ',': 'comma',
            '.': 'period',
            '<': 'less',
            '>': 'greater',
            '/': 'slash',
            '?': 'question',
            '`': 'grave',
            '~': 'asciitilde'
        }
        
        # Human-like typing patterns
        self.typing_patterns = {
            'burst_length': (3, 8),      # Characters per burst
            'burst_pause': (100, 300),   # Pause between bursts (ms)
            'char_variance': (5, 15),    # Random delay variance per char
            'punctuation_pause': (50, 150),  # Extra pause after punctuation
        }
    
    def _detect_methods(self) -> Dict[str, bool]:
        """Detect available typing methods"""
        methods = {}
        
        # Test xdotool
        try:
            result = subprocess.run(
                ['xdotool', '--version'],
                capture_output=True,
                timeout=5
            )
            methods['xdotool'] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            methods['xdotool'] = False
        
        # Test ydotool (Wayland alternative)
        try:
            result = subprocess.run(
                ['ydotool', '--help'],
                capture_output=True,
                timeout=5
            )
            methods['ydotool'] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            methods['ydotool'] = False
        
        return methods
    
    def is_available(self) -> bool:
        """Check if virtual keyboard is available"""
        return any(self.available_methods.values())
    
    def get_status(self) -> Dict[str, any]:
        """Get virtual keyboard status"""
        return {
            'available': self.is_available(),
            'methods': self.available_methods,
            'current_method': self.typing_method,
            'display_server': self._detect_display_server()
        }
    
    def _detect_display_server(self) -> str:
        """Detect display server (X11 or Wayland)"""
        if 'WAYLAND_DISPLAY' in subprocess.os.environ:
            return 'wayland'
        elif 'DISPLAY' in subprocess.os.environ:
            return 'x11'
        else:
            return 'unknown'
    
    def type_text(self, text: str, delay: int = 50, human_like: bool = True) -> bool:
        """
        Type text using virtual keyboard
        
        Args:
            text: Text to type
            delay: Base delay between keystrokes in milliseconds
            human_like: Whether to use human-like typing patterns
        """
        if not self.is_available():
            print("❌ No virtual keyboard method available")
            return False
        
        if not text:
            return True
        
        # Choose best method based on display server
        display_server = self._detect_display_server()
        
        if display_server == 'wayland' and self.available_methods.get('ydotool'):
            return self._type_with_ydotool(text, delay, human_like)
        elif display_server == 'x11' and self.available_methods.get('xdotool'):
            return self._type_with_xdotool(text, delay, human_like)
        elif self.available_methods.get('xdotool'):
            return self._type_with_xdotool(text, delay, human_like)
        elif self.available_methods.get('ydotool'):
            return self._type_with_ydotool(text, delay, human_like)
        else:
            print("❌ No suitable virtual keyboard method found")
            return False
    
    def _type_with_xdotool(self, text: str, delay: int, human_like: bool) -> bool:
        """Type using xdotool"""
        try:
            # For very long text, break into chunks to avoid command line limits
            chunk_size = 1000  # Characters per chunk
            
            if len(text) > chunk_size:
                return self._type_in_chunks(text, chunk_size, delay, human_like, 'xdotool')
            
            if human_like:
                return self._type_human_like_xdotool(text, delay)
            else:
                return self._type_simple_xdotool(text, delay)
                
        except Exception as e:
            print(f"❌ Error with xdotool: {e}")
            return False
    
    def _type_simple_xdotool(self, text: str, delay: int) -> bool:
        """Simple typing with xdotool"""
        # Escape text for xdotool
        escaped_text = self._escape_for_xdotool(text)
        
        cmd = ['xdotool', 'type', '--delay', str(delay), escaped_text]
        
        try:
            result = subprocess.run(cmd, timeout=30, capture_output=True)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print("❌ Typing timeout - text may have been too long")
            return False
    
    def _type_human_like_xdotool(self, text: str, delay: int) -> bool:
        """Human-like typing with xdotool"""
        try:
            i = 0
            while i < len(text):
                # Determine burst length
                burst_len = random.randint(*self.typing_patterns['burst_length'])
                burst_text = text[i:i + burst_len]
                
                # Type burst
                for char in burst_text:
                    if not self._type_single_char_xdotool(char, delay):
                        return False
                    
                    # Random variance in delay
                    if len(burst_text) > 1:  # Only add variance for multi-char bursts
                        variance = random.randint(*self.typing_patterns['char_variance'])
                        time.sleep(variance / 1000.0)
                
                i += burst_len
                
                # Pause between bursts (except at end)
                if i < len(text):
                    burst_pause = random.randint(*self.typing_patterns['burst_pause'])
                    time.sleep(burst_pause / 1000.0)
            
            return True
            
        except Exception as e:
            print(f"❌ Error in human-like typing: {e}")
            return False
    
    def _type_single_char_xdotool(self, char: str, base_delay: int) -> bool:
        """Type a single character with xdotool"""
        try:
            # Handle special characters
            if char in self.special_chars:
                cmd = ['xdotool', 'key', self.special_chars[char]]
            else:
                # For regular characters, use type
                escaped_char = self._escape_for_xdotool(char)
                cmd = ['xdotool', 'type', '--delay', str(base_delay), escaped_char]
            
            result = subprocess.run(cmd, timeout=5, capture_output=True)
            
            # Extra pause after punctuation for realism
            if char in '.,!?;:':
                pause = random.randint(*self.typing_patterns['punctuation_pause'])
                time.sleep(pause / 1000.0)
            
            return result.returncode == 0
            
        except Exception:
            return False
    
    def _escape_for_xdotool(self, text: str) -> str:
        """Escape text for xdotool safety"""
        # Remove or escape problematic characters
        # xdotool type handles most characters well, but we need to be careful with some
        problematic = ['\\', '"', "'", '$', '`']
        
        for char in problematic:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    def _type_with_ydotool(self, text: str, delay: int, human_like: bool) -> bool:
        """Type using ydotool (for Wayland)"""
        try:
            # ydotool works differently than xdotool
            cmd = ['ydotool', 'type', '--key-delay', str(delay)]
            
            if human_like:
                # For ydotool, we'll simulate human-like typing by varying delays
                return self._type_human_like_ydotool(text, delay)
            else:
                cmd.append(text)
                result = subprocess.run(cmd, timeout=30, capture_output=True)
                return result.returncode == 0
                
        except Exception as e:
            print(f"❌ Error with ydotool: {e}")
            return False
    
    def _type_human_like_ydotool(self, text: str, base_delay: int) -> bool:
        """Human-like typing with ydotool"""
        try:
            # Type in small bursts with varying delays
            i = 0
            while i < len(text):
                burst_len = random.randint(*self.typing_patterns['burst_length'])
                burst_text = text[i:i + burst_len]
                
                # Vary the delay for this burst
                burst_delay = base_delay + random.randint(-10, 20)
                burst_delay = max(10, burst_delay)  # Minimum delay
                
                cmd = ['ydotool', 'type', '--key-delay', str(burst_delay), burst_text]
                result = subprocess.run(cmd, timeout=10, capture_output=True)
                
                if result.returncode != 0:
                    return False
                
                i += burst_len
                
                # Pause between bursts
                if i < len(text):
                    pause = random.randint(*self.typing_patterns['burst_pause'])
                    time.sleep(pause / 1000.0)
            
            return True
            
        except Exception as e:
            print(f"❌ Error in ydotool human-like typing: {e}")
            return False
    
    def _type_in_chunks(self, text: str, chunk_size: int, delay: int, human_like: bool, method: str) -> bool:
        """Type long text in chunks to avoid command line limits"""
        print(f"📝 Typing {len(text)} characters in chunks...")
        
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            print(f"📝 Typing chunk {i // chunk_size + 1}...")
            
            if method == 'xdotool':
                success = self._type_with_xdotool(chunk, delay, human_like)
            else:
                success = self._type_with_ydotool(chunk, delay, human_like)
            
            if not success:
                print(f"❌ Failed to type chunk {i // chunk_size + 1}")
                return False
            
            # Small pause between chunks
            if i + chunk_size < len(text):
                time.sleep(0.2)
        
        return True
    
    def type_special_sequence(self, sequence: str) -> bool:
        """Type special key sequences (e.g., 'ctrl+a', 'alt+Tab')"""
        if not self.available_methods.get('xdotool', False):
            return False
        
        try:
            cmd = ['xdotool', 'key', sequence]
            result = subprocess.run(cmd, timeout=5, capture_output=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def get_active_window_info(self) -> Optional[Dict[str, str]]:
        """Get information about the active window"""
        if not self.available_methods.get('xdotool', False):
            return None
        
        try:
            # Get active window ID
            result = subprocess.run(
                ['xdotool', 'getactivewindow'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return None
            
            window_id = result.stdout.strip()
            
            # Get window name
            result = subprocess.run(
                ['xdotool', 'getwindowname', window_id],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            window_name = result.stdout.strip() if result.returncode == 0 else "Unknown"
            
            return {
                'id': window_id,
                'name': window_name
            }
            
        except Exception:
            return None
    
    def focus_window_by_name(self, name: str) -> bool:
        """Focus window by name (useful for automation)"""
        if not self.available_methods.get('xdotool', False):
            return False
        
        try:
            cmd = ['xdotool', 'search', '--name', name, 'windowactivate']
            result = subprocess.run(cmd, timeout=5, capture_output=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def simulate_paste(self, text: str) -> bool:
        """
        Simulate paste operation by:
        1. Setting clipboard
        2. Typing Ctrl+V
        
        This is a fallback if direct typing fails
        """
        try:
            # Import here to avoid circular imports
            import sys
            import os
            sys.path.insert(0, os.path.dirname(__file__))
            from clipboard_core import ClipboardManager
            
            clipboard = ClipboardManager()
            
            # Save current clipboard
            original_content = clipboard.get()
            
            # Set new content
            if not clipboard.set(text):
                return False
            
            # Type Ctrl+V
            success = self.type_special_sequence('ctrl+v')
            
            # Restore original clipboard after a short delay
            if original_content:
                time.sleep(0.5)
                clipboard.set(original_content)
            
            return success
            
        except Exception:
            return False