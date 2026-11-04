import argparse
from cloud_cost.report import generate_markdown_report
from cloud_cost.cost_calculator import estimate_terraform_cost


def main():
    parser = argparse.ArgumentParser(
        description="Estimate AWS costs from a Terraform file."
    )

    parser.add_argument(
        "terraform_file",
        help="Path to the Terraform file",
    )

    parser.add_argument(
        "--budget",
        type=float,
        required=True,
        help="Maximum monthly budget in USD",
    )

    parser.add_argument(
        "--report",
        help="Path to save the Markdown cost report",
    )

    args = parser.parse_args()      
    

    try:
        result = estimate_terraform_cost(
            args.terraform_file,
            args.budget,
        )
    except (ValueError, KeyError, FileNotFoundError) as error:
        parser.error(str(error))

    print("\nCloud-Cost-Gate: Cost Analysis")
    print("=" * 35)

    for resource in result["resources"]:
        print(f"{resource['name']}: " f"${resource['monthly_cost']:.2f}/month")

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
