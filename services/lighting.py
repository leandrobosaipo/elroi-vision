"""
Serviço de análise de iluminação e temperatura de cor
"""
from PIL import Image
import numpy as np
import cv2
from typing import Dict


class LightingService:
    """Serviço para análise de iluminação e temperatura de cor"""
    
    def analyze_lighting(self, image: Image) -> Dict:
        """
        Analisa iluminação e temperatura de cor
        
        Args:
            image: PIL Image
            
        Returns:
            Dicionário com análise de iluminação
        """
        try:
            img_array = np.array(image.convert("RGB"))
            
            # Converte para LAB para análise de luminância
            lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
            l_channel = lab[:, :, 0]  # Luminância
            
            # Calcula estatísticas de luminância
            avg_luminance = np.mean(l_channel)
            std_luminance = np.std(l_channel)
            
            # Classifica nível de iluminação
            if avg_luminance > 200:
                lighting_level = "muito_alto"
                lighting_meaning = "iluminação muito brilhante, transmite clareza e energia"
            elif avg_luminance > 150:
                lighting_level = "alto"
                lighting_meaning = "boa iluminação, transmite positividade"
            elif avg_luminance > 100:
                lighting_level = "moderado"
                lighting_meaning = "iluminação equilibrada, transmite naturalidade"
            elif avg_luminance > 50:
                lighting_level = "baixo"
                lighting_meaning = "iluminação suave, transmite intimidade ou mistério"
            else:
                lighting_level = "muito_baixo"
                lighting_meaning = "iluminação escura, transmite drama ou seriedade"
            
            # Análise de contraste de iluminação
            if std_luminance > 40:
                contrast_level = "alto"
                contrast_meaning = "grande variação de luz cria drama visual"
            elif std_luminance > 25:
                contrast_level = "moderado"
                contrast_meaning = "variação moderada cria profundidade"
            else:
                contrast_level = "baixo"
                contrast_meaning = "iluminação uniforme transmite suavidade"
            
            # Estima temperatura de cor (aproximada via balanço de branco)
            rgb = img_array.astype(np.float32)
            
            # Calcula médias por canal
            r_mean = np.mean(rgb[:, :, 0])
            g_mean = np.mean(rgb[:, :, 1])
            b_mean = np.mean(rgb[:, :, 2])
            
            # Estima temperatura aproximada (Kelvin)
            # Baseado na relação R/B
            if r_mean > 0 and b_mean > 0:
                rb_ratio = r_mean / b_mean
                
                # Aproximação simples: ratio alto = quente, ratio baixo = frio
                if rb_ratio > 1.3:
                    color_temp = "quente"
                    temp_kelvin_approx = 3000  # Lâmpada incandescente
                    temp_meaning = "luz quente transmite acolhimento e conforto"
                elif rb_ratio > 1.1:
                    color_temp = "neutra_quente"
                    temp_kelvin_approx = 4000  # Lâmpada fluorescente quente
                    temp_meaning = "temperatura neutra-quente transmite naturalidade"
                elif rb_ratio > 0.9:
                    color_temp = "neutra"
                    temp_kelvin_approx = 5000  # Luz do dia
                    temp_meaning = "temperatura neutra transmite objetividade"
                else:
                    color_temp = "fria"
                    temp_kelvin_approx = 6500  # Luz do dia nublado
                    temp_meaning = "luz fria transmite racionalidade e modernidade"
            else:
                color_temp = "indefinido"
                temp_kelvin_approx = 0
                temp_meaning = "Não foi possível determinar temperatura"
            
            return {
                "lighting_level": lighting_level,
                "average_luminance": round(float(avg_luminance), 1),
                "luminance_std": round(float(std_luminance), 1),
                "lighting_meaning": lighting_meaning,
                "contrast_level": contrast_level,
                "contrast_meaning": contrast_meaning,
                "color_temperature": color_temp,
                "temperature_kelvin_approx": temp_kelvin_approx,
                "temperature_meaning": temp_meaning,
                "explicacao": f"Iluminação {lighting_level} ({lighting_meaning}) com temperatura {color_temp} ({temp_meaning}). Em neuromarketing, luz quente ativa emoções de acolhimento, enquanto luz fria transmite racionalidade e modernidade."
            }
        except Exception as e:
            return {
                "lighting_level": "indefinido",
                "color_temperature": "indefinido",
                "error": str(e)
            }


# Instância global do serviço
lighting_service = LightingService()

