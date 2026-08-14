from fastapi.testclient import TestClient


def test_health_and_capabilities(client: TestClient) -> None:
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok", "version": "0.1.0"}

    capabilities = client.get("/api/v1/capabilities")
    assert capabilities.status_code == 200
    assert capabilities.json()["active_source"] == "demo"
    assert capabilities.json()["steam_configured"] is False
    assert capabilities.json()["llm_configured"] is False
    assert capabilities.json()["steam_write_supported"] is False


def test_demo_dashboard_has_useful_shelves(client: TestClient) -> None:
    response = client.get("/api/v1/dashboard")
    assert response.status_code == 200
    payload = response.json()

    assert payload["account"]["is_demo"] is True
    assert payload["stats"]["total_games"] == 14
    assert payload["stats"]["unplayed_games"] == 4
    assert payload["stats"]["recent_games"] == 3
    assert payload["spotlight"]["name"] == "Balatro"
    assert [shelf["id"] for shelf in payload["shelves"]] == [
        "continue",
        "unplayed",
        "rediscover",
    ]


def test_games_can_be_filtered_searched_and_favorited(client: TestClient) -> None:
    unplayed = client.get("/api/v1/games", params={"status": "unplayed", "sort": "name"})
    assert unplayed.status_code == 200
    assert unplayed.json()["total"] == 4
    assert unplayed.json()["items"][0]["playtime_forever"] == 0

    search = client.get("/api/v1/games", params={"q": "hades"})
    assert search.status_code == 200
    game = search.json()["items"][0]
    assert game["name"] == "Hades"
    assert game["favorite"] is True

    updated = client.patch(f"/api/v1/games/{game['app_id']}", json={"favorite": False})
    assert updated.status_code == 200
    assert updated.json()["favorite"] is False


def test_local_recommendation_is_structured_and_deterministic(client: TestClient) -> None:
    request = {"prompt": "我想轻松一点，从还没启动的游戏里挑三款", "prefer_unplayed": True}
    first = client.post("/api/v1/recommendations", json=request)
    second = client.post("/api/v1/recommendations", json=request)

    assert first.status_code == 200
    assert first.json() == second.json()
    payload = first.json()
    assert payload["generation_mode"] == "deterministic"
    assert len(payload["picks"]) == 3
    assert all(pick["game"]["status"] == "unplayed" for pick in payload["picks"])
    assert "OPENAI_API_KEY" in payload["fallback_reason"]


def test_collection_suggestions_are_read_only_drafts(client: TestClient) -> None:
    response = client.get("/api/v1/collections")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 4
    assert payload[0]["id"] == "in-motion"
    assert payload[0]["total"] == 3
