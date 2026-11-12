import argparse
import math
from pathlib import Path

import yaml

from cloud_cost.report import generate_markdown_report
from cloud_cost.cost_calculator import (
    estimate_terraform_cost,
    estimate_terraform_files,
)


def load_config(config_path):
    """Load and validate the Cloud-Cost-Gate YAML configuration."""

    if not config_path.is_file():
        return {}

    with open(config_path, "r", encoding="utf-8-sig") as file:
        config = yaml.safe_load(file)

    if config is None:
        return {}

    if not isinstance(config, dict):
        raise ValueError("Configuration must contain YAML key-value settings.")

    return config


def main():
    parser = argparse.ArgumentParser(
        description="Estimate AWS costs from Terraform files."
    )

    parser.add_argument(
        "terraform_files",
        nargs="*",
        help="Terraform files or a directory containing Terraform files",
    )

    parser.add_argument(
        "--budget",
        type=float,
        help="Optional monthly budget override in USD",
    )

    parser.add_argument(
        "--config",
        default=".cloud-cost.yml",
        help="Path to the YAML configuration file",
    )

    parser.add_argument(
        "--report",
        help="Path to save the Markdown cost report",
    )

    args = parser.parse_args()

    try:
        config_path = Path(args.config).resolve()
        config = load_config(config_path)

        configured_budget = config.get("monthly_budget")

        if args.budget is not None:
            budget = args.budget
        else:
            budget = configured_budget

        if (
            isinstance(budget, bool)
            or not isinstance(budget, (int, float))
            or not math.isfinite(budget)
            or budget < 0
        ):
            raise ValueError(
                "Provide a valid non-negative monthly_budget "
                "in .cloud-cost.yml or use --budget."
            )

        if args.terraform_files:
            paths = [Path(path) for path in args.terraform_files]
        else:
            terraform_directory = config.get("terraform_directory", ".")

            if (
                not isinstance(terraform_directory, str)
                or not terraform_directory.strip()
            ):
                raise ValueError(
                    "terraform_directory must be a valid directory path."
                )

            paths = [config_path.parent / terraform_directory]

        if len(paths) == 1 and paths[0].is_dir():
            terraform_files = sorted(paths[0].glob("*.tf"))

            if not terraform_files:
                raise ValueError(
                    "No Terraform .tf files found in the directory."
                )

            result = estimate_terraform_files(
                terraform_files,
                budget,
            )

        elif len(paths) == 1:
            result = estimate_terraform_cost(
                paths[0],
                budget,
            )

        else:
            result = estimate_terraform_files(
                paths,
                budget,
            )

    except (
        ValueError,
        KeyError,
        FileNotFoundError,
        OSError,
        yaml.YAMLError,
    ) as error:
        parser.error(str(error))

    print("\nCloud-Cost-Gate: Cost Analysis")
    print("=" * 35)

    for resource in result["resources"]:
        print(f"{resource['name']}: ${resource['monthly_cost']:.2f}/month")

    print("-" * 35)
    print(f"Estimated monthly total: ${result['total_monthly_cost']:.2f}")
    print(f"Monthly budget:          ${result['budget']:.2f}")
    print(f"Status:                  {result['status']}")
    print(f"Message:                 {result['message']}")

    if args.report:
        markdown_report = generate_markdown_report(result)

        with open(args.report, "w", encoding="utf-8") as file:
            file.write(markdown_report)

        print(f"Markdown report saved to: {args.report}")

    if result["status"] == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
