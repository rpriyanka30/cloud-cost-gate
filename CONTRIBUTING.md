# Contributing to Cloud-Cost-Gate

Thank you for your interest in contributing to Cloud-Cost-Gate!

Cloud-Cost-Gate is an open-source Python-based FinOps tool that analyzes Terraform configurations, estimates AWS infrastructure costs, and checks whether deployments stay within a defined budget.

We welcome bug reports, improvements, documentation updates, and new feature contributions.

## 1. Getting Started

### Prerequisites

Before contributing, make sure you have:

- Python 3.11 or later
- Git
- AWS CLI (required for live AWS pricing queries)
- An AWS account with permission to access the AWS Pricing API

### Clone the Repository

```bash
git clone https://github.com/rpriyanka30/cloud-cost-gate.git
cd cloud-cost-gate
```

### Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### Install Dependencies

Install the application dependencies:

```bash
python -m pip install -r requirements.txt
```

Install development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

## 2. Running the Project

Analyze the example Terraform configuration:

```bash
python -m cloud_cost.cli examples/main.tf --budget 25
```

The tool analyzes the configured resources, estimates their monthly costs, and compares the total against the specified budget.

Live AWS pricing requires valid AWS credentials and access to the AWS Pricing API.

## 3. Running Tests

Before submitting changes, run:

```bash
python -m pytest -q
```

All tests should pass.

## 4. Code Quality Checks

We use the following tools to maintain code quality.

**Black — Code formatting**

```bash
python -m black --check cloud_cost tests
```

**Flake8 — Code linting**

```bash
python -m flake8 cloud_cost tests
```

**Mypy — Static type checking**

```bash
python -m mypy cloud_cost
```

Please resolve any reported issues before submitting your changes.

## 5. Contribution Guidelines

- Keep changes focused and easy to understand.
- Follow the existing project structure and coding style.
- Add or update tests when changing functionality.
- Update documentation when introducing new features.
- Do not commit AWS credentials, access keys, passwords, or other secrets.
- Do not commit virtual environments, cache files, or temporary pricing data.

## 6. Submitting Changes

1. Create a separate branch for your contribution.

```bash
git checkout -b feature/your-feature-name
```

2. Make your changes.

3. Run the tests and code quality checks.

4. Commit your changes with a meaningful message.

```bash
git add .
git commit -m "Describe your changes"
```

5. Push your branch.

```bash
git push origin feature/your-feature-name
```

6. Open a Pull Request on GitHub and explain what you changed.

## 7. Reporting Issues

If you find a bug or have a feature suggestion, open an issue in the GitHub repository.

Include:
- A clear description of the problem.
- Steps to reproduce it.
- Expected and actual behavior.
- Relevant error messages, if applicable.

## 8. Thank You!

Every contribution helps improve Cloud-Cost-Gate.

Thank you for helping make cloud cost estimation more accessible and transparent!