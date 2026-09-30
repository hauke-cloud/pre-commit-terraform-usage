<!-- llm-readme-management spec=1 commit=2577496f54ddfbf8a45c92b8248e29397e7f4994 template=python model=qwen3.8-27b-q4 digest=08ee779219f6 generated=2026-09-30T14:58:57Z -->
<a href="https://hauke.cloud" target="_blank"><img src="https://img.shields.io/badge/home-hauke.cloud-brightgreen" alt="hauke.cloud" style="display: block;" /></a>
<a href="https://github.com/hauke-cloud" target="_blank"><img src="https://img.shields.io/badge/github-hauke.cloud-blue" alt="hauke.cloud Github Organisation" style="display: block;" /></a>
<a href="https://github.com/hauke-cloud/llm-readme-management" target="_blank"><img src="https://img.shields.io/badge/template-python-orange" alt="Repository type - python" style="display: block;" /></a>


# Pre Commit Terraform Usage


<img src="https://raw.githubusercontent.com/hauke-cloud/.github/main/resources/img/organisation-logo-small.png" alt="hauke.cloud logo" width="109" height="123" align="right">


<llm header hint="Name the distribution and say whether it is a library, a CLI or a service.">

A Python CLI that parses `variables.tf` from a Terraform module and keeps a fenced usage example in the module's `README.md` in sync with declared variables. It ships as a pre-commit hook, a composite GitHub Action, a GitLab CI template, and a standalone `terraform-usage-gen` command. If you maintain Terraform modules and want usage docs validated or auto-updated in CI, keep reading.

</llm>


## :book: Description

<llm description>

Terraform module maintainers must keep a usage example in their `README.md` in sync with the variables declared in `variables.tf`. This repository provides a Python tool that automates that task: it parses the `variable` blocks, classifies each as required (no `default`) or optional (has a `default`), and rewrites a fenced HCL `module "..." { ... }` example between two HTML-comment markers in the README.

The tool ships in four forms so you can wire it into whatever pipeline you already use:

- **Pre-commit hook** (`terraform-usage-docs`) triggered on `.tf` and `.md` file changes.
- **GitHub composite Action** with `check` and `update` modes.
- **GitLab CI template** defining a `check-terraform-usage` job.
- **Standalone CLI** (`terraform-usage-gen`) for local use or custom scripts.

In check mode the tool exits non-zero when the README block has drifted; in update mode it rewrites the block in place. Module name, source URL, and version are auto-detected from the git remote and tag history (conventional-commit aware), with CLI flags to override any field. Four built-in output templates (`default`, `compact`, `minimal`, `detailed`) and a `--template` flag for custom layouts are included. Only the Python standard library is required; no Terraform binary is needed.

</llm>


## :clipboard: Requirements

<llm requirements hint="Give the Python version from requires-python or the CI matrix, and name the packaging tool actually in use (uv, poetry, pip).">

- Python 3.8 or later (CI matrix covers 3.8–3.12). The package uses only the standard library; there are no third-party runtime dependencies.
- `pip` for installation; the build backend is setuptools.
- `pre-commit` if you consume the hook via `.pre-commit-hooks.yaml`.
- A target directory that contains a `variables.tf` file and a `README.md` with the `<!-- BEGIN_AUTOMATED_TF_USAGE_BLOCK -->` and `<!-- END_AUTOMATED_TF_USAGE_BLOCK -->` markers.
- For the GitHub Action in `update` mode: `contents: write` permission and a `GITHUB_TOKEN` secret.
- No Terraform binary is required; the tool performs text parsing of `variables.tf` only.

</llm>


## 🚀 Getting started

<llm getting_started hint="Use the project's real installation path -- editable install, uv sync, poetry install -- not a generic pip install.">

1. Clone the repository.

```bash
git clone https://github.com/hauke-cloud/pre-commit-terraform-usage.git
cd pre-commit-terraform-usage
```

2. Add the two marker comments to your Terraform module's `README.md`; no installation step is needed because the tool uses only the Python 3.8+ standard library.

```markdown
<!-- BEGIN_AUTOMATED_TF_USAGE_BLOCK -->
<!-- END_AUTOMATED_TF_USAGE_BLOCK -->
```

3. From the directory that contains your `variables.tf`, run the generator to populate the block.

```bash
python3 terraform_usage_gen.py --dir .
```

The tool parses every `variable "…"` block in `variables.tf`, renders a `module "…" { … }` example with aligned Required and Optional sections, and writes it between the markers. Re-run with `--check` to verify the block is current in a CI pipeline.

</llm>


## :airplane: Usage

<llm usage hint="Show the console-script entry points by name if the packaging metadata defines any.">

Once your Terraform module has a `variables.tf` and a `README.md` containing the markers `<!-- BEGIN_AUTOMATED_TF_USAGE_BLOCK -->` and `<!-- END_AUTOMATED_TF_USAGE_BLOCK -->`, you can keep the generated usage block in sync in three ways.

**Pre-commit hook**

Add the hook to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/hauke-cloud/pre-commit-terraform-usage
    rev: v1.0.0
    hooks:
      - id: terraform-usage-docs
```

The hook triggers on commits that touch `.tf` or `.md` files. It regenerates the block and fails the commit if the README was modified, prompting you to re-stage and commit again.

**Standalone CLI**

The package installs a `terraform-usage-gen` console script. From the module directory:

```bash
terraform-usage-gen --dir . --check
```

Omit `--check` to update the README in place. Pass `--template templates/minimal.tpl` to use a different built-in layout, or run `terraform-usage-gen --list-templates` to see all four options (`default`, `compact`, `minimal`, `detailed`).

**GitHub Action**

Reference the composite action in a workflow step:

```yaml
- name: Check Terraform usage docs
  uses: hauke-cloud/pre-commit-terraform-usage@v1.0.0
  with:
    mode: check
    directory: .
```

Set `mode: update` (and grant the job `contents: write` permission) to have CI push the regenerated README automatically.

</llm>


## :wrench: Configuration

<llm configuration>

The tool is configured entirely through CLI flags and, when used as a GitHub Action, through action inputs. No environment variables or configuration files are consumed.

CLI flags (`terraform_usage/cli.py`):

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `files` (positional) | list[str] | — | Pre-commit file list; only `.tf` paths contribute directories |
| `--dir` | Path | `.` | Directory containing `variables.tf` and `README.md` |
| `--readme` | Path | `<dir>/README.md` | Explicit README path |
| `--check` | flag | off | Validate only; exit 1 on mismatch |
| `--module-name` | str | auto-detected | Override module name |
| `--source` | str | auto-detected | Override source URL |
| `--version` | str | auto-detected | Override version string |
| `--no-auto-detect` | flag | off | Disable all git-based metadata detection |
| `--force-autodetect` | flag | off | Re-detect all metadata even if README already has it |
| `--force-autodetect-source` | flag | off | Re-detect source only |
| `--force-autodetect-version` | flag | off | Re-detect version only |
| `--force-autodetect-module` | flag | off | Re-detect module name only |
| `--template` | Path | `default.tpl` | Path to a custom template file |
| `--list-templates` | flag | — | Print the four built-in templates and exit |

GitHub Action inputs (`action.yml`):

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `mode` | `check` \| `update` | `check` | Validate or rewrite the block |
| `directory` | str | `.` | Target module directory |
| `readme-path` | str | `''` | Explicit README path (falls back to `<directory>/README.md`) |
| `fail-on-diff` | bool | `true` | Fail the step when the block differs (check mode) |

The tool reads `variable` blocks from `variables.tf` in the target directory and writes between the `<!-- BEGIN_AUTOMATED_TF_USAGE_BLOCK -->` / `<!-- END_AUTOMATED_TF_USAGE_BLOCK -->` markers in the README. The complete flag definitions live in `terraform_usage/cli.py`.

</llm>


## :hammer: Development

<llm development hint="Cover the test runner, the linter and any pre-commit hooks the repository configures.">

Install development dependencies:

```bash
pip install pytest pytest-cov black flake8 isort mypy
```

Run the test suite:

```bash
python -m pytest tests/ -v
```

CI executes the same suite across Python 3.8–3.12 on Ubuntu, macOS, and Windows. A failing test on any combination blocks the pull request.

Format and lint locally:

```bash
black terraform_usage tests
isort terraform_usage tests
flake8 terraform_usage tests --max-line-length=120
mypy terraform_usage --ignore-missing-imports
```

The CI lint step runs flake8, black, and isort with `continue-on-error: true`, so style violations do not block a merge. mypy is installed in the CI environment but never invoked.

The repository configures a pre-commit hook (`.pre-commit-config.yaml`) that references the published `terraform-usage-docs` hook at `rev: v1.0.0`. Run it locally with:

```bash
pre-commit run --all-files
```

Because no `variables.tf` exists at the repository root, the hook is a no-op here; it takes effect when downstream Terraform module repositories consume the hook.

There is no conventional-commit title check or generated-file regeneration step in the CI workflows.

</llm>


## 📄 License

This Project is licensed under the GNU General Public License v3.0

- see the [LICENSE](LICENSE) file for details.


## :coffee: Contributing

To become a contributor, please check out the [CONTRIBUTING](CONTRIBUTING.md) file.


## :email: Contact

For any inquiries or support requests, please open an issue in this
repository or contact us at [contact@hauke.cloud](mailto:contact@hauke.cloud).
