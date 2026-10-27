import json
import sys
from pathlib import Path

import pytest

from cloud_cost.parser import main, parse_terraform_file

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


def test_parser_returns_empty_list_when_no_resources(tmp_path):
    terraform_file = tmp_path / "empty.tf"
    terraform_file.write_text(
        'provider "aws" {\n  region = "us-east-1"\n}\n',
        encoding="utf-8",
    )

    resources = parse_terraform_file(terraform_file)

    assert resources == []


def test_parser_uses_unknown_region_when_provider_missing(tmp_path):
    terraform_file = tmp_path / "no_provider.tf"
    terraform_file.write_text(
        'resource "aws_instance" "test_server" {\n'
        '  ami = "ami-12345678"\n'
        '  instance_type = "t3.micro"\n'
        '}\n',
        encoding="utf-8",
    )

    resources = parse_terraform_file(terraform_file)

    assert len(resources) == 1
    assert resources[0]["region"] == "unknown"
    assert resources[0]["instance_type"] == "t3.micro"


def test_parser_raises_error_for_missing_file(tmp_path):
    missing_file = tmp_path / "missing.tf"

    try:
        parse_terraform_file(missing_file)
        assert False, "Expected an error for a missing file"
    except FileNotFoundError:
        pass


def test_parser_detects_resource_with_missing_instance_type(tmp_path):
    terraform_file = tmp_path / "missing_type.tf"
    terraform_file.write_text(
        'resource "aws_instance" "test_server" {\n'
        '  ami = "ami-12345678"\n'
        '}\n',
        encoding="utf-8",
    )

    resources = parse_terraform_file(terraform_file)

    assert len(resources) == 1
    assert resources[0]["name"] == "test_server"
    assert resources[0]["instance_type"] is None


def test_parser_detects_root_block_storage(tmp_path):
    terraform_file = tmp_path / "storage.tf"
    terraform_file.write_text(
        'resource "aws_instance" "server" {\n'
        '  instance_type = "t3.micro"\n'
        '  root_block_device {\n'
        '    volume_size = 30\n'
        '  }\n'
        '}\n',
        encoding="utf-8",
    )

    resources = parse_terraform_file(terraform_file)

    assert resources[0]["storage_gib"] == 30


def test_parser_cli_json_output(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        ["parser.py", str(SAMPLE_FILE), "--json"],
    )

    main()

    resources = json.loads(capsys.readouterr().out)

    assert len(resources) == 2
    assert resources[0]["resource_type"] == "aws_instance"


def test_parser_cli_rejects_missing_file(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["parser.py", "missing_file.tf"],
    )

    with pytest.raises(SystemExit) as result:
        main()

    assert result.value.code == 2


def test_parser_cli_rejects_non_tf_file(monkeypatch, tmp_path):
    other_file = tmp_path / "config.txt"
    other_file.write_text("example", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        ["parser.py", str(other_file)],
    )

    with pytest.raises(SystemExit) as result:
        main()

    assert result.value.code == 2
