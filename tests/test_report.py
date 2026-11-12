from cloud_cost.report import generate_markdown_report


def test_report_contains_compute_and_storage_breakdown():
    result = {
        "resources": [
            {
                "name": "web_server",
                "compute_monthly_cost": 7.59,
                "storage_monthly_cost": 1.60,
                "monthly_cost": 9.19,
            },
            {
                "name": "app_database",
                "compute_monthly_cost": 12.41,
                "storage_monthly_cost": 2.30,
                "monthly_cost": 14.71,
            },
        ],
        "total_monthly_cost": 23.90,
        "budget": 25.00,
        "status": "PASS",
        "message": "Within budget.",
    }

    report = generate_markdown_report(result)

    assert "PASS - Within budget" in report
    assert "web_server" in report
    assert "app_database" in report
    assert "$7.59" in report
    assert "$1.60" in report
    assert "$12.41" in report
    assert "$2.30" in report
    assert "$23.90" in report
    assert "$25.00" in report
    assert "AWS Price List API" in report


def test_report_shows_budget_failure():
    result = {
        "resources": [
            {
                "name": "web_server",
                "compute_monthly_cost": 7.59,
                "storage_monthly_cost": 1.60,
                "monthly_cost": 9.19,
            }
        ],
        "total_monthly_cost": 9.19,
        "budget": 5.00,
        "status": "FAIL",
        "message": "Budget exceeded.",
    }

    report = generate_markdown_report(result)

    assert "FAIL - Budget exceeded" in report
    assert "Budget exceeded." in report
