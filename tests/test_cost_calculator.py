import pytest

from cloud_cost.cost_calculator import (
    calculate_hourly_cost,
    calculate_monthly_cost,
    estimate_resources_cost,
    estimate_terraform_cost,
)


def test_calculate_hourly_cost():
    result = calculate_hourly_cost(
        "us-east-1",
        "aws_instance",
        "t3.micro",
    )

    assert result == 0.0104


def test_calculate_monthly_cost():
    result = calculate_monthly_cost(
        "us-east-1",
        "aws_instance",
        "t3.micro",
    )

    assert round(result, 3) == 7.592


def test_estimate_resources_cost():
    resources = [
        {
            "name": "web_server",
            "resource_type": "aws_instance",
            "instance_type": "t3.micro",
            "region": "us-east-1",
        }
    ]

    result = estimate_resources_cost(resources, 10)

    assert result["total_monthly_cost"] == 7.59
    assert result["status"] == "PASS"


def test_estimate_resources_exceeds_budget():
    resources = [
        {
            "name": "web_server",
            "resource_type": "aws_instance",
            "instance_type": "t3.micro",
            "region": "us-east-1",
        }
    ]

    result = estimate_resources_cost(resources, 5)

    assert result["status"] == "FAIL"


def test_estimate_terraform_cost():
    result = estimate_terraform_cost("examples/main.tf", 15)

    assert result["total_monthly_cost"] == 20.0
    assert result["status"] == "FAIL"