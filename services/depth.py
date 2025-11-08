"""
Serviço de análise de profundidade de campo e foco
"""
from PIL import Image
import numpy as np
import cv2
from typing import Dict


class DepthService:
    """Serviço para análise de profundidade de campo e blur"""
    
    def analyze_depth_of_field(self, image: Image) -> Dict:
        """
        Analisa profundidade de campo usando variância do Laplaciano
        
        Args:
            image: PIL Image
            
        Returns:
            Dicionário com análise de foco e profundidade
        """
        try:
            img_array = np.array(image.convert("RGB"))
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            height, width = gray.shape
            
            # Divide em quadrantes para análise local
            h_mid = height // 2
            w_mid = width // 2
            
            quadrants = {
                "superior_esquerdo": gray[0:h_mid, 0:w_mid],
                "superior_direito": gray[0:h_mid, w_mid:width],
                "inferior_esquerdo": gray[h_mid:height, 0:w_mid],
                "inferior_direito": gray[h_mid:height, w_mid:width],
                "centro": gray[h_mid//2:h_mid+h_mid//2, w_mid//2:w_mid+w_mid//2]
            }
            
            # Calcula variância do Laplaciano para cada quadrante
            laplacian_variances = {}
            for name, quadrant in quadrants.items():
                laplacian = cv2.Laplacian(quadrant, cv2.CV_64F)
                variance = laplacian.var()
                laplacian_variances[name] = {
                    "variance": round(float(variance), 2),
                    "focus_level": "alto" if variance > 100 else ("medio" if variance > 50 else "baixo")
                }
            
            # Determina área mais focada
            max_variance = max([v["variance"] for v in laplacian_variances.values()])
            min_variance = min([v["variance"] for v in laplacian_variances.values()])
            
            most_focused = max(laplacian_variances.items(), key=lambda x: x[1]["variance"])
            least_focused = min(laplacian_variances.items(), key=lambda x: x[1]["variance"])
            
            # Classifica profundidade de campo
            variance_range = max_variance - min_variance
            if variance_range > 200:
                depth_type = "rasa"
                depth_explanation = "Grande variação de foco cria hierarquia visual clara"
            elif variance_range > 100:
                depth_type = "moderada"
                depth_explanation = "Variação moderada de foco guia atenção sem distração"
            else:
                depth_type = "profunda"
                depth_explanation = "Foco uniforme transmite clareza e realismo"
            
            # Análise geral
            avg_variance = np.mean([v["variance"] for v in laplacian_variances.values()])
            overall_focus = "alto" if avg_variance > 100 else ("medio" if avg_variance > 50 else "baixo")
            
            return {
                "overall_focus_level": overall_focus,
                "average_variance": round(float(avg_variance), 2),
                "depth_of_field_type": depth_type,
                "depth_explanation": depth_explanation,
                "most_focused_region": most_focused[0],
                "least_focused_region": least_focused[0],
                "quadrant_analysis": laplacian_variances,
                "explicacao": f"Profundidade de campo {depth_type}: {depth_explanation}. Área mais focada: {most_focused[0]}. Em neuromarketing, áreas desfocadas direcionam o olhar para elementos principais e criam sensação de profundidade."
            }
        except Exception as e:
            return {
                "overall_focus_level": "indefinido",
                "average_variance": 0.0,
                "depth_of_field_type": "indefinido",
                "error": str(e)
            }


# Instância global do serviço
depth_service = DepthService()

