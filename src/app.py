"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import List, Dict
from pathlib import Path
from fastapi.staticfiles import StaticFiles





app = FastAPI(title="Merington High School Activities")
BASE_DIR = Path(__file__).parent  # هذا يشير إلى src/
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# --------- Data Model (in-memory) ---------
class Activity(BaseModel):
    name: str
    description: str
    schedule: str
    max_participants: int
    participants: List[EmailStr] = []

# بيانات تجريبية
activities: Dict[str, Activity] = {
    "Chess Club": Activity(
        name="Chess Club",
        description="Learn strategies and compete in chess tournaments",
        schedule="Fridays, 3:30 PM - 5:00 PM",
        max_participants=12,
        participants=["michael@mergington.edu", "daniel@mergington.edu"]
    ),
    "Programming Class": Activity(
        name="Programming Class",
        description="Learn programming fundamentals and build software projects",
        schedule="Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        max_participants=20,
        participants=["emma@mergington.edu", "sophia@mergington.edu"]
    ),
    "Gym Class": Activity(
        name="Gym Class",
        description="Physical education and sports activities",
        schedule="Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        max_participants=30,
        participants=["john@mergington.edu", "olivia@mergington.edu"]
    ),
}

# --------- Helpers ---------
def require_school_email(email: str) -> None:
    if not email.lower().endswith("@mergington.edu"):
        raise HTTPException(status_code=400, detail="Email must be @mergington.edu")

def get_activity_or_404(name: str) -> Activity:
    # مطابق للاسم بالحروف والمسافات
    act = activities.get(name)
    if not act:
        # جرّب تطابق غير حساس لحالة الأحرف
        for k in activities.keys():
            if k.lower() == name.lower():
                return activities[k]
        raise HTTPException(status_code=404, detail="Activity not found")
    return act

# --------- Endpoints ---------
@app.get("/activities", response_model=List[Activity])
def list_activities():
    """أعد كل الأنشطة مع التفاصيل والعدد الحالي للمشاركين."""
    return list(activities.values())

@app.post("/activities/{activity_name}/signup")
def signup_for_activity(
    activity_name: str,
    email: EmailStr = Query(..., description="Student email, must be @mergington.edu"),
):
    """سجّل الطالب في نشاط. يمنع التكرار ويتأكد من السعة."""
    require_school_email(str(email))
    act = get_activity_or_404(activity_name)

    if str(email) in [e.lower() for e in map(str, act.participants)]:
        raise HTTPException(status_code=409, detail="Student already signed up")

    if len(act.participants) >= act.max_participants:
        raise HTTPException(status_code=409, detail="Activity is full")

    act.participants.append(email)
    return {
        "message": f"Signed up {email} for {act.name}",
        "current_participants": len(act.participants),
        "max_participants": act.max_participants,
    }
