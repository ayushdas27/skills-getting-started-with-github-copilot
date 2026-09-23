"""
Tests for the Mergington High School Activities API.
Uses pytest and FastAPI TestClient with the AAA (Arrange-Act-Assert) pattern.
"""

from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_200(self):
        # Arrange - no setup needed

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self):
        # Arrange
        expected_count = len(activities)

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert len(data) == expected_count

    def test_get_activities_contains_expected_keys(self):
        # Arrange - no setup needed

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for name, details in data.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def setup_method(self):
        """Reset activities before each test."""
        activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]

    def test_signup_success(self):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]

        # Cleanup
        activities[activity_name]["participants"].remove(email)

    def test_signup_activity_not_found(self):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_registration(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is already signed up"


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def setup_method(self):
        """Reset activities before each test."""
        activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]

    def test_unregister_success(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]

    def test_unregister_activity_not_found(self):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 404

    def test_unregister_student_not_signed_up(self):
        # Arrange
        activity_name = "Chess Club"
        email = "unknown@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"


class TestRootRedirect:
    """Tests for the root endpoint."""

    def test_root_redirects(self):
        # Arrange - no setup needed

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
