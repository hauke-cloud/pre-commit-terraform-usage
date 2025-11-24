# Terraform Usage Block Validator

A multi-platform tool to validate and auto-generate Terraform usage blocks in README.md files. Works as a pre-commit hook, GitLab CI template, and GitHub Action.

## Features

- 🔍 **Validates** that your README usage block matches your `variables.tf`
- ✨ **Auto-generates** usage blocks with required/optional variables separated
- 🎯 **Multi-platform**: Pre-commit hook, GitLab CI, GitHub Actions
- 📝 **Clear formatting**: Shows descriptions, defaults, and types
- 🚀 **Easy integration**: Works with existing Terraform workflows

## Quick Start

### As a Standalone Script

```bash
# Check if usage block is up-to-date
python3 terraform_usage_gen.py --check

# Update the usage block
python3 terraform_usage_gen.py

# Specify directory
python3 terraform_usage_gen.py --dir ./terraform --readme ./docs/README.md
```

### As a Pre-commit Hook

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/hauke-cloud/pre-commit-terraform-usage
    rev: v1.0.0
    hooks:
      - id: terraform-usage-docs
```

### As a GitHub Action

```yaml
- name: Check Terraform Usage Block
  uses: hauke-cloud/pre-commit-terraform-usage@v1
  with:
    mode: 'check'
```

### As a GitLab CI Template

```yaml
include:
  - remote: 'https://github.com/hauke-cloud/pre-commit-terraform-usage/.gitlab-ci-template.yml'
```

## Installation

```bash
# Clone the repository
git clone https://github.com/hauke-cloud/pre-commit-terraform-usage.git
cd pre-commit-terraform-usage

# Run setup (optional, installs pre-commit)
./setup.sh
```

No external dependencies required - uses Python 3.6+ standard library only.

## Command-Line Options

```bash
# Disable automatic detection of module name, source, and version from git
python3 terraform_usage_gen.py --no-auto-detect

# Force auto-detection even when version/source/module metadata exists in README
python3 terraform_usage_gen.py --force-autodetect

# Specify custom module name, source, and version
python3 terraform_usage_gen.py --module-name "my-module" --source "github.com/user/repo" --version "v2.0.0"
```

## Usage Example

Given a `variables.tf`:

```hcl
variable "instance_name" {
  description = "Name of the OpenStack instance"
  type        = string
}

variable "tags" {
  description = "List of tags to assign"
  type        = list(string)
  default     = []
}
```

The tool generates:

```hcl
module "example" {
  source = "..."
  
  ###########
  # Required #
  ###########
  instance_name = # Required: Name of the OpenStack instance
  
  ###########
  # Optional #
  ###########
  # tags = [] # Optional: List of tags to assign
}
```

---

# nova-instance

Provides a Openstack Nova instance

## Usage

```hcl
module "nova-instance" {
  source  = "git.example.de/example-playground/nova-instance/local"
  version = "v1.0.0"

<!-- BEGIN_AUTOMATED_TF_USAGE_BLOCK -->
  ############
  # Required #
  ############
  instance_name                     = # Required: Name of the OpenStack instance
  flavor_name                       = # Required: Flavor name for the instance
  image_id                          = # Required: Image UUID to use for the instance
  key_pair_name                     = # Required: SSH key pair name
  networks                          = # Required: List of networks to attach to the instance

  ############
  # Optional #
  ############
  # metadata                          = {} # Optional: Metadata key/value pairs to assign to the instance
  # tags                              = [] # Optional: List of tags to assign to the instance
  # assign_floating_ip                = false # Optional: Whether to assign a floating IP to the instance
  # floating_ip_pool                  = "public" # Optional: Name of the floating IP pool
  # additional_security_groups        = [] # Optional: List of additional security group names to assign to the instance
  # ingress_rules                     = ... # Optional: List of ingress security group rules
  # egress_rules                      = ... # Optional: List of egress security group rules
  # root_volume_size                  = 20 # Optional: Size of the root volume in GB
  # delete_root_volume_on_termination = true # Optional: Whether to delete the root volume when the instance is terminated
  # additional_volumes                = [] # Optional: List of additional volumes to create and attach
  # cloud_init_config                 = "" # Optional: Custom cloud-init configuration (base64 encoded). If empty, uses the default template
  # cloud_init_vars                   = {} # Optional: Variables to pass to the cloud-init template
<!-- END_AUTOMATED_TF_USAGE_BLOCK -->
}
```

<!-- BEGIN_AUTOMATED_TF_DOCS_BLOCK -->
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->

# Contributing

Contributions are welcome. However, we would ask you to follow to the usual code guidelines and use the [SVU](https://github.com/caarlos0/svu) semantic pipeline functions.

:no_entry: **Please avoid using MANUAL GIT TAGS**
=======

### Setting up Pre-Commit

We use pre-commit to run checks and linters before each commit. Follow these steps to set up:

1. **Install ```pre-commit```**

```bash
pip install pre-commit
```

2. **Install the Git Hook**
From the repository’s root directory:

```bash
pre-commit install
```

3. **Run Pre-Commit manually**

```bash
pre-commit run --all-files
```

### GitLab CI Integration

To automatically check if the usage block is up-to-date in your CI/CD pipeline, see [GITLAB_CI.md](GITLAB_CI.md) for integration instructions.

### Versioning with ```caarlos0/svu```

We use [caarlos0/svu](https://github.com/caarlos0/svu) to manage semantic versioning of our charts. This tool helps us bump version numbers in a standardized way following [SemVer](https://semver.org/) rules.

1. **Bump version**
In the root directory of your project (or wherever your chart Chart.yaml is stored), you can bump patch, minor, or major versions:

```bash
# Bump patch version (e.g., 1.0.0 -> 1.0.1)
git commit "fix: example"

# Bump minor version (e.g., 1.0.0 -> 1.1.0)
git commit "feat: example"

# Bump major version (e.g., 1.0.0 -> 2.0.0)
git commit "fix!/feat! example"
```
