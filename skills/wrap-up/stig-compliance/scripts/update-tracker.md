# Tracker Maintenance Guide

## Quarterly Reference Update

DISA releases STIG updates quarterly. To update:

1. Check https://public.cyber.mil/stigs/ for new ASD STIG version
2. Compare new controls against `references/asd-stig-controls.md`
3. Add new controls to appropriate categories
4. Update removed/modified controls
5. Update the `last-updated` and `stig-version` in the frontmatter
6. Run `/stig-compliance review --full` to re-baseline

## Tracker File Management

- `docs/compliance/stig-status.md` is the cumulative tracker
- Each review updates it automatically
- To reset: delete the file and run `/stig-compliance review --full`
- Per-check reports in `docs/compliance/reports/` are append-only history
