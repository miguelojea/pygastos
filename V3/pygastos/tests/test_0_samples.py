from libs.testing_samples import sum, incremented_numbers, Increment
import pytest


def setup_module(module):
    """Actions to do at the beginning of the module"""
    pass


def teardown_module(module):
    """Actions to do at the beginning of the module"""
    pass


def test_sum_pass():
    assert sum(2, 5) == 7


def test_sum_fail():
    assert sum(1, 1) != 7


# Parameters to use and repeat the same TC
@pytest.mark.parametrize(
    "x, y, expected",
    [
        (1, 2, 3),
        (-2, -1, -3),
        (sum(1, 2), 3, 6)
    ]
)
def test_sum_params(x, y, expected):
    assert sum(x, y) == expected


def test_incremented_numbers_pass():
    result = incremented_numbers(1, 2, 3)
    assert result


def test_incremented_numbers_fail():
    result = incremented_numbers(1, 1, 2)
    assert not result


@pytest.fixture
def increment_class():
    """Class to use in TCs."""
    return Increment()


def test_class_1(increment_class: Increment):
    increment_class._inc()
    assert increment_class.x == 1


def test_class_2(increment_class: Increment):
    increment_class._inc()
    assert increment_class.x == 1


@pytest.fixture(scope="module")  # scopes: function (default), class, module, session
def increment_instance():
    """Instance to use in TCs."""
    return Increment()


def test_instance_1(increment_instance: Increment):
    increment_instance._inc()
    assert increment_instance.x == 1


def test_instance_2(increment_instance: Increment):
    increment_instance._inc()
    assert increment_instance.x == 2
