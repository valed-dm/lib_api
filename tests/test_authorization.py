import pytest

STATUS_OK = 200


@pytest.mark.asyncio
@pytest.mark.usefixtures("_override_dependencies")
async def test_auth_workflow(async_client, test_user):
    username, password = test_user

    login_response = await async_client.post(
        "/token",
        data={"username": username, "password": password},
    )

    if login_response.status_code != STATUS_OK:
        msg = (
            f"Login failed: expected status {STATUS_OK}, "
            f"but got {login_response.status_code}. "
            f"Response body: {login_response.text}"
        )
        raise AssertionError(msg)

    access_token = login_response.json().get("access_token")
    if not access_token:
        msg = "Access token not returned. Response body: {login_response.text}"
        raise AssertionError(msg)
