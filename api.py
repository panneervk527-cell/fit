from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from database.db import SessionLocal
from database.models import ChatHistory
from services.gemini_service import generate_workout_plan, generate_meal_plan, fitness_chat

app = FastAPI(title="SmartFit Planner AI API")

# Request schemas for JSON payloads
class UserDataRequest(BaseModel):
    user_id: int
    age: int
    weight: float
    height: float
    fitness_goal: str
    activity_level: str

@app.post("/api/workout-plan")
def api_generate_workout(data: UserDataRequest):
    try:
        plan = generate_workout_plan(data.dict())
        return {"success": True, "data": plan}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/meal-plan")
def api_generate_meal(data: UserDataRequest):
    try:
        plan = generate_meal_plan(data.dict())
        return {"success": True, "data": plan}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def api_chat(
    user_id: int = Form(...),
    message: str = Form(...),
    file: UploadFile = File(None)
):
    db = SessionLocal()
    try:
        # Load user chat history from database
        db_history = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).order_by(ChatHistory.timestamp).all()
        
        image_bytes = None
        mime_type = "image/jpeg"
        if file:
            image_bytes = await file.read()
            mime_type = file.content_type

        # Call your existing Gemini chat service
        response_text = fitness_chat(
            user_id=user_id,
            message=message,
            chat_history=db_history,
            image_bytes=image_bytes,
            mime_type=mime_type
        )

        # Save user message and AI response to SQLite database
        db.add(ChatHistory(user_id=user_id, role="user", message=message))
        db.add(ChatHistory(user_id=user_id, role="model", message=response_text))
        db.commit()

        return {"success": True, "response": response_text}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()