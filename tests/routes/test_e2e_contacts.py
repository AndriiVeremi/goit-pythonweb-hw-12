from unittest.mock import patch


def test_create_contact(client, get_token):
    with patch("src.services.auth.redis_client") as redis_mock:
        redis_mock.exists.return_value = False
        response = client.post(
            "/api/contacts",
            json={
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "email": "test@email.ua",
                "phone": "0000000000",
                "birthday": "2000-11-21",
                "extra_info": "test extra info",
            },
            headers={"Authorization": f"Bearer {get_token}"},
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["first_name"] == "test_first_name"
        assert data["last_name"] == "test_last_name"
        assert data["email"] == "test@email.ua"
        assert data["phone"] == "0000000000"
        assert data["birthday"] == "2000-11-21"
        assert data["extra_info"] == "test extra info"
        assert "id" in data


def test_get_contact(client, get_token):
    with patch("src.services.auth.redis_client") as redis_mock:
        redis_mock.exists.return_value = False
        response = client.get(
            "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["first_name"] == "test_first_name"
        assert "id" in data


def test_get_contact_not_found(client, get_token):
    with patch("src.services.auth.redis_client") as redis_mock:
        redis_mock.exists.return_value = False
        response = client.get(
            "/api/contacts/2", headers={"Authorization": f"Bearer {get_token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Contact not found"


def test_get_contacts(client, get_token):
    with patch("src.services.auth.redis_client") as redis_mock:
        redis_mock.exists.return_value = False
        response = client.get(
            "/api/contacts", headers={"Authorization": f"Bearer {get_token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        if data:  # Перевіряємо тільки якщо є контакти
            assert data[0]["first_name"] == "test_first_name"
            assert "id" in data[0]


def test_update_contact(client, get_token):
    with patch("src.services.auth.redis_client") as redis_mock:
        redis_mock.exists.return_value = False
        response = client.put(
            "/api/contacts/1",
            json={"first_name": "new_first_name", "extra_info": "new description"},
            headers={"Authorization": f"Bearer {get_token}"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["first_name"] == "new_first_name"
        assert data["extra_info"] == "new description"
        assert "id" in data


def test_update_contact_not_found(client, get_token):
    with patch("src.services.auth.redis_client") as redis_mock:
        redis_mock.exists.return_value = False
        response = client.put(
            "/api/contacts/2",
            json={"first_name": "new_test_contact"},
            headers={"Authorization": f"Bearer {get_token}"},
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Contact not found"


def test_delete_contact(client, get_token):
    with patch("src.services.auth.redis_client") as redis_mock:
        redis_mock.exists.return_value = False
        response = client.delete(
            "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
        )
        assert response.status_code == 204, response.text
