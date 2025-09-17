#!/usr/bin/env python3
"""
🧪 Integration Test for Clipboard Helper

Comprehensive test of template manager and data handler integration.
"""

import sys
import tempfile

# Add lib directory to Python path
sys.path.insert(0, "lib")

try:
    from template_manager import AdvancedTemplateManager
    from data_handlers import DataHandler
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)


def test_template_manager():
    """Test AdvancedTemplateManager functionality"""
    print("🧪 Testing AdvancedTemplateManager...")

    with tempfile.TemporaryDirectory() as tmpdir:
        tm = AdvancedTemplateManager(tmpdir)

        # Test template creation
        success = tm.create_template(
            name="email-template",
            description="Email template with greeting",
            content="Hello {{NAME}},\n\nYour account {{ACCOUNT}} is ready.\n\nBest regards,\n{{SENDER}}",
            category="communication",
            tags=["email", "greeting"],
        )
        assert success, "Template creation failed"
        print("✅ Template creation: PASSED")

        # Test template retrieval
        template = tm.get_template("email-template")
        assert template is not None, "Template retrieval failed"
        assert template["name"] == "email-template", "Template name mismatch"
        print("✅ Template retrieval: PASSED")

        # Test placeholder extraction
        placeholders = tm.extract_placeholders(template["content"])
        expected = ["NAME", "ACCOUNT", "SENDER"]
        assert set(placeholders) == set(expected), (
            f"Placeholders mismatch: got {placeholders}, expected {expected}"
        )
        print("✅ Placeholder extraction: PASSED")

        # Test template processing
        result, errors = tm.process_template(
            "email-template",
            {"NAME": "John Doe", "ACCOUNT": "jdoe123", "SENDER": "Support Team"},
        )
        assert result is not None, "Template processing failed"
        assert "John Doe" in result, "Name substitution failed"
        assert "jdoe123" in result, "Account substitution failed"
        assert "Support Team" in result, "Sender substitution failed"
        assert len(errors) == 0, f"Template processing had errors: {errors}"
        print("✅ Template processing: PASSED")

        # Test template suggestions
        suggestions = tm.suggest_templates("email greeting communication")
        assert len(suggestions) > 0, "No template suggestions found"
        assert suggestions[0]["name"] == "email-template", "Wrong template suggested"
        print("✅ Template suggestions: PASSED")

        # Test usage statistics
        stats = tm.get_usage_statistics()
        assert stats["total_templates"] == 1, "Total templates count wrong"
        assert stats["used_templates"] == 1, "Used templates count wrong"
        assert stats["usage_rate"] == 100.0, "Usage rate calculation wrong"
        print("✅ Usage statistics: PASSED")

        print("🎉 AdvancedTemplateManager: ALL TESTS PASSED")
        return True


def test_data_handler():
    """Test DataHandler functionality with template manager"""
    print("\n🧪 Testing DataHandler integration...")

    with tempfile.TemporaryDirectory() as tmpdir:
        tm = AdvancedTemplateManager(tmpdir)
        dh = DataHandler(template_manager=tm)

        # Create a test template first
        tm.create_template(
            name="code-snippet",
            description="Code snippet template",
            content="def {{FUNCTION_NAME}}():\n    {{BODY}}\n    return {{RETURN_VALUE}}",
            category="code",
            tags=["python", "function"],
        )

        # Test content analysis
        sample_code = "def hello_world():\n    print('Hello!')\n    return True"
        analysis = dh.analyze_content(sample_code)
        assert "primary_type" in analysis, "Analysis missing primary_type"
        assert "confidence" in analysis, "Analysis missing confidence"
        assert "detected_types" in analysis, "Analysis missing detected_types"
        print("✅ Content analysis: PASSED")

        # Test template creation from clipboard content
        success = dh.create_template_from_content(
            content="Hello {{USER}}, welcome to {{APP}}!",
            template_name="test-auto-template",
            description="Auto-generated template",
        )
        assert success, "Template creation from content failed"

        # Verify the template was created
        created_template = tm.get_template("test-auto-template")
        assert created_template is not None, (
            "Created template not found in template manager"
        )
        print("✅ Template creation from content: PASSED")

        print("🎉 DataHandler integration: ALL TESTS PASSED")
        return True


def test_gui_import():
    """Test that GUI can import all modules successfully"""
    print("\n🧪 Testing GUI imports...")

    try:
        # Test clipboard_core import
        from clipboard_core import ClipboardManager

        cm = ClipboardManager()
        print("✅ ClipboardManager import: PASSED")

        # Test virtual_keyboard import
        from virtual_keyboard import VirtualKeyboard

        vk = VirtualKeyboard()
        print("✅ VirtualKeyboard import: PASSED")

        # Test template manager imports
        from template_manager import TemplateManager, AdvancedTemplateManager

        print("✅ TemplateManager imports: PASSED")

        # Test data handler import
        from data_handlers import DataHandler

        print("✅ DataHandler import: PASSED")

        print("🎉 GUI imports: ALL TESTS PASSED")
        return True

    except ImportError as e:
        print(f"❌ GUI import test failed: {e}")
        return False


def main():
    """Run all integration tests"""
    print("🚀 Starting Clipboard Helper Integration Tests...\n")

    tests = [test_template_manager, test_data_handler, test_gui_import]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test {test.__name__} failed")
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL INTEGRATION TESTS PASSED! 🎉")
        print("\n✨ Your Clipboard Helper is ready to use!")
        return True
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
