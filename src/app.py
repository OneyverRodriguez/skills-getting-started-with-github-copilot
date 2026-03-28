"""
High School Management System API

A FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mergington High School API",
    description="API for viewing and signing up for extracurricular activities",
    version="1.0.0"
)

# Add CORS middleware for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:3000"],  # Restrict to specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
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


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


def is_valid_email(email: str) -> bool:
    """Simple email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    try:
        # Validate email format
        if not is_valid_email(email):
            logger.warning(f"Invalid email format attempted: {email}")
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        # Normalize email (lowercase, strip whitespace)
        email = email.lower().strip()
        
        # Validate activity exists
        if activity_name not in activities:
            logger.warning(f"Signup attempt for non-existent activity: {activity_name}")
            raise HTTPException(status_code=404, detail="Activity not found")

        # Get the specific activity
        activity = activities[activity_name]

        # Check if activity is full
        if len(activity["participants"]) >= activity["max_participants"]:
            logger.warning(f"Activity {activity_name} is full")
            raise HTTPException(status_code=400, detail="Activity is full")

        # Validate student is not already signed up
        if email in activity["participants"]:
            logger.info(f"Duplicate signup attempt: {email} for {activity_name}")
            raise HTTPException(status_code=400, detail="Student already signed up")

        # Add student
        activity["participants"].append(email)
        logger.info(f"Signup successful: {email} for {activity_name}")
        return {"message": f"Signed up {email} for {activity_name}"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during signup: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/activities/{activity_name}/signup")
def remove_from_activity(activity_name: str, email: str):
    """Remove a student from an activity"""
    try:
        # Normalize email
        email = email.lower().strip()
        
        if activity_name not in activities:
            logger.warning(f"Removal attempt from non-existent activity: {activity_name}")
            raise HTTPException(status_code=404, detail="Activity not found")

        activity = activities[activity_name]

        if email not in activity["participants"]:
            logger.warning(f"Removal attempt for non-enrolled student: {email} from {activity_name}")
            raise HTTPException(status_code=400, detail="Student not signed up for this activity")

        activity["participants"].remove(email)
        logger.info(f"Removal successful: {email} from {activity_name}")
        return {"message": f"Removed {email} from {activity_name}"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during removal: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
