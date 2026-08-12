from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from openai import OpenAI
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import datetime

# Database setup
DATABASE_URL = "sqlite:///./nyayamitra.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define Database Model for Consultation History
class ConsultationModel(Base):
    __tablename__ = "consultations"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    legal_opinion = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(
    title="NyayaMitra Full-Stack Legal API",
    version="2.1",
    description="Backend service with database persistence for multilingual AI legal counsel."
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class LegalRequest(BaseModel):
    query: str

class LegalResponse(BaseModel):
    id: int
    legal_opinion: str

@app.post("/api/consult", response_model=LegalResponse)
def consult_legal_counsel(request: LegalRequest, db: Session = Depends(get_db)):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    try:
        lawyer_system_prompt = (
            "You are 'NyayaMitra', a seasoned Advocate enrolled with the Bar Council of India, specializing in Indian Law. "
            "Structure your response strictly into:\n"
            "1. **Legal Issue Summary**\n"
            "2. **Governing Provisions** (Cite relevant Articles of the Constitution of India or statutes)\n"
            "3. **Legal Position & Analysis**\n"
            "4. **Actionable Recourse** (What legal steps the client can take)\n"
            "5. **Mandatory Disclaimer** Conclude with: 'Disclaimer: This response is for preliminary information and education only and does not constitute formal legal counsel.'"
        )
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": lawyer_system_prompt},
                {"role": "user", "content": request.query}
            ]
        )
        
        opinion = completion.choices[0].message.content
        
        # Save query and response to the database
        db_consultation = ConsultationModel(query=request.query, legal_opinion=opinion)
        db.add(db_consultation)
        db.commit()
        db.refresh(db_consultation)
        
        return LegalResponse(id=db_consultation.id, legal_opinion=opinion)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
def get_history(db: Session = Depends(get_db)):
    consultations = db.query(ConsultationModel).order_by(ConsultationModel.created_at.desc()).all()
    return consultations
import openai
from fastapi import File, UploadFile, HTTPException

@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # Save the uploaded audio file temporarily
        audio_bytes = await file.read()
        temp_file_path = "temp_audio.wav"
        with open(temp_file_path, "wb") as f:
            f.write(audio_bytes)
            
        # Call OpenAI Whisper API for transcription
        with open(temp_file_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            
        return {"text": transcript.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))