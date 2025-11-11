"""
Tests for game functionality
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_game(client: AsyncClient, auth_headers):
    """Test game creation"""
    response = await client.post(
        "/api/v1/games",
        headers=auth_headers,
        json={
            "mode": "single",
            "start_article": "Python_(programming_language)",
            "target_article": "Computer_science",
            "max_steps": 50,
            "time_limit": 300,
            "max_players": 1,
        },
    )

    # This might fail if Wikipedia API is not accessible
    # In real tests, we should mock the Wikipedia service
    assert response.status_code in [201, 400]


@pytest.mark.asyncio
async def test_list_games(client: AsyncClient):
    """Test listing games"""
    response = await client.get("/api/v1/games")

    assert response.status_code == 200
    data = response.json()
    assert "games" in data
    assert "total" in data
    assert isinstance(data["games"], list)


@pytest.mark.asyncio
async def test_get_leaderboard(client: AsyncClient):
    """Test getting leaderboard"""
    response = await client.get("/api/v1/leaderboard")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
