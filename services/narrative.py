"""
Serviço de análise narrativa e coerência contextual
"""
from PIL import Image
from typing import Dict, List, Optional


class NarrativeService:
    """Serviço para análise de narrativa implícita e contexto"""
    
    def analyze_narrative(self, image: Image, objects: List[Dict], emotions: Dict, text: Dict, colors: Dict) -> Dict:
        """
        Analisa narrativa implícita e coerência contextual
        
        Args:
            image: PIL Image
            objects: Lista de objetos detectados
            emotions: Resultado de análise emocional
            text: Resultado de OCR
            colors: Resultado de análise de cores
            
        Returns:
            Dicionário com análise narrativa
        """
        try:
            # Extrai informações relevantes
            object_names = [obj.get("name", "") for obj in objects] if objects else []
            emotion = emotions.get("scene_emotion", "neutral")
            text_content = text.get("full_text", "").lower()
            color_palette = colors.get("emotion_palette", "neutral")
            
            # Analisa coerência narrativa
            narrative_elements = []
            
            # Verifica consistência emocional
            if emotion == "happy" and "warm" in color_palette:
                narrative_elements.append("coerencia_emocional_positiva")
            elif emotion == "sad" and "dark" in color_palette or "neutral" in color_palette:
                narrative_elements.append("coerencia_emocional_neutra")
            
            # Detecta elementos de escassez/urgência no texto
            urgency_keywords = ["agora", "urgente", "limitado", "últimas", "restam", "aproveite", "corra", "rápido"]
            scarcity_detected = any(keyword in text_content for keyword in urgency_keywords)
            
            # Detecta símbolos de tempo/urgência nos objetos
            time_objects = ["clock", "watch", "timer", "hourglass"]
            has_time_symbols = any(obj in object_names for obj in time_objects)
            
            # Analisa história implícita
            if "person" in object_names and emotion == "happy":
                story = "pessoa_feliz"
                story_meaning = "imagem transmite felicidade e conexão humana"
            elif len(object_names) > 3:
                story = "cena_complexa"
                story_meaning = "múltiplos elementos criam narrativa rica e envolvente"
            elif scarcity_detected or has_time_symbols:
                story = "urgencia_acao"
                story_meaning = "elementos de urgência despertam ação imediata"
            else:
                story = "narrativa_simples"
                story_meaning = "narrativa direta e clara"
            
            # Detecta incongruência/humor
            incongruence_detected = False
            incongruence_explanation = ""
            
            # Verifica contradições entre elementos
            if emotion == "happy" and "dark" in color_palette:
                incongruence_detected = True
                incongruence_explanation = "Contraste entre emoção positiva e paleta escura cria interesse"
            elif "person" in object_names and len(object_names) == 1 and "car" in object_names:
                # Pessoa sozinha com carro pode sugerir liberdade ou solidão
                pass
            
            # Efeito surpresa
            surprise_score = 0.0
            if incongruence_detected:
                surprise_score = 0.7
            elif scarcity_detected:
                surprise_score = 0.5
            elif len(object_names) > 5:
                surprise_score = 0.3
            
            surprise_level = "alto" if surprise_score > 0.6 else ("moderado" if surprise_score > 0.3 else "baixo")
            
            return {
                "implicit_story": story,
                "story_meaning": story_meaning,
                "narrative_elements": narrative_elements,
                "scarcity_trigger_detected": scarcity_detected or has_time_symbols,
                "scarcity_elements": {
                    "text_keywords": [kw for kw in urgency_keywords if kw in text_content],
                    "time_symbols": [obj for obj in object_names if obj in time_objects]
                },
                "incongruence_detected": incongruence_detected,
                "incongruence_explanation": incongruence_explanation if incongruence_detected else None,
                "surprise_level": surprise_level,
                "surprise_score": round(surprise_score, 2),
                "narrative_coherence": "alta" if len(narrative_elements) > 0 else "moderada",
                "explicacao": f"Narrativa implícita: {story_meaning}. {'Elementos de escassez detectados despertam ação imediata. ' if (scarcity_detected or has_time_symbols) else ''}{'Contraste visual cria interesse e quebra expectativas. ' if incongruence_detected else ''}Em neuromarketing, narrativas coerentes aumentam engajamento, enquanto elementos de surpresa liberam dopamina e criam memorabilidade."
            }
        except Exception as e:
            return {
                "implicit_story": "indefinido",
                "error": str(e)
            }


# Instância global do serviço
narrative_service = NarrativeService()

