"""
Test suite for FastAPI endpoints using Arrange-Act-Assert (AAA) pattern.

Tests cover all CRUD operations for the activity registration system:
- GET / - Redirect to static index
- GET /activities - Retrieve all activities
- POST /activities/{activity_name}/signup - Register student for activity
- DELETE /activities/{activity_name}/signup - Unregister student from activity
"""

import pytest


class TestRootEndpoint:
    """Tests for the root endpoint GET /"""

    def test_root_redirects_to_static_index(self, client):
        """
        ARRANGE: Client is ready to make requests
        ACT: Make GET request to root endpoint
        ASSERT: Verify redirect response to /static/index.html
        """
        # ARRANGE
        expected_url = "/static/index.html"

        # ACT
        response = client.get("/", follow_redirects=False)

        # ASSERT
        assert response.status_code == 307
        assert response.headers["location"] == expected_url


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        ARRANGE: Client is ready, activities are in initial state
        ACT: Make GET request to /activities
        ASSERT: Verify all 9 activities are returned with correct structure
        """
        # ARRANGE
        expected_activity_count = 9
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class",
            "Basketball Team", "Soccer Club", "Art Club",
            "Drama Club", "Debate Club", "Science Club"
        ]

        # ACT
        response = client.get("/activities")

        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert len(data) == expected_activity_count
        assert set(data.keys()) == set(expected_activities)

    def test_get_activities_returns_correct_structure(self, client, reset_activities):
        """
        ARRANGE: Client is ready
        ACT: Make GET request to /activities
        ASSERT: Verify each activity has required fields with correct types
        """
        # ARRANGE
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # ACT
        response = client.get("/activities")

        # ASSERT
        assert response.status_code == 200
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data, dict)
            assert set(activity_data.keys()) == required_fields
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_includes_initial_participants(self, client, reset_activities):
        """
        ARRANGE: Client is ready, activities have initial participants
        ACT: Make GET request to /activities
        ASSERT: Verify activities contain their initial participants
        """
        # ARRANGE
        expected_initial_state = {
            "Chess Club": ["michael@mergington.edu", "daniel@mergington.edu"],
            "Programming Class": ["emma@mergington.edu", "sophia@mergington.edu"],
        }

        # ACT
        response = client.get("/activities")

        # ASSERT
        assert response.status_code == 200
        data = response.json()
        
        for activity_name, expected_participants in expected_initial_state.items():
            assert data[activity_name]["participants"] == expected_participants


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success_adds_email_to_activity(self, client, reset_activities):
        """
        ARRANGE: Client is ready, new email to register
        ACT: Make POST request to signup endpoint with valid activity and email
        ASSERT: Verify response confirms signup and participant is added
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_verifies_participant_added_to_roster(self, client, reset_activities):
        """
        ARRANGE: Client ready, new email to register
        ACT: Sign up student, then retrieve activities to verify roster
        ASSERT: Verify new participant appears in activity's participant list
        """
        # ARRANGE
        activity_name = "Programming Class"
        email = "alice@mergington.edu"

        # ACT
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        activities_response = client.get("/activities")

        # ASSERT
        assert signup_response.status_code == 200
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]

    def test_signup_activity_not_found_returns_404(self, client, reset_activities):
        """
        ARRANGE: Client ready, nonexistent activity name
        ACT: Attempt to signup for activity that doesn't exist
        ASSERT: Verify 404 error response
        """
        # ARRANGE
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_email_returns_400(self, client, reset_activities):
        """
        ARRANGE: Client ready, email already signed up for activity
        ACT: Attempt to signup with email that's already registered
        ASSERT: Verify 400 error response with appropriate message
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered for Chess Club

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_same_email_different_activities_succeeds(self, client, reset_activities):
        """
        ARRANGE: Client ready, email already in one activity
        ACT: Sign up same email for a different activity
        ASSERT: Verify signup succeeds (student can join multiple activities)
        """
        # ARRANGE
        email = "michael@mergington.edu"  # Already in Chess Club
        different_activity = "Basketball Team"

        # ACT
        response = client.post(
            f"/activities/{different_activity}/signup",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert email in data["message"]
        assert different_activity in data["message"]


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""

    def test_unregister_success_removes_email_from_activity(self, client, reset_activities):
        """
        ARRANGE: Client ready, email currently registered for activity
        ACT: Make DELETE request to unregister endpoint
        ASSERT: Verify response confirms unregistration
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_unregister_verifies_participant_removed_from_roster(self, client, reset_activities):
        """
        ARRANGE: Client ready, email registered for activity
        ACT: Unregister student, then retrieve activities to verify removal
        ASSERT: Verify participant is no longer in activity's participant list
        """
        # ARRANGE
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Already registered
        
        # ACT
        unregister_response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        activities_response = client.get("/activities")

        # ASSERT
        assert unregister_response.status_code == 200
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]

    def test_unregister_activity_not_found_returns_404(self, client, reset_activities):
        """
        ARRANGE: Client ready, nonexistent activity name
        ACT: Attempt to unregister from activity that doesn't exist
        ASSERT: Verify 404 error response
        """
        # ARRANGE
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_email_not_registered_returns_400(self, client, reset_activities):
        """
        ARRANGE: Client ready, email not registered for activity
        ACT: Attempt to unregister email that's not in the activity
        ASSERT: Verify 400 error response with appropriate message
        """
        # ARRANGE
        activity_name = "Basketball Team"
        email = "notregistered@mergington.edu"  # Not in Basketball Team

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_sequence_signup_then_unregister(self, client, reset_activities):
        """
        ARRANGE: Client ready, new email to test full signup/unregister cycle
        ACT: Sign up new email, then unregister same email
        ASSERT: Verify both operations succeed and roster reflects changes
        """
        # ARRANGE
        activity_name = "Art Club"
        email = "cycle@mergington.edu"

        # ACT
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        verify_after_signup = client.get("/activities")
        
        unregister_response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        verify_after_unregister = client.get("/activities")

        # ASSERT
        assert signup_response.status_code == 200
        assert email in verify_after_signup.json()[activity_name]["participants"]
        
        assert unregister_response.status_code == 200
        assert email not in verify_after_unregister.json()[activity_name]["participants"]
