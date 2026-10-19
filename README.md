# Cloud-Cost-Gate ☁️

**Catch cloud costs before your infrastructure changes are merged.**

Cloud-Cost-Gate is a Python-based tool designed to analyze Terraform infrastructure changes, estimate their potential monthly cloud costs, and help teams enforce spending policies before approving changes.

## Problem

Cloud infrastructure changes can increase monthly expenses without developers realizing the financial impact.

Cloud-Cost-Gate aims to make infrastructure costs more visible during code review.

## Planned Features

- Parse Terraform infrastructure files.
- Identify supported AWS resources and their configurations.
- Estimate monthly infrastructure costs.
- Compare infrastructure costs before and after changes.
- Generate readable cost reports.
- Comment automatically on GitHub Pull Requests.
- Enforce configurable spending limits.

## Technology Stack

- Python
- Terraform / HCL
- python-hcl2
- PyYAML
- AWS Pricing API
- PyGithub
- GitHub Actions

## Current Status

The initial development version includes a Terraform parser for basic resource configurations.

Pricing integration, cost-delta analysis, automated Pull Request comments, and policy enforcement are planned features.

## Project Goal

Help developers understand the potential financial impact of infrastructure changes before those changes are approved.

## License

MIT License — to be added when the project is prepared for open-source release.