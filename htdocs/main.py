from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import hashlib
import secrets
from datetime import datetime
import uvicorn
import os

# Initialize FastAPI app
app = FastAPI(
    title="AI Health Chatbot API",
    description="Backend API for AI-Driven Public Health Chatbot",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "chatbot.db"

def get_db():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with required tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create consultations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consultations (
            id TEXT PRIMARY KEY,
            patient_name TEXT NOT NULL,
            symptoms TEXT NOT NULL,
            chatbot_recommendation TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            doctor_name TEXT,
            doctor_note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create doctors table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            access_key TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create users table (for login/signup)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert default doctor if not exists
    cursor.execute("SELECT COUNT(*) FROM doctors")
    if cursor.fetchone()[0] == 0:
        default_key = "doctor123"  # In production, use secure key generation
        cursor.execute("""
            INSERT INTO doctors (name, email, access_key) 
            VALUES (?, ?, ?)
        """, ("Dr. Admin", "admin@healthcare.com", default_key))
    
    conn.commit()
    conn.close()

# Pydantic models
class ConsultationCreate(BaseModel):
    patient_name: str
    symptoms: str
    chatbot_recommendation: str

class ConsultationResponse(BaseModel):
    id: str
    patient_name: str
    symptoms: str
    chatbot_recommendation: str
    status: str
    doctor_name: Optional[str] = None
    doctor_note: Optional[str] = None
    created_at: str
    updated_at: str

class DoctorReview(BaseModel):
    consult_id: str
    action: str  # "approve" or "modify"
    doctor_name: str
    doctor_note: Optional[str] = None

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class ChatMessage(BaseModel):
    message: str
    user_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    consultation_id: Optional[str] = None

# Authentication dependency
def verify_doctor_key(x_doctor_key: str = Header(None)):
    if not x_doctor_key:
        raise HTTPException(status_code=401, detail="Doctor access key required")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM doctors WHERE access_key = ?", (x_doctor_key,))
    doctor = cursor.fetchone()
    conn.close()
    
    if not doctor:
        raise HTTPException(status_code=401, detail="Invalid doctor access key")
    
    return doctor[0]

# Routes
@app.get("/")
async def root():
    return {"message": "AI Health Chatbot API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Consultation endpoints
@app.post("/consultation", response_model=ConsultationResponse)
async def create_consultation(consultation: ConsultationCreate):
    """Create a new consultation"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Generate unique ID
    consult_id = secrets.token_urlsafe(16)
    
    try:
        cursor.execute("""
            INSERT INTO consultations (id, patient_name, symptoms, chatbot_recommendation)
            VALUES (?, ?, ?, ?)
        """, (consult_id, consultation.patient_name, consultation.symptoms, consultation.chatbot_recommendation))
        
        conn.commit()
        
        # Fetch the created consultation
        cursor.execute("SELECT * FROM consultations WHERE id = ?", (consult_id,))
        result = cursor.fetchone()
        
        return ConsultationResponse(
            id=result["id"],
            patient_name=result["patient_name"],
            symptoms=result["symptoms"],
            chatbot_recommendation=result["chatbot_recommendation"],
            status=result["status"],
            doctor_name=result["doctor_name"],
            doctor_note=result["doctor_note"],
            created_at=result["created_at"],
            updated_at=result["updated_at"]
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating consultation: {str(e)}")
    finally:
        conn.close()

@app.get("/_list_recent", response_model=List[ConsultationResponse])
async def list_recent_consultations():
    """Get recent consultations for doctor review"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM consultations 
        WHERE status = 'pending' 
        ORDER BY created_at DESC 
        LIMIT 50
    """)
    
    consultations = []
    for row in cursor.fetchall():
        consultations.append(ConsultationResponse(
            id=row["id"],
            patient_name=row["patient_name"],
            symptoms=row["symptoms"],
            chatbot_recommendation=row["chatbot_recommendation"],
            status=row["status"],
            doctor_name=row["doctor_name"],
            doctor_note=row["doctor_note"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        ))
    
    conn.close()
    return consultations

@app.post("/doctor_review")
async def doctor_review(review: DoctorReview, doctor_id: int = Depends(verify_doctor_key)):
    """Doctor review of consultation"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Check if consultation exists
        cursor.execute("SELECT * FROM consultations WHERE id = ?", (review.consult_id,))
        consultation = cursor.fetchone()
        
        if not consultation:
            raise HTTPException(status_code=404, detail="Consultation not found")
        
        if review.action == "approve":
            cursor.execute("""
                UPDATE consultations 
                SET status = 'approved', doctor_name = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (review.doctor_name, review.consult_id))
            
        elif review.action == "modify":
            if not review.doctor_note:
                raise HTTPException(status_code=400, detail="Doctor note required for modification")
            
            cursor.execute("""
                UPDATE consultations 
                SET status = 'modified', doctor_name = ?, doctor_note = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (review.doctor_name, review.doctor_note, review.consult_id))
        
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Use 'approve' or 'modify'")
        
        conn.commit()
        
        return {
            "message": f"Consultation {review.action}d successfully",
            "consultation_id": review.consult_id,
            "doctor_name": review.doctor_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing review: {str(e)}")
    finally:
        conn.close()

# Chatbot endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_with_bot(message: ChatMessage):
    """Chat with the AI health bot"""
    
    # Simple rule-based responses (replace with actual AI model)
    user_message = message.message.lower()
    
    if any(word in user_message for word in ["fever", "cough", "cold"]):
        response = """Based on your symptoms, here are some general recommendations:

1. **Rest and Hydration**: Get plenty of rest and drink fluids
2. **Monitor Temperature**: Check your temperature regularly
3. **Over-the-counter Relief**: Consider acetaminophen or ibuprofen for fever
4. **Seek Medical Care If**:
   - Fever persists for more than 3 days
   - Difficulty breathing
   - Severe headache or neck stiffness
   - Symptoms worsen

⚠️ This is general advice. Consult a healthcare professional for proper diagnosis."""
        
    elif any(word in user_message for word in ["vaccine", "vaccination"]):
        response = """Vaccination Information:

1. **COVID-19**: Stay updated with booster shots as recommended
2. **Flu**: Annual vaccination recommended, especially for high-risk groups
3. **General Schedule**: Check with your local health department
4. **Side Effects**: Mild reactions are normal (soreness, low-grade fever)

📅 Consult your healthcare provider for personalized vaccination schedule."""
        
    elif any(word in user_message for word in ["dengue", "malaria", "mosquito"]):
        response = """Mosquito-borne Disease Prevention:

1. **Protection**:
   - Use mosquito repellent (DEET 20%+)
   - Wear long sleeves and pants
   - Use mosquito nets while sleeping

2. **Eliminate Breeding Sites**:
   - Remove standing water
   - Clean gutters and drains
   - Cover water storage containers

3. **Seek Immediate Care If**:
   - High fever with severe headache
   - Bleeding from nose/gums
   - Severe abdominal pain

🩺 Early detection and treatment are crucial."""
        
    else:
        response = """I can help with:
- Symptom assessment and general health advice
- Vaccination information and schedules
- Disease prevention strategies
- When to seek medical care

Please describe your symptoms or health concern, and I'll provide evidence-based guidance.

⚠️ Remember: I provide general information only. Always consult healthcare professionals for medical advice."""

    # Create consultation record for doctor review
    conn = get_db()
    cursor = conn.cursor()
    
    consult_id = secrets.token_urlsafe(16)
    cursor.execute("""
        INSERT INTO consultations (id, patient_name, symptoms, chatbot_recommendation)
        VALUES (?, ?, ?, ?)
    """, (consult_id, f"User_{message.user_id or 'Anonymous'}", message.message, response))
    
    conn.commit()
    conn.close()
    
    return ChatResponse(response=response, consultation_id=consult_id)

# User authentication endpoints
@app.post("/register")
async def register_user(user: UserCreate):
    """Register a new user"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password (in production, use proper password hashing)
        hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
        
        cursor.execute("""
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
        """, (user.name, user.email, hashed_password))
        
        conn.commit()
        return {"message": "User registered successfully", "user_id": cursor.lastrowid}
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error registering user: {str(e)}")
    finally:
        conn.close()

@app.post("/login")
async def login_user(login: UserLogin):
    """Login user"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        hashed_password = hashlib.sha256(login.password.encode()).hexdigest()
        
        cursor.execute("""
            SELECT id, name, email FROM users 
            WHERE email = ? AND password = ?
        """, (login.email, hashed_password))
        
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return {
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")
    finally:
        conn.close()

# Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")

if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=5000,
        reload=True,
        log_level="info"
    )
