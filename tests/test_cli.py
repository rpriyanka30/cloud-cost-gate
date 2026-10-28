
import pytest

from cloud_cost.cli import main


@pytest.fixture
def mock_pricing(monkeypatch):
    """Provide predictable prices without calling AWS."""

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

    monkeypatch.setattr(
        "cloud_cost.cost_calculator.get_hourly_price",
        fake_get_hourly_price,
    )


def test_cli_passes_when_cost_is_within_budget(
    monkeypatch, capsys, mock_pricing
):
    monkeypatch.setattr(
        "sys.argv",
        ["cli.py", "examples/main.tf", "--budget", "25"],
    )

    main()

    output = capsys.readouterr().out
    assert "Status:                  PASS" in output
    assert "Within budget." in output


def test_cli_fails_when_cost_exceeds_budget(
    monkeypatch, capsys, mock_pricing
):
    monkeypatch.setattr(
        "sys.argv",
        ["cli.py", "examples/main.tf", "--budget", "15"],
    )

    with pytest.raises(SystemExit) as result:
        main()

    assert result.value.code == 1

    output = capsys.readouterr().out
    assert "Status:                  FAIL" in output


def test_cli_reports_missing_file(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        ["cli.py", "examples/missing.tf", "--budget", "15"],
    )

    with pytest.raises(SystemExit) as result:
        main()

    assert result.value.code == 2

    error_output = capsys.readouterr().err
    assert "No such file or directory" in error_output
