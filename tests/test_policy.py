import pytest
from cloud_cost.policy import check_budget


def test_budget_within_limit():
    result = check_budget(30, 40)

    assert result["status"] == "PASS"
    assert result["message"] == "Within budget."


def test_budget_exceeded():
    result = check_budget(50, 40)

    assert result["status"] == "FAIL"
    assert result["message"] == "Budget exceeded!"


def test_cost_equal_to_budget():
    result = check_budget(40, 40)

    assert result["status"] == "PASS"


def test_negative_estimated_cost():
    with pytest.raises(ValueError):
        check_budget(-10, 40)


def test_negative_budget():
    with pytest.raises(ValueError):
        check_budget(30, -40)