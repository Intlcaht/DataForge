from pydantic import  AnyHttpUrl
# from pydantic.settings import BaseSettings # type: ignore
from typing import List, Optional

class Settings():
    PROJECT_NAME: str = "ICaht BK Api"
    PROJECT_DESCRIPTION: str = ""
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    DOCS: bool = True
    
    API_V1_STR: str = "/api/v1"
    
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()