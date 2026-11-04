
def generate_markdown_report(result):
    """Generate a Markdown cost report for a GitHub Pull Request."""

    status = result["status"]
    total = result["total_monthly_cost"]
    budget = result["budget"]

    if status == "PASS":
        badge = "✅ PASS — Within budget"
    else:
        badge = "❌ FAIL — Budget exceeded"

    report = [
        "## Cloud-Cost-Gate Cost Report",
        "",
        f"**Status:** {badge}",
        "",
        "| AWS Resource | Monthly Cost |",
        "|---|---:|",
    ]

    for resource in result["resources"]:
        report.append(
            f"| {resource['name']} | "
            f"${resource['monthly_cost']:.2f} |"
        )

    report.extend([
        "",
        f"**Estimated Monthly Total:** ${total:.2f}",
        f"**Monthly Budget:** ${budget:.2f}",
        f"**Result:** {result['message']}",
        "",
        "---",
        "*Generated automatically by Cloud-Cost-Gate.*",
    ])

    return "\n".join(report)
