"""
Test suite for Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Create test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities_state():
    """Reset activities state before each test to avoid interference"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball with training and tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis lessons and matches for all skill levels",
            "schedule": "Tuesdays and Thursdays, 4:30 PM - 5:30 PM",
            "max_participants": 10,
            "participants": ["lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Join our school band and orchestra performances",
            "schedule": "Mondays and Fridays, 4:00 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop critical thinking and public speaking skills",
            "schedule": "Thursdays, 3:30 PM - 4:45 PM",
            "max_participants": 16,
            "participants": ["grace@mergington.edu"]
        },
        "Science Research": {
            "description": "Conduct experiments and research projects in STEM",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": ["aaron@mergington.edu", "mia@mergington.edu"]
        }
    }
    
    # Clear and repopulate activities before each test
    activities.clear()
    for key, value in original_activities.items():
        activities[key] = {
            "description": value["description"],
            "schedule": value["schedule"],
            "max_participants": value["max_participants"],
            "participants": value["participants"].copy()  # Copy list to avoid shared references
        }
    
    yield
    
    # Cleanup after test (optional but good practice)
    activities.clear()
    for key, value in original_activities.items():
        activities[key] = {
            "description": value["description"],
            "schedule": value["schedule"],
            "max_participants": value["max_participants"],
            "participants": value["participants"].copy()
        }


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_contains_required_fields(self):
        """Test that activities contain required fields"""
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)

    def test_get_activities_returns_correct_participant_count(self):
        """Test that participant counts are accurate"""
        response = client.get("/activities")
        data = response.json()
        # Chess Club should have at least 2 participants
        assert len(data["Chess Club"]["participants"]) >= 2


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert "newstudent@mergington.edu" in response.json()["message"]

    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/NonExistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_participant(self):
        """Test that duplicate signup is prevented"""
        email = "duplicate@mergington.edu"
        # First signup should succeed
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response1.status_code == 200

        # Second signup with same email should fail
        response2 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_verifies_participant_added(self):
        """Test that participant is actually added to activity"""
        email = "verify@mergington.edu"
        client.post(f"/activities/Programming%20Class/signup?email={email}")

        response = client.get("/activities")
        data = response.json()
        assert email in data["Programming Class"]["participants"]


class TestRemoveFromActivity:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""

    def test_remove_participant_success(self):
        """Test successful removal of participant"""
        email = "remove@mergington.edu"
        # Add participant first
        client.post(f"/activities/Gym%20Class/signup?email={email}")

        # Remove participant
        response = client.delete(
            f"/activities/Gym%20Class/signup?email={email}"
        )
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

    def test_remove_participant_not_signed_up(self):
        """Test removal of participant who is not signed up"""
        response = client.delete(
            "/activities/Chess%20Club/signup?email=notexist@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_remove_activity_not_found(self):
        """Test removal from non-existent activity"""
        response = client.delete(
            "/activities/Fake%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_verifies_participant_removed(self):
        """Test that participant is actually removed from activity"""
        email = "verify_remove@mergington.edu"
        # Add participant
        client.post(f"/activities/Science%20Research/signup?email={email}")

        # Verify participant was added
        response1 = client.get("/activities")
        data1 = response1.json()
        assert email in data1["Science Research"]["participants"]

        # Remove participant
        client.delete(f"/activities/Science%20Research/signup?email={email}")

        # Verify participant was removed
        response2 = client.get("/activities")
        data2 = response2.json()
        assert email not in data2["Science Research"]["participants"]


class TestRootRedirect:
    """Tests for root endpoint"""

    def test_root_redirects_to_static(self):
        """Test that root path redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestIntegration:
    """Integration tests for complete workflows"""

    def test_full_signup_and_removal_workflow(self):
        """Test complete workflow: signup, verify, remove, verify again"""
        email = "workflow@mergington.edu"
        activity = "Chess Club"

        # Signup
        response1 = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response1.status_code == 200

        # Verify signup
        response2 = client.get("/activities")
        assert email in response2.json()[activity]["participants"]

        # Remove
        response3 = client.delete(f"/activities/Chess%20Club/signup?email={email}")
        assert response3.status_code == 200

        # Verify removal
        response4 = client.get("/activities")
        assert email not in response4.json()[activity]["participants"]

    def test_participant_limit_validation(self):
        """Test that max participants is tracked correctly"""
        response = client.get("/activities")
        data = response.json()

        for activity_name, activity in data.items():
            participants_count = len(activity["participants"])
            max_participants = activity["max_participants"]
            assert participants_count <= max_participants, \
                f"{activity_name} exceeds max participants"
