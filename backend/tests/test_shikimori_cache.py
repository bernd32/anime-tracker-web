import httpx

from app.api.deps import get_shikimori_service, session_context
from app.core.config import get_settings
from app.services.shikimori import ShikimoriService


class DummyResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {
            "data": {
                "animes": [
                    {
                        "russian": "Фрирен",
                        "japanese": "葬送のフリーレン",
                        "score": "8.9",
                        "episodes": 28,
                        "airedOn": {"date": "2023-09-29"},
                        "fansubbers": ["Fansub"],
                        "studios": [{"name": "Madhouse"}],
                        "genres": [{"name": "Fantasy"}],
                        "description": "desc",
                    }
                ]
            }
        }


class DummyClient:
    def __init__(self):
        self.calls = 0

    def post(self, *args, **kwargs):
        self.calls += 1
        return DummyResponse()


class FailingClient:
    def post(self, *args, **kwargs):
        raise httpx.ConnectError("network down")


def test_shikimori_uses_cache(client):
    create_response = client.post(
        "/api/v1/anime",
        json={
            "name": "Frieren",
            "year": 2023,
            "season": "fall",
            "status": "unwatched",
            "type": "TV",
            "comment": "",
            "url": "",
            "downloaded": False,
        },
    )
    anime_id = create_response.json()["item"]["id"]

    dummy_client = DummyClient()
    service = ShikimoriService(session_context, get_settings(), client=dummy_client)
    client.app.dependency_overrides[get_shikimori_service] = lambda: service

    first = client.get(f"/api/v1/anime/{anime_id}/shikimori")
    assert first.status_code == 200
    assert first.json()["cache"]["source"] == "network"
    assert dummy_client.calls == 1

    second = client.get(f"/api/v1/anime/{anime_id}/shikimori")
    assert second.status_code == 200
    assert second.json()["cache"]["source"] == "memory"
    assert dummy_client.calls == 1

    client.app.dependency_overrides.clear()


def test_shikimori_returns_stale_cache_on_network_failure(client):
    create_response = client.post(
        "/api/v1/anime",
        json={
            "name": "Frieren",
            "year": 2023,
            "season": "fall",
            "status": "unwatched",
            "type": "TV",
            "comment": "",
            "url": "",
            "downloaded": False,
        },
    )
    anime_id = create_response.json()["item"]["id"]

    warm_service = ShikimoriService(session_context, get_settings(), client=DummyClient())
    client.app.dependency_overrides[get_shikimori_service] = lambda: warm_service
    first = client.get(f"/api/v1/anime/{anime_id}/shikimori")
    assert first.status_code == 200
    assert first.json()["cache"]["source"] == "network"

    failing_service = ShikimoriService(session_context, get_settings(), client=FailingClient())
    failing_service.cache = warm_service.cache
    client.app.dependency_overrides[get_shikimori_service] = lambda: failing_service

    second = client.get(f"/api/v1/anime/{anime_id}/shikimori?force_refresh=true")
    assert second.status_code == 200, second.text
    assert second.json()["cache"]["source"] == "memory"
    assert second.json()["cache"]["stale"] is True

    client.app.dependency_overrides.clear()
