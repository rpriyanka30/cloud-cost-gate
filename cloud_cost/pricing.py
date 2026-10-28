
import json
import boto3
from botocore.exceptions import BotoCoreError, ClientError


# AWS Price List API endpoint region -> AWS service region name.
AWS_REGION_NAMES = {
    "us-east-1": "US East (N. Virginia)",
    "us-east-2": "US East (Ohio)",
    "us-west-1": "US West (N. California)",
    "us-west-2": "US West (Oregon)",
    "ap-south-1": "Asia Pacific (Mumbai)",
    "ap-southeast-1": "Asia Pacific (Singapore)",
    "ap-southeast-2": "Asia Pacific (Sydney)",
    "eu-west-1": "Europe (Ireland)",
    "eu-central-1": "Europe (Frankfurt)",
}


def _extract_hourly_price(product):
    """Extract the first valid USD hourly price from an AWS product."""
    terms = product.get("terms", {}).get("OnDemand", {})

    for term in terms.values():
        for dimension in term.get("priceDimensions", {}).values():
            price = dimension.get("pricePerUnit", {}).get("USD")
            if price is not None and dimension.get("unit") == "Hrs":
                return float(price)

    return None


def get_hourly_price(
    region,
    resource_type,
    instance_type,
    engine="mysql",
):
    """Fetch a live hourly price from the AWS Price List API."""

    if region not in AWS_REGION_NAMES:
        raise ValueError(f"Unsupported AWS region: {region}")

    if resource_type not in ("aws_instance", "aws_db_instance"):
        raise ValueError(f"Unsupported resource type: {resource_type}")

    if not isinstance(instance_type, str) or not instance_type:
        raise ValueError("Unsupported instance type: instance type is missing")

    service_code = (
        "AmazonEC2"
        if resource_type == "aws_instance"
        else "AmazonRDS"
    )

    filters = [
        {
            "Type": "TERM_MATCH",
            "Field": "instanceType",
            "Value": instance_type,
        },
        {
            "Type": "TERM_MATCH",
            "Field": "location",
            "Value": AWS_REGION_NAMES[region],
        },
    ]

    if resource_type == "aws_instance":
        filters.extend([
            {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": "Linux"},
            {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
            {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
            {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"},
            {"Type": "TERM_MATCH", "Field": "marketoption", "Value": "OnDemand"},
        ])
    else:
        if not isinstance(engine, str) or not engine.strip():
            raise ValueError("RDS engine must be specified")

        filters.extend([
            {
                "Type": "TERM_MATCH",
                "Field": "databaseEngine",
                "Value": engine,
            },
            {
                "Type": "TERM_MATCH",
                "Field": "deploymentOption",
                "Value": "Single-AZ",
            },
        ])

    try:
        client = boto3.client("pricing", region_name="us-east-1")
        response = client.get_products(
            ServiceCode=service_code,
            Filters=filters,
            FormatVersion="aws_v1",
            MaxResults=100,
        )

        while True:
            for item in response.get("PriceList", []):
                product = json.loads(item)
                price = _extract_hourly_price(product)

                if price is not None:
                    return price

            next_token = response.get("NextToken")
            if not next_token:
                break

            response = client.get_products(
                ServiceCode=service_code,
                Filters=filters,
                FormatVersion="aws_v1",
                MaxResults=100,
                NextToken=next_token,
            )

    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(
            f"Could not fetch live AWS pricing: {exc}"
        ) from exc

    raise ValueError(
        f"No hourly price found for {resource_type} "
        f"{instance_type} in {region}. Check the instance type, "
        "region, engine, and AWS pricing filters."
    )
