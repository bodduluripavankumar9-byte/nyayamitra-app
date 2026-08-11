import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="NyayaMitra Full-Stack Legal API",
    version="2.0",
    description="Backend service for multilingual AI legal counsel based on Indian Law."
)

# Initialize OpenAI client securely (replace with your actual API key if not using environment variables)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class LegalRequest(BaseModel):
    query: str

class LegalResponse(BaseModel):
    legal_opinion: str

@app.post("/api/consult", response_model=LegalResponse)
def consult_legal_counsel(request: LegalRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        lawyer_system_prompt = (
            "You are 'NyayaMitra', a seasoned Advocate enrolled with the Bar Council of India, specializing in the Constitution of India. "
            "Structure your response strictly into:\n"
            "1. **Legal Issue Summary**\n"
            "2. **Governing Provisions** (Cite relevant Articles of the Constitution of India or statutes)\n"
            "3. **Legal Position & Analysis**\n"
            "4. **Actionable Recourse** (What legal steps the client can take)\n"
            "5. **Mandatory Disclaimer:** Conclude with: 'Disclaimer: This response is for preliminary informational purposes only.'\n"
            "CRITICAL RULE: Automatically detect the language of the user's query (such as Telugu, Hindi, Spanish, French, English, etc.) "
            "and provide your entire response in that exact same language, while keeping legal terms and statutory sections accurate."
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": lawyer_system_prompt},
                {"role": "user", "content": request.query}
            ],
            temperature=0.2
        )

        opinion = response.choices[0].message.content
        return LegalResponse(legal_opinion=opinion)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health_check():
    return {"status": "online", "app": "NyayaMitra API is running successfully"}