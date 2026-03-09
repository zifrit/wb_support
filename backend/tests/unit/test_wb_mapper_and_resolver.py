from backend.app.external.wb_client.credentials_resolver import WbCredentialsResolver
from backend.app.external.wb_client.error_mapper import ErrorMapper
from backend.app.core.config import Settings
from backend.app.core.exceptions import AuthorizationError, TooManyRequestsError


def test_credentials_resolver_composes_headers():
    settings = Settings(WB_CLIENT_SECRET="secret", wb_user_agent="wbas_xway", wb_authorization_template="{token}")
    resolver = WbCredentialsResolver(settings=settings)
    creds = resolver.resolve(username="alice", token="token-1")

    assert creds.client_secret == "secret"
    assert creds.user_agent == "wbas_xway"
    assert creds.authorization == "token-1"


def test_error_mapper_maps_status_and_body():
    mapper = ErrorMapper()

    err = mapper.map(401, {"message": "unauthorized"})
    assert isinstance(err, AuthorizationError)
    assert err.details["wbStatus"] == 401

    rate_err = mapper.map(429, {"error": "slow down"})
    assert isinstance(rate_err, TooManyRequestsError)
    assert rate_err.details["wbBody"]["error"] == "slow down"
