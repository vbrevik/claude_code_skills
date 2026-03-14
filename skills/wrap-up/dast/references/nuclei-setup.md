# Nuclei Setup

## Installation

### macOS
```bash
brew install nuclei
```

### Linux (Go install)
```bash
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
```

### Linux (binary)
```bash
curl -sSL https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_$(uname -s)_$(uname -m).zip -o nuclei.zip
unzip nuclei.zip nuclei && mv nuclei /usr/local/bin/ && rm nuclei.zip
```

### Docker (air-gapped alternative)
```bash
docker pull projectdiscovery/nuclei
docker run --rm --network host -v /path/to/templates:/templates projectdiscovery/nuclei -u http://localhost:5173 -t /templates/
```

## Verify Installation
```bash
nuclei --version
```

## Air-Gapped Usage

Nuclei runs fully local with bundled templates. Disable automatic template updates:

```bash
nuclei -u <target> -t /path/to/templates/ -duc
```

The `-duc` flag disables automatic update checks. The `-t` flag points to bundled template directory.

## JSON Output

```bash
nuclei -u <target> -t /path/to/templates/ -jsonl -o findings.jsonl -duc
```

JSONL (one JSON object per line) is the output format consumed by the `nuclei_to_findings.py` script.
