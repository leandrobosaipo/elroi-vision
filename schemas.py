"""
Schemas Pydantic para validação e documentação da API
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class DetectionObject(BaseModel):
    """Objeto detectado na imagem"""
    name: str = Field(..., description="Nome da classe do objeto detectado", example="person")
    confidence: float = Field(..., description="Confiança da detecção (0.0 a 1.0)", example=0.95, ge=0.0, le=1.0)


class DetectionResponse(BaseModel):
    """Resposta da detecção de objetos em formato JSON"""
    detect_objects: List[DetectionObject] = Field(..., description="Lista de objetos detectados")
    detect_objects_names: str = Field(..., description="Nomes dos objetos detectados separados por vírgula", example="person, car, dog")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detect_objects": [
                    {"name": "person", "confidence": 0.95},
                    {"name": "car", "confidence": 0.87},
                    {"name": "dog", "confidence": 0.72}
                ],
                "detect_objects_names": "person, car, dog"
            }
        }


class HealthCheckResponse(BaseModel):
    """Resposta do healthcheck"""
    healthcheck: str = Field(..., description="Status do serviço", example="Everything OK!")
    
    class Config:
        json_schema_extra = {
            "example": {
                "healthcheck": "Everything OK!"
            }
        }

