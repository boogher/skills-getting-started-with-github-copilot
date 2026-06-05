from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
initial_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(initial_activities))
    yield
    activities.clear()
    activities.update(deepcopy(initial_activities))


def test_get_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["max_participants"] == 12
    assert "participants" in data["Chess Club"]


def test_signup_for_activity():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_fails():
    existing_email = activities["Chess Club"]["participants"][0]

    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": existing_email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant():
    email_to_remove = activities["Chess Club"]["participants"][0]

    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email_to_remove},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email_to_remove} from Chess Club"
    assert email_to_remove not in activities["Chess Club"]["participants"]


def test_remove_nonexistent_participant():
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "unknown@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
