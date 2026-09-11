"""
Rate-limiting tests for CYBREZ.

Strategy
--------
Each test directly manipulates the rate-limiter instances to use a
tiny window (e.g. 2 calls / 60 s) so we can trigger the limit without
spamming real endpoint logic.  The autouse fixture in conftest.py resets
all limiters between tests, so no state leaks.

Tests verify:
  - requests under the limit succeed (correct status codes returned)
  - requests over the limit return HTTP 429
  - 429 responses include a Retry-After header
  - different callers (different IPs / different users) have independent buckets
  - rate limiting does not break normal, infrequent usage
"""

import pytest

from app.core.rate_limit import (
    RateLimiter,
    clear_all_limiters,
    invite_create_limiter,
    invite_resend_limiter,
    login_limiter,
    refresh_limiter,
    register_limiter,
    search_limiter,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _register(client, email, password="password123", name="Test User"):
    return client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": name},
    )


def _login(client, email, password="password123"):
    return client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )


def _register_and_login(client, email):
    _register(client, email)
    resp = _login(client, email)
    assert resp.status_code == 200, resp.json()
    return resp.json()["access_token"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def _set_limiter_capacity(limiter: RateLimiter, max_calls: int):
    """Shrink a limiter's capacity for the duration of a test."""
    limiter.max_calls = max_calls


def _restore_limiter(limiter: RateLimiter, original: int):
    limiter.max_calls = original


# ---------------------------------------------------------------------------
# 1. Login — IP-based
# ---------------------------------------------------------------------------

class TestLoginRateLimit:

    def test_login_succeeds_within_limit(self, client):
        _register(client, "rl-login-ok@example.com")
        _set_limiter_capacity(login_limiter, 3)

        for _ in range(3):
            resp = _login(client, "rl-login-ok@example.com")
            # Allow 200 (correct creds) or 401 (wrong creds); either way
            # the rate limiter did NOT block the request.
            assert resp.status_code != 429, "Login blocked before limit reached"

    def test_login_returns_429_over_limit(self, client):
        _register(client, "rl-login-block@example.com")
        _set_limiter_capacity(login_limiter, 2)

        # Exhaust the limit
        for _ in range(2):
            _login(client, "rl-login-block@example.com")

        resp = _login(client, "rl-login-block@example.com")
        assert resp.status_code == 429

    def test_login_429_has_retry_after_header(self, client):
        _register(client, "rl-login-retry@example.com")
        _set_limiter_capacity(login_limiter, 1)

        _login(client, "rl-login-retry@example.com")
        resp = _login(client, "rl-login-retry@example.com")

        assert resp.status_code == 429
        assert "retry-after" in resp.headers
        assert int(resp.headers["retry-after"]) > 0

    def test_login_different_ips_independent(self, client):
        """
        Two different X-Forwarded-For IPs must have independent buckets.
        """
        _register(client, "rl-login-ip@example.com")
        _set_limiter_capacity(login_limiter, 1)

        # First IP exhausts its bucket
        resp1 = client.post(
            "/api/v1/auth/login",
            data={"username": "rl-login-ip@example.com", "password": "password123"},
            headers={"X-Forwarded-For": "1.2.3.4"},
        )
        assert resp1.status_code != 429

        # Same IP is now blocked
        resp2 = client.post(
            "/api/v1/auth/login",
            data={"username": "rl-login-ip@example.com", "password": "password123"},
            headers={"X-Forwarded-For": "1.2.3.4"},
        )
        assert resp2.status_code == 429

        # Different IP still has a fresh bucket
        resp3 = client.post(
            "/api/v1/auth/login",
            data={"username": "rl-login-ip@example.com", "password": "password123"},
            headers={"X-Forwarded-For": "9.9.9.9"},
        )
        assert resp3.status_code != 429


# ---------------------------------------------------------------------------
# 2. Register — IP-based
# ---------------------------------------------------------------------------

class TestRegisterRateLimit:

    def test_register_succeeds_within_limit(self, client):
        _set_limiter_capacity(register_limiter, 3)

        for i in range(3):
            resp = _register(client, f"rl-reg-ok-{i}@example.com")
            assert resp.status_code != 429

    def test_register_returns_429_over_limit(self, client):
        _set_limiter_capacity(register_limiter, 2)

        _register(client, "rl-reg-a@example.com")
        _register(client, "rl-reg-b@example.com")

        resp = _register(client, "rl-reg-c@example.com")
        assert resp.status_code == 429

    def test_register_429_has_retry_after_header(self, client):
        _set_limiter_capacity(register_limiter, 1)

        _register(client, "rl-reg-retry-a@example.com")
        resp = _register(client, "rl-reg-retry-b@example.com")

        assert resp.status_code == 429
        assert "retry-after" in resp.headers


# ---------------------------------------------------------------------------
# 3. Refresh — IP-based
# ---------------------------------------------------------------------------

class TestRefreshRateLimit:

    def test_refresh_succeeds_within_limit(self, client):
        _register_and_login(client, "rl-refresh-ok@example.com")
        _set_limiter_capacity(refresh_limiter, 3)

        for _ in range(3):
            resp = client.post("/api/v1/auth/refresh")
            assert resp.status_code != 429

    def test_refresh_returns_429_over_limit(self, client):
        _register_and_login(client, "rl-refresh-block@example.com")
        _set_limiter_capacity(refresh_limiter, 2)

        client.post("/api/v1/auth/refresh")
        client.post("/api/v1/auth/refresh")

        resp = client.post("/api/v1/auth/refresh")
        assert resp.status_code == 429

    def test_refresh_429_has_retry_after_header(self, client):
        _register_and_login(client, "rl-refresh-retry@example.com")
        _set_limiter_capacity(refresh_limiter, 1)

        client.post("/api/v1/auth/refresh")
        resp = client.post("/api/v1/auth/refresh")

        assert resp.status_code == 429
        assert "retry-after" in resp.headers


# ---------------------------------------------------------------------------
# 4. Search — user-based
# ---------------------------------------------------------------------------

class TestSearchRateLimit:

    def test_search_succeeds_within_limit(self, client):
        token = _register_and_login(client, "rl-search-ok@example.com")
        _set_limiter_capacity(search_limiter, 3)

        for _ in range(3):
            resp = client.get(
                "/api/v1/search/",
                params={"q": "test"},
                headers=_auth_header(token),
            )
            assert resp.status_code != 429

    def test_search_returns_429_over_limit(self, client):
        token = _register_and_login(client, "rl-search-block@example.com")
        _set_limiter_capacity(search_limiter, 2)

        for _ in range(2):
            client.get("/api/v1/search/", params={"q": "x"}, headers=_auth_header(token))

        resp = client.get("/api/v1/search/", params={"q": "x"}, headers=_auth_header(token))
        assert resp.status_code == 429

    def test_search_429_has_retry_after_header(self, client):
        token = _register_and_login(client, "rl-search-retry@example.com")
        _set_limiter_capacity(search_limiter, 1)

        client.get("/api/v1/search/", params={"q": "x"}, headers=_auth_header(token))
        resp = client.get("/api/v1/search/", params={"q": "x"}, headers=_auth_header(token))

        assert resp.status_code == 429
        assert "retry-after" in resp.headers

    def test_search_different_users_independent(self, client):
        """Two different users must have independent search buckets."""
        token_a = _register_and_login(client, "rl-search-user-a@example.com")
        token_b = _register_and_login(client, "rl-search-user-b@example.com")
        _set_limiter_capacity(search_limiter, 1)

        # User A exhausts bucket
        client.get("/api/v1/search/", params={"q": "x"}, headers=_auth_header(token_a))
        resp_a = client.get("/api/v1/search/", params={"q": "x"}, headers=_auth_header(token_a))
        assert resp_a.status_code == 429

        # User B is unaffected
        resp_b = client.get("/api/v1/search/", params={"q": "x"}, headers=_auth_header(token_b))
        assert resp_b.status_code == 200


# ---------------------------------------------------------------------------
# 5. Invitation create — user-based
# ---------------------------------------------------------------------------

class TestInviteCreateRateLimit:

    def _setup(self, client):
        """Create owner + org + an invitee account. Returns (token, org_id)."""
        token = _register_and_login(client, "rl-inv-owner@example.com")
        _register(client, "rl-inv-invitee@example.com")

        org_resp = client.post(
            "/api/v1/organizations/",
            json={"name": "Rate Limit Org", "description": "test", "slug": "rl-org"},
            headers=_auth_header(token),
        )
        assert org_resp.status_code == 201
        return token, org_resp.json()["public_id"]

    def test_invite_create_succeeds_within_limit(self, client):
        token, org_id = self._setup(client)
        _set_limiter_capacity(invite_create_limiter, 3)

        for _ in range(3):
            resp = client.post(
                f"/api/v1/invitations/{org_id}/invite",
                json={"email": "rl-inv-invitee@example.com", "role": "viewer"},
                headers=_auth_header(token),
            )
            # 200/201 = success, 400 = already invited — both are under the limit
            assert resp.status_code != 429

    def test_invite_create_returns_429_over_limit(self, client):
        token, org_id = self._setup(client)
        _set_limiter_capacity(invite_create_limiter, 2)

        for _ in range(2):
            client.post(
                f"/api/v1/invitations/{org_id}/invite",
                json={"email": "rl-inv-invitee@example.com", "role": "viewer"},
                headers=_auth_header(token),
            )

        resp = client.post(
            f"/api/v1/invitations/{org_id}/invite",
            json={"email": "rl-inv-invitee@example.com", "role": "viewer"},
            headers=_auth_header(token),
        )
        assert resp.status_code == 429

    def test_invite_create_429_has_retry_after_header(self, client):
        token, org_id = self._setup(client)
        _set_limiter_capacity(invite_create_limiter, 1)

        client.post(
            f"/api/v1/invitations/{org_id}/invite",
            json={"email": "rl-inv-invitee@example.com", "role": "viewer"},
            headers=_auth_header(token),
        )
        resp = client.post(
            f"/api/v1/invitations/{org_id}/invite",
            json={"email": "rl-inv-invitee@example.com", "role": "viewer"},
            headers=_auth_header(token),
        )
        assert resp.status_code == 429
        assert "retry-after" in resp.headers


# ---------------------------------------------------------------------------
# 6. Invitation resend — user-based
# ---------------------------------------------------------------------------

class TestInviteResendRateLimit:

    def _setup(self, client):
        """Create owner, invitee, org, and one pending invitation."""
        token = _register_and_login(client, "rl-resend-owner@example.com")
        _register(client, "rl-resend-invitee@example.com")

        org_resp = client.post(
            "/api/v1/organizations/",
            json={"name": "Resend Org", "description": "test", "slug": "resend-org"},
            headers=_auth_header(token),
        )
        assert org_resp.status_code == 201
        org_id = org_resp.json()["public_id"]

        inv_resp = client.post(
            f"/api/v1/invitations/{org_id}/invite",
            json={"email": "rl-resend-invitee@example.com", "role": "viewer"},
            headers=_auth_header(token),
        )
        assert inv_resp.status_code == 201
        inv_id = inv_resp.json()["public_id"]

        return token, inv_id

    def test_invite_resend_succeeds_within_limit(self, client):
        token, inv_id = self._setup(client)
        _set_limiter_capacity(invite_resend_limiter, 3)

        for _ in range(3):
            resp = client.post(
                f"/api/v1/invitations/{inv_id}/resend",
                headers=_auth_header(token),
            )
            assert resp.status_code != 429

    def test_invite_resend_returns_429_over_limit(self, client):
        token, inv_id = self._setup(client)
        _set_limiter_capacity(invite_resend_limiter, 2)

        for _ in range(2):
            client.post(f"/api/v1/invitations/{inv_id}/resend", headers=_auth_header(token))

        resp = client.post(f"/api/v1/invitations/{inv_id}/resend", headers=_auth_header(token))
        assert resp.status_code == 429

    def test_invite_resend_429_has_retry_after_header(self, client):
        token, inv_id = self._setup(client)
        _set_limiter_capacity(invite_resend_limiter, 1)

        client.post(f"/api/v1/invitations/{inv_id}/resend", headers=_auth_header(token))
        resp = client.post(f"/api/v1/invitations/{inv_id}/resend", headers=_auth_header(token))

        assert resp.status_code == 429
        assert "retry-after" in resp.headers


# ---------------------------------------------------------------------------
# 7. Generic exception handler — no internal detail in 500 responses
# ---------------------------------------------------------------------------

class TestExceptionHandler:

    def test_unhandled_exception_returns_generic_500(self, client):
        """
        An unexpected internal error must not expose stack traces, SQL,
        filesystem paths, secret values, or any other internal detail.
        """
        from app.main import app

        @app.get("/_test_internal_error_do_not_use")
        def _raise():
            raise RuntimeError(
                "SECRET_KEY=supersecret, DATABASE_URL=postgres://admin:pass@db/prod"
            )

        try:
            resp = client.get("/_test_internal_error_do_not_use")
            assert resp.status_code == 500
            body = resp.json()
            assert body.get("detail") == "Internal server error"
            # Verify nothing sensitive leaks through
            text = resp.text
            assert "SECRET_KEY" not in text
            assert "DATABASE_URL" not in text
            assert "postgres" not in text
            assert "supersecret" not in text
            assert "Traceback" not in text
        finally:
            # Remove the temporary test route
            routes_to_keep = [
                r for r in app.routes
                if getattr(r, "path", None) != "/_test_internal_error_do_not_use"
            ]
            app.routes[:] = routes_to_keep

    def test_normal_404_still_works(self, client):
        """The generic handler must not swallow normal HTTPExceptions."""
        resp = client.get("/api/v1/organizations/00000000-0000-0000-0000-000000000000")
        # Requires auth (401) or not found (404) — either way, not 500
        assert resp.status_code in (401, 403, 404)

    def test_validation_error_still_returns_422(self, client):
        """RequestValidationError must still produce 422, not 500."""
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": "not-an-email", "password": "x"},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 8. Limiter isolation — clear_all_limiters works
# ---------------------------------------------------------------------------

class TestLimiterIsolation:

    def test_clear_all_limiters_resets_state(self):
        """Verify the clear helper actually resets counter state."""
        limiter = RateLimiter(max_calls=2, period_seconds=60)
        limiter.is_allowed("test-key")
        limiter.is_allowed("test-key")

        allowed, _ = limiter.is_allowed("test-key")
        assert not allowed, "Should be blocked after 2 calls"

        limiter.clear()

        allowed, _ = limiter.is_allowed("test-key")
        assert allowed, "Should be allowed after clear()"

    def test_different_keys_are_independent(self):
        """Different keys within the same limiter must be independent."""
        limiter = RateLimiter(max_calls=1, period_seconds=60)

        allowed_a, _ = limiter.is_allowed("key-a")
        assert allowed_a

        blocked_a, _ = limiter.is_allowed("key-a")
        assert not blocked_a

        # key-b is independent
        allowed_b, _ = limiter.is_allowed("key-b")
        assert allowed_b
