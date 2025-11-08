"""
Serviço de detecção de CTAs (Call-to-Action)
"""
from PIL import Image
import numpy as np
from typing import List, Dict, Optional
import re


class CTAService:
    """Serviço para detecção de elementos Call-to-Action"""
    
    # Palavras-chave comuns em CTAs
    CTA_KEYWORDS = [
        "compre", "buy", "comprar", "adquira", "peça", "order",
        "saiba mais", "learn more", "descubra", "discover",
        "cadastre-se", "sign up", "registre-se", "register",
        "baixe", "download", "baixar",
        "clique", "click", "toque", "tap",
        "agora", "now", "já", "already",
        "grátis", "free", "gratuito",
        "oferta", "offer", "promoção", "promotion",
        "experimente", "try", "teste", "test"
    ]
    
    def detect_cta_elements(self, image: Image, text_segments: List[Dict]) -> List[Dict]:
        """
        Detecta elementos CTA na imagem baseado em texto e posição
        
        Args:
            image: PIL Image
            text_segments: Lista de segmentos de texto detectados
            
        Returns:
            Lista de CTAs detectados
        """
        cta_elements = []
        
        if not text_segments:
            return cta_elements
        
        image_width, image_height = image.size
        
        for segment in text_segments:
            text = segment.get("text", "").lower()
            bbox = segment.get("bbox", {})
            
            # Verifica se contém palavras-chave de CTA
            cta_keywords_found = []
            for keyword in self.CTA_KEYWORDS:
                if keyword.lower() in text:
                    cta_keywords_found.append(keyword)
            
            if cta_keywords_found:
                # Calcula posição relativa
                x_center = (bbox.get("xmin", 0) + bbox.get("xmax", 0)) / 2
                y_center = (bbox.get("ymin", 0) + bbox.get("ymax", 0)) / 2
                
                normalized_x = x_center / image_width
                normalized_y = y_center / image_height
                
                # Verifica se está em posição estratégica (inferior direito é comum para CTAs)
                is_strategic_position = (
                    normalized_x > 0.6 and normalized_y > 0.6  # Inferior direito
                    or normalized_x > 0.4 and normalized_x < 0.6 and normalized_y > 0.7  # Centro inferior
                )
                
                # Calcula tamanho relativo do texto
                text_width = bbox.get("xmax", 0) - bbox.get("xmin", 0)
                text_height = bbox.get("ymax", 0) - bbox.get("ymin", 0)
                relative_size = (text_width * text_height) / (image_width * image_height)
                
                cta_elements.append({
                    "text": segment.get("text", ""),
                    "keywords": cta_keywords_found,
                    "bbox": bbox,
                    "position": {
                        "x": round(x_center, 1),
                        "y": round(y_center, 1),
                        "normalized_x": round(normalized_x, 3),
                        "normalized_y": round(normalized_y, 3)
                    },
                    "is_strategic_position": is_strategic_position,
                    "relative_size": round(relative_size * 100, 2),
                    "confidence": segment.get("confidence", 0.0)
                })
        
        return cta_elements
    
    def analyze_cta_effectiveness(self, cta_elements: List[Dict], color_analysis: Dict) -> Dict:
        """
        Analisa efetividade dos CTAs baseado em posição, tamanho e contraste
        
        Args:
            cta_elements: Lista de CTAs detectados
            color_analysis: Análise de cores da imagem
            
        Returns:
            Análise de efetividade dos CTAs
        """
        if not cta_elements:
            return {
                "cta_present": False,
                "effectiveness_score": 0.0,
                "recommendations": ["Adicione um Call-to-Action claro e visível"]
            }
        
        effectiveness_scores = []
        recommendations = []
        
        for cta in cta_elements:
            score = 0.0
            
            # Pontuação por posição estratégica
            if cta["is_strategic_position"]:
                score += 0.3
            else:
                recommendations.append(f"CTA '{cta['text']}' poderia estar em posição mais estratégica (inferior direito)")
            
            # Pontuação por tamanho
            if cta["relative_size"] > 2.0:  # Mais de 2% da imagem
                score += 0.3
            elif cta["relative_size"] < 0.5:
                recommendations.append(f"CTA '{cta['text']}' é muito pequeno para ser facilmente notado")
            
            # Pontuação por confiança do texto
            score += cta["confidence"] * 0.2
            
            # Pontuação por contraste (se disponível)
            if color_analysis.get("average_contrast", 0) > 4.5:
                score += 0.2
            
            effectiveness_scores.append(score)
        
        avg_score = np.mean(effectiveness_scores) if effectiveness_scores else 0.0
        
        if avg_score < 0.5:
            recommendations.append("Melhore visibilidade do CTA aumentando contraste e tamanho")
        
        return {
            "cta_present": True,
            "cta_count": len(cta_elements),
            "effectiveness_score": round(avg_score, 2),
            "recommendations": recommendations if recommendations else ["CTAs bem posicionados e visíveis"]
        }


# Instância global do serviço
cta_service = CTAService()

