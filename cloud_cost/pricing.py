# Illustrative AWS hourly prices in USD.
# These values are for development only, not verified current prices.
AWS_HOURLY_PRICES = {
    "us-east-1": {
        "aws_instance": {
            "t3.micro": 0.0104,
        },
        "aws_db_instance": {
            "db.t3.micro": 0.0170,
        },
    },
}

def get_hourly_price(region, resource_type, instance_type):
    """Return the illustrative hourly price for an AWS resource."""

    if region not in AWS_HOURLY_PRICES:
        raise ValueError(f"Unsupported AWS region: {region}")

    if resource_type not in AWS_HOURLY_PRICES[region]:
        raise ValueError(f"Unsupported resource type: {resource_type}")

    if instance_type not in AWS_HOURLY_PRICES[region][resource_type]:
        raise ValueError(f"Unsupported instance type: {instance_type}")

    return AWS_HOURLY_PRICES[region][resource_type][instance_type]