import pytest
from cloud_cost.pricing import get_hourly_price


def test_get_ec2_hourly_price():
    price = get_hourly_price(
        "us-east-1",
        "aws_instance",
        "t3.micro",
    )

    assert price == 0.0104


def test_get_rds_hourly_price():
    price = get_hourly_price(
        "us-east-1",
        "aws_db_instance",
        "db.t3.micro",
    )

    assert price == 0.0170


def test_unknown_instance_raises_error():
    with pytest.raises(ValueError, match="Unsupported instance type"):
        get_hourly_price(
            "us-east-1",
            "aws_instance",
            "t3.unknown",
        )

def test_unknown_region_raises_error():
    with pytest.raises(ValueError, match="Unsupported AWS region"):
        get_hourly_price(
            "unknown-region",
            "aws_instance",
            "t3.micro",
        )


def test_unknown_resource_type_raises_error():
    with pytest.raises(ValueError, match="Unsupported resource type"):
        get_hourly_price(
            "us-east-1",
            "unknown_resource",
            "t3.micro",
        )
   