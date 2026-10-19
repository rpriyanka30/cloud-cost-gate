from pathlib import Path

from cloud_cost.parser import parse_terraform_file


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_FILE = PROJECT_ROOT / "examples" / "main.tf"


def test_parser_detects_both_resources():
    resources = parse_terraform_file(SAMPLE_FILE)

    assert len(resources) == 2


def test_parser_detects_ec2_instance():
    resources = parse_terraform_file(SAMPLE_FILE)

    ec2 = next(
        resource
        for resource in resources
        if resource["name"] == "web_server"
    )

    assert ec2["resource_type"] == "aws_instance"
    assert ec2["instance_type"] == "t3.micro"
    assert ec2["storage_gib"] == 20
    assert ec2["region"] == "us-east-1"


def test_parser_detects_rds_database():
    resources = parse_terraform_file(SAMPLE_FILE)

    database = next(
        resource
        for resource in resources
        if resource["name"] == "app_database"
    )

    assert database["resource_type"] == "aws_db_instance"
    assert database["instance_type"] == "db.t3.micro"
    assert database["storage_gib"] == 20
    assert database["region"] == "us-east-1"