"""
Serviço de detecção de emoções faciais
"""
from PIL import Image
import numpy as np
from typing import List, Dict, Optional

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False


class EmotionService:
    """Serviço para detecção de emoções faciais"""
    
    def detect_emotions(self, image: Image) -> Dict:
        """
        Detecta emoções em faces na imagem
        
        Args:
            image: PIL Image
            
        Returns:
            Dicionário com emoções detectadas
        """
        if not DEEPFACE_AVAILABLE:
            return {
                "faces_detected": 0,
                "emotions": [],
                "method": "none",
                "message": "DeepFace não disponível. Instale: pip install deepface"
            }
        
        try:
            # Converte PIL para numpy array
            img_array = np.array(image.convert("RGB"))
            
            # Detecta emoções usando DeepFace
            # Retorna lista de resultados (uma por face)
            results = DeepFace.analyze(
                img_array,
                actions=['emotion'],
                enforce_detection=False,
                silent=True
            )
            
            # Se apenas uma face, DeepFace retorna dict, não lista
            if isinstance(results, dict):
                results = [results]
            
            emotions_list = []
            for i, result in enumerate(results):
                emotion_data = result.get('emotion', {})
                
                # Encontra emoção dominante
                dominant_emotion = max(emotion_data.items(), key=lambda x: x[1])
                
                emotions_list.append({
                    "face_id": i + 1,
                    "emotions": emotion_data,
                    "dominant_emotion": dominant_emotion[0],
                    "dominant_confidence": round(dominant_emotion[1] / 100.0, 3),
                    "bbox": result.get('region', {})
                })
            
            # Calcula emoção geral da cena
            if emotions_list:
                dominant_emotions = [e["dominant_emotion"] for e in emotions_list]
                scene_emotion = max(set(dominant_emotions), key=dominant_emotions.count)
                avg_confidence = np.mean([e["dominant_confidence"] for e in emotions_list])
            else:
                scene_emotion = "neutral"
                avg_confidence = 0.0
            
            return {
                "faces_detected": len(emotions_list),
                "emotions": emotions_list,
                "scene_emotion": scene_emotion,
                "average_confidence": round(avg_confidence, 3),
                "method": "deepface"
            }
        except Exception as e:
            # Se não detectar faces, retorna estrutura vazia
            error_msg = str(e)
            if "Face could not be detected" in error_msg or "No face detected" in error_msg:
                return {
                    "faces_detected": 0,
                    "emotions": [],
                    "method": "deepface",
                    "message": "Nenhuma face detectada na imagem"
                }
            else:
                return {
                    "faces_detected": 0,
                    "emotions": [],
                    "method": "error",
                    "error": error_msg
                }
    
    def analyze_emotional_impact(self, image: Image, emotions_result: Dict) -> Dict:
        """
        Analisa impacto emocional geral da imagem
        
        Args:
            image: PIL Image
            emotions_result: Resultado de detect_emotions
            
        Returns:
            Análise de impacto emocional
        """
        if emotions_result.get("faces_detected", 0) == 0:
            return {
                "emotional_impact": "neutral",
                "valence": "neutral",  # positivo/negativo/neutro
                "arousal": "low",  # baixo/alto
                "recommendation": "Adicione faces humanas para análise emocional mais precisa"
            }
        
        # Mapeia emoções para valência e ativação
        positive_emotions = ["happy", "surprise"]
        negative_emotions = ["sad", "angry", "fear", "disgust"]
        high_arousal = ["angry", "fear", "surprise", "happy"]
        
        scene_emotion = emotions_result.get("scene_emotion", "neutral")
        
        if scene_emotion in positive_emotions:
            valence = "positive"
        elif scene_emotion in negative_emotions:
            valence = "negative"
        else:
            valence = "neutral"
        
        arousal = "high" if scene_emotion in high_arousal else "low"
        
        # Recomendações baseadas na análise
        recommendations = []
        if valence == "positive" and arousal == "high":
            recommendations.append("Imagem transmite energia positiva - ideal para campanhas motivacionais")
        elif valence == "positive" and arousal == "low":
            recommendations.append("Imagem transmite calma e confiança - ideal para produtos premium")
        elif valence == "negative":
            recommendations.append("Considere ajustar para transmitir emoções mais positivas")
        
        return {
            "emotional_impact": f"{valence}-{arousal}",
            "valence": valence,
            "arousal": arousal,
            "recommendations": recommendations
        }


# Instância global do serviço
emotion_service = EmotionService()

