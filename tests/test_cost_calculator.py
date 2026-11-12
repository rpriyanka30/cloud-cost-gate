
import pytest

from cloud_cost.cost_calculator import (
    calculate_hourly_cost,
    calculate_monthly_cost,
    estimate_resources_cost,
    estimate_terraform_cost,
    estimate_terraform_files,
)


@pytest.fixture
def mock_pricing(monkeypatch):
    """Return predictable compute and storage prices."""

    def fake_get_hourly_price(
        region, resource_type, instance_type, engine="mysql"
    ):
        prices = {
            ("us-east-1", "aws_instance", "t3.micro"): 0.0104,
            ("us-east-1", "aws_db_instance", "db.t3.micro"): 0.0170,
        }

        key = (region, resource_type, instance_type)

        if key not in prices:
            raise ValueError("Unsupported instance type")

        return prices[key]

    def fake_get_storage_price(
        region, resource_type, storage_type, engine="mysql"
    ):
        prices = {
            ("aws_instance", "gp2"): 0.10,
            ("aws_instance", "gp3"): 0.08,
            ("aws_db_instance", "gp2"): 0.115,
            ("aws_db_instance", "gp3"): 0.115,
        }

        key = (resource_type, storage_type)

        if key not in prices:
            raise ValueError("Unsupported storage type")

        return prices[key]

    monkeypatch.setattr(
        "cloud_cost.cost_calculator.get_hourly_price",
        fake_get_hourly_price,
    )

    monkeypatch.setattr(
        "cloud_cost.cost_calculator.get_storage_price_per_gib_month",
        fake_get_storage_price,
    )


def test_calculate_hourly_cost(mock_pricing):
    result = calculate_hourly_cost(
        "us-east-1", "aws_instance", "t3.micro"
    )
    assert result == 0.0104


def test_calculate_monthly_cost(mock_pricing):
    result = calculate_monthly_cost(
        "us-east-1", "aws_instance", "t3.micro"
    )
    assert round(result, 3) == 7.592


def test_estimate_resources_cost(mock_pricing):
    resources = [
        {
            "name": "web_server",
            "resource_type": "aws_instance",
            "instance_type": "t3.micro",
            "storage_gib": 20,
            "volume_type": "gp3",
            "region": "us-east-1",
        }
    ]

    result = estimate_resources_cost(resources, 10)

    assert result["resources"][0]["compute_monthly_cost"] == 7.59
    assert result["resources"][0]["storage_monthly_cost"] == 1.60
    assert result["resources"][0]["monthly_cost"] == 9.19
    assert result["total_monthly_cost"] == 9.19
    assert result["status"] == "PASS"


def test_estimate_resources_exceeds_budget(mock_pricing):
    resources = [
        {
            "name": "web_server",
            "resource_type": "aws_instance",
            "instance_type": "t3.micro",
            "storage_gib": 20,
            "volume_type": "gp3",
            "region": "us-east-1",
        }
    ]

    result = estimate_resources_cost(resources, 5)
    assert result["status"] == "FAIL"


def test_estimate_terraform_cost(mock_pricing):
    result = estimate_terraform_cost("examples/main.tf", 15)

    assert result["total_monthly_cost"] == 23.9
    assert result["status"] == "FAIL"


def test_empty_resources_raises_error():
    with pytest.raises(
        ValueError,
        match="No supported resources found",
    ):
        estimate_resources_cost([], budget=15)


def test_estimate_multiple_terraform_files(mock_pricing, tmp_path):
    provider_file = tmp_path / "provider.tf"
    compute_file = tmp_path / "compute.tf"
    database_file = tmp_path / "database.tf"

    provider_file.write_text(
        'provider "aws" {\n'
        '  region = "us-east-1"\n'
        '}\n',
        encoding="utf-8",
    )

    compute_file.write_text(
        'resource "aws_instance" "web_server" {\n'
        '  instance_type = "t3.micro"\n'
        '  root_block_device {\n'
        '    volume_size = 20\n'
        '    volume_type = "gp3"\n'
        '  }\n'
        '}\n',
        encoding="utf-8",
    )

    database_file.write_text(
        'resource "aws_db_instance" "app_database" {\n'
        '  instance_class = "db.t3.micro"\n'
        '  allocated_storage = 20\n'
        '  storage_type = "gp2"\n'
        '  engine = "mysql"\n'
        '}\n',
        encoding="utf-8",
    )

    result = estimate_terraform_files(
        [provider_file, compute_file, database_file],
        budget=25,
    )

    assert result["total_monthly_cost"] == 23.9
    assert result["status"] == "PASS"
    assert len(result["resources"]) == 2


def test_missing_storage_type_raises_error(mock_pricing):
    resources = [
        {
            "name": "web_server",
            "resource_type": "aws_instance",
            "instance_type": "t3.micro",
            "storage_gib": 20,
            "region": "us-east-1",
        }
    ]

    with pytest.raises(ValueError, match="Storage type is missing"):
        estimate_resources_cost(resources, 25)


def test_calculate_monthly_storage_cost(mock_pricing):
    from cloud_cost.cost_calculator import calculate_monthly_storage_cost

    result = calculate_monthly_storage_cost(
        "us-east-1", "aws_instance", 20, "gp3"
    )

    assert result == 1.6
