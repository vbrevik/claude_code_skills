# SCA Tools Setup

## Syft (SBOM Generation)

### macOS (Homebrew)
```bash
brew install syft
```

### Linux (curl)
```bash
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
```

### Docker
```bash
docker run --rm -v $(pwd):/project anchore/syft:latest scan dir:/project -o cyclonedx-json
```

### Verify
```bash
syft version
```

## Grype (Vulnerability Scanner)

### macOS (Homebrew)
```bash
brew install grype
```

### Linux (curl)
```bash
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin
```

### Docker
```bash
docker run --rm -v /tmp:/tmp anchore/grype:latest sbom:/tmp/sbom.json -o json
```

### Verify
```bash
grype version
```

## Air-Gap Setup (Grype Database)

For RESTRICTED environments without internet access, pre-download the Grype vulnerability database:

### On Connected Machine

```bash
# Download the latest DB archive
grype db download

# Find the DB location
grype db status
# Output shows: Location: /Users/<user>/Library/Caches/grype/db/5/

# Copy the entire db directory for transfer
tar czf grype-db-export.tar.gz -C ~/Library/Caches/grype/db .
```

### On Air-Gapped Machine

```bash
# Create cache directory
mkdir -p /opt/grype/db

# Extract pre-downloaded DB
tar xzf grype-db-export.tar.gz -C /opt/grype/db/

# Set environment variable
export GRYPE_DB_CACHE_DIR=/opt/grype/db

# Verify DB is recognized
grype db status
```

### Configuration

Use the provided `assets/grype-config.yaml`:

```bash
# Copy config to grype's expected location
cp ~/.claude/skills/sca/assets/grype-config.yaml ~/.grype.yaml
```

Key settings for air-gap:
- `db.auto-update: false` — prevents attempted internet access
- `check-for-app-update: false` — prevents update check

### DB Update Schedule

The Grype vulnerability database should be refreshed:
- **Minimum**: Monthly
- **Recommended**: Weekly
- **After major CVE announcements**: As soon as practical

Transfer updated DB via approved removable media per site security policy.

## npm audit (Fallback)

No additional installation needed if Node.js/npm is available:

```bash
npm --version  # Verify npm is available
npm audit --json  # Run audit with JSON output
```

Limitations of npm audit fallback:
- Only covers npm ecosystem dependencies
- Does not produce CycloneDX SBOM
- No license analysis capability
- Severity mapping is approximate (npm uses its own severity scale)
