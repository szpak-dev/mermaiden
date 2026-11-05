from pathlib import Path

from .application_policy import ApplicationTestCheck


def test_product_tests_use_public_gates_and_cover_public_operations() -> None:
    check = ApplicationTestCheck(Path(__file__).resolve().parents[2])
    check.check_policy()
    assert not check.violations, "\n".join(item.render() for item in check.violations)


def test_verification_inputs_match_the_accepted_freeze() -> None:
    check = ApplicationTestCheck(Path(__file__).resolve().parents[2])
    check.check_freeze()
    assert not check.violations, "\n".join(item.render() for item in check.violations)
