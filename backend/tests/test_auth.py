from fastapi import status


def test_session_endpoint_reports_anonymous_state(anonymous_client):
    response = anonymous_client.get("/api/v1/auth/session")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "auth_enabled": True,
        "authenticated": False,
        "can_write": False,
        "username": None,
    }


def test_write_routes_require_authenticated_owner(anonymous_client):
    response = anonymous_client.post(
        "/api/v1/anime",
        json={
            "name": "Monster",
            "year": 2004,
            "season": "other",
            "status": "unwatched",
            "type": "TV",
            "comment": "",
            "url": "",
            "downloaded": False,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["error"]["code"] == "authentication_required"


def test_login_sets_session_and_allows_follow_up_requests(anonymous_client):
    login_response = anonymous_client.post(
        "/api/v1/auth/login",
        json={"username": "owner", "password": "test-owner-password"},
    )

    assert login_response.status_code == status.HTTP_200_OK
    assert anonymous_client.cookies.get("anime_tracker_session")
    csrf_token = anonymous_client.cookies.get("anime_tracker_csrf")
    assert csrf_token

    session_response = anonymous_client.get("/api/v1/auth/session")
    assert session_response.status_code == status.HTTP_200_OK
    assert session_response.json()["authenticated"] is True

    create_response = anonymous_client.post(
        "/api/v1/anime",
        headers={"X-CSRF-Token": csrf_token},
        json={
            "name": "Paranoia Agent",
            "year": 2004,
            "season": "other",
            "status": "unwatched",
            "type": "TV",
            "comment": "",
            "url": "",
            "downloaded": False,
        },
    )
    assert create_response.status_code == status.HTTP_201_CREATED


def test_write_routes_reject_missing_or_invalid_csrf(anonymous_client):
    login_response = anonymous_client.post(
        "/api/v1/auth/login",
        json={"username": "owner", "password": "test-owner-password"},
    )
    assert login_response.status_code == status.HTTP_200_OK

    payload = {
        "name": "Ergo Proxy",
        "year": 2006,
        "season": "winter",
        "status": "unwatched",
        "type": "TV",
        "comment": "",
        "url": "",
        "downloaded": False,
    }

    missing_csrf = anonymous_client.post("/api/v1/anime", json=payload)
    assert missing_csrf.status_code == status.HTTP_403_FORBIDDEN
    assert missing_csrf.json()["error"]["code"] == "csrf_missing"

    invalid_csrf = anonymous_client.post(
        "/api/v1/anime",
        headers={"X-CSRF-Token": "not-the-cookie-value"},
        json=payload,
    )
    assert invalid_csrf.status_code == status.HTTP_403_FORBIDDEN
    assert invalid_csrf.json()["error"]["code"] == "csrf_invalid"
