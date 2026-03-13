# Container Security Tools Setup

## Trivy

### macOS (Homebrew)
```bash
brew install trivy
```

### Linux (binary)
```bash
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
```

### Docker (no local install)
```bash
docker run --rm -v $(pwd):/src aquasec/trivy:latest config /src
```

### Air-Gapped Setup
Download the vulnerability database on an internet-connected machine:
```bash
trivy image --download-db-only
# DB is stored at ~/.cache/trivy/db/
```

Copy `~/.cache/trivy/` to the air-gapped host. Then run with:
```bash
trivy config --skip-db-update --offline-scan <path>
trivy image --skip-db-update --offline-scan <image>
```

## Kubescape

### Install
```bash
# macOS / Linux
curl -s https://raw.githubusercontent.com/kubescape/kubescape/master/install.sh | /bin/bash
```

### Air-Gapped Setup
Download frameworks on an internet-connected machine:
```bash
kubescape download framework nsa --output nsa-framework.json
kubescape download framework mitre --output mitre-framework.json
```

Copy framework files to air-gapped host. Run with:
```bash
kubescape scan framework nsa --use-from nsa-framework.json <k8s-dir>
```

## Docker

Required only for image scanning. Install via:
- macOS: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Linux: `apt install docker.io` or `dnf install docker`

## Verification

```bash
which trivy && trivy version || echo "trivy not installed"
which kubescape && kubescape version || echo "kubescape not installed"
which docker && docker --version || echo "docker not installed"
```
