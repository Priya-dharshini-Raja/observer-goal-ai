
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import goal detection
from goal_model import detect_goals

# Import content processor
from content_processor import process_content

# Import specialized agents
from agents import security_analysis_agent
from business_agent import business_analysis_agent
from technical_agent import technical_analysis_agent
from ux_agent import ux_analysis_agent

# Import orchestrator
from orchestrator import adaptive_analysis, generate_observer_report


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="Observer Goal Modeling API",
    description="Multi-Agent Adaptive Intelligence System",
    version="0.2.0",
)


# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------

class GoalRequest(BaseModel):
    query: str


class ContentRequest(BaseModel):
    content: str
    chunk_size: int = 500


class SecurityAnalysisRequest(BaseModel):
    content: str


class BusinessAnalysisRequest(BaseModel):
    content: str


class TechnicalAnalysisRequest(BaseModel):
    content: str


class UXAnalysisRequest(BaseModel):
    content: str


class AdaptiveAnalysisRequest(BaseModel):
    content: str
    user_query: str


class ObserverReportRequest(BaseModel):
    content: str
    user_query: str


# --------------------------------------------------
# BASIC API ENDPOINTS
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Observer Goal Modeling API is running",
        "status": "success",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# --------------------------------------------------
# GOAL DETECTION
# --------------------------------------------------

@app.post("/detect-goal")
def detect_goal(request: GoalRequest):

    return detect_goals(request.query)


# --------------------------------------------------
# CONTENT PROCESSING
# --------------------------------------------------

@app.post("/process-content")
def process_source_content(request: ContentRequest):

    chunks = process_content(
        request.content,
        request.chunk_size
    )

    return {
        "total_chunks": len(chunks),
        "chunks": chunks,
    }


# --------------------------------------------------
# SECURITY ANALYSIS
# --------------------------------------------------

@app.post("/analyze-security")
def analyze_security(request: SecurityAnalysisRequest):

    return security_analysis_agent(request.content)


# --------------------------------------------------
# BUSINESS ANALYSIS
# --------------------------------------------------

@app.post("/analyze-business")
def analyze_business(request: BusinessAnalysisRequest):

    return business_analysis_agent(request.content)


# --------------------------------------------------
# TECHNICAL ANALYSIS
# --------------------------------------------------

@app.post("/analyze-technical")
def analyze_technical(request: TechnicalAnalysisRequest):

    return technical_analysis_agent(request.content)


# --------------------------------------------------
# USER EXPERIENCE ANALYSIS
# --------------------------------------------------

@app.post("/analyze-ux")
def analyze_ux(request: UXAnalysisRequest):

    return ux_analysis_agent(request.content)


# --------------------------------------------------
# ADAPTIVE MULTI-AGENT ANALYSIS
# --------------------------------------------------

@app.post("/adaptive-analysis")
def run_adaptive_analysis(request: AdaptiveAnalysisRequest):

    return adaptive_analysis(
        request.content,
        request.user_query
    )


# --------------------------------------------------
# UNIFIED OBSERVER REPORT
# --------------------------------------------------

@app.post("/observer-report")
def create_observer_report(request: ObserverReportRequest):

    adaptive_result = adaptive_analysis(
        request.content,
        request.user_query
    )

    return generate_observer_report(adaptive_result)
