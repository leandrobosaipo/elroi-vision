from PIL import Image
import io
import pandas as pd
import numpy as np
from typing import Optional
import torch

# Configurar PyTorch para permitir carregamento do modelo YOLO no PyTorch 2.6+
# Isso é necessário porque o PyTorch 2.6+ mudou o padrão de weights_only para True
# Usamos um monkey patch para modificar temporariamente o torch.load usado pela ultralytics
_original_torch_load = torch.load

def _patched_torch_load(*args, **kwargs):
    """Patch do torch.load para usar weights_only=False ao carregar modelos YOLO"""
    # Se weights_only não foi especificado explicitamente, usa False para modelos YOLO
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)

# Aplicar o patch apenas se estivermos no PyTorch 2.6+
if hasattr(torch.serialization, 'add_safe_globals'):
    # Monkey patch do torch.load usado pela ultralytics
    import ultralytics.nn.tasks as ultralytics_tasks
    ultralytics_tasks.torch.load = _patched_torch_load

from ultralytics import YOLO
from ultralytics.yolo.utils.plotting import Annotator, colors

from config import settings

# Initialize the models
model_sample_model = None


def load_model():
    """Carrega o modelo YOLO usando o caminho das configurações"""
    global model_sample_model
    if model_sample_model is None:
        model_sample_model = YOLO(settings.MODEL_PATH)
    return model_sample_model


def get_image_from_bytes(binary_image: bytes) -> Image:
    """Convert image from bytes to PIL RGB format
    
    Args:
        binary_image (bytes): The binary representation of the image
    
    Returns:
        PIL.Image: The image in PIL RGB format
    """
    input_image = Image.open(io.BytesIO(binary_image)).convert("RGB")
    return input_image


def get_bytes_from_image(image: Image) -> bytes:
    """
    Convert PIL image to Bytes
    
    Args:
    image (Image): A PIL image instance
    
    Returns:
    bytes : BytesIO object that contains the image in JPEG format with quality 85
    """
    return_image = io.BytesIO()
    image.save(return_image, format='JPEG', quality=85)  # save the image in JPEG format with quality 85
    return_image.seek(0)  # set the pointer to the beginning of the file
    return return_image

def transform_predict_to_df(results: list, labeles_dict: dict) -> pd.DataFrame:
    """
    Transform predict from yolov8 (torch.Tensor) to pandas DataFrame.

    Args:
        results (list): A list containing the predict output from yolov8 in the form of a torch.Tensor.
        labeles_dict (dict): A dictionary containing the labels names, where the keys are the class ids and the values are the label names.
        
    Returns:
        predict_bbox (pd.DataFrame): A DataFrame containing the bounding box coordinates, confidence scores and class labels.
    """
    # Transform the Tensor to numpy array
    predict_bbox = pd.DataFrame(results[0].to("cpu").numpy().boxes.xyxy, columns=['xmin', 'ymin', 'xmax','ymax'])
    # Add the confidence of the prediction to the DataFrame
    predict_bbox['confidence'] = results[0].to("cpu").numpy().boxes.conf
    # Add the class of the prediction to the DataFrame
    predict_bbox['class'] = (results[0].to("cpu").numpy().boxes.cls).astype(int)
    # Replace the class number with the class name from the labeles_dict
    predict_bbox['name'] = predict_bbox["class"].replace(labeles_dict)
    return predict_bbox

def get_model_predict(model: YOLO, input_image: Image, save: bool = False, image_size: int = 1248, conf: float = 0.5, augment: bool = False) -> pd.DataFrame:
    """
    Get the predictions of a model on an input image.
    
    Args:
        model (YOLO): The trained YOLO model.
        input_image (Image): The image on which the model will make predictions.
        save (bool, optional): Whether to save the image with the predictions. Defaults to False.
        image_size (int, optional): The size of the image the model will receive. Defaults to 1248.
        conf (float, optional): The confidence threshold for the predictions. Defaults to 0.5.
        augment (bool, optional): Whether to apply data augmentation on the input image. Defaults to False.
    
    Returns:
        pd.DataFrame: A DataFrame containing the predictions.
    """
    # Make predictions
    predictions = model.predict(
                        imgsz=image_size, 
                        source=input_image, 
                        conf=conf,
                        save=save, 
                        augment=augment,
                        flipud= 0.0,
                        fliplr= 0.0,
                        mosaic = 0.0,
                        )
    
    # Transform predictions to pandas dataframe
    predictions = transform_predict_to_df(predictions, model.model.names)
    return predictions


################################# BBOX Func #####################################

def add_bboxs_on_img(image: Image, predict: pd.DataFrame()) -> Image:
    """
    add a bounding box on the image

    Args:
    image (Image): input image
    predict (pd.DataFrame): predict from model

    Returns:
    Image: image whis bboxs
    """
    # Create an annotator object
    annotator = Annotator(np.array(image))

    # sort predict by xmin value
    predict = predict.sort_values(by=['xmin'], ascending=True)

    # iterate over the rows of predict dataframe
    for i, row in predict.iterrows():
        # create the text to be displayed on image
        text = f"{row['name']}: {int(row['confidence']*100)}%"
        # get the bounding box coordinates
        bbox = [row['xmin'], row['ymin'], row['xmax'], row['ymax']]
        # add the bounding box and text on the image
        annotator.box_label(bbox, text, color=colors(row['class'], True))
    # convert the annotated image to PIL image
    return Image.fromarray(annotator.result())


################################# Models #####################################


def detect_sample_model(input_image: Image) -> pd.DataFrame:
    """
    Predict from sample_model.
    Base on YoloV8

    Args:
        input_image (Image): The input image.

    Returns:
        pd.DataFrame: DataFrame containing the object location.
    """
    model = load_model()
    predict = get_model_predict(
        model=model,
        input_image=input_image,
        save=False,
        image_size=settings.IMAGE_SIZE,
        augment=settings.AUGMENT,
        conf=settings.CONFIDENCE_THRESHOLD,
    )
    return predict


################################# Neuromarketing Orchestrator #####################################

def analyze_neuromarketing(input_image: Image) -> dict:
    """
    Orquestra todas as análises de neuromarketing e consolida resultados
    
    Args:
        input_image: PIL Image
        
    Returns:
        Dicionário completo com todas as análises de neuromarketing
    """
    # Importa serviços (fazendo aqui para evitar imports circulares)
    from services.ocr import ocr_service
    from services.colors import color_service
    from services.emotion import emotion_service
    from services.saliency import saliency_service
    from services.cta import cta_service
    from services.gaze import gaze_service
    from services.pose import pose_service
    from services.depth import depth_service
    from services.symmetry import symmetry_service
    from services.lighting import lighting_service
    from services.texture import texture_service
    from services.scene import scene_service
    from services.narrative import narrative_service
    
    # Executa todas as análises
    results = {}
    
    # 1. Detecção de objetos
    predict = detect_sample_model(input_image)
    objects_list = [
        {"name": row['name'], "confidence": float(row['confidence'])}
        for _, row in predict.iterrows()
    ]
    results["objetos"] = objects_list
    results["numero_de_pessoas"] = len([obj for obj in objects_list if obj["name"] == "person"])
    
    # 2. OCR e texto
    ocr_result = ocr_service.extract_text(input_image)
    results["texto_em_imagem"] = ocr_result
    
    # 3. Análise de cores
    color_result = color_service.analyze_image_colors(input_image)
    results["cores_dominantes"] = color_result
    results["emocao_das_cores"] = {
        "paleta_emocional": color_result.get("emotion_palette", "neutral"),
        "cores": color_result.get("dominant_colors", [])
    }
    
    # 4. Expressão facial e emoções
    emotion_result = emotion_service.detect_emotions(input_image)
    results["expressao_emocional"] = {
        "faces_detectadas": emotion_result.get("faces_detected", 0),
        "emocao_dominante": emotion_result.get("scene_emotion", "neutral"),
        "confianca_media": emotion_result.get("average_confidence", 0.0),
        "detalhes": emotion_result
    }
    
    # 5. Direção do olhar
    gaze_result = gaze_service.estimate_gaze_direction(input_image)
    results["direcao_olhar"] = gaze_result
    
    # 6. Linguagem corporal e movimento
    pose_result = pose_service.analyze_body_language(input_image)
    results["postura_corporea"] = pose_result
    results["sensacao_de_movimento"] = {
        "nivel": pose_result.get("movement_sensation", "nenhum"),
        "explicacao": pose_result.get("movement_explanation", "")
    }
    
    # 7. Contraste visual
    results["contraste_local"] = {
        "contraste_medio": color_result.get("average_contrast", 0.0),
        "explicacao": "Contraste alto guia atenção e cria hierarquia visual"
    }
    
    # 8. Profundidade de campo
    depth_result = depth_service.analyze_depth_of_field(input_image)
    results["profundidade_de_campo"] = depth_result
    
    # 9. Simetria
    symmetry_result = symmetry_service.analyze_symmetry(input_image)
    results["simetria_visual"] = symmetry_result
    
    # 10. Distância e enquadramento (estimado via objetos)
    people_objects = [obj for obj in objects_list if obj["name"] == "person"]
    if people_objects:
        # Estima tipo de plano baseado no número de pessoas e confiança
        if len(people_objects) == 1 and people_objects[0]["confidence"] > 0.8:
            plano = "close_up"
            plano_meaning = "close-up transmite intimidade e conexão emocional"
        elif len(people_objects) <= 2:
            plano = "medio"
            plano_meaning = "plano médio transmite contexto e relacionamento"
        else:
            plano = "aberto"
            plano_meaning = "plano aberto transmite status e ambiente"
    else:
        plano = "indefinido"
        plano_meaning = "sem pessoas detectadas para determinar enquadramento"
    
    results["tipo_de_plano"] = {
        "plano": plano,
        "significado": plano_meaning
    }
    
    # 11. Iluminação e temperatura
    lighting_result = lighting_service.analyze_lighting(input_image)
    results["iluminacao_emocional"] = lighting_result
    
    # 12. Contexto simbólico (objetos detectados)
    simbolos = []
    simbolos_sociais = ["flag", "cross", "star", "crown", "money", "dollar"]
    for obj in objects_list:
        if any(simbolo in obj["name"].lower() for simbolo in simbolos_sociais):
            simbolos.append(obj["name"])
    
    results["simbolos_sociais"] = {
        "simbolos_detectados": simbolos,
        "explicacao": "Símbolos sociais despertam pertencimento e status" if simbolos else "Nenhum símbolo social detectado"
    }
    
    # 13. Ponto focal (atenção)
    attention_result = saliency_service.analyze_attention_distribution(input_image)
    attention_points = saliency_service.find_attention_points(input_image, n_points=5)
    results["area_de_atencao_visual"] = {
        **attention_result,
        "pontos_de_atencao": attention_points
    }
    
    # 14. Textura
    texture_result = texture_service.analyze_texture(input_image)
    results["textura_sensorial"] = texture_result
    
    # 15. Natureza vs tecnologia
    scene_result = scene_service.classify_scene(input_image)
    results["natureza_vs_tecnologia"] = scene_result
    
    # 16. Elementos de urgência/escassez
    text_segments = ocr_result.get("segments", [])
    cta_elements = cta_service.detect_cta_elements(input_image, text_segments)
    results["gatilho_escassez_visual"] = {
        "ctas_detectados": len(cta_elements) > 0,
        "elementos_cta": cta_elements,
        "explicacao": "CTAs e elementos de urgência despertam ação imediata" if cta_elements else "Nenhum elemento de urgência detectado"
    }
    
    # 17. Textos e tipografia (já em OCR)
    results["textos_e_tipografia"] = {
        "texto_completo": ocr_result.get("full_text", ""),
        "segmentos": text_segments,
        "explicacao": "Textos com verbos de ação reforçam estímulos de neuromarketing"
    }
    
    # 18. Humor e incongruência
    narrative_result = narrative_service.analyze_narrative(
        input_image, objects_list, emotion_result, ocr_result, color_result
    )
    results["efeito_surpresa_ou_ironia"] = {
        "incongruencia_detectada": narrative_result.get("incongruence_detected", False),
        "nivel_surpresa": narrative_result.get("surprise_level", "baixo"),
        "explicacao": narrative_result.get("incongruence_explanation", "")
    }
    
    # 19. Coerência narrativa
    results["historia_implicita"] = {
        "narrativa": narrative_result.get("implicit_story", "indefinido"),
        "significado": narrative_result.get("story_meaning", ""),
        "coerencia": narrative_result.get("narrative_coherence", "moderada")
    }
    
    return results