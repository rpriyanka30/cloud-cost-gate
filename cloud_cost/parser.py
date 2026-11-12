import argparse
import json
from pathlib import Path

import hcl2


def parse_terraform_file(file_path):
    """Read a Terraform file and extract supported resources."""

    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(f"No such file or directory: '{file_path}'")

    if file_path.suffix != ".tf":
        raise ValueError(f"Not a Terraform file: {file_path}")

    with open(file_path, "r", encoding="utf-8-sig") as file:
        data = hcl2.load(file)

    resources = []
    region = "unknown"

    # Find the AWS region.
    for provider in data.get("provider", []):
        if not isinstance(provider, dict):
            continue

        for provider_name, aws_config in provider.items():
            if provider_name.strip('"') != "aws":
                continue

            configs = (
                aws_config if isinstance(aws_config, list) else [aws_config]
            )

            for config in configs:
                if isinstance(config, dict):
                    region_value = config.get("region", region)

                    if isinstance(region_value, str):
                        region = region_value.strip('"')
                    else:
                        region = region_value

    # Read Terraform resource blocks.
    for block in data.get("resource", []):
        if not isinstance(block, dict):
            continue

        for resource_type, named_resources in block.items():
            resource_type = resource_type.strip('"')

            for resource_name, attributes in named_resources.items():
                resource_name = resource_name.strip('"')

                # Reject unsupported Multi-AZ RDS configurations.
                multi_az = attributes.get("multi_az", False)

                if isinstance(multi_az, str):
                    multi_az = multi_az.strip('"').lower() == "true"

                if resource_type == "aws_db_instance" and multi_az is True:
                    raise ValueError(
                        "Multi-AZ RDS is not currently supported: "
                        f"{resource_name}"
                    )

                # Read instance type or database class.
                instance_type = attributes.get("instance_type")

                if instance_type is None:
                    instance_type = attributes.get("instance_class")

                # Read database engine.
                engine = attributes.get("engine")

                if isinstance(engine, str):
                    engine = engine.strip('"')

                # Read storage size and storage type.
                storage = attributes.get("allocated_storage")
                volume_type = attributes.get("storage_type")

                if storage is None:
                    root_device = attributes.get("root_block_device", [])

                    if isinstance(root_device, dict):
                        root_device = [root_device]

                    if root_device:
                        storage = root_device[0].get("volume_size")
                        volume_type = root_device[0].get("volume_type")

                if isinstance(volume_type, str):
                    volume_type = volume_type.strip('"')

                # Default EC2 storage to gp2 only when type is absent.
                if (
                    storage is not None
                    and volume_type is None
                    and resource_type == "aws_instance"
                ):
                    volume_type = "gp2"

                resources.append(
                    {
                        "resource_type": resource_type,
                        "name": resource_name,
                        "instance_type": (
                            instance_type.strip('"')
                            if isinstance(instance_type, str)
                            else instance_type
                        ),
                        "storage_gib": storage,
                        "volume_type": volume_type,
                        "engine": engine,
                        "region": region,
                    }
                )

    return resources


def parse_terraform_files(file_paths):
    """Parse multiple Terraform files as one configuration."""

    paths = [Path(path) for path in file_paths]

    if not paths:
        raise ValueError("No Terraform files provided.")

    global_region = "unknown"

    # Find the AWS region across all files.
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(f"No such file or directory: '{path}'")

        if path.suffix != ".tf":
            raise ValueError(f"Not a Terraform file: {path}")

        with open(path, "r", encoding="utf-8-sig") as file:
            data = hcl2.load(file)

        for provider in data.get("provider", []):
            if not isinstance(provider, dict):
                continue

            for provider_name, configs in provider.items():
                if provider_name.strip('"') != "aws":
                    continue

                if not isinstance(configs, list):
                    configs = [configs]

                for config in configs:
                    if isinstance(config, dict):
                        region = config.get("region")

                        if isinstance(region, str):
                            global_region = region.strip('"')
                            break

                if global_region != "unknown":
                    break

            if global_region != "unknown":
                break

        if global_region != "unknown":
            break

    # Collect resources from every file.
    all_resources = []

    for path in paths:
        resources = parse_terraform_file(path)

        for resource in resources:
            if resource["region"] == "unknown":
                resource["region"] = global_region

            all_resources.append(resource)

    return all_resources


def main():
    cli = argparse.ArgumentParser(
        description="Analyze Terraform infrastructure."
    )

    cli.add_argument("path", help="Path to a Terraform .tf file")

    cli.add_argument(
        "--json",
        action="store_true",
        help="Display the results as JSON",
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
        print(f"Storage type: {resource['volume_type']}")
        print(f"Region: {resource['region']}")

    print(f"\nResources detected: {len(resources)}")


if __name__ == "__main__":
    main()
