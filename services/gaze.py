"""
Serviço de análise de direção do olhar (gaze estimation)
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


class GazeService:
    """Serviço para estimar direção do olhar"""
    
    def __init__(self):
        self.face_mesh = None
        if MEDIAPIPE_AVAILABLE:
            try:
                self.mp_face_mesh = mp.solutions.face_mesh
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    static_image_mode=True,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5
                )
            except Exception as e:
                print(f"Warning: MediaPipe FaceMesh não pôde ser inicializado: {e}")
    
    def estimate_gaze_direction(self, image: Image) -> Dict:
        """
        Estima direção do olhar usando MediaPipe
        
        Args:
            image: PIL Image
            
        Returns:
            Dicionário com direção do olhar e região focada
        """
        if not MEDIAPIPE_AVAILABLE or self.face_mesh is None:
            return {
                "faces_detected": 0,
                "gaze_directions": [],
                "primary_gaze_direction": "indefinido",
                "gaze_target_region": "centro",
                "method": "none",
                "explicacao": "MediaPipe não disponível. Instale: pip install mediapipe"
            }
        
        try:
            img_array = np.array(image.convert("RGB"))
            results = self.face_mesh.process(img_array)
            
            if not results.multi_face_landmarks:
                return {
                    "faces_detected": 0,
                    "gaze_directions": [],
                    "primary_gaze_direction": "indefinido",
                    "gaze_target_region": "centro",
                    "method": "mediapipe",
                    "explicacao": "Nenhuma face detectada para análise de olhar"
                }
            
            height, width = img_array.shape[:2]
            gaze_directions = []
            
            for face_landmarks in results.multi_face_landmarks:
                # Pontos-chave dos olhos (índices do MediaPipe Face Mesh)
                left_eye_center = [
                    face_landmarks.landmark[33].x * width,
                    face_landmarks.landmark[33].y * height
                ]
                right_eye_center = [
                    face_landmarks.landmark[263].x * width,
                    face_landmarks.landmark[263].y * height
                ]
                
                # Estima direção baseada na posição dos olhos e nariz
                nose_tip = [
                    face_landmarks.landmark[4].x * width,
                    face_landmarks.landmark[4].y * height
                ]
                
                # Calcula vetor médio do olhar
                eye_center_x = (left_eye_center[0] + right_eye_center[0]) / 2
                eye_center_y = (left_eye_center[1] + right_eye_center[1]) / 2
                
                # Direção relativa ao nariz
                dx = nose_tip[0] - eye_center_x
                dy = nose_tip[1] - eye_center_y
                
                # Normaliza e classifica direção
                angle = np.arctan2(dy, dx) * 180 / np.pi
                
                if angle < -45:
                    direction = "esquerda"
                elif angle > 45:
                    direction = "direita"
                elif dy < -10:
                    direction = "cima"
                elif dy > 10:
                    direction = "baixo"
                else:
                    direction = "frente"
                
                # Determina região focada na imagem
                normalized_x = eye_center_x / width
                normalized_y = eye_center_y / height
                
                if normalized_x < 0.33:
                    region_x = "esquerda"
                elif normalized_x > 0.67:
                    region_x = "direita"
                else:
                    region_x = "centro"
                
                if normalized_y < 0.33:
                    region_y = "superior"
                elif normalized_y > 0.67:
                    region_y = "inferior"
                else:
                    region_y = "central"
                
                gaze_target = f"{region_y}-{region_x}"
                
                gaze_directions.append({
                    "direction": direction,
                    "angle_degrees": round(angle, 1),
                    "gaze_target_region": gaze_target,
                    "normalized_position": {
                        "x": round(normalized_x, 3),
                        "y": round(normalized_y, 3)
                    }
                })
            
            primary_direction = gaze_directions[0]["direction"] if gaze_directions else "indefinido"
            primary_region = gaze_directions[0]["gaze_target_region"] if gaze_directions else "centro"
            
            return {
                "faces_detected": len(gaze_directions),
                "gaze_directions": gaze_directions,
                "primary_gaze_direction": primary_direction,
                "gaze_target_region": primary_region,
                "method": "mediapipe",
                "explicacao": f"Olhar direcionado para {primary_direction}, focando na região {primary_region}. Em neuromarketing, o olhar guia o foco do observador e cria conexão emocional."
            }
        except Exception as e:
            return {
                "faces_detected": 0,
                "gaze_directions": [],
                "primary_gaze_direction": "indefinido",
                "gaze_target_region": "centro",
                "method": "error",
                "error": str(e)
            }


# Instância global do serviço
gaze_service = GazeService()

