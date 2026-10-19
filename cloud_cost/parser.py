import argparse
import json
from pathlib import Path

import hcl2


def parse_terraform_file(file_path):
    """Read a Terraform file and extract supported resources."""

    with open(file_path, "r", encoding="utf-8") as file:
        data = hcl2.load(file)


    resources = []
    region = "unknown"

   
    # Find the AWS region.
    providers = data.get("provider", [])

    for provider in providers:
      if not isinstance(provider, dict):
        continue

      for provider_name, aws_config in provider.items():
        # Remove quotation marks added by the parser.
        provider_name = provider_name.strip('"')

        if provider_name != "aws":
            continue

        if isinstance(aws_config, list):
            configs = aws_config
        else:
            configs = [aws_config]

        for config in configs:
            if isinstance(config, dict):
                region_value = config.get("region", region)

                if isinstance(region_value, str):
                    region = region_value.strip('"')
                else:
                    region = region_value


    # Read the resource blocks.
    for block in data.get("resource", []):
        for resource_type, named_resources in block.items():

            for resource_name, attributes in named_resources.items():

                # Read the instance type or database class.
                instance_type = attributes.get("instance_type")

                if instance_type is None:
                    instance_type = attributes.get("instance_class")

                # Read the storage size.
                storage = attributes.get("allocated_storage")

                if storage is None:
                    root_device = attributes.get(
                        "root_block_device", []
                    )

                    if isinstance(root_device, dict):
                        root_device = [root_device]

                    if root_device:
                        storage = root_device[0].get("volume_size")

                resources.append({
                        "resource_type": resource_type.strip('"'),
                        "name": resource_name.strip('"'),
                        "instance_type": (
                            instance_type.strip('"')
                            if isinstance(instance_type, str)
                            else instance_type
                        ),
                        "storage_gib": storage,
                        "region": region,
                    })

    return resources


def main():
    cli = argparse.ArgumentParser(
        description="Analyze Terraform infrastructure."
    )

    cli.add_argument(
        "path",
        help="Path to a Terraform .tf file"
    )

    cli.add_argument(
        "--json",
        action="store_true",
        help="Display the results as JSON"
    )

    args = cli.parse_args()
    file_path = Path(args.path)

    if not file_path.is_file():
        cli.error(f"File not found: {file_path}")

    if file_path.suffix != ".tf":
        cli.error("Please provide a .tf file")

    resources = parse_terraform_file(file_path)

    if args.json:
        print(json.dumps(resources, indent=2))
        return

    print("\nCloud-Cost-Gate: Terraform Analysis")
    print("=" * 40)

    for resource in resources:
        print(f"\nResource: {resource['name']}")
        print(f"Type: {resource['resource_type']}")
        print(f"Instance type: {resource['instance_type']}")
        print(f"Storage: {resource['storage_gib']} GiB")
        print(f"Region: {resource['region']}")

    print(f"\nResources detected: {len(resources)}")


if __name__ == "__main__":
    main()