import pytest
from caseinsight.utils.retry import with_retry


def test_succeeds_first_try():
    calls = {"n": 0}

    @with_retry(max_attempts=3, base_delay=0)
    def fn():
        calls["n"] += 1
        return "ok"

    assert fn() == "ok"
    assert calls["n"] == 1


def test_retries_then_succeeds():
    calls = {"n": 0}

    @with_retry(max_attempts=4, base_delay=0)
    def fn():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("transient")
        return "ok"

    assert fn() == "ok"
    assert calls["n"] == 3


def test_exhausts_and_reraises():
    @with_retry(max_attempts=3, base_delay=0, retry_on=(ValueError,))
    def fn():
        raise ValueError("always")

    with pytest.raises(ValueError, match="always"):
        fn()


def test_non_retryable_raises_immediately():
    calls = {"n": 0}

    @with_retry(max_attempts=3, base_delay=0, retry_on=(ValueError,))
    def fn():
        calls["n"] += 1
        raise KeyError("nope")

    with pytest.raises(KeyError):
        fn()
    assert calls["n"] == 1
