from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
from enum import Enum
import uuid

app = FastAPI(title="Habit Tracker API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class HabitCategory(str, Enum):
    HEALTH = "health"
    LEARNING = "learning"
    PRODUCTIVITY = "productivity"
    MINDFULNESS = "mindfulness"
    OTHER = "other"

class HabitSchedule(str, Enum):
    DAILY = "daily"
    WEEKDAYS = "weekdays"
    WEEKEND = "weekend"

class HabitBase(BaseModel):
    name: str
    category: HabitCategory
    schedule: HabitSchedule
    reminder_time: Optional[str] = None

class HabitCreate(HabitBase):
    pass

class Habit(HabitBase):
    id: str
    streak: int
    created_at: datetime

# Storage
habits_db = {}
completions_db = {}

@app.get("/")
async def root():
    return {"message": "Habit Tracker API"}

@app.get("/habits", response_model=List[Habit])
async def get_habits():
    return list(habits_db.values())

@app.post("/habits", response_model=Habit)
async def create_habit(habit: HabitCreate):
    habit_id = str(uuid.uuid4())
    new_habit = Habit(
        id=habit_id,
        name=habit.name,
        category=habit.category,
        schedule=habit.schedule,
        reminder_time=habit.reminder_time,
        streak=0,
        created_at=datetime.now()
    )
    habits_db[habit_id] = new_habit
    return new_habit

@app.post("/habits/{habit_id}/complete")
async def complete_habit(habit_id: str):
    if habit_id not in habits_db:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    habit = habits_db[habit_id]
    habit.streak += 1
    return {"message": "Habit completed", "streak": habit.streak}

@app.delete("/habits/{habit_id}")
async def delete_habit(habit_id: str):
    if habit_id not in habits_db:
        raise HTTPException(status_code=404, detail="Habit not found")
    del habits_db[habit_id]
    return {"message": "Habit deleted"}

@app.get("/stats/success-rate")
async def get_success_rate():
    if not habits_db:
        return 0
    total_completions = sum(habit.streak for habit in habits_db.values())
    total_possible = len(habits_db) * 30
    return round((total_completions / total_possible) * 100, 2) if total_possible > 0 else 0

@app.get("/stats/current-streak")
async def get_current_streak():
    return max((habit.streak for habit in habits_db.values()), default=0)

@app.get("/stats/longest-streak")
async def get_longest_streak():
    return max((habit.streak for habit in habits_db.values()), default=0)

# Sample data
@app.on_event("startup")
async def startup_event():
    habits_db.clear()
    sample_habits = [
        Habit(
            id=str(uuid.uuid4()),
            name="Morning Exercise",
            category=HabitCategory.HEALTH,
            schedule=HabitSchedule.DAILY,
            reminder_time="07:00",
            streak=7,
            created_at=datetime.now()
        ),
        Habit(
            id=str(uuid.uuid4()),
            name="Read 30 minutes",
            category=HabitCategory.LEARNING,
            schedule=HabitSchedule.DAILY,
            reminder_time="21:00",
            streak=12,
            created_at=datetime.now()
        )
    ]
    for habit in sample_habits:
        habits_db[habit.id] = habit

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)