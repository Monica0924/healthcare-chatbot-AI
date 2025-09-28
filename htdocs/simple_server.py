#!/usr/bin/env python3
"""
Simple HTTP Server for AI Health Chatbot
Works without FastAPI dependencies
"""

import http.server
import socketserver
import json
import sqlite3
import hashlib
import secrets
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import os

# Server configuration
PORT = 5000
HOST = "127.0.0.1"

# Database setup
DATABASE_URL = "chatbot.db"

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DATABASE_URL)
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
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert default doctor
    cursor.execute("SELECT COUNT(*) FROM doctors")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO doctors (name, email, access_key) 
            VALUES (?, ?, ?)
        """, ("Dr. Admin", "admin@healthcare.com", "doctor123"))
    
    conn.commit()
    conn.close()

class ChatbotHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        # API endpoints
        if parsed_path.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {"status": "healthy", "timestamp": datetime.now().isoformat()}
            self.wfile.write(json.dumps(response).encode())
            return
            
        elif parsed_path.path == "/_list_recent":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            conn = sqlite3.connect(DATABASE_URL)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM consultations 
                WHERE status = 'pending' 
                ORDER BY created_at DESC 
                LIMIT 50
            """)
            
            consultations = []
            for row in cursor.fetchall():
                consultations.append({
                    "id": row["id"],
                    "patient_name": row["patient_name"],
                    "symptoms": row["symptoms"],
                    "chatbot_recommendation": row["chatbot_recommendation"],
                    "status": row["status"],
                    "doctor_name": row["doctor_name"],
                    "doctor_note": row["doctor_note"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                })
            
            conn.close()
            self.wfile.write(json.dumps(consultations).encode())
            return
            
        # Serve static files
        else:
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except:
            data = {}
        
        # Chat endpoint
        if parsed_path.path == "/chat":
            self.handle_chat(data)
            return
            
        # Doctor review endpoint
        elif parsed_path.path == "/doctor_review":
            self.handle_doctor_review(data)
            return
            
        # User registration
        elif parsed_path.path == "/register":
            self.handle_register(data)
            return
            
        # User login
        elif parsed_path.path == "/login":
            self.handle_login(data)
            return
        
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
    
    def handle_chat(self, data):
        """Handle chat requests"""
        message = data.get("message", "")
        user_id = data.get("user_id", 1)
        
        # Generate AI response
        response = self.generate_ai_response(message)
        
        # Save consultation
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        consult_id = secrets.token_urlsafe(16)
        cursor.execute("""
            INSERT INTO consultations (id, patient_name, symptoms, chatbot_recommendation)
            VALUES (?, ?, ?, ?)
        """, (consult_id, f"User_{user_id}", message, response))
        
        conn.commit()
        conn.close()
        
        # Send response
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        
        response_data = {
            "response": response,
            "consultation_id": consult_id
        }
        self.wfile.write(json.dumps(response_data).encode())
    
    def generate_ai_response(self, message):
        """Generate AI health response"""
        user_message = message.lower()
        
        if any(word in user_message for word in ["fever", "cough", "cold"]):
            return """Based on your symptoms, here are some general recommendations:

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
            return """Vaccination Information:

1. **COVID-19**: Stay updated with booster shots as recommended
2. **Flu**: Annual vaccination recommended, especially for high-risk groups
3. **General Schedule**: Check with your local health department
4. **Side Effects**: Mild reactions are normal (soreness, low-grade fever)

📅 Consult your healthcare provider for personalized vaccination schedule."""
        
        elif any(word in user_message for word in ["dengue", "malaria", "mosquito"]):
            return """Mosquito-borne Disease Prevention:

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
            return """I can help with:
- Symptom assessment and general health advice
- Vaccination information and schedules
- Disease prevention strategies
- When to seek medical care

Please describe your symptoms or health concern, and I'll provide evidence-based guidance.

⚠️ Remember: I provide general information only. Always consult healthcare professionals for medical advice."""
    
    def handle_doctor_review(self, data):
        """Handle doctor review requests"""
        consult_id = data.get("consult_id")
        action = data.get("action")
        doctor_name = data.get("doctor_name")
        doctor_note = data.get("doctor_note")
        
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        try:
            if action == "approve":
                cursor.execute("""
                    UPDATE consultations 
                    SET status = 'approved', doctor_name = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (doctor_name, consult_id))
                
            elif action == "modify":
                cursor.execute("""
                    UPDATE consultations 
                    SET status = 'modified', doctor_name = ?, doctor_note = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (doctor_name, doctor_note, consult_id))
            
            conn.commit()
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            response = {
                "message": f"Consultation {action}d successfully",
                "consultation_id": consult_id,
                "doctor_name": doctor_name
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            conn.rollback()
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {"error": str(e)}
            self.wfile.write(json.dumps(response).encode())
        finally:
            conn.close()
    
    def handle_register(self, data):
        """Handle user registration"""
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        try:
            # Check if email exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                raise Exception("Email already registered")
            
            # Hash password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO users (name, email, password)
                VALUES (?, ?, ?)
            """, (name, email, hashed_password))
            
            conn.commit()
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            response = {"message": "User registered successfully", "user_id": cursor.lastrowid}
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            conn.rollback()
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {"error": str(e)}
            self.wfile.write(json.dumps(response).encode())
        finally:
            conn.close()
    
    def handle_login(self, data):
        """Handle user login"""
        email = data.get("email")
        password = data.get("password")
        
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute("""
                SELECT id, name, email FROM users 
                WHERE email = ? AND password = ?
            """, (email, hashed_password))
            
            user = cursor.fetchone()
            if not user:
                raise Exception("Invalid credentials")
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            response = {
                "message": "Login successful",
                "user": {
                    "id": user[0],
                    "name": user[1],
                    "email": user[2]
                }
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(401)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {"error": str(e)}
            self.wfile.write(json.dumps(response).encode())
        finally:
            conn.close()

def main():
    """Start the server"""
    print("🚀 Starting AI Health Chatbot Server...")
    print("=" * 50)
    
    # Initialize database
    print("📊 Initializing database...")
    init_db()
    print("✅ Database initialized successfully")
    
    # Start server
    with socketserver.TCPServer((HOST, PORT), ChatbotHandler) as httpd:
        print(f"🌐 Server running on http://{HOST}:{PORT}")
        print("📚 Available endpoints:")
        print(f"   - Health: http://{HOST}:{PORT}/health")
        print(f"   - Chat: http://{HOST}:{PORT}/chat")
        print(f"   - Consultations: http://{HOST}:{PORT}/_list_recent")
        print(f"   - Doctor Panel: http://{HOST}:{PORT}/doctor-panel.html")
        print(f"   - Chatbot Demo: http://{HOST}:{PORT}/chatbot-demo.html")
        print(f"   - Main Site: http://{HOST}:{PORT}/index.html")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped. Goodbye!")

if __name__ == "__main__":
    main()
