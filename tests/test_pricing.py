
import json
import pytest

from cloud_cost.pricing import get_hourly_price


class MockPricingClient:
    """Simulate AWS Price List API responses."""

    def __init__(self, price):
        self.price = price
        self.last_request = None

    def get_products(self, **kwargs):
        self.last_request = kwargs

        if self.price is None:
            return {"PriceList": []}

        product = {
            "terms": {
                "OnDemand": {
                    "test-term": {
                        "priceDimensions": {
                            "test-dimension": {
                                "unit": "Hrs",
                                "pricePerUnit": {
                                    "USD": str(self.price)
                                },
                            }
                        }
                    }
                }
            }
        }

        return {"PriceList": [json.dumps(product)]}


def test_get_ec2_hourly_price(monkeypatch):
    mock_client = MockPricingClient(0.0104)

    monkeypatch.setattr(
        "cloud_cost.pricing.boto3.client",
        lambda *args, **kwargs: mock_client,
    )

    price = get_hourly_price(
        "us-east-1",
        "aws_instance",
        "t3.micro",
    )

    assert price == 0.0104
    assert mock_client.last_request["ServiceCode"] == "AmazonEC2"


def test_get_rds_hourly_price(monkeypatch):
    mock_client = MockPricingClient(0.0170)

    monkeypatch.setattr(
        "cloud_cost.pricing.boto3.client",
        lambda *args, **kwargs: mock_client,
    )

    price = get_hourly_price(
        "us-east-1",
        "aws_db_instance",
        "db.t3.micro",
        engine="mysql",
    )

    assert price == 0.0170
    assert mock_client.last_request["ServiceCode"] == "AmazonRDS"

    filters = mock_client.last_request["Filters"]
    assert any(
        item["Field"] == "databaseEngine"
        and item["Value"] == "mysql"
        for item in filters
    )


def test_unknown_instance_raises_error(monkeypatch):
    mock_client = MockPricingClient(None)

    monkeypatch.setattr(
        "cloud_cost.pricing.boto3.client",
        lambda *args, **kwargs: mock_client,
    )

    with pytest.raises(ValueError, match="No hourly price found"):
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


def test_missing_rds_engine_raises_error():
    with pytest.raises(ValueError, match="RDS engine must be specified"):
        get_hourly_price(
            "us-east-1",
            "aws_db_instance",
            "db.t3.micro",
            engine="",
        )
