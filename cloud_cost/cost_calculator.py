
from cloud_cost.parser import (
    parse_terraform_file,
    parse_terraform_files,
)
from cloud_cost.pricing import (
    get_hourly_price,
    get_storage_price_per_gib_month,
)


def calculate_hourly_cost(
    region, resource_type, instance_type, engine="mysql"
):
    return get_hourly_price(
        region,
        resource_type,
        instance_type,
        engine=engine,
    )


def calculate_monthly_cost(
    region, resource_type, instance_type, engine="mysql"
):
    hourly_cost = calculate_hourly_cost(
        region,
        resource_type,
        instance_type,
        engine=engine,
    )

    return hourly_cost * 730


def calculate_monthly_storage_cost(
    region,
    resource_type,
    storage_gib,
    storage_type,
    engine="mysql",
):
    """Calculate monthly storage cost using live AWS pricing."""

    if (
        isinstance(storage_gib, bool)
        or not isinstance(storage_gib, (int, float))
        or storage_gib < 0
    ):
        raise ValueError("Storage size must be a non-negative number.")

    storage_price = get_storage_price_per_gib_month(
        region,
        resource_type,
        storage_type,
        engine=engine,
    )

    return storage_gib * storage_price


def estimate_resources_cost(resources, budget):
    """Estimate compute and storage costs and check the total budget."""

    if not resources:
        raise ValueError("No supported resources found in the Terraform file.")

    from cloud_cost.policy import check_budget

    total_monthly_cost = 0
    resource_costs = []

    for resource in resources:
        engine = resource.get("engine") or "mysql"

        compute_monthly_cost = calculate_monthly_cost(
            resource["region"],
            resource["resource_type"],
            resource["instance_type"],
            engine=engine,
        )

        storage_gib = resource.get("storage_gib")
        storage_monthly_cost = 0.0

        if storage_gib is not None:
            storage_type = resource.get("volume_type")

            if not storage_type:
                raise ValueError(
                    f"Storage type is missing for resource "
                    f"'{resource['name']}'. Specify storage_type "
                    "in your Terraform configuration."
                )

            storage_monthly_cost = calculate_monthly_storage_cost(
                resource["region"],
                resource["resource_type"],
                storage_gib,
                storage_type,
                engine=engine,
            )

        monthly_cost = compute_monthly_cost + storage_monthly_cost
        total_monthly_cost += monthly_cost

        resource_costs.append(
            {
                "name": resource["name"],
                "compute_monthly_cost": round(compute_monthly_cost, 2),
                "storage_monthly_cost": round(storage_monthly_cost, 2),
                "monthly_cost": round(monthly_cost, 2),
            }
        )

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


def estimate_terraform_files(file_paths, budget):
    """Estimate combined monthly costs across multiple Terraform files."""

    resources = parse_terraform_files(file_paths)

    return estimate_resources_cost(resources, budget)
