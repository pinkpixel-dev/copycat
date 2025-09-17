#!/usr/bin/env python3
"""
🔍 Data Handlers Module

Special data type detection and handling for different content formats
including JSON, API keys, URLs, and more.

Made with ❤️ by Pink Pixel
"""

import json
import re
import base64
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse
import xml.etree.ElementTree as ET


class DataHandler:
    """Handles detection and processing of various data types"""

    def __init__(self, template_manager=None):
        self.template_manager = template_manager
        # API key patterns for different services
        self.api_key_patterns = {
            "openai": r"sk-[a-zA-Z0-9]{48}",
            "anthropic": r"sk-ant-api03-[a-zA-Z0-9_-]{95}",
            "github": r"ghp_[a-zA-Z0-9]{36}",
            "google": r"AIza[0-9A-Za-z_-]{35}",
            "aws_access": r"AKIA[0-9A-Z]{16}",
            "stripe": r"sk_live_[0-9a-zA-Z]{24}",
            "slack": r"xoxb-[0-9]{11}-[0-9]{11}-[a-zA-Z0-9]{24}",
            "discord": r"[MN][A-Za-z\d]{23}\.[A-Za-z\d_-]{6}\.[A-Za-z\d_-]{27}",
            "jwt": r"eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
        }

        # URL patterns
        self.url_patterns = {
            "http": r'https?://[^\s<>"]+',
            "ftp": r'ftp://[^\s<>"]+',
            "file": r'file://[^\s<>"]+',
            "ssh": r'ssh://[^\s<>"]+',
        }

        # Email pattern
        self.email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

        # Phone patterns (various formats)
        self.phone_patterns = [
            r"\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}",  # US
            r"\+?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}",  # International
        ]

        # Code patterns
        self.code_patterns = {
            "json": r"^\s*[\{\[].*[\}\]]\s*$",
            "xml": r"^\s*<.*>\s*$",
            "yaml": r"^[a-zA-Z_][a-zA-Z0-9_]*:\s*.*",
            "sql": r"(?i)^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)",
            "dockerfile": r"^\s*FROM\s+[a-zA-Z0-9/:.-]+",
            "shell": r"^\s*#!/.*",
            "python": r"^\s*(import|from|def|class|if __name__)",
            "javascript": r"^\s*(function|const|let|var|import|export)",
            "html": r"^\s*<!DOCTYPE|^\s*<html",
            "css": r"^\s*[.#]?[a-zA-Z0-9-_]+\s*\{",
        }

    def analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze content and return detailed information about its type and properties"""
        if not content:
            return {"type": "empty", "confidence": 1.0}

        analysis = {
            "original_length": len(content),
            "lines": content.count("\n") + 1,
            "words": len(content.split()),
            "detected_types": [],
            "primary_type": "text",
            "confidence": 0.0,
            "metadata": {},
            "sensitive": False,
        }

        # Run all detectors
        detectors = [
            self._detect_api_key,
            self._detect_json,
            self._detect_xml,
            self._detect_url,
            self._detect_email,
            self._detect_phone,
            self._detect_code,
            self._detect_base64,
            self._detect_hash,
            self._detect_ip_address,
            self._detect_credit_card,
            self._detect_coordinates,
        ]

        for detector in detectors:
            result = detector(content)
            if result:
                analysis["detected_types"].append(result)

        # Track sensitivity across all detectors
        analysis["sensitive"] = any(
            detector_result.get("sensitive", False)
            for detector_result in analysis["detected_types"]
        )

        # Determine primary type (highest confidence)
        if analysis["detected_types"]:
            primary = max(
                analysis["detected_types"], key=lambda x: x.get("confidence", 0)
            )
            analysis["primary_type"] = primary["type"]
            analysis["confidence"] = primary["confidence"]

            metadata = dict(primary.get("metadata", {}))
            if primary.get("sensitive"):
                metadata.setdefault("sensitive", True)
                analysis["sensitive"] = True

            analysis["metadata"] = metadata

        return analysis

    def _detect_api_key(self, content: str) -> Optional[Dict[str, Any]]:
        """Detect API keys from various services"""
        content_clean = content.strip()

        for service, pattern in self.api_key_patterns.items():
            if re.search(pattern, content_clean):
                return {
                    "type": "api_key",
                    "service": service,
                    "confidence": 0.95,
                    "sensitive": True,
                    "metadata": {
                        "service": service,
                        "masked": content_clean[:8]
                        + "*" * (len(content_clean) - 12)
                        + content_clean[-4:]
                        if len(content_clean) > 12
                        else "*" * len(content_clean),
                    },
                }

        # Generic API key detection (long alphanumeric strings)
        if len(content_clean) > 20 and re.match(r"^[a-zA-Z0-9_-]+$", content_clean):
            return {
                "type": "api_key",
                "service": "unknown",
                "confidence": 0.7,
                "sensitive": True,
                "metadata": {
                    "service": "unknown",
                    "masked": content_clean[:4]
                    + "*" * (len(content_clean) - 8)
                    + content_clean[-4:]
                    if len(content_clean) > 8
                    else "*" * len(content_clean),
                },
            }

        return None

    def _detect_json(self, content: str) -> Optional[Dict[str, Any]]:
        """Detect and validate JSON content"""
        content_clean = content.strip()

        if not (
            content_clean.startswith(("{", "[")) and content_clean.endswith(("}", "]"))
        ):
            return None

        try:
            parsed = json.loads(content_clean)

            # Analyze JSON structure
            if isinstance(parsed, dict):
                keys = (
                    list(parsed.keys())
                    if len(parsed) <= 10
                    else list(parsed.keys())[:10]
                )
                structure = "object"
            elif isinstance(parsed, list):
                keys = []
                structure = "array"
            else:
                keys = []
                structure = "primitive"

            return {
                "type": "json",
                "confidence": 0.95,
                "metadata": {
                    "structure": structure,
                    "keys": keys[:5],  # Limit keys for privacy
                    "size": len(str(parsed)),
                    "valid": True,
                },
            }
        except json.JSONDecodeError:
            # Looks like JSON but invalid
            if re.match(self.code_patterns["json"], content_clean):
                return {
                    "type": "json",
                    "confidence": 0.6,
                    "metadata": {"valid": False, "error": "Invalid JSON syntax"},
                }

        return None

    def _detect_xml(self, content: str) -> Optional[Dict[str, Any]]:
        """Detect XML content"""
        content_clean = content.strip()

        if not content_clean.startswith("<"):
            return None

        try:
            root = ET.fromstring(content_clean)
            return {
                "type": "xml",
                "confidence": 0.9,
                "metadata": {"root_tag": root.tag, "valid": True},
            }
        except ET.ParseError:
            if re.match(self.code_patterns["xml"], content_clean):
                return {
                    "type": "xml",
                    "confidence": 0.6,
                    "metadata": {"valid": False, "error": "Invalid XML syntax"},
                }

        return None

    def _detect_url(self, content: str) -> Optional[Dict[str, Any]]:
        """Detect URLs"""
        content_clean = content.strip()

        for url_type, pattern in self.url_patterns.items():
            if re.match(pattern, content_clean):
                try:
                    parsed = urlparse(content_clean)
                    return {
                        "type": "url",
                        "confidence": 0.95,
                        "metadata": {
                            "scheme": parsed.scheme,
                            "domain": parsed.netloc,
                            "path": parsed.path,
                            "url_type": url_type,
                        },
                    }
                except:
                    return {
                        "type": "url",
                        "confidence": 0.7,
                        "metadata": {"url_type": url_type},
                    }

        return None

    def _detect_email(self, content: str) -> Optional[Dict[str, Any]]:
        """Detect email addresses"""
        content_clean = content.strip()

        if re.match(self.email_pattern, content_clean):
            parts = content_clean.split("@")
            return {
                "type": "email",
                "confidence": 0.9,
                "metadata": {
                    "username": parts[0],
                    "domain": parts[1] if len(parts) > 1 else "",
                },
            }

        return None

    def _detect_phone(self, content: str) -> Optional[Dict[str, Any]]:
        """Detect phone numbers"""
        content_clean = content.strip()

        for pattern in self.phone_patterns:
            if re.match(pattern, content_clean):
                return {
                    "type": "phone",
                    "confidence": 0.8,
                    "sensitive": True,
                    "metadata": {
                        "formatted": content_clean,
                        "digits_only": re.sub(r"[^\d]", "", content_clean),
                    },
                }

        return None

    def _detect_code(self, content: str) -> Optional[Dict[str, Any]]:
        """Detect code in various languages"""
        content_clean = content.strip().lower()

        for language, pattern in self.code_patterns.items():
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                return {
                    "type": "code",
                    "confidence": 0.8,
                    "metadata": {
                        "language": language,
                        "lines": content.count("\n") + 1,
                    },
                }

        # Generic code detection based on common indicators
        code_indicators = [
            "{",
            "}",
            "(",
            ")",
            ";",
            "==",
            "!=",
            "&&",
            "||",
            "function",
            "class",
        ]
        indicator_count = sum(
            1 for indicator in code_indicators if indicator in content_clean
        )

        if indicator_count >= 3:
            return {
                "type": "code",
                "confidence": 0.6,
                "metadata": {"language": "unknown", "indicators": indicator_count},
            }

        return None

    def _detect_base64(self, content: str) -> Optional[Dict[str, Any]]:
        """Detect base64 encoded content"""
        content_clean = content.strip()

        # Base64 pattern
        if len(content_clean) > 20 and re.match(
            r"^[A-Za-z0-9+/]+={0,2}$", content_clean
        ):
            try:
                decoded = base64.b64decode(content_clean)
                return {
                    "type": "base64",
                    "confidence": 0.85,
                    "metadata": {
                        "decoded_length": len(decoded),
                        "original_length": len(content_clean),
                        "compression_ratio": len(decoded) / len(content_clean),
                    },
                }
            except:
                pass

        return None

    def _detect_hash(self, content: str) -> Optional[Dict[str, Any]]:
        """Detect hash values (MD5, SHA1, SHA256, etc.)"""
        content_clean = content.strip().lower()

        hash_patterns = {
            "md5": (r"^[a-f0-9]{32}$", 32),
            "sha1": (r"^[a-f0-9]{40}$", 40),
            "sha256": (r"^[a-f0-9]{64}$", 64),
            "sha512": (r"^[a-f0-9]{128}$", 128),
        }

        for hash_type, (pattern, length) in hash_patterns.items():
            if re.match(pattern, content_clean):
                return {
                    "type": "hash",
                    "confidence": 0.9,
                    "metadata": {"hash_type": hash_type, "length": length},
                }

        return None

    def _detect_ip_address(self, content: str) -> Optional[Dict[str, Any]]:
        """Detect IP addresses (IPv4 and IPv6)"""
        content_clean = content.strip()

        # IPv4 pattern
        ipv4_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        if re.match(ipv4_pattern, content_clean):
            return {
                "type": "ip_address",
                "confidence": 0.95,
                "metadata": {
                    "version": "ipv4",
                    "private": self._is_private_ipv4(content_clean),
                },
            }

        # IPv6 pattern (simplified)
        ipv6_pattern = r"^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$"
        if re.match(ipv6_pattern, content_clean):
            return {
                "type": "ip_address",
                "confidence": 0.9,
                "metadata": {"version": "ipv6"},
            }

        return None

    def _is_private_ipv4(self, ip: str) -> bool:
        """Check if IPv4 address is private"""
        octets = ip.split(".")
        if len(octets) != 4:
            return False

        try:
            first = int(octets[0])
            second = int(octets[1])

            # Private ranges: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
            if first == 10:
                return True
            elif first == 172 and 16 <= second <= 31:
                return True
            elif first == 192 and second == 168:
                return True
            elif first == 127:  # Loopback
                return True

        except ValueError:
            pass

        return False

    def _detect_credit_card(self, content: str) -> Optional[Dict[str, Any]]:
        """Detect credit card numbers (basic patterns)"""
        content_clean = re.sub(r"[^\d]", "", content.strip())

        if len(content_clean) >= 13 and len(content_clean) <= 19:
            # Basic Luhn algorithm check
            if self._luhn_check(content_clean):
                # Determine card type based on first digits
                card_type = self._get_card_type(content_clean)

                return {
                    "type": "credit_card",
                    "confidence": 0.8,
                    "sensitive": True,
                    "metadata": {
                        "card_type": card_type,
                        "masked": "*" * (len(content_clean) - 4) + content_clean[-4:],
                    },
                }

        return None

    def _luhn_check(self, card_number: str) -> bool:
        """Validate credit card using Luhn algorithm"""

        def luhn_checksum(card_num):
            def digits_of(n):
                return [int(d) for d in str(n)]

            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            return checksum % 10

        return luhn_checksum(card_number) == 0

    def _get_card_type(self, card_number: str) -> str:
        """Determine credit card type from number"""
        if card_number.startswith("4"):
            return "visa"
        elif card_number.startswith("5") or card_number.startswith("2"):
            return "mastercard"
        elif card_number.startswith("3"):
            return "amex"
        elif card_number.startswith("6"):
            return "discover"
        else:
            return "unknown"

    def _detect_coordinates(self, content: str) -> Optional[Dict[str, Any]]:
        """Detect GPS coordinates"""
        content_clean = content.strip()

        # Decimal degrees pattern
        coord_pattern = r"^-?\d+\.?\d*,\s*-?\d+\.?\d*$"
        if re.match(coord_pattern, content_clean):
            try:
                lat, lon = map(float, content_clean.split(","))
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return {
                        "type": "coordinates",
                        "confidence": 0.85,
                        "metadata": {
                            "latitude": lat,
                            "longitude": lon,
                            "format": "decimal_degrees",
                        },
                    }
            except ValueError:
                pass

        return None

    def format_for_display(self, content: str, analysis: Dict[str, Any]) -> str:
        """Format content for safe display based on analysis"""
        metadata = analysis.get("metadata", {})

        if analysis.get("primary_type") == "api_key" and analysis.get("sensitive"):
            return metadata.get("masked", content)
        elif analysis.get("primary_type") == "credit_card" and analysis.get(
            "sensitive"
        ):
            return metadata.get("masked", content)
        elif analysis.get("primary_type") == "phone" and analysis.get("sensitive"):
            # Mask middle digits of phone number
            digits = metadata.get("digits_only", content)
            if len(digits) >= 10:
                return digits[:3] + "*" * (len(digits) - 6) + digits[-3:]

        # For very long content, truncate
        if len(content) > 200:
            return content[:200] + "..."

        return content

    def get_security_level(self, analysis: Dict[str, Any]) -> str:
        """Determine security level of content"""
        if analysis.get("sensitive"):
            return "high"
        elif analysis.get("primary_type") in ["email", "phone", "ip_address"]:
            return "medium"
        elif analysis.get("primary_type") in ["url", "code"]:
            return "low"
        else:
            return "none"

    def suggest_templates(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest relevant templates based on content analysis"""
        if not self.template_manager:
            return []

        primary_type = analysis.get("primary_type", "text")
        suggestions = []

        # Map data types to template suggestions
        type_mapping = {
            "json": ["json-schema", "mcp-server-config", "api-response"],
            "api_key": ["api-key", "environment-vars", "mcp-server-config"],
            "url": ["curl-request", "bookmark", "api-endpoint"],
            "email": ["email-signature", "contact-info"],
            "sql": ["sql-query", "database-schema"],
            "coordinates": ["location-info", "map-link"],
            "ip_address": ["server-config", "network-info"],
            "phone": ["contact-info", "emergency-contacts"],
        }

        # Get content for template suggestion
        content = analysis.get("original_content", "")
        if content and hasattr(self.template_manager, "suggest_templates"):
            template_suggestions = self.template_manager.suggest_templates(
                content, limit=3
            )
            suggestions.extend(template_suggestions)

        # Add type-specific suggestions
        suggested_names = type_mapping.get(primary_type, [])
        for name in suggested_names:
            template = self.template_manager.get_template(name)
            if template and not any(s.get("name") == name for s in suggestions):
                template_copy = template.copy()
                template_copy["suggestion_reason"] = f"Matches {primary_type} content"
                suggestions.append(template_copy)

        return suggestions[:5]  # Return top 5 suggestions

    def validate_data_format(
        self, content: str, expected_type: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate content against expected data format"""
        content_clean = content.strip()

        validators = {
            "json": self._validate_json,
            "xml": self._validate_xml,
            "email": self._validate_email,
            "url": self._validate_url,
            "phone": self._validate_phone,
            "ip_address": self._validate_ip,
            "coordinates": self._validate_coordinates,
            "api_key": self._validate_api_key,
        }

        validator = validators.get(expected_type)
        if validator:
            return validator(content_clean)

        return True, None  # Unknown type, assume valid

    def _validate_json(self, content: str) -> Tuple[bool, Optional[str]]:
        """Validate JSON format"""
        try:
            json.loads(content)
            return True, None
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"

    def _validate_xml(self, content: str) -> Tuple[bool, Optional[str]]:
        """Validate XML format"""
        try:
            ET.fromstring(content)
            return True, None
        except ET.ParseError as e:
            return False, f"Invalid XML: {str(e)}"

    def _validate_email(self, content: str) -> Tuple[bool, Optional[str]]:
        """Validate email format"""
        if re.match(self.email_pattern, content):
            return True, None
        return False, "Invalid email format"

    def _validate_url(self, content: str) -> Tuple[bool, Optional[str]]:
        """Validate URL format"""
        try:
            result = urlparse(content)
            if result.scheme and result.netloc:
                return True, None
            return False, "Invalid URL format - missing scheme or netloc"
        except Exception:
            return False, "Invalid URL format"

    def _validate_phone(self, content: str) -> Tuple[bool, Optional[str]]:
        """Validate phone number format"""
        for pattern in self.phone_patterns:
            if re.match(pattern, content):
                return True, None
        return False, "Invalid phone number format"

    def _validate_ip(self, content: str) -> Tuple[bool, Optional[str]]:
        """Validate IP address format"""
        # IPv4
        ipv4_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        if re.match(ipv4_pattern, content):
            return True, None

        # IPv6 (simplified)
        ipv6_pattern = r"^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$"
        if re.match(ipv6_pattern, content):
            return True, None

        return False, "Invalid IP address format"

    def _validate_coordinates(self, content: str) -> Tuple[bool, Optional[str]]:
        """Validate GPS coordinates format"""
        coord_pattern = r"^-?\d+\.?\d*,\s*-?\d+\.?\d*$"
        if re.match(coord_pattern, content):
            try:
                lat, lon = map(float, content.split(","))
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return True, None
                return (
                    False,
                    "Coordinates out of valid range (lat: -90 to 90, lon: -180 to 180)",
                )
            except ValueError:
                return False, "Invalid coordinate format"
        return False, "Invalid coordinate format (expected: lat,lon)"

    def _validate_api_key(self, content: str) -> Tuple[bool, Optional[str]]:
        """Validate API key format"""
        # Check against known patterns
        for service, pattern in self.api_key_patterns.items():
            if re.match(pattern, content):
                return True, None

        # Generic validation - should be alphanumeric and reasonable length
        if len(content) >= 20 and re.match(r"^[a-zA-Z0-9_.-]+$", content):
            return True, None

        return (
            False,
            "API key should be at least 20 characters and contain only alphanumeric characters, underscores, dots, and dashes",
        )

    def enhance_content_with_templates(self, content: str) -> Dict[str, Any]:
        """Enhance content analysis with template suggestions"""
        analysis = self.analyze_content(content)
        analysis["original_content"] = (
            content  # Store original for template suggestions
        )

        if self.template_manager:
            analysis["suggested_templates"] = self.suggest_templates(analysis)
            analysis["security_level"] = self.get_security_level(analysis)
            analysis["display_content"] = self.format_for_display(content, analysis)

        return analysis

    def create_template_from_content(
        self, content: str, template_name: str, description: str = None
    ) -> bool:
        """Create a template from analyzed content"""
        if not self.template_manager:
            return False

        analysis = self.analyze_content(content)
        primary_type = analysis.get("primary_type", "text")

        # Auto-generate description if not provided
        if not description:
            description = f"Template created from {primary_type} content"

        # Determine category based on content type
        category_mapping = {
            "json": "development",
            "xml": "development",
            "sql": "database",
            "api_key": "security",
            "email": "personal",
            "url": "development",
            "code": "development",
        }

        category = category_mapping.get(primary_type, "custom")
        tags = [primary_type, "auto-generated"]

        # Add service-specific tags for API keys
        if primary_type == "api_key" and analysis.get("metadata", {}).get("service"):
            tags.append(analysis["metadata"]["service"])

        return self.template_manager.create_template(
            name=template_name,
            description=description,
            content=content,
            category=category,
            tags=tags,
        )
