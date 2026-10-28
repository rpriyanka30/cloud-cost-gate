
from cloud_cost.parser import parse_terraform_file
from cloud_cost.pricing import get_hourly_price


def calculate_hourly_cost(
    region, resource_type, instance_type, engine="mysql"
):
    """Calculate the hourly cost of one AWS resource."""

    hourly_price = get_hourly_price(
        region,
        resource_type,
        instance_type,
        engine=engine,
    )

    return hourly_price


def calculate_monthly_cost(
    region, resource_type, instance_type, engine="mysql"
):
    """Estimate monthly cost assuming 730 hours per month."""

    hourly_cost = calculate_hourly_cost(
        region,
        resource_type,
        instance_type,
        engine=engine,
    )

    return hourly_cost * 730


def estimate_resources_cost(resources, budget):
    """Estimate monthly costs for resources and check the total budget."""

    if not resources:
        raise ValueError("No supported resources found in the Terraform file.")

    from cloud_cost.policy import check_budget

    total_monthly_cost = 0
    resource_costs = []

    for resource in resources:
        hourly_cost = calculate_hourly_cost(
            resource["region"],
            resource["resource_type"],
            resource["instance_type"],
            engine=resource.get("engine", "mysql"),
        )

        monthly_cost = hourly_cost * 730
        total_monthly_cost += monthly_cost

        resource_costs.append({
            "name": resource["name"],
            "monthly_cost": round(monthly_cost, 2),
        })

    budget_result = check_budget(total_monthly_cost, budget)

    return {
        "resources": resource_costs,
        "total_monthly_cost": round(total_monthly_cost, 2),
        "budget": budget,
        "status": budget_result["status"],
        "message": budget_result["message"],
    }


def estimate_terraform_cost(file_path, budget):
    """Parse a Terraform file and estimate its monthly AWS costs."""

    resources = parse_terraform_file(file_path)

    return estimate_resources_cost(resources, budget)
