"""
Serviço de classificação de cena (natural vs artificial)
"""
from PIL import Image
import numpy as np
import cv2
from typing import Dict

TORCHVISION_AVAILABLE = False
try:
    import torch
    import torchvision.transforms as transforms
    from torchvision import models
    TORCHVISION_AVAILABLE = True
except ImportError:
    pass


class SceneService:
    """Serviço para classificação de ambiente (natural vs artificial)"""
    
    def __init__(self):
        self.model = None
        self.transform = None
        
        if TORCHVISION_AVAILABLE:
            try:
                # Usa modelo pré-treinado ResNet para classificação de cena
                # Nota: Para produção, considere usar Places365 ou modelo específico
                self.model = models.resnet18(pretrained=True)
                self.model.eval()
                
                self.transform = transforms.Compose([
                    transforms.Resize(256),
                    transforms.CenterCrop(224),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
            except Exception as e:
                print(f"Warning: Modelo de classificação de cena não pôde ser carregado: {e}")
    
    def classify_scene(self, image: Image) -> Dict:
        """
        Classifica se a cena é natural ou artificial
        
        Args:
            image: PIL Image
            
        Returns:
            Dicionário com classificação de ambiente
        """
        if not TORCHVISION_AVAILABLE or self.model is None:
            # Fallback baseado em análise de cores e padrões
            return self._simple_scene_classification(image)
        
        try:
            # Prepara imagem
            img_tensor = self.transform(image).unsqueeze(0)
            
            with torch.no_grad():
                outputs = self.model(img_tensor)
                # Nota: ResNet padrão não classifica cenas diretamente
                # Para produção, use modelo específico como Places365
            
            # Fallback para análise simples
            return self._simple_scene_classification(image)
        except Exception as e:
            return self._simple_scene_classification(image)
    
    def _simple_scene_classification(self, image: Image) -> Dict:
        """
        Classificação simples baseada em cores e padrões
        """
        try:
            img_array = np.array(image.convert("RGB"))
            
            # Analisa distribuição de cores (verde = natural, cinza/preto = urbano)
            hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
            h_channel = hsv[:, :, 0]
            s_channel = hsv[:, :, 1]
            v_channel = hsv[:, :, 2]
            
            # Detecta verdes (natureza)
            green_mask = (h_channel > 40) & (h_channel < 80) & (s_channel > 50)
            green_percentage = np.sum(green_mask) / (img_array.shape[0] * img_array.shape[1]) * 100
            
            # Detecta tons de cinza/preto (urbano/tecnologia)
            gray_mask = (s_channel < 30) & (v_channel < 200)
            gray_percentage = np.sum(gray_mask) / (img_array.shape[0] * img_array.shape[1]) * 100
            
            # Detecta azuis (céu/água = natural, ou tecnologia)
            blue_mask = (h_channel > 100) & (h_channel < 130) & (s_channel > 50)
            blue_percentage = np.sum(blue_mask) / (img_array.shape[0] * img_array.shape[1]) * 100
            
            # Classifica ambiente
            if green_percentage > 20:
                scene_type = "natural"
                scene_meaning = "ambiente natural transmite relaxamento e bem-estar"
            elif gray_percentage > 30:
                scene_type = "urbano_tecnologico"
                scene_meaning = "ambiente urbano/tecnológico transmite estímulo cognitivo e modernidade"
            elif blue_percentage > 15:
                scene_type = "natural_aquatico"
                scene_meaning = "elementos aquáticos/naturais transmitem calma e serenidade"
            else:
                scene_type = "misto"
                scene_meaning = "ambiente misto transmite equilíbrio entre natural e artificial"
            
            return {
                "scene_type": scene_type,
                "natural_elements_percentage": round(green_percentage, 1),
                "urban_elements_percentage": round(gray_percentage, 1),
                "scene_meaning": scene_meaning,
                "method": "color_analysis",
                "explicacao": f"Ambiente classificado como {scene_type}: {scene_meaning}. Em neuromarketing, ambientes naturais despertam relaxamento, enquanto ambientes urbanos estimulam cognição e ação."
            }
        except Exception as e:
            return {
                "scene_type": "indefinido",
                "error": str(e)
            }


# Instância global do serviço
scene_service = SceneService()

