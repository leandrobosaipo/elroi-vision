"""
Serviço de geração de descrição/caption de imagens
"""
from PIL import Image
from typing import Dict, Optional

BLIP_AVAILABLE = False
try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
    import torch
    BLIP_AVAILABLE = True
except ImportError:
    pass


class CaptionService:
    """Serviço para geração de descrições de imagens"""
    
    def __init__(self):
        self.processor = None
        self.model = None
        
        if BLIP_AVAILABLE:
            try:
                self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
                self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
                if torch.cuda.is_available():
                    self.model = self.model.to("cuda")
                else:
                    self.model = self.model.to("cpu")
            except Exception as e:
                print(f"Warning: BLIP não pôde ser carregado: {e}")
                pass
    
    def generate_caption(self, image: Image, max_length: int = 50) -> Dict:
        """
        Gera descrição da imagem usando BLIP
        
        Args:
            image: PIL Image
            max_length: Comprimento máximo da descrição
            
        Returns:
            Dicionário com descrição e metadados
        """
        if not BLIP_AVAILABLE or self.processor is None or self.model is None:
            return {
                "caption": "Serviço de caption não disponível. Instale transformers e blip.",
                "method": "none",
                "confidence": 0.0
            }
        
        try:
            # Converte para RGB se necessário
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            # Processa imagem
            inputs = self.processor(image, return_tensors="pt")
            
            # Move para GPU se disponível
            device = next(self.model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Gera caption
            with torch.no_grad():
                out = self.model.generate(**inputs, max_length=max_length)
            
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            
            return {
                "caption": caption,
                "method": "blip",
                "confidence": 0.85,  # BLIP não retorna confiança, valor estimado
                "length": len(caption.split())
            }
        except Exception as e:
            print(f"Erro ao gerar caption: {e}")
            return {
                "caption": f"Erro ao gerar descrição: {str(e)}",
                "method": "error",
                "confidence": 0.0
            }
    
    def generate_detailed_description(self, image: Image, objects: list) -> Dict:
        """
        Gera descrição detalhada combinando objetos detectados e caption
        
        Args:
            image: PIL Image
            objects: Lista de objetos detectados
            
        Returns:
            Descrição narrativa completa
        """
        caption_result = self.generate_caption(image)
        caption = caption_result.get("caption", "")
        
        # Adiciona informações dos objetos detectados
        if objects:
            object_names = [obj.get("name", "") for obj in objects if obj.get("confidence", 0) > 0.5]
            if object_names:
                unique_objects = list(set(object_names))
                objects_text = ", ".join(unique_objects)
                detailed = f"{caption} A imagem contém: {objects_text}."
            else:
                detailed = caption
        else:
            detailed = caption
        
        return {
            "short_caption": caption,
            "detailed_description": detailed,
            "detected_objects": len(objects) if objects else 0,
            "method": caption_result.get("method", "unknown")
        }


# Instância global do serviço
caption_service = CaptionService()

