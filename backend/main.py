import logging
import sys
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, validator
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import config și modulele
try:
    from config import settings, validate_settings
    from search_engine import get_top_results, is_safe_url
    from content_extractor import extract_from_urls
    from ai_synthesizer import generate_answer
except ImportError as e:
    logger.error(f"Eroare la import: {e}")
    sys.exit(1)

# Validează configurația
validate_settings()

# Inițializează FastAPI
app = FastAPI(
    title="MiniSearch AI",
    description="AI-powered web search application",
    version="1.0.0"
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler pentru rate limit
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Prea multe cereri. Încearcă mai târziu."}
    )

# Models
class SearchRequest(BaseModel):
    question: str
    
    @validator('question')
    def validate_question(cls, v):
        if not v or not v.strip():
            raise ValueError("Întrebarea nu poate fi goală")
        if len(v) > 500:
            raise ValueError(f"Întrebarea e prea lungă (max 500 caractere)")
        if any(char in v for char in ['<', '>', '{', '}', '`']):
            raise ValueError("Caractere nepermise în întrebare")
        return v.strip()

class SearchResponse(BaseModel):
    question: str
    answer: str
    sources: list

# Routes
@app.get("/")
async def root():
    """Servește pagina principală"""
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "search_engine": settings.SEARCH_ENGINE,
        "ai_model": settings.AI_MODEL_TYPE
    }

@app.post("/api/search")
@limiter.limit("20/minute")
async def search(request: Request, search_req: SearchRequest):
    """Endpoint principal pentru căutare și sintetizare"""
    try:
        question = search_req.question
        logger.info(f"Nouă căutare: {question}")
        
        # 1. Căutare web
        logger.info("Pas 1: Căutare web...")
        search_results = await get_top_results(question, max_results=3)
        
        if not search_results:
            raise HTTPException(
                status_code=404,
                detail="Nu s-au găsit rezultate pe web."
            )
        
        logger.info(f"Găsite {len(search_results)} rezultate")
        
        # 2. Extrage conținut
        logger.info("Pas 2: Extragere conținut...")
        urls_to_fetch = [result.url for result in search_results]
        sources_content = await extract_from_urls(urls_to_fetch)
        
        if not sources_content:
            raise HTTPException(
                status_code=503,
                detail="Nu s-a putut extrage conținut din pagini."
            )
        
        logger.info(f"Extras conținut de la {len(sources_content)} surse")
        
        # 3. Sintetizează răspuns
        logger.info("Pas 3: Sintetizare AI...")
        answer = await generate_answer(question, sources_content)
        
        if not answer:
            raise HTTPException(
                status_code=503,
                detail="Nu s-a putut genera răspunsul."
            )
        
        # 4. Pregătește sursele
        sources = []
        for i, result in enumerate(search_results):
            if result.url in sources_content:
                sources.append({
                    "id": i + 1,
                    "title": result.title,
                    "url": result.url,
                    "snippet": result.snippet
                })
        
        logger.info("Răspuns returnat cu succes")
        return SearchResponse(
            question=question,
            answer=answer,
            sources=sources
        )
    
    except ValueError as e:
        logger.warning(f"Validare eșuată: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Eroare: {str(e)}")
        raise HTTPException(status_code=500, detail="Eroare la procesare.")

@app.get("/api/config")
async def get_config():
    """Returnează configurația publică"""
    return {
        "search_engine": settings.SEARCH_ENGINE,
        "ai_model": settings.AI_MODEL_TYPE,
        "max_results": 3
    }

# Servește fișierele statice
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 50)
    logger.info("MiniSearch AI - Server Starting")
    logger.info(f"Search Engine: {settings.SEARCH_ENGINE}")
    logger.info(f"AI Model: {settings.AI_MODEL_TYPE}")
    logger.info("=" * 50)

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Pornire pe http://{settings.BACKEND_HOST}:{settings.BACKEND_PORT}")
    
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG
    )
