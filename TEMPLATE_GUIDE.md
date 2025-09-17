# 🎯 CopyCat Template System Guide

**Version:** 1.0.0  
**Updated:** September 17, 2025  
**Author:** Pink Pixel  

*Made with ❤️ by Pink Pixel - Dream it, Pixel it ✨*

---

## 📋 Table of Contents

1. [Overview](#-overview)
2. [Getting Started](#-getting-started)
3. [Built-in Templates](#-built-in-templates)
4. [Using Templates](#-using-templates)
5. [Creating Custom Templates](#-creating-custom-templates)
6. [Placeholder System](#-placeholder-system)
7. [Template Categories](#-template-categories)
8. [Advanced Features](#-advanced-features)
9. [Command Reference](#-command-reference)
10. [Troubleshooting](#-troubleshooting)

---

## 🎯 Overview

CopyCat's template system is a powerful feature that allows you to create and use reusable text snippets with dynamic placeholders. Perfect for:

- 🔐 **API keys and configuration strings**
- 💻 **Code snippets and boilerplate**
- 📧 **Email signatures and professional communications**
- 🗄️ **Database queries and commands**
- 🌐 **HTTP requests and API calls**
- ⚙️ **Configuration files and settings**

### Key Features

- **Built-in Templates**: 6 professionally crafted templates ready to use
- **Smart Placeholders**: Dynamic `{{PLACEHOLDER}}` system with validation
- **Usage Analytics**: Track which templates you use most
- **Category Organization**: Templates grouped by purpose
- **Security-First**: Automatic sensitive data detection and protection
- **Import/Export**: Share template collections with others
- **Smart Suggestions**: AI-powered template recommendations

---

## 🚀 Getting Started

### Viewing Available Templates

**CLI Method:**
```bash
copycat --templates
```

**GUI Method:**
1. Launch CopyCat GUI: `copycat-gui` or `copycat --gui`
2. Click the **Templates** tab
3. Browse available templates by category

### Quick Template Test

Let's try the email signature template:

1. Open CopyCat GUI
2. Go to Templates tab
3. Select "email-signature" template
4. Fill in the placeholders:
   - **NAME**: Your full name
   - **TITLE**: Your job title
   - **COMPANY**: Your company name
   - **EMAIL**: Your email address
   - **PHONE**: Your phone number (optional)
   - **WEBSITE**: Your website URL (optional)
5. Click **Process Template**
6. The result is automatically copied to your clipboard!

---

## 📦 Built-in Templates

CopyCat includes 6 professionally crafted templates organized by category:

### 🔐 Security Templates

#### **API Key Template**
- **Name:** `api-key`
- **Purpose:** Secure handling of API keys
- **Placeholders:** `{{API_KEY}}`
- **Usage:** Perfect for pasting API keys while maintaining security
- **Example Output:**
  ```
  sk-1234567890abcdefghijklmnopqrstuvwxyz
  ```

### 💻 Development Templates

#### **JSON Schema Template**
- **Name:** `json-schema`  
- **Purpose:** Generate JSON schema definitions
- **Placeholders:** 
  - `{{PROPERTY_NAME}}` - Property name
  - `{{PROPERTY_TYPE}}` - Data type (string, number, boolean, object, array)
  - `{{PROPERTY_DESC}}` - Property description
- **Example Output:**
  ```json
  {
    "type": "object",
    "properties": {
      "username": {
        "type": "string",
        "description": "User's login name"
      }
    },
    "required": ["username"]
  }
  ```

#### **MCP Server Configuration**
- **Name:** `mcp-server-config`
- **Purpose:** Generate MCP server configuration blocks
- **Placeholders:**
  - `{{SERVER_NAME}}` - Server identifier
  - `{{COMMAND}}` - Command to run server
  - `{{ARGS}}` - Command arguments (comma-separated, quoted)
  - `{{ENV_KEY}}` - Environment variable key (optional)
  - `{{ENV_VALUE}}` - Environment variable value (optional)
- **Example Output:**
  ```json
  {
    "mcpServers": {
      "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/files"],
        "env": {
          "FILE_ACCESS_LEVEL": "read-write"
        }
      }
    }
  }
  ```

#### **cURL Request Template**
- **Name:** `curl-request`
- **Purpose:** Generate HTTP requests using cURL
- **Placeholders:**
  - `{{METHOD}}` - HTTP method (GET, POST, PUT, DELETE, PATCH)
  - `{{URL}}` - Request URL
  - `{{TOKEN}}` - Authorization token (optional, sensitive)
  - `{{DATA}}` - Request body data in JSON format (optional)
- **Example Output:**
  ```bash
  curl -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer your-token-here" \
    -d '{"key": "value"}' \
    https://api.example.com/endpoint
  ```

### 👤 Personal Templates

#### **Email Signature**
- **Name:** `email-signature`
- **Purpose:** Professional email signatures
- **Placeholders:**
  - `{{NAME}}` - Your full name
  - `{{TITLE}}` - Your job title  
  - `{{COMPANY}}` - Company name
  - `{{EMAIL}}` - Email address
  - `{{PHONE}}` - Phone number (optional)
  - `{{WEBSITE}}` - Website URL (optional)
- **Example Output:**
  ```
  Best regards,

  John Smith
  Senior Developer
  Tech Solutions Inc.
  john.smith@techsolutions.com
  +1-555-123-4567
  https://techsolutions.com
  ```

### 🗄️ Database Templates

#### **SQL Query Template**
- **Name:** `sql-query`
- **Purpose:** Generate SQL SELECT statements
- **Placeholders:**
  - `{{COLUMNS}}` - Columns to select (default: *)
  - `{{TABLE}}` - Table name
  - `{{CONDITIONS}}` - WHERE conditions (optional, default: 1=1)
  - `{{ORDER_BY}}` - ORDER BY clause (optional)
  - `{{LIMIT}}` - LIMIT clause (optional, default: 10)
- **Example Output:**
  ```sql
  SELECT id, name, email
  FROM users
  WHERE status = 'active'
  ORDER BY created_at DESC
  LIMIT 10;
  ```

---

## 🎯 Using Templates

### Via GUI (Recommended)

1. **Launch GUI:** `copycat --gui` or `copycat-gui`
2. **Navigate to Templates:** Click the Templates tab
3. **Browse Categories:** Use category dropdown to filter templates
4. **Select Template:** Click on desired template
5. **Fill Placeholders:** Enter values in the form fields
6. **Process:** Click "Process Template" button
7. **Result:** Processed template is copied to clipboard automatically

### Via CLI (Basic)

```bash
# View all templates
copycat --templates

# Note: Direct CLI template processing is not yet implemented
# Use the GUI for template processing
```

### Template Processing Workflow

1. **Template Selection** → Choose from built-in or custom templates
2. **Placeholder Filling** → Enter values for required and optional fields
3. **Validation** → System validates inputs based on placeholder types
4. **Processing** → Placeholders replaced with actual values
5. **Output** → Result copied to clipboard and/or displayed
6. **Analytics** → Usage statistics updated for future improvements

---

## 🛠️ Creating Custom Templates

### Via GUI Template Editor

1. **Open Templates Tab** in CopyCat GUI
2. **Click "New Template"** button
3. **Fill Template Details:**
   - **Name:** Unique template identifier (no spaces, use hyphens)
   - **Description:** Brief explanation of template purpose
   - **Category:** Choose existing or create new category
   - **Tags:** Keywords for easy searching (comma-separated)
4. **Write Template Content:**
   - Use `{{PLACEHOLDER_NAME}}` syntax for dynamic content
   - Example: `Hello {{NAME}}, your order {{ORDER_ID}} is ready!`
5. **Configure Placeholders:**
   - System auto-detects placeholders from content
   - Set placeholder types, descriptions, and default values
   - Mark required vs optional placeholders
6. **Save Template**

### Template Content Examples

**Simple Greeting:**
```
Hello {{NAME}}, 

Welcome to {{COMPANY}}! We're excited to have you on board.

Best regards,
{{SENDER_NAME}}
```

**Configuration File:**
```ini
[{{SECTION_NAME}}]
server_url = {{SERVER_URL}}
api_key = {{API_KEY}}
debug = {{DEBUG_MODE}}
timeout = {{TIMEOUT_SECONDS}}
```

**Code Snippet:**
```python
def {{FUNCTION_NAME}}({{PARAMETERS}}):
    """{{DESCRIPTION}}"""
    {{FUNCTION_BODY}}
    return {{RETURN_VALUE}}
```

### Placeholder Best Practices

1. **Use UPPERCASE names:** `{{USER_NAME}}` not `{{user_name}}`
2. **Be descriptive:** `{{DATABASE_CONNECTION_STRING}}` not `{{DB}}`
3. **Group related fields:** `{{EMAIL_FROM}}`, `{{EMAIL_TO}}`, `{{EMAIL_SUBJECT}}`
4. **Consider defaults:** Provide sensible defaults for optional fields
5. **Think about types:** Use appropriate input types (text, email, url, number, etc.)

---

## 🔧 Placeholder System

### Placeholder Syntax

Use double curly braces around placeholder names:
```
{{PLACEHOLDER_NAME}}
```

### Placeholder Types

| Type | Description | Validation | Example |
|------|-------------|------------|---------|
| `text` | Basic text input | None | Any text string |
| `sensitive` | Masked input (passwords, API keys) | None | Displayed as `****` |
| `email` | Email address | Email format | `user@domain.com` |
| `url` | Website URL | URL format | `https://example.com` |
| `number` | Numeric input | Number format | `42`, `3.14` |
| `select` | Dropdown options | Predefined choices | Choose from list |

### Placeholder Configuration

Each placeholder can have:

- **Name:** Unique identifier within template
- **Description:** User-friendly explanation
- **Type:** Input validation and UI widget type
- **Required:** Whether field is mandatory (true/false)
- **Default:** Pre-filled value
- **Options:** For select type, list of choices

### Example Placeholder Definition

```json
{
  "name": "EMAIL_TYPE",
  "description": "Type of email to send",
  "type": "select",
  "options": ["welcome", "notification", "reminder", "alert"],
  "required": true,
  "default": "notification"
}
```

---

## 📁 Template Categories

### Built-in Categories

| Category | Icon | Purpose | Example Templates |
|----------|------|---------|-------------------|
| **development** | 💻 | Programming templates | JSON schema, API requests |
| **security** | 🔐 | Security-related content | API keys, tokens |
| **personal** | 👤 | Personal use templates | Email signatures, letters |
| **database** | 🗄️ | Database-related queries | SQL statements, schema |

### Custom Categories

Create your own categories when making templates:
- **business** - Business documents and forms
- **academic** - Research papers and citations
- **creative** - Creative writing templates
- **devops** - Infrastructure and deployment
- **documentation** - Technical documentation

---

## ⚡ Advanced Features

### 🔍 Smart Template Suggestions

CopyCat analyzes your clipboard content and suggests relevant templates:

1. **Content Analysis:** System detects data types (JSON, URLs, code, etc.)
2. **Keyword Matching:** Matches content against template tags and descriptions
3. **Usage Patterns:** Considers your most-used templates
4. **Context Awareness:** Suggests based on recent activity

**Example:**
- Copy a JSON object → Suggests "json-schema" template
- Copy an email address → Suggests "email-signature" template
- Copy "curl" command → Suggests "curl-request" template

### 📊 Usage Analytics

Track your template usage with detailed statistics:

- **Usage Count:** How many times each template has been used
- **Success Rate:** Percentage of successful template processing
- **Most Common Values:** Frequently used placeholder values for auto-completion
- **Category Statistics:** Usage patterns by template category
- **Last Used:** When you last used each template

**Access Analytics:**
1. Open Templates tab in GUI
2. Click "Usage Statistics" button
3. View detailed analytics dashboard

### 🔄 Import/Export Templates

**Export Templates:**
```python
# Via Python API (for advanced users)
from copycat.template_manager import AdvancedTemplateManager
tm = AdvancedTemplateManager()
tm.export_templates("/path/to/my_templates.json")
```

**Import Templates:**
- Drag and drop template files into GUI
- Use Import button in Templates tab
- Merge with existing templates or overwrite

**Template File Format:**
```json
{
  "templates": [...],
  "categories": [...],
  "export_date": "2025-09-17T07:36:52Z",
  "version": "1.0"
}
```

### 🔐 Security Features

**Sensitive Data Protection:**
- Automatic detection of API keys, tokens, passwords
- Masked display in UI (shows `sk-****...****`)
- Excluded from clipboard history
- Encrypted in template backups

**Security Indicators:**
- 🔐 Lock icon for sensitive templates
- Warning messages for sensitive content
- Secure processing notifications

---

## 📚 Command Reference

### CLI Commands

```bash
# View all available templates
copycat --templates

# Launch GUI with Templates tab
copycat --gui

# Launch standalone GUI
copycat-gui
```

### GUI Navigation

**Templates Tab Features:**
- **Category Filter:** Dropdown to filter by category
- **Search Bar:** Find templates by name, description, or tags
- **Template List:** All available templates with descriptions
- **Template Editor:** Create/edit custom templates
- **Processing Form:** Fill placeholders and process templates
- **Usage Statistics:** View analytics and usage patterns

### Keyboard Shortcuts (in GUI)

- **Ctrl+N:** New template
- **Ctrl+E:** Edit selected template
- **Ctrl+D:** Delete selected template
- **Ctrl+P:** Process template
- **Ctrl+F:** Search templates
- **F5:** Refresh template list

---

## 🔧 Troubleshooting

### Common Issues

**Problem:** "No templates found"
**Solution:** 
- Ensure CopyCat is properly installed: `pip install -e .`
- Check that built-in templates are loading correctly
- Verify template files exist in package resources

**Problem:** Template processing fails
**Solution:**
- Check all required placeholders are filled
- Verify placeholder syntax uses `{{NAME}}` format
- Ensure no special characters in placeholder names

**Problem:** GUI shows template errors
**Solution:**
- Restart CopyCat GUI
- Clear template cache: Delete `~/.copycat/templates.json` (user templates only)
- Check for JSON syntax errors in custom templates

**Problem:** Templates not saving
**Solution:**
- Verify write permissions to `~/.copycat/` directory
- Check disk space availability
- Ensure template names are unique

### Template Validation

**Valid Template Content:**
```
Hello {{NAME}}, welcome to {{COMPANY}}!
```

**Invalid Template Content:**
```
Hello {NAME}, welcome to {{COMPANY}!     # Single braces
Hello {{ NAME }}, welcome to {{COMPANY}} # Spaces in placeholder
Hello {{name}}, welcome to {{COMPANY}}   # Lowercase (works but not recommended)
```

### File Locations

- **Built-in Templates:** `copycat/resources/templates.json` (read-only)
- **User Templates:** `~/.copycat/templates.json`
- **Usage Statistics:** `~/.copycat/template_usage.json`
- **Analytics:** `~/.copycat/analytics.json`
- **Backups:** `~/.copycat/template_backups/`

### Getting Help

1. **Check Status:** `copycat --status` - Verify system dependencies
2. **View Logs:** Check terminal output for error messages
3. **Reset Templates:** Delete user template files to restore defaults
4. **GUI Issues:** Try CLI template listing to isolate GUI problems

---

## 🎯 Pro Tips

### Template Creation Tips

1. **Start Simple:** Begin with basic placeholders, add complexity gradually
2. **Test Thoroughly:** Process templates with various inputs before saving
3. **Use Categories:** Organize templates into logical categories
4. **Add Good Descriptions:** Make it easy to find templates later
5. **Consider Security:** Mark sensitive placeholders appropriately

### Workflow Optimization

1. **Favorite Templates:** Most-used templates appear first in lists
2. **Smart Defaults:** Use common values as placeholder defaults
3. **Batch Processing:** Create multiple related templates together
4. **Regular Cleanup:** Review and remove unused custom templates
5. **Export Collections:** Backup important template collections

### Integration Ideas

- **Development:** API endpoint templates, configuration files
- **Documentation:** Standard headers, code examples, references
- **Communication:** Meeting invites, status updates, announcements
- **DevOps:** Deployment configs, monitoring alerts, incident reports
- **Business:** Proposals, invoices, contracts, agreements

---

## 🚀 What's Next?

The template system continues to evolve with planned features:

- **Template Variables:** Environment-based dynamic values
- **Template Inheritance:** Base templates with specialized variants  
- **Collaborative Templates:** Share templates across teams
- **AI-Generated Templates:** Smart template creation from examples
- **Conditional Logic:** If/then template behavior
- **Template Macros:** Complex multi-step template processing

---

## 📞 Support & Feedback

**Found a bug or have a suggestion?**
- Open an issue on the project repository
- Share your custom templates with the community
- Contribute improvements to built-in templates

**Need help?**
- Check the troubleshooting section above
- Run `copycat --status` to verify system setup
- Test with built-in templates first before creating custom ones

---

*This guide covers CopyCat Template System v1.0.0. For the latest updates and features, check the project documentation.*

**Made with ❤️ by Pink Pixel - Dream it, Pixel it ✨**