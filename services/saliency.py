"""
Serviço de análise de saliência e atenção visual
"""
from PIL import Image
import numpy as np
from typing import Dict, List, Tuple, Optional
import cv2


class SaliencyService:
    """
    Serviço para análise de saliência visual (mapa de atenção)
    """
    
    def calculate_saliency_map(self, image: Image) -> Optional[np.ndarray]:
        """
        Calcula mapa de saliência usando algoritmo de saliência
        
        Args:
            image: PIL Image
            
        Returns:
            Array numpy com mapa de saliência (0-255)
        """
        try:
            # Converte PIL para numpy
            img_array = np.array(image.convert("RGB"))
            
            # Usa algoritmo de saliência do OpenCV
            saliency = cv2.saliency.StaticSaliencySpectralResidual_create()
            success, saliency_map = saliency.computeSaliency(img_array)
            
            if success:
                # Normaliza para 0-255
                saliency_map = (saliency_map * 255).astype(np.uint8)
                return saliency_map
            else:
                return None
        except Exception as e:
            print(f"Erro ao calcular mapa de saliência: {e}")
            return None
    
    def find_attention_points(self, image: Image, n_points: int = 5) -> List[Dict]:
        """
        Encontra pontos de maior atenção na imagem
        
        Args:
            image: PIL Image
            n_points: Número de pontos de atenção a retornar
            
        Returns:
            Lista de pontos com coordenadas e score
        """
        saliency_map = self.calculate_saliency_map(image)
        
        if saliency_map is None:
            return []
        
        try:
            # Encontra máximos locais
            try:
                from scipy.ndimage import maximum_filter
            except ImportError:
                # Fallback simples se scipy não estiver disponível
                attention_points = []
                height, width = saliency_map.shape
                # Pega os 5 pontos mais brilhantes
                flat_indices = np.argsort(saliency_map.flatten())[::-1][:n_points]
                for idx in flat_indices:
                    y, x = np.unravel_index(idx, saliency_map.shape)
                    score = float(saliency_map[y, x]) / 255.0
                    attention_points.append({
                        "x": int(x),
                        "y": int(y),
                        "score": round(score, 3),
                        "normalized_x": round(x / width, 3),
                        "normalized_y": round(y / height, 3)
                    })
                return attention_points
            
            # Aplica filtro de máximo
            local_maxima = maximum_filter(saliency_map, size=20) == saliency_map
            
            # Pega valores dos máximos
            maxima_values = saliency_map[local_maxima]
            maxima_positions = np.where(local_maxima)
            
            # Ordena por valor
            sorted_indices = np.argsort(maxima_values)[::-1][:n_points]
            
            attention_points = []
            height, width = saliency_map.shape
            
            for idx in sorted_indices:
                y, x = maxima_positions[0][idx], maxima_positions[1][idx]
                score = float(maxima_values[idx]) / 255.0
                
                attention_points.append({
                    "x": int(x),
                    "y": int(y),
                    "score": round(score, 3),
                    "normalized_x": round(x / width, 3),
                    "normalized_y": round(y / height, 3)
                })
            
            return attention_points
        except Exception as e:
            print(f"Erro ao encontrar pontos de atenção: {e}")
            return []
    
    def analyze_attention_distribution(self, image: Image) -> Dict:
        """
        Analisa distribuição de atenção na imagem
        
        Args:
            image: PIL Image
            
        Returns:
            Análise de distribuição de atenção
        """
        saliency_map = self.calculate_saliency_map(image)
        
        if saliency_map is None:
            return {
                "attention_score": 0.0,
                "focus_center": False,
                "rule_of_thirds_alignment": "unknown"
            }
        
        try:
            height, width = saliency_map.shape
            
            # Calcula centro de massa da atenção
            total_saliency = np.sum(saliency_map)
            if total_saliency == 0:
                return {"attention_score": 0.0, "focus_center": False}
            
            y_coords, x_coords = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')
            center_x = np.sum(x_coords * saliency_map) / total_saliency
            center_y = np.sum(y_coords * saliency_map) / total_saliency
            
            # Normaliza para 0-1
            normalized_x = center_x / width
            normalized_y = center_y / height
            
            # Verifica se está próximo do centro (regra dos terços)
            rule_of_thirds_zones = [1/3, 2/3]
            x_zone = min(rule_of_thirds_zones, key=lambda z: abs(normalized_x - z))
            y_zone = min(rule_of_thirds_zones, key=lambda z: abs(normalized_y - z))
            
            alignment = "aligned" if abs(normalized_x - x_zone) < 0.1 or abs(normalized_y - y_zone) < 0.1 else "center"
            
            # Score geral de atenção (média da saliência)
            attention_score = np.mean(saliency_map) / 255.0
            
            return {
                "attention_score": round(attention_score, 3),
                "focus_center": {
                    "x": round(center_x, 1),
                    "y": round(center_y, 1),
                    "normalized_x": round(normalized_x, 3),
                    "normalized_y": round(normalized_y, 3)
                },
                "rule_of_thirds_alignment": alignment,
                "primary_focus_zone": f"{alignment}-{x_zone:.1f}-{y_zone:.1f}"
            }
        except Exception as e:
            print(f"Erro ao analisar distribuição de atenção: {e}")
            return {"attention_score": 0.0, "focus_center": False}


# Instância global do serviço
saliency_service = SaliencyService()

