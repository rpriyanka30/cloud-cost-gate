
def generate_markdown_report(result):
    """Generate a Markdown cost report for a GitHub Pull Request."""

    status = result["status"]
    total = result["total_monthly_cost"]
    budget = result["budget"]

    if status == "PASS":
        badge = "PASS - Within budget"
    else:
        badge = "FAIL - Budget exceeded"

    lines = [
        "## Cloud-Cost-Gate Cost Report",
        "",
        f"**Status:** {badge}",
        "",
        "| AWS Resource | Compute / Month | Storage / Month | Total / Month |",
        "|---|---:|---:|---:|",
    ]

    for resource in result["resources"]:
        compute = resource.get("compute_monthly_cost", 0)
        storage = resource.get("storage_monthly_cost", 0)
        resource_total = resource["monthly_cost"]

        lines.append(
            f"| {resource['name']} "
            f"| ${compute:.2f} "
            f"| ${storage:.2f} "
            f"| ${resource_total:.2f} |"
        )

    lines.extend([
        "",
        f"**Estimated Monthly Total:** ${total:.2f}",
        f"**Monthly Budget:** ${budget:.2f}",
        f"**Result:** {result['message']}",
        "",
        "---",
        "",
        "*Pricing source: AWS Price List API.*",
        "*Compute estimate assumes 730 hours per month.*",
        "*Storage estimate uses the configured storage size and type.*",
        "*This estimate excludes data transfer, snapshots, backups, taxes, "
        "discounts, and other unmodeled charges.*",
    ])

    return "\n".join(lines) + "\n"
