from superconductors.api.auth import (
    LoginRateLimiter,
    issue_access_token,
    verify_access_token,
)


def test_access_tokens_verify_and_expire():
    token = issue_access_token("secret")
    assert verify_access_token(token, "secret") is True
    assert verify_access_token(token, "wrong") is False
    assert verify_access_token(issue_access_token("secret", lifetime_seconds=-1), "secret") is False
    assert verify_access_token("malformed", "secret") is False


def test_login_limiter_bounds_retained_identities():
    limiter = LoginRateLimiter(attempts=1, max_identities=2)
    limiter.record_failure("first")
    limiter.record_failure("second")
    assert limiter.is_blocked("first") is True

    limiter.record_failure("third")

    assert limiter.is_blocked("first") is False
    assert limiter.is_blocked("second") is True
    assert limiter.is_blocked("third") is True


def test_login_limiter_reset_clears_failures():
    limiter = LoginRateLimiter(attempts=1)
    limiter.record_failure("client")
    assert limiter.is_blocked("client") is True
    limiter.reset("client")
    assert limiter.is_blocked("client") is False
