# Cloud-Cost-Gate

**Catch cloud costs before your infrastructure changes are merged.**

Cloud-Cost-Gate is a Python-based FinOps automation tool that analyzes Terraform infrastructure configurations, estimates monthly AWS costs using the AWS Price List API, and checks them against a configurable budget.

It integrates with GitHub Actions to automatically run cost checks, generate Markdown cost reports, and publish reports on Pull Requests. When estimated costs exceed the configured budget, the workflow fails and can block merging through GitHub branch protection rules.

### How Do Users Interact With Cloud-Cost-Gate?

Cloud-Cost-Gate is a developer-focused command-line tool and GitHub Actions integration. It does not require a website, dashboard, or manual file upload.

Users interact with it through:

1. **Terraform files (`.tf`)** – Define the AWS infrastructure they want to analyze.
2. **`.cloud-cost.yml`** – Configure their monthly budget and Terraform directory.
3. **GitHub Actions** – Automatically run cost analysis when they create or update a pull request.
4. **Pull request comments** – View the estimated monthly cost, budget status, and cost report directly on GitHub.

For local testing, developers can also run Cloud-Cost-Gate using its Python CLI.

## Features

- **Terraform Parsing:** Reads Terraform (`.tf`) files and identifies supported AWS resources.
- **Live AWS Pricing:** Retrieves applicable compute and storage prices through the AWS Price List API.
- **Cost Estimation:** Estimates monthly compute and storage costs.
- **Budget Enforcement:** Compares estimated costs against a configurable monthly budget and returns PASS or FAIL.
- **Markdown Reports:** Generates resource-level cost breakdowns and monthly totals.
- **GitHub Actions Integration:** Automatically runs cost checks on pushes and Pull Requests targeting `master`.
- **Automatic PR Comments:** Publishes and updates cost reports directly on Pull Requests.
- **Merge Protection:** Supports GitHub required status checks to prevent merging when the cost gate fails.
- **Automated Testing:** Uses pytest to validate parsing, pricing, cost calculations, policies, CLI behavior, and reports.
- **Secure AWS Authentication:** Uses GitHub Actions OIDC and temporary AWS credentials instead of long-term access keys.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application and cost calculations |
| Terraform / HCL | Infrastructure configuration |
| python-hcl2 | Terraform file parsing |
| AWS Price List API | AWS pricing information |
| Boto3 | AWS API integration |
| PyYAML | Configuration handling |
| pytest | Automated testing |
| Git & GitHub | Version control |
| GitHub Actions | CI/CD automation |
| AWS IAM & STS | Permissions and temporary credentials |
| GitHub OIDC | Secure authentication |

## How It Works

1. A developer creates or updates Terraform infrastructure code.
2. A Pull Request is opened against `master`.
3. GitHub Actions authenticates with AWS using OIDC.
4. Cloud-Cost-Gate parses the Terraform configuration.
5. Supported AWS resources are identified.
6. Applicable AWS compute and storage prices are retrieved.
7. Estimated monthly costs are calculated.
8. The estimated total is compared against the configured budget.
9. A Markdown cost report is published on the Pull Request.
10. The workflow fails if the estimated cost exceeds the budget.

With the corresponding GitHub branch protection rule enabled, a failed cost check prevents the Pull Request from being merged.

## Project Structure

```text
cloud-cost-gate/
│
├── .github/
│   └── workflows/
│       └── cloud-cost-gate.yml
│
├── cloud_cost/
│   ├── __init__.py
│   ├── cli.py
│   ├── cost_calculator.py
│   ├── parser.py
│   ├── policy.py
│   ├── pricing.py
│   └── report.py
│
├── examples/
│   ├── demo/
│   │   └── main.tf
│   └── main.tf
│
├── tests/
│   ├── test_cli.py
│   ├── test_cost_calculator.py
│   ├── test_parser.py
│   ├── test_policy.py
│   ├── test_pricing.py
│   └── test_report.py
│
├── .cloud-cost.yml
├── .gitignore
├── requirements.txt
├── README.md
└── LICENSE
```

## Getting Started

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

### 4. Configure the budget

Edit `.cloud-cost.yml`:

```yaml
monthly_budget: 25
terraform_directory: examples/demo
```

### 5. Configure AWS credentials

For local execution, configure AWS credentials with permission to access the AWS Pricing API.

For GitHub Actions, configure the required AWS IAM OIDC trust relationship and pricing permissions.

### 6. Run cost analysis

```bash
python -m cloud_cost.cli --report cost-report.md
```

The CLI reads the configured Terraform directory and monthly budget, estimates costs, and generates a Markdown report.

### 7. Run automated tests

```bash
python -m pytest -v
```

## Sample Output

Example output from a successful cost analysis:

```text
Cloud-Cost-Gate: Cost Analysis
===================================
web_server: $9.19/month
app_database: $14.71/month
-----------------------------------
Estimated monthly total: $23.90
Monthly budget:          $25.00
Status:                  PASS
Message:                 Within budget.
```

When the estimated monthly cost exceeds the configured budget, the tool returns FAIL and exits with a non-zero exit code.

## Testing and Validation

The project has been tested with:

- Automated Python test suite: **39 tests passed**.
- Terraform resource parsing.
- Live AWS compute and storage pricing retrieval.
- Monthly cost calculations.
- Budget PASS and FAIL scenarios.
- Markdown report generation.
- GitHub Actions execution.
- Successful Pull Request cost report publication.
- Over-budget Pull Request failure.
- GitHub branch protection preventing an over-budget merge.

## Security

Cloud-Cost-Gate uses GitHub Actions OpenID Connect (OIDC) to authenticate with AWS.

- No long-term AWS access keys are stored in GitHub repository secrets for the workflow.
- GitHub Actions assumes a dedicated AWS IAM role.
- AWS STS supplies temporary credentials.
- IAM permissions are limited to the required AWS Pricing API access.

## Cost Estimation Limitations

Cloud-Cost-Gate provides estimates, not exact AWS bills.

Current implementation limitations include:

- Supports selected EC2 and RDS configurations.
- Supports a defined set of AWS regions.
- RDS storage pricing currently supports MySQL configurations.
- RDS Multi-AZ configurations are not supported.
- Additional gp3 IOPS and throughput charges are not included.
- Data transfer, snapshots, backups, taxes, discounts, and other unmodeled charges are excluded.
- Compute estimates assume 730 hours per month.

Actual AWS costs may differ depending on usage, region, configuration, discounts, and other pricing factors.

## Project Goal

The goal of Cloud-Cost-Gate is to introduce cost awareness into the infrastructure development lifecycle by identifying potential AWS expenses before infrastructure changes are merged.

## Project Status

**Core implementation and end-to-end pull-request validation completed.**

The project has successfully demonstrated live pricing retrieval, budget enforcement, automated PR reporting, and merge protection.

Further improvements may include additional AWS resources, regions, pricing dimensions, and estimation accuracy.

## License

Cloud-Cost-Gate is licensed under the MIT License.

You are free to use, modify, distribute, and contribute to this project under the terms of the MIT License. See the LICENSE file for details.

## Author

**R Priyanka**

GitHub: https://github.com/rpriyanka30



