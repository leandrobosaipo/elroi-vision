"""
Serviço de análise de pose e linguagem corporal
"""
from PIL import Image
import numpy as np
from typing import Dict, List, Optional

MEDIAPIPE_AVAILABLE = False
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    pass


class PoseService:
    """Serviço para análise de pose e linguagem corporal"""
    
    def __init__(self):
        self.pose = None
        if MEDIAPIPE_AVAILABLE:
            try:
                self.mp_pose = mp.solutions.pose
                self.pose = self.mp_pose.Pose(
                    static_image_mode=True,
                    model_complexity=1,
                    enable_segmentation=False,
                    min_detection_confidence=0.5
                )
            except Exception as e:
                print(f"Warning: MediaPipe Pose não pôde ser inicializado: {e}")
    
    def analyze_body_language(self, image: Image) -> Dict:
        """
        Analisa linguagem corporal e postura
        
        Args:
            image: PIL Image
            
        Returns:
            Dicionário com análise de pose e linguagem corporal
        """
        if not MEDIAPIPE_AVAILABLE or self.pose is None:
            return {
                "people_detected": 0,
                "postures": [],
                "dominant_posture": "indefinido",
                "movement_sensation": "nenhum",
                "body_language_analysis": {},
                "method": "none",
                "explicacao": "MediaPipe não disponível. Instale: pip install mediapipe"
            }
        
        try:
            img_array = np.array(image.convert("RGB"))
            results = self.pose.process(img_array)
            
            if not results.pose_landmarks:
                return {
                    "people_detected": 0,
                    "postures": [],
                    "dominant_posture": "indefinido",
                    "movement_sensation": "nenhum",
                    "body_language_analysis": {},
                    "method": "mediapipe",
                    "explicacao": "Nenhuma pessoa detectada para análise de pose"
                }
            
            height, width = img_array.shape[:2]
            landmarks = results.pose_landmarks.landmark
            
            # Extrai pontos-chave usando índices do MediaPipe Pose
            mp_pose_landmarks = self.mp_pose.PoseLandmark
            
            left_shoulder = landmarks[mp_pose_landmarks.LEFT_SHOULDER.value]
            right_shoulder = landmarks[mp_pose_landmarks.RIGHT_SHOULDER.value]
            left_hip = landmarks[mp_pose_landmarks.LEFT_HIP.value]
            right_hip = landmarks[mp_pose_landmarks.RIGHT_HIP.value]
            nose = landmarks[mp_pose_landmarks.NOSE.value]
            
            # Calcula inclinação do corpo (movimento implícito)
            shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2
            hip_center_y = (left_hip.y + right_hip.y) / 2
            body_angle = np.arctan2(
                (hip_center_y - shoulder_center_y) * height,
                abs(left_shoulder.x - right_shoulder.x) * width
            ) * 180 / np.pi
            
            # Classifica postura
            if abs(body_angle) < 5:
                posture = "ereta"
                posture_meaning = "confiança e autoridade"
            elif body_angle > 10:
                posture = "inclinada_para_frente"
                posture_meaning = "engajamento e ação"
            elif body_angle < -10:
                posture = "inclinada_para_tras"
                posture_meaning = "relaxamento ou defesa"
            else:
                posture = "leve_inclinacao"
                posture_meaning = "naturalidade"
            
            # Analisa abertura dos braços
            left_wrist = landmarks[mp_pose_landmarks.LEFT_WRIST.value]
            right_wrist = landmarks[mp_pose_landmarks.RIGHT_WRIST.value]
            
            arm_span = abs(left_wrist.x - right_wrist.x) * width
            shoulder_width = abs(left_shoulder.x - right_shoulder.x) * width
            
            if arm_span > shoulder_width * 1.5:
                arm_position = "abertos"
                arm_meaning = "abertura e confiança"
            elif arm_span < shoulder_width * 0.8:
                arm_position = "fechados"
                arm_meaning = "proteção ou concentração"
            else:
                arm_position = "neutros"
                arm_meaning = "neutralidade"
            
            # Sensação de movimento
            if abs(body_angle) > 15:
                movement = "alto"
                movement_explanation = "Corpo inclinado sugere ação e dinamismo"
            elif abs(body_angle) > 5:
                movement = "moderado"
                movement_explanation = "Leve inclinação transmite movimento sutil"
            else:
                movement = "baixo"
                movement_explanation = "Postura estática transmite estabilidade"
            
            # Análise de linguagem corporal geral
            body_language = {
                "posture_type": posture,
                "posture_meaning": posture_meaning,
                "arm_position": arm_position,
                "arm_meaning": arm_meaning,
                "body_angle_degrees": round(body_angle, 1),
                "confidence_level": "alto" if all([
                    left_shoulder.visibility > 0.5,
                    right_shoulder.visibility > 0.5,
                    left_hip.visibility > 0.5,
                    right_hip.visibility > 0.5
                ]) else "medio"
            }
            
            return {
                "people_detected": 1,
                "postures": [{
                    "posture": posture,
                    "body_angle": round(body_angle, 1),
                    "arm_position": arm_position,
                    "normalized_position": {
                        "x": round(nose.x, 3),
                        "y": round(nose.y, 3)
                    }
                }],
                "dominant_posture": posture,
                "movement_sensation": movement,
                "movement_explanation": movement_explanation,
                "body_language_analysis": body_language,
                "method": "mediapipe",
                "explicacao": f"Postura {posture} ({posture_meaning}) com braços {arm_position} ({arm_meaning}). Em neuromarketing, postura aberta transmite confiança, enquanto inclinação sugere movimento e ação."
            }
        except Exception as e:
            return {
                "people_detected": 0,
                "postures": [],
                "dominant_posture": "indefinido",
                "movement_sensation": "nenhum",
                "body_language_analysis": {},
                "method": "error",
                "error": str(e)
            }


# Instância global do serviço
pose_service = PoseService()

