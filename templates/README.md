# Templates Directory

This directory contains built-in templates for the Terraform Usage Block Validator.

## Available Templates

- **default.tpl** - Standard format with code fences and section headers (used when no template is specified)
- **compact.tpl** - Compact format without extra spacing
- **minimal.tpl** - Just the module block without markdown code fences
- **detailed.tpl** - Extended format with usage instructions and documentation

## Using Templates

```bash
# Use a built-in template
python3 terraform_usage_gen.py --template templates/minimal.tpl

# List all available templates
python3 terraform_usage_gen.py --list-templates
```

## Creating Custom Templates

See [TEMPLATES.md](../TEMPLATES.md) for complete documentation on creating custom templates.

### Template Variables

- `{module_name}` - Module name
- `{source}` - Module source URL
- `{version}` - Module version
- `{source_line}` - Formatted source line
- `{version_line}` - Formatted version line
- `{required_variables}` - Required variables section (pre-formatted)
- `{optional_variables}` - Optional variables section (pre-formatted)

### Example Custom Template

Create a file `custom.tpl`:

```
# My Custom Template

```hcl
module "{module_name}" {{
{source_line}{version_line}
{required_variables}
{optional_variables}}}
```
```

Then use it:

```bash
python3 terraform_usage_gen.py --template custom.tpl
```

## Template Format

- Lines starting with `#` are comments and are removed
- Use double curly braces `{{` `}}` for literal braces
- Use single curly braces `{variable}` for variables
- Variables are replaced during generation
