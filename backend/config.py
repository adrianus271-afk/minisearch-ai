import os
from dotenv import load_dotenv
from pydantic import BaseSettings

# Încarc variabilele din .env
load_dotenv()

class Settings(BaseSettings):
    # Web Search Configuration
    SEARCH_ENGINE: str = os.getenv("SEARCH_ENGINE", "brave_search")
    BRAVE_SEARCH_API_KEY: str = os.getenv("BRAVE_SEARCH_API_KEY", "")
    SERPAPI_API_KEY: str = os.getenv("SERPAPI_API_KEY", "")
    BING_SEARCH_API_KEY: str = os.getenv("BING_SEARCH_API_KEY", "")

    # AI/LLM Configuration
    AI_MODEL_TYPE: str = os.getenv("AI_MODEL_TYPE", "openai")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama2")

    # Backend Configuration
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    BACKEND_WORKERS: int = int(os.getenv("BACKEND_WORKERS", "4"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Security & Limits
    MAX_RESULTS_PER_QUERY: int = int(os.getenv("MAX_RESULTS_PER_QUERY", "3"))
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
    PAGE_FETCH_TIMEOUT_SECONDS: int = int(os.getenv("PAGE_FETCH_TIMEOUT_SECONDS", "8"))
    MAX_PAGE_SIZE_MB: int = int(os.getenv("MAX_PAGE_SIZE_MB", "5"))
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "20"))
    MAX_QUESTION_LENGTH: int = int(os.getenv("MAX_QUESTION_LENGTH", "500"))

    # CORS Configuration
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

    class Config:
        env_file = ".env"
        case_sensitive = True

# Instanță globală de configurare
settings = Settings()

# Validări la startup
def validate_settings():
    """Validează că configurația necesară este prezentă"""
    errors = []
    
    if settings.SEARCH_ENGINE not in ["brave_search", "serpapi", "bing"]:
        errors.append(f"SEARCH_ENGINE '{settings.SEARCH_ENGINE}' nu este suportat")
    
    if settings.SEARCH_ENGINE == "brave_search" and not settings.BRAVE_SEARCH_API_KEY:
        errors.append("BRAVE_SEARCH_API_KEY este necesar pentru brave_search")
    
    if settings.SEARCH_ENGINE == "serpapi" and not settings.SERPAPI_API_KEY:
        errors.append("SERPAPI_API_KEY este necesar pentru serpapi")
    
    if settings.SEARCH_ENGINE == "bing" and not settings.BING_SEARCH_API_KEY:
        errors.append("BING_SEARCH_API_KEY este necesar pentru bing")
    
    if settings.AI_MODEL_TYPE not in ["openai", "anthropic", "ollama"]:
        errors.append(f"AI_MODEL_TYPE '{settings.AI_MODEL_TYPE}' nu este suportat")
    
    if settings.AI_MODEL_TYPE == "openai" and not settings.OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY este necesar pentru openai")
    
    if settings.AI_MODEL_TYPE == "anthropic" and not settings.ANTHROPIC_API_KEY:
        errors.append("ANTHROPIC_API_KEY este necesar pentru anthropic")
    
    if errors:
        print("\n❌ ERORI DE CONFIGURARE:")
        for error in errors:
            print(f"  - {error}")
        print("\nVerifică fișierul .env și copiază din .env.example")
        exit(1)
    
    print("✅ Configurare validă!")

if __name__ == "__main__":
    validate_settings()
    print(f"Search Engine: {settings.SEARCH_ENGINE}")
    print(f"AI Model: {settings.AI_MODEL_TYPE}")
    print(f"Backend: {settings.BACKEND_HOST}:{settings.BACKEND_PORT}")
