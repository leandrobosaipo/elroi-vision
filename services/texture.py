"""
Serviço de análise de textura e materialidade
"""
from PIL import Image
import numpy as np
import cv2
from typing import Dict

SKIMAGE_AVAILABLE = False
try:
    from skimage import feature, filters
    SKIMAGE_AVAILABLE = True
except ImportError:
    pass


class TextureService:
    """Serviço para análise de textura e sensações táteis"""
    
    def analyze_texture(self, image: Image) -> Dict:
        """
        Analisa textura usando Local Binary Patterns (LBP)
        
        Args:
            image: PIL Image
            
        Returns:
            Dicionário com análise de textura
        """
        try:
            img_array = np.array(image.convert("RGB"))
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            if SKIMAGE_AVAILABLE:
                # Usa LBP para análise de textura
                radius = 3
                n_points = 8 * radius
                lbp = feature.local_binary_pattern(gray, n_points, radius, method='uniform')
                
                # Calcula histograma de LBP
                hist, _ = np.histogram(lbp.ravel(), bins=n_points + 2, range=(0, n_points + 2))
                hist = hist.astype(float)
                hist /= (hist.sum() + 1e-7)  # Normaliza
                
                # Calcula entropia da textura (medida de complexidade)
                entropy = -np.sum(hist * np.log(hist + 1e-7))
                
                # Calcula variância do LBP (medida de contraste de textura)
                texture_variance = np.var(lbp)
                
                # Classifica tipo de textura
                if entropy > 4.0:
                    texture_type = "complexa"
                    texture_meaning = "superfície com muitos detalhes, transmite riqueza e sofisticação"
                elif entropy > 3.0:
                    texture_type = "moderada"
                    texture_meaning = "textura equilibrada, transmite naturalidade"
                else:
                    texture_type = "simples"
                    texture_meaning = "superfície lisa, transmite limpeza e modernidade"
                
                # Classifica sensação tátil baseada em variância
                if texture_variance > 500:
                    tactile_sensation = "aspera"
                    tactile_meaning = "textura áspera evoca sensação de rusticidade e autenticidade"
                elif texture_variance > 200:
                    tactile_sensation = "texturizada"
                    tactile_meaning = "textura moderada transmite qualidade e materialidade"
                elif texture_variance > 50:
                    tactile_sensation = "lisa"
                    tactile_meaning = "superfície lisa transmite elegância e sofisticação"
                else:
                    tactile_sensation = "muito_lisa"
                    tactile_meaning = "superfície muito lisa transmite modernidade e tecnologia"
            else:
                # Fallback simples usando variância de gradiente
                sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
                sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
                gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
                texture_variance = np.var(gradient_magnitude)
                
                entropy = 0.0  # Não disponível sem scikit-image
                
                if texture_variance > 500:
                    texture_type = "complexa"
                    tactile_sensation = "aspera"
                    texture_meaning = "superfície com muitos detalhes"
                    tactile_meaning = "textura áspera evoca rusticidade"
                elif texture_variance > 200:
                    texture_type = "moderada"
                    tactile_sensation = "texturizada"
                    texture_meaning = "textura equilibrada"
                    tactile_meaning = "textura moderada transmite qualidade"
                else:
                    texture_type = "simples"
                    tactile_sensation = "lisa"
                    texture_meaning = "superfície lisa"
                    tactile_meaning = "superfície lisa transmite elegância"
            
            return {
                "texture_type": texture_type,
                "texture_entropy": round(float(entropy), 3) if SKIMAGE_AVAILABLE else None,
                "texture_variance": round(float(texture_variance), 2),
                "texture_meaning": texture_meaning,
                "tactile_sensation": tactile_sensation,
                "tactile_meaning": tactile_meaning,
                "method": "lbp" if SKIMAGE_AVAILABLE else "gradient",
                "explicacao": f"Textura {texture_type} ({texture_meaning}) com sensação {tactile_sensation} ({tactile_meaning}). Em neuromarketing, texturas evocam sensações táteis e influenciam percepção de qualidade e autenticidade."
            }
        except Exception as e:
            return {
                "texture_type": "indefinido",
                "tactile_sensation": "indefinido",
                "error": str(e)
            }


# Instância global do serviço
texture_service = TextureService()

