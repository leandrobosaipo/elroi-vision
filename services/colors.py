"""
Serviço de análise de cores e contraste
"""
from PIL import Image
import numpy as np
from typing import List, Dict, Tuple
from collections import Counter
import colorsys


class ColorAnalysisService:
    """Serviço para análise de cores e contraste em imagens"""
    
    def extract_dominant_colors(self, image: Image, n_colors: int = 5) -> List[Dict]:
        """
        Extrai cores dominantes da imagem usando k-means
        
        Args:
            image: PIL Image
            n_colors: Número de cores dominantes a extrair
            
        Returns:
            Lista de cores dominantes com porcentagem e informações
        """
        try:
            # Redimensiona para acelerar processamento
            img_small = image.resize((150, 150))
            img_array = np.array(img_small)
            
            # Converte para RGB se necessário
            if img_array.shape[2] == 4:  # RGBA
                img_array = img_array[:, :, :3]
            
            # Achatamento para k-means
            pixels = img_array.reshape(-1, 3)
            
            # K-means simples usando contagem de cores aproximadas
            # Agrupa cores similares
            quantized = (pixels // 32) * 32  # Quantização
            color_counts = Counter(map(tuple, quantized))
            
            # Pega as cores mais frequentes
            most_common = color_counts.most_common(n_colors)
            total_pixels = len(pixels)
            
            dominant_colors = []
            for color_rgb, count in most_common:
                percentage = (count / total_pixels) * 100
                hex_color = f"#{color_rgb[0]:02x}{color_rgb[1]:02x}{color_rgb[2]:02x}"
                
                # Converte para HSV para análise emocional
                h, s, v = colorsys.rgb_to_hsv(
                    color_rgb[0]/255.0,
                    color_rgb[1]/255.0,
                    color_rgb[2]/255.0
                )
                
                # Classifica cor emocionalmente
                emotion_tag = self._classify_color_emotion(h, s, v)
                
                dominant_colors.append({
                    "rgb": list(color_rgb),
                    "hex": hex_color,
                    "percentage": round(percentage, 2),
                    "hsv": {
                        "h": round(h * 360, 1),
                        "s": round(s * 100, 1),
                        "v": round(v * 100, 1)
                    },
                    "emotion_tag": emotion_tag
                })
            
            return dominant_colors
        except Exception as e:
            print(f"Erro ao extrair cores dominantes: {e}")
            return []
    
    def _classify_color_emotion(self, h: float, s: float, v: float) -> str:
        """
        Classifica cor por impacto emocional
        
        Args:
            h: Hue (0-1)
            s: Saturation (0-1)
            v: Value/Brightness (0-1)
            
        Returns:
            Tag emocional da cor
        """
        h_deg = h * 360
        
        if v < 0.3:
            return "dark"
        elif v > 0.8 and s < 0.3:
            return "light"
        elif s < 0.3:
            return "neutral"
        elif 0 <= h_deg < 30 or h_deg >= 330:
            return "warm-energetic"  # Vermelho/Laranja
        elif 30 <= h_deg < 90:
            return "cheerful"  # Amarelo
        elif 90 <= h_deg < 150:
            return "fresh"  # Verde
        elif 150 <= h_deg < 210:
            return "calm"  # Ciano
        elif 210 <= h_deg < 270:
            return "trustworthy"  # Azul
        elif 270 <= h_deg < 330:
            return "creative"  # Roxo/Magenta
        else:
            return "neutral"
    
    def calculate_contrast(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
        """
        Calcula contraste WCAG entre duas cores
        
        Args:
            color1: RGB tuple
            color2: RGB tuple
            
        Returns:
            Razão de contraste (1-21, idealmente >4.5 para texto)
        """
        def get_luminance(rgb):
            """Calcula luminância relativa"""
            r, g, b = [c / 255.0 for c in rgb]
            
            def adjust(c):
                if c <= 0.03928:
                    return c / 12.92
                return ((c + 0.055) / 1.055) ** 2.4
            
            r = adjust(r)
            g = adjust(g)
            b = adjust(b)
            
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        l1 = get_luminance(color1)
        l2 = get_luminance(color2)
        
        lighter = max(l1, l2)
        darker = min(l1, l2)
        
        contrast = (lighter + 0.05) / (darker + 0.05)
        return round(contrast, 2)
    
    def analyze_image_colors(self, image: Image, n_colors: int = 5) -> Dict:
        """
        Análise completa de cores da imagem
        
        Args:
            image: PIL Image
            
        Returns:
            Dicionário com análise completa de cores
        """
        dominant_colors = self.extract_dominant_colors(image, n_colors=n_colors)
        
        # Calcula contraste entre cores principais
        contrast_scores = []
        if len(dominant_colors) >= 2:
            for i in range(len(dominant_colors) - 1):
                c1 = tuple(dominant_colors[i]["rgb"])
                c2 = tuple(dominant_colors[i+1]["rgb"])
                contrast = self.calculate_contrast(c1, c2)
                contrast_scores.append(contrast)
        
        # Determina paleta emocional geral
        emotion_tags = [c["emotion_tag"] for c in dominant_colors if c["percentage"] > 10]
        dominant_emotion = max(set(emotion_tags), key=emotion_tags.count) if emotion_tags else "neutral"
        
        return {
            "dominant_colors": dominant_colors,
            "average_contrast": round(np.mean(contrast_scores), 2) if contrast_scores else 0,
            "emotion_palette": dominant_emotion,
            "color_count": len(dominant_colors)
        }


# Instância global do serviço
color_service = ColorAnalysisService()

