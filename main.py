from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
from datetime import datetime

from crewai import Crew, Process
from agents import financial_analyst
from task import analyze_financial_document

# DATABASE IMPORTS
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ================= DATABASE SETUP ================= #

DATABASE_URL = "sqlite:///./financial.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class FinancialReport(Base):
    __tablename__ = "financial_reports"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    query = Column(Text, nullable=False)
    analysis = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

# ================= FASTAPI APP ================= #

app = FastAPI(title="Financial Document Analyzer")


def run_crew(query: str, file_path: str):
    """Run the crew analysis"""
    financial_crew = Crew(
        agents=[financial_analyst],
        tasks=[analyze_financial_document],
        process=Process.sequential,
    )

    result = financial_crew.kickoff({
        'query': query,
        'file_path': file_path
    })

    return result


@app.get("/")
async def root():
    return {"message": "Financial Document Analyzer API is running"}


@app.post("/analyze")
async def analyze_financial_endpoint(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):

    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"

    try:
        os.makedirs("data", exist_ok=True)

        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        if not query:
            query = "Analyze this financial document for investment insights"

        # Run AI Analysis
        response = run_crew(query=query.strip(), file_path=file_path)

        # ============ SAVE TO DATABASE ============ #
        db = SessionLocal()

        report = FinancialReport(
            file_name=file.filename,
            query=query,
            analysis=str(response)
        )

        db.add(report)
        db.commit()
        db.close()

        return {
            "status": "success",
            "query": query,
            "analysis": str(response),
            "file_processed": file.filename
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing financial document: {str(e)}"
        )

    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)