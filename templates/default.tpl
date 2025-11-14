# Default Template
# This is the standard format used for Terraform module usage blocks
#
# Available variables:
# - {module_name}: Name of the module
# - {source}: Module source URL
# - {version}: Module version
# - {required_variables}: Rendered required variables section
# - {optional_variables}: Rendered optional variables section

```hcl
module "{module_name}" {{
{source_line}{version_line}
{required_variables}
{optional_variables}}}
```
