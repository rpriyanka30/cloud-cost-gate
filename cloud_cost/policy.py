def check_budget(estimated_cost, budget):
    """Check whether the estimated cost is within the budget."""

    if estimated_cost < 0:
        raise ValueError("Estimated cost cannot be negative.")

    if budget < 0:
        raise ValueError("Budget cannot be negative.")

    if estimated_cost > budget:
        return {
            "status": "FAIL",
            "message": "Budget exceeded!",
            "estimated_cost": estimated_cost,
            "budget": budget,
        }

    return {
        "status": "PASS",
        "message": "Within budget.",
        "estimated_cost": estimated_cost,
        "budget": budget,
    }