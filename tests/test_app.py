import copy
import urllib.parse

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    yield


def test_get_activities_returns_activity_data():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    url = f"/activities/{urllib.parse.quote(activity_name)}/signup?email={urllib.parse.quote(new_email)}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == f"Signed up {new_email} for {activity_name}"
    assert new_email in activities[activity_name]["participants"]


def test_duplicate_signup_returns_400():
    # Arrange
    activity_name = "Chess Club"
    existing_email = activities[activity_name]["participants"][0]
    url = f"/activities/{urllib.parse.quote(activity_name)}/signup?email={urllib.parse.quote(existing_email)}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_unregisters_student():
    # Arrange
    activity_name = "Chess Club"
    email_to_remove = activities[activity_name]["participants"][0]
    url = f"/activities/{urllib.parse.quote(activity_name)}/participants?email={urllib.parse.quote(email_to_remove)}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email_to_remove} from {activity_name}"
    assert email_to_remove not in activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    missing_email = "missing@mergington.edu"
    url = f"/activities/{urllib.parse.quote(activity_name)}/participants?email={urllib.parse.quote(missing_email)}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
