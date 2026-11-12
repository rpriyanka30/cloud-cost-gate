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
        "AmazonEC2" if resource_type == "aws_instance" else "AmazonRDS"
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
        filters.extend(
            [
                {
                    "Type": "TERM_MATCH",
                    "Field": "operatingSystem",
                    "Value": "Linux",
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "tenancy",
                    "Value": "Shared",
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "preInstalledSw",
                    "Value": "NA",
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "capacitystatus",
                    "Value": "Used",
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "marketoption",
                    "Value": "OnDemand",
                },
            ]
        )
    else:
        if not isinstance(engine, str) or not engine.strip():
            raise ValueError("RDS engine must be specified")

        filters.extend(
            [
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
            ]
        )

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
        raise RuntimeError(f"Could not fetch live AWS pricing: {exc}") from exc

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "AWS Pricing API returned invalid JSON product data."
        ) from exc

    raise ValueError(
        f"No hourly price found for {resource_type} "
        f"{instance_type} in {region}. Check the instance type, "
        "region, engine, and AWS pricing filters."
    )


def _extract_storage_price(product):
    """Extract a USD price per GB-month from an AWS product."""
    terms = product.get("terms", {}).get("OnDemand", {})

    for term in terms.values():
        for dimension in term.get("priceDimensions", {}).values():
            price = dimension.get("pricePerUnit", {}).get("USD")

            if price is not None and dimension.get("unit") == "GB-Mo":
                return float(price)

    return None


def get_storage_price_per_gib_month(
    region,
    resource_type,
    storage_type,
    engine="mysql",
):
    """Fetch live monthly storage pricing from the AWS Price List API."""

    if region not in AWS_REGION_NAMES:
        raise ValueError(f"Unsupported AWS region: {region}")

    if resource_type not in ("aws_instance", "aws_db_instance"):
        raise ValueError(f"Unsupported resource type: {resource_type}")

    if storage_type not in ("gp2", "gp3"):
        raise ValueError(
            f"Unsupported storage type: {storage_type}. Use gp2 or gp3."
        )

    service_code = (
        "AmazonEC2" if resource_type == "aws_instance" else "AmazonRDS"
    )

    filters = [
        {
            "Type": "TERM_MATCH",
            "Field": "location",
            "Value": AWS_REGION_NAMES[region],
        },
    ]

    if resource_type == "aws_instance":
        filters.append(
            {
                "Type": "TERM_MATCH",
                "Field": "productFamily",
                "Value": "Storage",
            }
        )
        expected_usage_suffix = f"EBS:VolumeUsage.{storage_type}"

    else:
        if not isinstance(engine, str) or not engine.strip():
            raise ValueError("RDS engine must be specified")

        engine_names = {
            "mysql": "MySQL",
        }

        aws_engine = engine_names.get(engine.lower())

        if aws_engine is None:
            raise ValueError(f"Unsupported RDS storage engine: {engine}")

        filters.extend(
            [
                {
                    "Type": "TERM_MATCH",
                    "Field": "productFamily",
                    "Value": "Database Storage",
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "databaseEngine",
                    "Value": aws_engine,
                },
                {
                    "Type": "TERM_MATCH",
                    "Field": "deploymentOption",
                    "Value": "Single-AZ",
                },
            ]
        )

        expected_usage_suffix = (
            "RDS:GP2-Storage" if storage_type == "gp2" else "RDS:GP3-Storage"
        )

    try:
        client = boto3.client("pricing", region_name="us-east-1")

        request = {
            "ServiceCode": service_code,
            "Filters": filters,
            "FormatVersion": "aws_v1",
            "MaxResults": 100,
        }

        while True:
            response = client.get_products(**request)

            for item in response.get("PriceList", []):
                product = json.loads(item)

                attributes = product.get("product", {}).get("attributes", {})

                usage_type = attributes.get("usagetype", "")

                if not usage_type.endswith(expected_usage_suffix):
                    continue

                price = _extract_storage_price(product)

                if price is not None:
                    return price

            next_token = response.get("NextToken")

            if not next_token:
                break

            request["NextToken"] = next_token

    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(
            f"Could not fetch AWS storage pricing: {exc}"
        ) from exc

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "AWS Pricing API returned invalid JSON product data."
        ) from exc

    raise ValueError(
        f"No storage price found for {resource_type}, "
        f"{storage_type}, in {region}. Check the storage type, "
        "region, engine, and AWS pricing filters."
    )
