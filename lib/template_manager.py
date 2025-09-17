#!/usr/bin/env python3
"""
🔧 Template Manager for Clipboard Helper

Provides template management functionality including creation, editing,
organization, and usage analytics.

Made with ❤️ by Pink Pixel
"""

import json
import os
import re
import datetime
import shutil
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid


@dataclass
class TemplateUsage:
    """Template usage statistics"""

    last_used: str
    count: int
    average_processing_time: float
    success_rate: float
    most_common_values: Dict[str, str]


class TemplateManager:
    """Template management system"""

    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir)
        self.templates_file = self.config_dir / "templates.json"
        self.usage_file = self.config_dir / "template_usage.json"
        self.backups_dir = self.config_dir / "template_backups"

        # Create directories if they don't exist
        self.config_dir.mkdir(exist_ok=True)
        self.backups_dir.mkdir(exist_ok=True)

        self.templates_data = self._load_templates()
        self.usage_data = self._load_usage()

        # Compiled regex patterns for placeholders
        self.placeholder_pattern = re.compile(r"\{\{(\w+)\}\}")

    def _load_templates(self) -> Dict[str, Any]:
        """Load templates from JSON file"""
        try:
            if self.templates_file.exists():
                with open(self.templates_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                return {"templates": [], "categories": [], "settings": {}}
        except Exception as e:
            print(f"Error loading templates: {e}")
            return {"templates": [], "categories": [], "settings": {}}

    def _load_usage(self) -> Dict[str, TemplateUsage]:
        """Load template usage statistics"""
        try:
            if self.usage_file.exists():
                with open(self.usage_file, "r", encoding="utf-8") as f:
                    usage_dict = json.load(f)
                    return {
                        name: TemplateUsage(**data) for name, data in usage_dict.items()
                    }
            else:
                return {}
        except Exception as e:
            print(f"Error loading usage data: {e}")
            return {}

    def _save_templates(self) -> bool:
        """Save templates to JSON file with backup"""
        try:
            # Create backup
            if self.templates_file.exists():
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = self.backups_dir / f"templates_backup_{timestamp}.json"
                shutil.copy2(self.templates_file, backup_path)

                # Keep only last 10 backups
                backups = sorted(self.backups_dir.glob("templates_backup_*.json"))
                if len(backups) > 10:
                    for backup in backups[:-10]:
                        backup.unlink()

            # Save current templates
            self.templates_data["settings"]["last_updated"] = (
                datetime.datetime.now().isoformat()
            )
            with open(self.templates_file, "w", encoding="utf-8") as f:
                json.dump(self.templates_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving templates: {e}")
            return False

    def _save_usage(self) -> bool:
        """Save template usage statistics"""
        try:
            usage_dict = {
                name: asdict(usage) for name, usage in self.usage_data.items()
            }
            with open(self.usage_file, "w", encoding="utf-8") as f:
                json.dump(usage_dict, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving usage data: {e}")
            return False

    def get_templates(
        self, category: Optional[str] = None, search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get templates with optional filtering"""
        templates = self.templates_data.get("templates", [])

        # Filter by category
        if category:
            templates = [t for t in templates if t.get("category") == category]

        # Search in name, description, and tags
        if search:
            search_lower = search.lower()
            templates = [
                t
                for t in templates
                if (
                    search_lower in t.get("name", "").lower()
                    or search_lower in t.get("description", "").lower()
                    or any(search_lower in tag.lower() for tag in t.get("tags", []))
                )
            ]

        # Sort by usage count and last used
        def sort_key(template):
            usage = self.usage_data.get(template["name"])
            if usage:
                return (-usage.count, usage.last_used)
            return (0, "1970-01-01")

        return sorted(templates, key=sort_key, reverse=True)

    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific template by name"""
        templates = self.templates_data.get("templates", [])
        for template in templates:
            if template.get("name") == name:
                return template
        return None

    def extract_placeholders(self, content: str) -> List[str]:
        """Extract placeholder names from template content"""
        return self.placeholder_pattern.findall(content)

    def create_template(
        self,
        name: str,
        description: str,
        content: str,
        category: str = "custom",
        tags: List[str] = None,
    ) -> bool:
        """Create a new template"""
        if self.get_template(name):
            return False  # Template already exists

        # Extract placeholders from content
        placeholder_names = self.extract_placeholders(content)
        placeholders = []

        for ph_name in placeholder_names:
            placeholders.append(
                {
                    "name": ph_name,
                    "description": f"Value for {ph_name}",
                    "type": "text",
                    "required": True,
                }
            )

        new_template = {
            "name": name,
            "description": description,
            "category": category,
            "content": content,
            "placeholders": placeholders,
            "usage_count": 0,
            "created": datetime.datetime.now().strftime("%Y-%m-%d"),
            "tags": tags or [],
            "id": str(uuid.uuid4()),  # Unique identifier
        }

        self.templates_data.setdefault("templates", []).append(new_template)
        return self._save_templates()

    def update_template(self, name: str, **kwargs) -> bool:
        """Update an existing template"""
        template = self.get_template(name)
        if not template:
            return False

        templates = self.templates_data["templates"]
        for i, t in enumerate(templates):
            if t["name"] == name:
                # Update specified fields
                for key, value in kwargs.items():
                    if key in [
                        "name",
                        "description",
                        "content",
                        "category",
                        "tags",
                        "placeholders",
                    ]:
                        t[key] = value

                # Update placeholders if content changed
                if "content" in kwargs:
                    placeholder_names = self.extract_placeholders(kwargs["content"])
                    existing_placeholders = {
                        p["name"]: p for p in t.get("placeholders", [])
                    }

                    new_placeholders = []
                    for ph_name in placeholder_names:
                        if ph_name in existing_placeholders:
                            new_placeholders.append(existing_placeholders[ph_name])
                        else:
                            new_placeholders.append(
                                {
                                    "name": ph_name,
                                    "description": f"Value for {ph_name}",
                                    "type": "text",
                                    "required": True,
                                }
                            )
                    t["placeholders"] = new_placeholders

                templates[i] = t
                break

        return self._save_templates()

    def delete_template(self, name: str) -> bool:
        """Delete a template"""
        templates = self.templates_data["templates"]
        original_count = len(templates)
        self.templates_data["templates"] = [t for t in templates if t["name"] != name]

        # Also remove from usage data
        if name in self.usage_data:
            del self.usage_data[name]
            self._save_usage()

        if len(self.templates_data["templates"]) < original_count:
            return self._save_templates()
        return False

    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all template categories"""
        return self.templates_data.get("categories", [])

    def process_template(
        self, template_name: str, values: Dict[str, str]
    ) -> Tuple[Optional[str], List[str]]:
        """Process template with placeholder values"""
        template = self.get_template(template_name)
        if not template:
            return None, [f"Template '{template_name}' not found"]

        content = template.get("content", "")
        processed_content = content

        # Replace placeholders with values
        for placeholder_name in self.extract_placeholders(content):
            value = values.get(placeholder_name, "")
            processed_content = processed_content.replace(
                f"{{{{{placeholder_name}}}}}", value
            )

        # Update usage statistics
        self._update_usage_stats(template_name, values, success=True)

        return processed_content, []

    def _update_usage_stats(
        self, template_name: str, values: Dict[str, str], success: bool = True
    ) -> None:
        """Update template usage statistics"""
        now = datetime.datetime.now().isoformat()

        if template_name not in self.usage_data:
            self.usage_data[template_name] = TemplateUsage(
                last_used=now,
                count=0,
                average_processing_time=0.0,
                success_rate=100.0,
                most_common_values={},
            )

        usage = self.usage_data[template_name]
        usage.last_used = now
        usage.count += 1

        # Update success rate
        total_attempts = usage.count
        if success:
            usage.success_rate = (
                (usage.success_rate * (total_attempts - 1)) + 100
            ) / total_attempts
        else:
            usage.success_rate = (
                usage.success_rate * (total_attempts - 1)
            ) / total_attempts

        # Track most common values
        for name, value in values.items():
            if value and len(value) < 100:  # Avoid storing very long values
                if name not in usage.most_common_values:
                    usage.most_common_values[name] = value

        self._save_usage()

    def export_templates(
        self, export_path: str, template_names: List[str] = None
    ) -> bool:
        """Export templates to a file"""
        try:
            if template_names:
                # Export specific templates
                templates_to_export = [
                    t
                    for t in self.templates_data.get("templates", [])
                    if t["name"] in template_names
                ]
            else:
                # Export all templates
                templates_to_export = self.templates_data.get("templates", [])

            export_data = {
                "templates": templates_to_export,
                "categories": self.templates_data.get("categories", []),
                "export_date": datetime.datetime.now().isoformat(),
                "version": "1.0",
            }

            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Error exporting templates: {e}")
            return False

    def import_templates(
        self, import_path: str, overwrite: bool = False
    ) -> Tuple[int, List[str]]:
        """Import templates from a file"""
        try:
            with open(import_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)

            imported_count = 0
            errors = []
            existing_names = {
                t["name"] for t in self.templates_data.get("templates", [])
            }

            for template in import_data.get("templates", []):
                name = template.get("name")
                if not name:
                    errors.append("Template missing name field")
                    continue

                if name in existing_names and not overwrite:
                    errors.append(
                        f"Template '{name}' already exists (use overwrite=True)"
                    )
                    continue

                if overwrite and name in existing_names:
                    # Remove existing template
                    self.templates_data["templates"] = [
                        t for t in self.templates_data["templates"] if t["name"] != name
                    ]

                # Add unique ID if missing
                if "id" not in template:
                    template["id"] = str(uuid.uuid4())

                self.templates_data.setdefault("templates", []).append(template)
                imported_count += 1

            # Import categories
            existing_category_names = {
                c["name"] for c in self.templates_data.get("categories", [])
            }
            for category in import_data.get("categories", []):
                if category["name"] not in existing_category_names:
                    self.templates_data.setdefault("categories", []).append(category)

            if imported_count > 0:
                self._save_templates()

            return imported_count, errors

        except Exception as e:
            return 0, [f"Error importing templates: {e}"]


class AdvancedTemplateManager(TemplateManager):
    """Enhanced template manager with advanced features"""

    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = os.path.expanduser("~/.clipboard-helper")
        super().__init__(config_dir)

        # Initialize analytics data
        self.analytics_data = self._load_analytics()

    def _load_analytics(self) -> Dict[str, Any]:
        """Load analytics data"""
        analytics_file = self.config_dir / "analytics.json"
        try:
            if analytics_file.exists():
                with open(analytics_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                return {"template_suggestions": {}, "content_analysis": {}}
        except Exception:
            return {"template_suggestions": {}, "content_analysis": {}}

    def _save_analytics(self) -> bool:
        """Save analytics data"""
        analytics_file = self.config_dir / "analytics.json"
        try:
            with open(analytics_file, "w", encoding="utf-8") as f:
                json.dump(self.analytics_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def suggest_templates(self, content: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Suggest templates based on content analysis"""
        suggestions = []
        templates = self.get_templates()

        # Simple keyword matching for template suggestions
        content_lower = content.lower()

        for template in templates:
            score = 0
            name = template.get("name", "").lower()
            description = template.get("description", "").lower()
            tags = [tag.lower() for tag in template.get("tags", [])]

            # Score based on name matches
            for word in name.split():
                if word in content_lower:
                    score += 3

            # Score based on description matches
            for word in description.split():
                if word in content_lower:
                    score += 2

            # Score based on tag matches
            for tag in tags:
                if tag in content_lower:
                    score += 4

            if score > 0:
                template_copy = template.copy()
                template_copy["suggestion_score"] = score
                template_copy["suggestion_reason"] = (
                    f"Content analysis match (score: {score})"
                )
                suggestions.append(template_copy)

        # Sort by score and return top suggestions
        suggestions.sort(key=lambda x: x["suggestion_score"], reverse=True)
        return suggestions[:limit]

    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics"""
        templates = self.templates_data.get("templates", [])
        total_templates = len(templates)
        used_templates = len([t for t in templates if t["name"] in self.usage_data])

        # Most used templates
        most_used = sorted(
            [(name, usage.count) for name, usage in self.usage_data.items()],
            key=lambda x: x[1],
            reverse=True,
        )[:10]

        # Category statistics
        category_stats = {}
        for template in templates:
            category = template.get("category", "uncategorized")
            if category not in category_stats:
                category_stats[category] = {"total": 0, "used": 0}
            category_stats[category]["total"] += 1
            if template["name"] in self.usage_data:
                category_stats[category]["used"] += 1

        # Get last backup info
        last_backup = None
        backups = sorted(self.backups_dir.glob("templates_backup_*.json"))
        if backups:
            last_backup = backups[-1].stat().st_mtime
            last_backup = datetime.datetime.fromtimestamp(last_backup).isoformat()

        return {
            "total_templates": total_templates,
            "used_templates": used_templates,
            "usage_rate": (used_templates / total_templates * 100)
            if total_templates > 0
            else 0,
            "most_used": most_used,
            "category_stats": category_stats,
            "last_backup": last_backup,
        }


def main():
    """Test the template manager"""
    import tempfile

    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        tm = AdvancedTemplateManager(tmpdir)

        # Create a test template
        success = tm.create_template(
            name="test-template",
            description="A test template",
            content="Hello {{NAME}}, your email is {{EMAIL}}",
            category="test",
            tags=["test", "demo"],
        )
        print(f"Created template: {success}")

        # Process the template
        result, errors = tm.process_template(
            "test-template", {"NAME": "John Doe", "EMAIL": "john@example.com"}
        )
        print(f"Processed template: {result}")
        print(f"Errors: {errors}")

        # Get usage statistics
        stats = tm.get_usage_statistics()
        print(f"Usage statistics: {stats}")

        # Test suggestions
        suggestions = tm.suggest_templates("hello test demo")
        print(f"Suggestions: {len(suggestions)}")


if __name__ == "__main__":
    main()
