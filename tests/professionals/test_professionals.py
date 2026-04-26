import pytest
from httpx import AsyncClient

STORES_URL = "/api/v1/stores"
REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"

ADMIN_USER = {
    "name": "Admin Dono",
    "email": "admin@example.com",
    "password": "password123",
    "role": "store_admin",
    "accepted_terms": True,
}

OTHER_ADMIN_USER = {
    "name": "Outro Admin",
    "email": "outro@example.com",
    "password": "password123",
    "role": "store_admin",
    "accepted_terms": True,
}

CLIENT_USER = {
    "name": "Cliente",
    "email": "cliente@example.com",
    "password": "password123",
    "role": "client",
    "accepted_terms": True,
}

VALID_STORE = {"name": "Salão da Ana"}

VALID_PROFESSIONAL = {
    "name": "Maria Profissional",
    "email": "maria@example.com",
    "password": "senha123",
}


async def _get_token(client: AsyncClient, user: dict) -> str:
    await client.post(REGISTER_URL, json=user)
    response = await client.post(
        LOGIN_URL, json={"email": user["email"], "password": user["password"]}
    )
    return response.json()["access_token"]


async def _create_store(client: AsyncClient, token: str) -> str:
    response = await client.post(
        STORES_URL,
        json=VALID_STORE,
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json()["id"]


# ---------------------------------------------------------------------------
# POST /stores/{store_id}/professionals — create professional (new user)
# ---------------------------------------------------------------------------


async def test_add_professional_success(client: AsyncClient):
    token = await _get_token(client, ADMIN_USER)
    store_id = await _create_store(client, token)

    response = await client.post(
        f"{STORES_URL}/{store_id}/professionals",
        json=VALID_PROFESSIONAL,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    body = response.json()
    assert "id" in body
    assert body["store_id"] == store_id
    assert "deleted_at" not in body


async def test_add_professional_not_owner(client: AsyncClient):
    admin_token = await _get_token(client, ADMIN_USER)
    other_token = await _get_token(client, OTHER_ADMIN_USER)
    store_id = await _create_store(client, admin_token)

    response = await client.post(
        f"{STORES_URL}/{store_id}/professionals",
        json=VALID_PROFESSIONAL,
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 403


async def test_add_professional_duplicate_email(client: AsyncClient):
    token = await _get_token(client, ADMIN_USER)
    store_id = await _create_store(client, token)

    await client.post(
        f"{STORES_URL}/{store_id}/professionals",
        json=VALID_PROFESSIONAL,
        headers={"Authorization": f"Bearer {token}"},
    )
    response = await client.post(
        f"{STORES_URL}/{store_id}/professionals",
        json=VALID_PROFESSIONAL,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 409


async def test_add_professional_unauthenticated(client: AsyncClient):
    token = await _get_token(client, ADMIN_USER)
    store_id = await _create_store(client, token)

    response = await client.post(
        f"{STORES_URL}/{store_id}/professionals",
        json=VALID_PROFESSIONAL,
    )
    assert response.status_code == 401


async def test_add_professional_client_role(client: AsyncClient):
    admin_token = await _get_token(client, ADMIN_USER)
    client_token = await _get_token(client, CLIENT_USER)
    store_id = await _create_store(client, admin_token)

    response = await client.post(
        f"{STORES_URL}/{store_id}/professionals",
        json=VALID_PROFESSIONAL,
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# POST /stores/{store_id}/professionals/me — admin registers as professional
# ---------------------------------------------------------------------------


async def test_add_admin_as_professional_success(client: AsyncClient):
    token = await _get_token(client, ADMIN_USER)
    store_id = await _create_store(client, token)

    response = await client.post(
        f"{STORES_URL}/{store_id}/professionals/me",
        json={"bio": "Especialista em cortes", "photo_url": None},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    body = response.json()
    assert "id" in body
    assert body["store_id"] == store_id
    assert body["bio"] == "Especialista em cortes"


async def test_add_admin_as_professional_empty_payload(client: AsyncClient):
    token = await _get_token(client, ADMIN_USER)
    store_id = await _create_store(client, token)

    response = await client.post(
        f"{STORES_URL}/{store_id}/professionals/me",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201


async def test_add_admin_as_professional_not_owner(client: AsyncClient):
    admin_token = await _get_token(client, ADMIN_USER)
    other_token = await _get_token(client, OTHER_ADMIN_USER)
    store_id = await _create_store(client, admin_token)

    response = await client.post(
        f"{STORES_URL}/{store_id}/professionals/me",
        json={},
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 403


async def test_add_admin_as_professional_duplicate(client: AsyncClient):
    token = await _get_token(client, ADMIN_USER)
    store_id = await _create_store(client, token)

    await client.post(
        f"{STORES_URL}/{store_id}/professionals/me",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = await client.post(
        f"{STORES_URL}/{store_id}/professionals/me",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 409


async def test_add_admin_as_professional_unauthenticated(client: AsyncClient):
    token = await _get_token(client, ADMIN_USER)
    store_id = await _create_store(client, token)

    response = await client.post(
        f"{STORES_URL}/{store_id}/professionals/me",
        json={},
    )
    assert response.status_code == 401


async def test_add_admin_as_professional_client_role(client: AsyncClient):
    admin_token = await _get_token(client, ADMIN_USER)
    client_token = await _get_token(client, CLIENT_USER)
    store_id = await _create_store(client, admin_token)

    response = await client.post(
        f"{STORES_URL}/{store_id}/professionals/me",
        json={},
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert response.status_code == 403
