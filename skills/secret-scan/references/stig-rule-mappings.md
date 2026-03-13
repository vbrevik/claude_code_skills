# STIG Rule Mappings

Mapping from gitleaks rule IDs to DISA STIG V-IDs.

## V-222642 — No Embedded Authenticators (CAT I)

> The application must not contain embedded authentication data.

| Gitleaks Rule ID | Description |
|---|---|
| `generic-api-key` | Generic API key patterns |
| `private-key` | RSA/DSA/EC/PGP private keys |
| `aws-access-key-id` | AWS access key ID |
| `aws-secret-access-key` | AWS secret access key |
| `gcp-api-key` | Google Cloud Platform API key |
| `gcp-service-account` | GCP service account key file |
| `azure-storage-key` | Azure storage account key |
| `github-pat` | GitHub personal access token |
| `github-oauth` | GitHub OAuth token |
| `github-app-token` | GitHub App token |
| `github-refresh-token` | GitHub refresh token |
| `gitlab-pat` | GitLab personal access token |
| `jwt-token` | JSON Web Tokens (static/embedded) |
| `slack-token` | Slack bot/user/webhook tokens |
| `slack-webhook` | Slack incoming webhook URL |
| `stripe-api-key` | Stripe secret/publishable key |
| `twilio-api-key` | Twilio API key |
| `sendgrid-api-key` | SendGrid API key |
| `npm-access-token` | npm access token |
| `pypi-upload-token` | PyPI upload token |
| `nuget-api-key` | NuGet API key |
| `docker-config` | Docker registry credentials |
| `heroku-api-key` | Heroku API key |
| `hashicorp-tf-password` | Terraform Cloud/Enterprise token |
| `vault-token` | HashiCorp Vault token |
| `ssh-password` | SSH password in config |
| `encryption-key` | Hardcoded encryption keys |
| `generic-password` | Generic password assignments |

## V-222543 — Encrypted Credential Transmission (CAT I)

> The application must transmit credentials only over encrypted channels.

| Gitleaks Rule ID | Description |
|---|---|
| `password-in-url` | Credentials embedded in URLs (e.g., `postgres://user:pass@host`) |
| `connection-string` | Database connection strings with inline credentials |

## Default Mapping

Any gitleaks rule ID not listed above defaults to **V-222642 (CAT I)**, since all secret detection inherently relates to embedded authenticators.
