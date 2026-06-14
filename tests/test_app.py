import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

initial_activities = copy.deepcopy(activities)
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))
    yield


def test_get_activities_returns_all_activities():
    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == initial_activities


def test_signup_for_activity_adds_participant():
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = quote("Chess Club", safe="")

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_error():
    # Arrange
    email = "michael@mergington.edu"
    activity_name = quote("Chess Club", safe="")

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_delete_participant_removes_existing_participant():
    # Arrange
    email = "james@mergington.edu"
    activity_name = quote("Basketball Team", safe="")

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Basketball Team"}
    assert email not in activities["Basketball Team"]["participants"]


def test_delete_missing_participant_returns_not_found():
    # Arrange
    email = "missing@mergington.edu"
    activity_name = quote("Chess Club", safe="")

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
