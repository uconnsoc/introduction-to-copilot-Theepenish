"""
Pytest configuration and fixtures for FastAPI tests.
Provides setup and teardown for test client and application state.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """
    Fixture: Provides a TestClient for making requests to the FastAPI app.
    This client is configured for synchronous testing of all endpoints.
    """
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Fixture: Resets the in-memory activities dictionary to a clean state
    before each test. Ensures test isolation and predictable initial conditions.
    
    This fixture should be used in any test that modifies activities (signup/unregister tests).
    """
    # Store original activities
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
            "description": "Practice and compete in basketball games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Train and play soccer matches",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act in plays and improve theatrical skills",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": ["mason@mergington.edu", "charlotte@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["ethan@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and learn about scientific concepts",
            "schedule": "Tuesdays, 3:00 PM - 4:30 PM",
            "max_participants": 25,
            "participants": ["harper@mergington.edu", "logan@mergington.edu"]
        }
    }
    
    # Clear current activities and restore original state (ARRANGE phase)
    activities.clear()
    activities.update(original_activities)
    
    yield  # Hand control to test
    
    # Cleanup: reset to original state after test completes (cleanup phase)
    activities.clear()
    activities.update(original_activities)
