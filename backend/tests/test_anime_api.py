from fastapi import status


def test_anime_crud_and_filters(client):
    create_payload = {
        "name": "Frieren",
        "year": 2023,
        "season": "fall",
        "status": "unwatched",
        "type": "TV",
        "comment": "hello",
        "url": "https://example.com/anime/1",
        "downloaded": False,
    }
    response = client.post("/api/v1/anime", json=create_payload)
    assert response.status_code == status.HTTP_201_CREATED, response.text
    created = response.json()["item"]
    anime_id = created["id"]

    get_response = client.get(f"/api/v1/anime/{anime_id}")
    assert get_response.status_code == 200
    assert get_response.json()["item"]["name"] == "Frieren"

    list_response = client.get("/api/v1/anime", params={"search": "frie"})
    assert list_response.status_code == 200
    assert list_response.json()["meta"]["total"] == 1

    patch_response = client.patch(
        f"/api/v1/anime/{anime_id}",
        json={"status": "watching", "downloaded": True},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["item"]["status"] == "watching"
    assert patch_response.json()["item"]["downloaded"] is True

    pre_response = client.post(
        "/api/v1/anime",
        json={
            "name": "Nana",
            "year": 2006,
            "season": "spring",
            "status": "unwatched",
            "type": "TV",
            "comment": "",
            "url": "",
            "downloaded": False,
        },
    )
    assert pre_response.status_code == 201
    assert pre_response.json()["item"]["season"] == "other"

    pre_list = client.get("/api/v1/anime", params={"scope_kind": "pre2010"})
    assert pre_list.status_code == 200
    assert pre_list.json()["meta"]["total"] == 1

    delete_response = client.delete(f"/api/v1/anime/{anime_id}")
    assert delete_response.status_code == 204


def test_duplicate_detection_is_case_and_space_insensitive(client):
    payload = {
        "name": "Fullmetal   Alchemist",
        "year": 2003,
        "season": "other",
        "status": "unwatched",
        "type": "TV",
        "comment": "",
        "url": "",
        "downloaded": False,
    }
    assert client.post("/api/v1/anime", json=payload).status_code == 201
    duplicate = client.post(
        "/api/v1/anime",
        json={**payload, "name": " fullmetal alchemist  "},
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "anime_conflict"


def test_random_pick_and_stats(client):
    items = [
        {"name": "A", "year": 2024, "season": "winter", "status": "unwatched", "type": "TV", "comment": "", "url": "", "downloaded": False},
        {"name": "B", "year": 2024, "season": "spring", "status": "completed", "type": "Movie", "comment": "", "url": "", "downloaded": False},
    ]
    for item in items:
        assert client.post("/api/v1/anime", json=item).status_code == 201

    random_response = client.get("/api/v1/anime/random-pick", params={"scope_kind": "year", "scope_year": 2024})
    assert random_response.status_code == 200
    body = random_response.json()
    assert body["meta"]["candidate_count"] == 1
    assert body["item"]["name"] == "A"

    stats_response = client.get("/api/v1/anime/stats")
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["totals"]["total"] == 2
    assert stats["totals"]["completed"] == 1
