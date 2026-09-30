import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def activities(monkeypatch):
    activity_store = {
        "Chess Club": {
            "description": "Learn chess strategies",
            "schedule": "Fridays, 3:30 PM",
            "max_participants": 3,
            "participants": ["existing@mergington.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activity_store)
    return activity_store


@pytest.fixture
def client(activities):
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client, activities):
    # Arrange
    expected_activities = activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client, activities):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert activities["Chess Club"]["participants"] == [
        "existing@mergington.edu",
        email,
    ]


def test_signup_rejects_duplicate_participant(client, activities):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert activities["Chess Club"]["participants"] == [email]


def test_signup_rejects_unknown_activity(client, activities):
    # Arrange
    original_activities = activities.copy()

    # Act
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activities == original_activities


def test_unregister_removes_participant(client, activities):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Chess Club"
    }
    assert activities["Chess Club"]["participants"] == []


def test_unregister_rejects_unknown_activity(client, activities):
    # Arrange
    original_activities = activities.copy()

    # Act
    response = client.delete(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activities == original_activities


def test_unregister_rejects_unenrolled_participant(client, activities):
    # Arrange
    email = "absent@mergington.edu"
    original_participants = activities["Chess Club"]["participants"].copy()

    # Act
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student not signed up for this activity"
    }
    assert activities["Chess Club"]["participants"] == original_participants