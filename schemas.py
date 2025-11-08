"""
Schemas Pydantic para validação e documentação da API
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


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


# Schemas para novos endpoints de neuromarketing

class TextSegment(BaseModel):
    """Segmento de texto detectado"""
    text: str = Field(..., description="Texto extraído", example="Frete Grátis")
    confidence: float = Field(..., description="Confiança da detecção", example=0.92, ge=0.0, le=1.0)
    bbox: Dict[str, float] = Field(..., description="Coordenadas do bounding box", example={"xmin": 100, "ymin": 50, "xmax": 300, "ymax": 80})


class OCRResponse(BaseModel):
    """Resposta da extração de texto (OCR)"""
    full_text: str = Field(..., description="Texto completo extraído", example="Frete Grátis Compre Agora")
    segments: List[TextSegment] = Field(..., description="Segmentos de texto com coordenadas")
    total_segments: int = Field(..., description="Número total de segmentos", example=2)
    method_used: str = Field(..., description="Método usado para OCR", example="easyocr")


class DominantColor(BaseModel):
    """Cor dominante detectada"""
    rgb: List[int] = Field(..., description="Valores RGB", example=[255, 100, 50])
    hex: str = Field(..., description="Cor em hexadecimal", example="#FF6432")
    percentage: float = Field(..., description="Porcentagem da cor na imagem", example=35.5)
    emotion_tag: str = Field(..., description="Tag emocional da cor", example="warm-energetic")


class ColorAnalysisResponse(BaseModel):
    """Resposta da análise de cores"""
    dominant_colors: List[DominantColor] = Field(..., description="Cores dominantes")
    average_contrast: float = Field(..., description="Contraste médio", example=4.8)
    emotion_palette: str = Field(..., description="Paleta emocional geral", example="warm-energetic")
    color_count: int = Field(..., description="Número de cores analisadas", example=5)


class CaptionResponse(BaseModel):
    """Resposta da geração de descrição"""
    caption: str = Field(..., description="Descrição gerada", example="A woman smiling while holding a cosmetic product")
    method: str = Field(..., description="Método usado", example="blip")
    confidence: float = Field(..., description="Confiança da descrição", example=0.85)
    length: Optional[int] = Field(None, description="Número de palavras", example=8)


class FaceEmotion(BaseModel):
    """Emoção detectada em uma face"""
    face_id: int = Field(..., description="ID da face", example=1)
    dominant_emotion: str = Field(..., description="Emoção dominante", example="happy")
    dominant_confidence: float = Field(..., description="Confiança da emoção", example=0.92)
    bbox: Dict[str, Any] = Field(..., description="Coordenadas da face")


class EmotionResponse(BaseModel):
    """Resposta da detecção de emoções"""
    faces_detected: int = Field(..., description="Número de faces detectadas", example=1)
    emotions: List[FaceEmotion] = Field(..., description="Emoções detectadas")
    scene_emotion: str = Field(..., description="Emoção geral da cena", example="happy")
    average_confidence: float = Field(..., description="Confiança média", example=0.88)
    method: str = Field(..., description="Método usado", example="deepface")


class AttentionPoint(BaseModel):
    """Ponto de atenção visual"""
    x: int = Field(..., description="Coordenada X", example=320)
    y: int = Field(..., description="Coordenada Y", example=240)
    score: float = Field(..., description="Score de atenção", example=0.85)
    normalized_x: float = Field(..., description="X normalizado (0-1)", example=0.5)
    normalized_y: float = Field(..., description="Y normalizado (0-1)", example=0.5)


class SaliencyResponse(BaseModel):
    """Resposta da análise de saliência"""
    attention_score: float = Field(..., description="Score geral de atenção", example=0.72)
    focus_center: Dict[str, float] = Field(..., description="Centro de foco", example={"x": 320, "y": 240, "normalized_x": 0.5, "normalized_y": 0.5})
    rule_of_thirds_alignment: str = Field(..., description="Alinhamento com regra dos terços", example="aligned")
    primary_focus_zone: str = Field(..., description="Zona de foco primário", example="aligned-0.33-0.33")
    attention_points: List[AttentionPoint] = Field(default=[], description="Pontos de maior atenção")


class CTAElement(BaseModel):
    """Elemento Call-to-Action detectado"""
    text: str = Field(..., description="Texto do CTA", example="Compre Agora")
    keywords: List[str] = Field(..., description="Palavras-chave detectadas", example=["compre", "agora"])
    bbox: Dict[str, float] = Field(..., description="Coordenadas do CTA")
    is_strategic_position: bool = Field(..., description="Se está em posição estratégica", example=True)
    relative_size: float = Field(..., description="Tamanho relativo (%)", example=2.5)
    confidence: float = Field(..., description="Confiança", example=0.95)


class CTAResponse(BaseModel):
    """Resposta da detecção de CTAs"""
    cta_present: bool = Field(..., description="Se há CTA presente", example=True)
    cta_count: int = Field(..., description="Número de CTAs", example=1)
    cta_elements: List[CTAElement] = Field(..., description="Elementos CTA detectados")
    effectiveness_score: float = Field(..., description="Score de efetividade", example=0.75)
    recommendations: List[str] = Field(..., description="Recomendações", example=["CTAs bem posicionados"])


class NeuromarketingReportResponse(BaseModel):
    """Resposta completa do relatório de neuromarketing"""
    objects: List[DetectionObject] = Field(..., description="Objetos detectados")
    text: OCRResponse = Field(..., description="Análise de texto")
    colors: ColorAnalysisResponse = Field(..., description="Análise de cores")
    caption: CaptionResponse = Field(..., description="Descrição da imagem")
    emotions: EmotionResponse = Field(..., description="Análise emocional")
    attention: SaliencyResponse = Field(..., description="Análise de atenção")
    cta: CTAResponse = Field(..., description="Análise de CTAs")
    summary: Dict[str, Any] = Field(..., description="Resumo executivo")


# Schema detalhado para análise completa de neuromarketing em português

class NeuromarketingDetailedResponse(BaseModel):
    """Resposta completa de análise neuromarketing com todos os parâmetros em português"""
    
    # 1. Expressão facial
    expressao_emocional: Dict[str, Any] = Field(..., description="Análise de expressões faciais e emoções detectadas")
    
    # 2. Direção do olhar
    direcao_olhar: Dict[str, Any] = Field(..., description="Direção do olhar e região focada")
    
    # 3. Paleta de cores dominante
    cores_dominantes: Dict[str, Any] = Field(..., description="Cores dominantes e análise emocional")
    emocao_das_cores: Dict[str, Any] = Field(..., description="Impacto emocional das cores")
    
    # 4. Contraste visual
    contraste_local: Dict[str, Any] = Field(..., description="Análise de contraste visual")
    
    # 5. Foco e profundidade
    profundidade_de_campo: Dict[str, Any] = Field(..., description="Análise de profundidade de campo e foco")
    
    # 6. Movimento implícito
    sensacao_de_movimento: Dict[str, Any] = Field(..., description="Sensação de movimento detectada")
    
    # 7. Simetria e equilíbrio
    simetria_visual: Dict[str, Any] = Field(..., description="Análise de simetria visual")
    
    # 8. Distância e enquadramento
    tipo_de_plano: Dict[str, Any] = Field(..., description="Tipo de plano (close-up, médio, aberto)")
    
    # 9. Iluminação e temperatura
    iluminacao_emocional: Dict[str, Any] = Field(..., description="Análise de iluminação e temperatura de cor")
    
    # 10. Contexto simbólico
    simbolos_sociais: Dict[str, Any] = Field(..., description="Símbolos sociais detectados")
    
    # 11. Proximidade social
    numero_de_pessoas: int = Field(..., description="Número de pessoas detectadas na imagem")
    objetos: List[Dict[str, Any]] = Field(..., description="Lista de objetos detectados")
    
    # 12. Emoção cromática (já em emocao_das_cores)
    
    # 13. Ponto focal
    area_de_atencao_visual: Dict[str, Any] = Field(..., description="Mapa de atenção visual e pontos focais")
    
    # 14. Linguagem corporal
    postura_corporea: Dict[str, Any] = Field(..., description="Análise de linguagem corporal e postura")
    
    # 15. Coerência narrativa
    historia_implicita: Dict[str, Any] = Field(..., description="Narrativa implícita e coerência contextual")
    
    # 16. Elementos de urgência
    gatilho_escassez_visual: Dict[str, Any] = Field(..., description="Elementos de urgência e escassez detectados")
    
    # 17. Textos e tipografia
    texto_em_imagem: Dict[str, Any] = Field(..., description="Texto extraído da imagem")
    textos_e_tipografia: Dict[str, Any] = Field(..., description="Análise de textos e tipografia")
    
    # 18. Humor e incongruência
    efeito_surpresa_ou_ironia: Dict[str, Any] = Field(..., description="Detecção de humor e incongruência")
    
    # 19. Textura e materialidade
    textura_sensorial: Dict[str, Any] = Field(..., description="Análise de textura e sensações táteis")
    
    # 20. Natureza vs tecnologia
    natureza_vs_tecnologia: Dict[str, Any] = Field(..., description="Classificação de ambiente (natural vs artificial)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "expressao_emocional": {
                    "faces_detectadas": 1,
                    "emocao_dominante": "happy",
                    "confianca_media": 0.92
                },
                "direcao_olhar": {
                    "primary_gaze_direction": "frente",
                    "gaze_target_region": "central-centro"
                },
                "cores_dominantes": {
                    "dominant_colors": [
                        {"rgb": [255, 100, 50], "hex": "#FF6432", "percentage": 35.5, "emotion_tag": "warm-energetic"}
                    ],
                    "emotion_palette": "warm-energetic"
                }
            }
        }

