
import pytest

from cloud_cost.cli import main



def test_cli_passes_when_cost_is_within_budget(
    monkeypatch, capsys
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
    monkeypatch, capsys
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
