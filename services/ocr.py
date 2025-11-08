"""
Serviço de OCR (Optical Character Recognition)
"""
from PIL import Image
from typing import List, Dict, Optional
import numpy as np

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


class OCRService:
    """Serviço para extração de texto de imagens"""
    
    def __init__(self):
        self.easyocr_reader = None
        if EASYOCR_AVAILABLE:
            try:
                # Inicializa EasyOCR (carrega modelos na primeira chamada)
                self.easyocr_reader = easyocr.Reader(['en', 'pt'], gpu=False)
            except Exception as e:
                print(f"Warning: EasyOCR não pôde ser inicializado: {e}")
    
    def extract_text_easyocr(self, image: Image) -> List[Dict]:
        """
        Extrai texto usando EasyOCR
        
        Args:
            image: PIL Image
            
        Returns:
            Lista de dicionários com texto e coordenadas
        """
        if not EASYOCR_AVAILABLE or self.easyocr_reader is None:
            return []
        
        try:
            # Converte PIL para numpy array
            img_array = np.array(image)
            results = self.easyocr_reader.readtext(img_array)
            
            text_segments = []
            for (bbox, text, confidence) in results:
                # bbox é uma lista de 4 pontos [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                
                text_segments.append({
                    "text": text,
                    "confidence": float(confidence),
                    "bbox": {
                        "xmin": min(x_coords),
                        "ymin": min(y_coords),
                        "xmax": max(x_coords),
                        "ymax": max(y_coords)
                    }
                })
            
            return text_segments
        except Exception as e:
            print(f"Erro ao extrair texto com EasyOCR: {e}")
            return []
    
    def extract_text_tesseract(self, image: Image) -> List[Dict]:
        """
        Extrai texto usando Tesseract OCR
        
        Args:
            image: PIL Image
            
        Returns:
            Lista de dicionários com texto e coordenadas
        """
        if not TESSERACT_AVAILABLE:
            return []
        
        try:
            # Extrai texto com coordenadas
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            text_segments = []
            n_boxes = len(data['text'])
            
            for i in range(n_boxes):
                text = data['text'][i].strip()
                if text and int(data['conf'][i]) > 0:
                    text_segments.append({
                        "text": text,
                        "confidence": float(data['conf'][i]) / 100.0,
                        "bbox": {
                            "xmin": int(data['left'][i]),
                            "ymin": int(data['top'][i]),
                            "xmax": int(data['left'][i]) + int(data['width'][i]),
                            "ymax": int(data['top'][i]) + int(data['height'][i])
                        }
                    })
            
            return text_segments
        except Exception as e:
            print(f"Erro ao extrair texto com Tesseract: {e}")
            return []
    
    def extract_text(self, image: Image, method: str = "easyocr") -> Dict:
        """
        Extrai texto da imagem usando o método especificado
        
        Args:
            image: PIL Image
            method: "easyocr" ou "tesseract"
            
        Returns:
            Dicionário com texto extraído e metadados
        """
        if method == "easyocr":
            segments = self.extract_text_easyocr(image)
        elif method == "tesseract":
            segments = self.extract_text_tesseract(image)
        else:
            # Tenta EasyOCR primeiro, depois Tesseract
            segments = self.extract_text_easyocr(image)
            if not segments:
                segments = self.extract_text_tesseract(image)
        
        # Combina todo o texto
        full_text = " ".join([seg["text"] for seg in segments])
        
        return {
            "full_text": full_text,
            "segments": segments,
            "total_segments": len(segments),
            "method_used": method
        }


# Instância global do serviço
ocr_service = OCRService()

