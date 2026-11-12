# Cloud-Cost-Gate

**Catch cloud costs before your infrastructure changes are merged.**

Cloud-Cost-Gate is a Python-based FinOps automation tool that analyzes Terraform infrastructure configurations, estimates monthly AWS costs, and checks them against a defined budget.

It integrates with GitHub Actions to automatically run cost checks and publish Markdown cost reports on Pull Requests.

## Features

- **Terraform Parsing:** Reads Terraform (`.tf`) files and identifies supported AWS resources.
- **AWS Cost Estimation:** Uses the AWS Pricing API to retrieve pricing information for supported resources.
- **Budget Enforcement:** Compares estimated monthly costs against a user-defined budget and returns PASS or FAIL.
- **Markdown Reports:** Generates readable cost reports containing resource-level costs and the estimated monthly total.
- **GitHub Actions Integration:** Automatically runs tests and cost checks on pushes and Pull Requests targeting `master`.
- **Automatic PR Comments:** Publishes the generated cost report directly on GitHub Pull Requests.
- **Automated Testing:** Uses pytest to validate parsing, pricing, cost calculations, and budget policies.
- **Secure AWS Authentication:** Uses GitHub Actions OIDC to assume an AWS IAM role with temporary credentials.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application and cost calculations |
| Terraform / HCL | Infrastructure configuration |
| python-hcl2 | Terraform file parsing |
| AWS Pricing API | AWS pricing information |
| Boto3 | AWS service integration |
| PyYAML | Configuration handling |
| pytest | Automated testing |
| Git & GitHub | Version control and collaboration |
| GitHub Actions | CI/CD automation |
| AWS IAM & STS | Secure identity and temporary credentials |
| GitHub OIDC | Keyless authentication from GitHub Actions |

##  How It Works

1. A developer creates or updates Terraform infrastructure code.
2. Cloud-Cost-Gate parses the Terraform configuration.
3. Supported AWS resources are identified.
4. The tool retrieves applicable pricing information and estimates monthly costs.
5. The estimated total is compared against the configured budget.
6. A Markdown report is generated.
7. GitHub Actions publishes the report as a Pull Request comment.
8. The workflow fails if the cost check fails.

##  Project Structure

```text
cloud-cost-gate/
|
|-- .github/
|   |-- workflows/
|       |-- cloud-cost-gate.yml
|
|-- cloud_cost/
|   |-- __init__.py
|   |-- cli.py
|   |-- cost_calculator.py
|   |-- parser.py
|   |-- policy.py
|   |-- pricing.py
|   |-- report.py
|
|-- examples/
|   |-- main.tf
|
|-- tests/
|   |-- test_cli.py
|   |-- test_cost_calculator.py
|   |-- test_parser.py
|   |-- test_policy.py
|   |-- test_pricing.py
|
|-- requirements.txt
|-- README.md
|-- .gitignore
```

##  Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/rpriyanka30/cloud-cost-gate.git
cd cloud-cost-gate
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the cost analysis

```bash
python -m cloud_cost.cli examples/main.tf --budget 25 --report cost-report.md
```

The command analyzes the example Terraform configuration, checks it against a monthly budget of $25, and generates a Markdown report.

### 5. Run automated tests

```bash
python -m pytest -v
```

##  Sample Output

```text
Cloud-Cost-Gate: Cost Analysis
===================================
web_server: $7.59/month
app_database: $12.41/month
-----------------------------------
Estimated monthly total: $20.00
Monthly budget:          $25.00
Status:                  PASS
Message:                 Within budget.
```

If the estimated cost exceeds the configured budget, the tool returns a FAIL status and exits with a non-zero exit code.

##  Security

Cloud-Cost-Gate uses GitHub Actions OpenID Connect (OIDC) to authenticate with AWS.

- No long-term AWS access keys are stored in GitHub repository secrets for this workflow.
- GitHub Actions assumes a dedicated AWS IAM role.
- AWS STS provides temporary credentials.
- IAM permissions are restricted to the required AWS Pricing API access.

##  Cost Estimation Disclaimer

Cost estimates are indicative and should not be treated as exact AWS bills.

Actual costs may vary based on usage, region, resource configuration, data transfer, discounts, taxes, and other pricing factors. Only supported resource configurations and pricing dimensions are included.

##  Project Goal

The goal of Cloud-Cost-Gate is to bring cost awareness into the development workflow by helping teams identify potential infrastructure expenses before changes are merged.

## Project Status

**Phases 1–6 completed. Phase 7: Open-source release preparation in progress.**

##  License

The project will be released under the MIT License. The LICENSE file will be added before the v1.0.0 release.

##  Author

**R Priyanka**

GitHub: [rpriyanka30](https://github.com/rpriyanka30)
