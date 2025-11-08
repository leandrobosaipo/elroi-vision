"""
Configurações da aplicação usando variáveis de ambiente
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação carregadas de variáveis de ambiente"""
    
    # Caminho do modelo YOLO
    MODEL_PATH: str = "./models/sample_model/yolov8n.pt"
    
    # Configurações de detecção
    CONFIDENCE_THRESHOLD: float = 0.5
    IMAGE_SIZE: int = 640
    AUGMENT: bool = False
    
    # Configurações do servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    RELOAD: bool = False
    
    # CORS
    CORS_ORIGINS: str = "*"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "log.log"
    LOG_ROTATION: str = "1 MB"
    
    # Ambiente
    ENVIRONMENT: str = "production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instância global das configurações
settings = Settings()

