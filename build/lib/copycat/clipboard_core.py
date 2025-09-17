#!/usr/bin/env python3
"""
🐾 CopyCat Clipboard Core Module

Core clipboard management functionality including read/write operations,
history tracking, and cross-platform clipboard access.

Made with ❤️ by Pink Pixel
"""

import subprocess
import json
import os
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

class ClipboardManager:
    """Manages clipboard operations and history"""
    
    def __init__(self):
        self.history_file = Path.home() / ".local/share/copycat/history.json"
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Maximum history entries
        self.max_history = 100
        
        # Load existing history
        self.history = self._load_history()
        
        # Sensitive data patterns to exclude from history
        self.sensitive_patterns = [
            r'(?i)password',
            r'(?i)token',
            r'(?i)key',
            r'(?i)secret',
            r'(?i)auth',
            r'sk-[a-zA-Z0-9]{48}',  # OpenAI API keys
            r'[a-zA-Z0-9+/]{40}',   # Base64 encoded secrets
        ]
    
    def get(self) -> Optional[str]:
        """Get current clipboard content"""
        try:
            # Try primary selection first (Linux middle-click)
            result = subprocess.run(
                ['xclip', '-selection', 'clipboard', '-o'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout:
                content = result.stdout
                # Add to history if it's new
                self._add_to_history(content)
                return content
            
            return None
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to alternative methods
            return self._get_fallback()
    
    def _get_fallback(self) -> Optional[str]:
        """Fallback clipboard access methods"""
        methods = [
            ['xsel', '-b', '-o'],  # xsel clipboard
            ['xsel', '-p', '-o'],  # xsel primary
            ['pbpaste'],           # macOS (in case of cross-platform use)
        ]
        
        for method in methods:
            try:
                result = subprocess.run(
                    method,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout:
                    return result.stdout
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        return None
    
    def set(self, content: str) -> bool:
        """Set clipboard content"""
        try:
            # Set both clipboard and primary selection
            process = subprocess.Popen(
                ['xclip', '-selection', 'clipboard'],
                stdin=subprocess.PIPE,
                text=True
            )
            process.communicate(input=content)
            
            if process.returncode == 0:
                # Also set primary selection
                try:
                    process2 = subprocess.Popen(
                        ['xclip', '-selection', 'primary'],
                        stdin=subprocess.PIPE,
                        text=True
                    )
                    process2.communicate(input=content)
                except:
                    pass  # Primary selection is optional
                
                # Add to history
                self._add_to_history(content)
                return True
            
            return False
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            return self._set_fallback(content)
    
    def _set_fallback(self, content: str) -> bool:
        """Fallback clipboard set methods"""
        methods = [
            ['xsel', '-b', '-i'],  # xsel clipboard
            ['pbcopy'],            # macOS
        ]
        
        for method in methods:
            try:
                process = subprocess.Popen(
                    method,
                    stdin=subprocess.PIPE,
                    text=True
                )
                process.communicate(input=content)
                if process.returncode == 0:
                    self._add_to_history(content)
                    return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        return False
    
    def clear(self) -> bool:
        """Clear clipboard content"""
        try:
            # Clear both selections
            for selection in ['clipboard', 'primary']:
                subprocess.run(
                    ['xclip', '-selection', selection],
                    input='',
                    text=True,
                    check=True
                )
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            return self._clear_fallback()
    
    def _clear_fallback(self) -> bool:
        """Fallback clipboard clear methods"""
        methods = [
            ['xsel', '-b', '-c'],  # xsel clipboard
            ['xsel', '-p', '-c'],  # xsel primary
        ]
        
        for method in methods:
            try:
                subprocess.run(method, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        return True  # Best effort
    
    def _add_to_history(self, content: str):
        """Add content to clipboard history"""
        if not content or len(content.strip()) == 0:
            return
        
        # Don't add sensitive data to history
        if self._is_sensitive(content):
            return
        
        # Create content hash to avoid duplicates
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Check if already in recent history (last 5 entries)
        recent_hashes = [entry.get('hash') for entry in self.history[-5:]]
        if content_hash in recent_hashes:
            return
        
        # Create history entry
        entry = {
            'content': content,
            'hash': content_hash,
            'timestamp': datetime.now().isoformat(),
            'length': len(content),
            'preview': content[:50] + ('...' if len(content) > 50 else '')
        }
        
        # Add to history
        self.history.append(entry)
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        # Save history
        self._save_history()
    
    def _is_sensitive(self, content: str) -> bool:
        """Check if content appears to be sensitive data"""
        for pattern in self.sensitive_patterns:
            if re.search(pattern, content):
                return True
        
        # Check for long strings that might be tokens/keys
        if len(content) > 40 and re.match(r'^[a-zA-Z0-9+/=]+$', content):
            return True
        
        return False
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get clipboard history"""
        return self.history.copy()
    
    def clear_history(self):
        """Clear clipboard history"""
        self.history = []
        self._save_history()
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load history from file"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('history', [])
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load clipboard history: {e}")
        
        return []
    
    def _save_history(self):
        """Save history to file"""
        try:
            data = {
                'version': '1.0',
                'last_updated': datetime.now().isoformat(),
                'history': self.history
            }
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except IOError as e:
            print(f"Warning: Could not save clipboard history: {e}")
    
    def search_history(self, query: str) -> List[Dict[str, Any]]:
        """Search clipboard history"""
        if not query:
            return self.history
        
        query_lower = query.lower()
        results = []
        
        for entry in self.history:
            if query_lower in entry['content'].lower():
                results.append(entry)
        
        return results
    
    def get_history_entry(self, index: int) -> Optional[str]:
        """Get specific history entry content"""
        try:
            if 0 <= index < len(self.history):
                return self.history[index]['content']
        except (IndexError, KeyError):
            pass
        
        return None
    
    def restore_from_history(self, index: int) -> bool:
        """Restore clipboard from history entry"""
        content = self.get_history_entry(index)
        if content:
            return self.set(content)
        return False
    
    def get_clipboard_info(self) -> Dict[str, Any]:
        """Get comprehensive clipboard information"""
        content = self.get()
        
        info = {
            'has_content': bool(content),
            'length': len(content) if content else 0,
            'lines': content.count('\n') + 1 if content else 0,
            'words': len(content.split()) if content else 0,
            'is_json': False,
            'is_url': False,
            'is_email': False,
            'is_code': False,
            'preview': content[:100] + ('...' if len(content or '') > 100 else '') if content else ''
        }
        
        if content:
            # Detect content types
            info['is_json'] = self._is_json(content)
            info['is_url'] = self._is_url(content)
            info['is_email'] = self._is_email(content)
            info['is_code'] = self._is_code(content)
        
        return info
    
    def _is_json(self, content: str) -> bool:
        """Check if content is valid JSON"""
        try:
            json.loads(content)
            return True
        except (json.JSONDecodeError, ValueError):
            return False
    
    def _is_url(self, content: str) -> bool:
        """Check if content is a URL"""
        url_pattern = r'^https?://[^\s]+$'
        return bool(re.match(url_pattern, content.strip()))
    
    def _is_email(self, content: str) -> bool:
        """Check if content is an email"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, content.strip()))
    
    def _is_code(self, content: str) -> bool:
        """Check if content appears to be code"""
        code_indicators = [
            '{', '}', '(', ')',
            'function', 'class', 'def', 'import',
            '#!/', '<?', '<script', 'SELECT', 'FROM'
        ]
        
        content_lower = content.lower()
        indicator_count = sum(1 for indicator in code_indicators if indicator.lower() in content_lower)
        
        # If we have multiple code indicators, likely code
        return indicator_count >= 2
