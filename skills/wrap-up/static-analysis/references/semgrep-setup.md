# Semgrep Setup

## Installation

### macOS
```bash
brew install semgrep
```

### Linux (pip)
```bash
pip install semgrep
```

### Linux (binary)
```bash
curl -sSL https://semgrep.dev/static/install.sh | sh
```

### Docker (air-gapped alternative)
```bash
docker pull semgrep/semgrep
docker run --rm -v "$(pwd):/src" semgrep/semgrep semgrep --config /rules /src
```

### Windows (WSL)
Install via pip or brew inside WSL.

## Verify Installation
```bash
semgrep --version
```

## Air-Gapped Usage

Semgrep runs fully local with bundled rules. No network access needed.

```bash
# Run with local rules only (no registry fetch)
semgrep --config /path/to/rules/ --no-git-ignore target/
```

The `--config` flag points to a directory of YAML rule files. Semgrep loads all `.yaml` files recursively.

## SARIF Output

```bash
semgrep --config /path/to/rules/ --sarif -o findings.sarif target/
```

SARIF (Static Analysis Results Interchange Format) is the standard output format consumed by the `sarif_to_findings.py` script.
