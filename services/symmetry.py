"""
Serviço de análise de simetria visual
"""
from PIL import Image
import numpy as np
import cv2
from typing import Dict


class SymmetryService:
    """Serviço para análise de simetria e equilíbrio visual"""
    
    def analyze_symmetry(self, image: Image) -> Dict:
        """
        Analisa simetria horizontal e vertical
        
        Args:
            image: PIL Image
            
        Returns:
            Dicionário com análise de simetria
        """
        try:
            img_array = np.array(image.convert("RGB"))
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            height, width = gray.shape
            
            # Simetria horizontal (comparar metades esquerda e direita)
            left_half = gray[:, :width//2]
            right_half_flipped = cv2.flip(gray[:, width//2:], 1)
            
            # Redimensiona para mesmo tamanho se necessário
            if left_half.shape[1] != right_half_flipped.shape[1]:
                min_width = min(left_half.shape[1], right_half_flipped.shape[1])
                left_half = left_half[:, :min_width]
                right_half_flipped = right_half_flipped[:, :min_width]
            
            # Calcula correlação para simetria horizontal
            horizontal_corr = cv2.matchTemplate(left_half, right_half_flipped, cv2.TM_CCOEFF_NORMED)[0][0]
            
            # Simetria vertical (comparar metades superior e inferior)
            top_half = gray[:height//2, :]
            bottom_half_flipped = cv2.flip(gray[height//2:, :], 0)
            
            # Redimensiona se necessário
            if top_half.shape[0] != bottom_half_flipped.shape[0]:
                min_height = min(top_half.shape[0], bottom_half_flipped.shape[0])
                top_half = top_half[:min_height, :]
                bottom_half_flipped = bottom_half_flipped[:min_height, :]
            
            # Calcula correlação para simetria vertical
            vertical_corr = cv2.matchTemplate(top_half, bottom_half_flipped, cv2.TM_CCOEFF_NORMED)[0][0]
            
            # Classifica nível de simetria
            avg_symmetry = (horizontal_corr + vertical_corr) / 2
            
            if avg_symmetry > 0.85:
                symmetry_level = "muito_alto"
                symmetry_meaning = "harmonia visual máxima, transmite confiança e beleza"
            elif avg_symmetry > 0.70:
                symmetry_level = "alto"
                symmetry_meaning = "boa harmonia visual, transmite equilíbrio"
            elif avg_symmetry > 0.50:
                symmetry_level = "moderado"
                symmetry_meaning = "equilíbrio moderado, composição natural"
            else:
                symmetry_level = "baixo"
                symmetry_meaning = "assimetria proposital pode criar dinamismo"
            
            # Determina tipo de simetria dominante
            if horizontal_corr > vertical_corr + 0.1:
                dominant_symmetry = "horizontal"
            elif vertical_corr > horizontal_corr + 0.1:
                dominant_symmetry = "vertical"
            else:
                dominant_symmetry = "ambas"
            
            return {
                "symmetry_level": symmetry_level,
                "symmetry_score": round(float(avg_symmetry), 3),
                "horizontal_symmetry": round(float(horizontal_corr), 3),
                "vertical_symmetry": round(float(vertical_corr), 3),
                "dominant_symmetry_type": dominant_symmetry,
                "symmetry_meaning": symmetry_meaning,
                "explicacao": f"Simetria {symmetry_level}: {symmetry_meaning}. Em neuromarketing, simetria alta está associada a confiança e beleza percebida, enquanto assimetria controlada pode criar interesse visual."
            }
        except Exception as e:
            return {
                "symmetry_level": "indefinido",
                "symmetry_score": 0.0,
                "error": str(e)
            }


# Instância global do serviço
symmetry_service = SymmetryService()

