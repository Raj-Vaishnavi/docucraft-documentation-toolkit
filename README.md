# DocuCraft

**Documentation Quality & Automation Toolkit** — a small, dependency-free Python project for checking Markdown documentation and demonstrating a practical technical-writing workflow.

DocuCraft checks required document structure, relative links to missing files, and inconsistent product terminology. It is designed as an approachable portfolio project: the product and its SafeRestore backup examples are fictional, and the linter checks writing mechanics rather than whether product claims are true.

## What’s included

- A Python command-line Markdown linter.
- Tests using Python’s built-in `unittest` framework.
- Fictional SafeRestore user guide, troubleshooting guide, release notes, and linked examples.
- A concise writing style guide, AI drafting and review prompts, and a human fact-check checklist.

## Requirements

Python 3.9 or newer. No third-party packages are required.

## Quick start

From this directory, run:

```bash
python scripts/docucraft.py docs --config docucraft.toml
```

Check an individual file:

```bash
python scripts/docucraft.py docs/user-guide.md --config docucraft.toml
```

Run the tests:

```bash
python -m unittest discover -s tests -v
```

The linter exits with status `1` when it finds errors and `0` when all checked files pass. Warnings are reported but do not fail the run. Use `--format json` for machine-readable output. Use `--no-config` to run with built-in defaults.

## Checks

1. **Title:** each file has one Markdown H1 title.
2. **Required sections:** configurable headings must be present (default: `Overview`, `Before you begin`, `Procedure`, `Troubleshooting`).
3. **Relative links:** local Markdown links and image links must resolve to an existing file. External URLs, mail links, and in-page anchors are skipped. Anchor fragments on relative links are ignored; heading-anchor existence is not checked.
4. **Terminology:** configured preferred terms are checked case-insensitively, including simple plural forms. A hit is a warning so a writer can review context.

Line numbers are included in findings. Code blocks are excluded from structure and terminology checks; links inside code blocks are ignored. The linter does not rewrite files.

## Configuration

Edit [`docucraft.toml`](docucraft.toml). Example:

```toml
required_sections = ["Overview", "Before you begin", "Procedure"]

[terminology]
"SafeRestore" = ["Safe Restore", "saferestore"]
"recovery point" = ["restore point"]
```

The TOML file uses only Python’s standard library (`tomllib`, Python 3.11+). For Python 3.9–3.10, install the optional compatibility package with `python -m pip install tomli`; the built-in defaults remain available with `--no-config`.

## Example output

```text
PASS docs/user-guide.md (0 errors, 0 warnings)
```

To see the checker catch issues, run it against [`examples/quality-sample.md`](examples/quality-sample.md). That intentionally flawed sample is excluded from the clean documentation run.

## Project layout

```text
docucraft/
├── docs/                  # Fictional SafeRestore product documentation
├── examples/              # Good and intentionally flawed Markdown samples
├── prompts/               # AI drafting/review prompts and human fact-check list
├── scripts/docucraft.py   # Standalone CLI linter
├── tests/                 # Automated unit tests
├── docucraft.toml         # Project-specific checks
└── README.md
```

## GitHub

1. Create a new **public** repository named `docucraft-documentation-toolkit` on GitHub. Leave “Add a README” unchecked because this project already includes one.
2. Extract the downloaded ZIP, open PowerShell in the extracted `docucraft` folder, then run:

   ```powershell
   git init
   git add .
   git commit -m "Add DocuCraft documentation toolkit"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/docucraft-documentation-toolkit.git
   git push -u origin main
   ```

   Replace `YOUR-USERNAME` with your GitHub username. GitHub may ask you to sign in or authorize Git. Alternatively, create the repository and use **Add file → Upload files** to upload the extracted contents.

## License

MIT. See [`LICENSE`](LICENSE).
