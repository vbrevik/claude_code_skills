# Gitleaks Setup

## Installation

### macOS (Homebrew)

```bash
brew install gitleaks
```

### Linux (Go install)

```bash
go install github.com/gitleaks/gitleaks/v8@latest
```

Requires Go 1.21+. Binary lands in `$GOPATH/bin/` (ensure this is in your `$PATH`).

### Linux (Pre-built binary)

```bash
VERSION=8.30.0
curl -sSL "https://github.com/gitleaks/gitleaks/releases/download/v${VERSION}/gitleaks_${VERSION}_linux_x64.tar.gz" \
  | tar xz -C /usr/local/bin gitleaks
```

### Docker (any platform)

```bash
docker run --rm -v "$(pwd):/repo" zricethezav/gitleaks:latest detect --source /repo
```

Useful for CI pipelines or when local install is not desired.

## Air-Gap Installation

For air-gapped / RESTRICTED environments:

1. Download the release tarball on an internet-connected machine
2. Transfer via approved media to the air-gapped system
3. Extract to a directory in `$PATH`

The skill's custom config (`assets/gitleaks.toml`) is bundled and does not require network access at runtime.

## Verify Installation

```bash
gitleaks version
# Expected: 8.x.x
```

## Fallback

If gitleaks cannot be installed, the `run_scan.sh` script falls back to grep-based pattern matching. This catches common patterns (API keys, passwords, private keys) but is less comprehensive than gitleaks' rule engine.
