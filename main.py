####################################### IMPORT #################################
import json
import pandas as pd
from PIL import Image
from loguru import logger
import sys

from fastapi import FastAPI, File, status, UploadFile, Query
from fastapi.responses import RedirectResponse
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException

from io import BytesIO

from app import get_image_from_bytes
from app import detect_sample_model
from app import add_bboxs_on_img
from app import get_bytes_from_image
from schemas import (
    DetectionResponse, HealthCheckResponse, OCRResponse, ColorAnalysisResponse,
    CaptionResponse, EmotionResponse, SaliencyResponse, CTAResponse,
    NeuromarketingReportResponse, DetectionObject
)
from config import settings

# Importar serviços de neuromarketing
from services.ocr import ocr_service
from services.colors import color_service
from services.caption import caption_service
from services.emotion import emotion_service
from services.saliency import saliency_service
from services.cta import cta_service

####################################### logger #################################

logger.remove()
logger.add(
    sys.stderr,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>",
    level=settings.LOG_LEVEL,
)
logger.add(settings.LOG_FILE, rotation=settings.LOG_ROTATION, level="DEBUG", compression="zip")

###################### FastAPI Setup #############################

# title
app = FastAPI(
    title="ElRoi Vision - Object Detection API",
    description="""
    API de detecção de objetos usando YOLOv8.
    
    ## Funcionalidades
    
    * **Detecção para JSON**: Recebe uma imagem e retorna os objetos detectados em formato JSON
    * **Detecção para Imagem**: Recebe uma imagem e retorna a imagem anotada com bounding boxes
    * **Healthcheck**: Verifica o status do serviço
    * **OCR**: Extração de texto de imagens
    * **Análise de Cores**: Identifica cores dominantes e impacto emocional
    * **Geração de Descrição**: Gera descrições automáticas de imagens
    * **Análise Emocional**: Detecta emoções em faces
    * **Análise de Atenção**: Mapa de saliência e pontos de foco
    * **Detecção de CTAs**: Identifica elementos Call-to-Action
    * **Relatório Neuromarketing**: Análise completa para análise de marketing
    
    ## Modelos
    
    O serviço utiliza modelos YOLOv8 pré-treinados para detecção de objetos em tempo real,
    além de modelos especializados para OCR, captioning e análise emocional.
    """,
    version="1.0.0",
    contact={
        "name": "ElRoi Vision",
    },
    license_info={
        "name": "MIT",
    },
)

# This function is needed if you want to allow client requests 
# from specific domains (specified in the origins argument) 
# to access resources from the FastAPI server, 
# and the client and server are hosted on different domains.
origins = settings.CORS_ORIGINS.split(",") if "," in settings.CORS_ORIGINS else [settings.CORS_ORIGINS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def save_openapi_json():
    '''This function is used to save the OpenAPI documentation 
    data of the FastAPI application to a JSON file. 
    The purpose of saving the OpenAPI documentation data is to have 
    a permanent and offline record of the API specification, 
    which can be used for documentation purposes or 
    to generate client libraries. It is not necessarily needed, 
    but can be helpful in certain scenarios.'''
    openapi_data = app.openapi()
    # Change "openapi.json" to desired filename
    with open("openapi.json", "w") as file:
        json.dump(openapi_data, file)

# redirect
@app.get("/", include_in_schema=False)
async def redirect():
    return RedirectResponse("/docs")


@app.get(
    '/healthcheck',
    status_code=status.HTTP_200_OK,
    response_model=HealthCheckResponse,
    summary="Verificar status do serviço",
    description="""
    Endpoint de healthcheck para verificar se o serviço está funcionando corretamente.
    
    Retorna um status 200 OK se o serviço estiver operacional.
    Este endpoint é útil para:
    - Monitoramento de saúde do serviço
    - Load balancers e orquestradores de containers
    - Verificação de disponibilidade antes de fazer requisições
    """,
    responses={
        200: {
            "description": "Serviço está funcionando corretamente",
            "content": {
                "application/json": {
                    "example": {
                        "healthcheck": "Everything OK!"
                    }
                }
            }
        }
    },
    tags=["Monitoramento"]
)
def perform_healthcheck():
    """
    Verifica o status do serviço.
    
    Returns:
        HealthCheckResponse: Resposta indicando que o serviço está funcionando
    """
    return {'healthcheck': 'Everything OK!'}


######################### Support Func #################################

def crop_image_by_predict(image: Image, predict: pd.DataFrame(), crop_class_name: str,) -> Image:
    """Crop an image based on the detection of a certain object in the image.
    
    Args:
        image: Image to be cropped.
        predict (pd.DataFrame): Dataframe containing the prediction results of object detection model.
        crop_class_name (str, optional): The name of the object class to crop the image by. if not provided, function returns the first object found in the image.
    
    Returns:
        Image: Cropped image or None
    """
    crop_predicts = predict[(predict['name'] == crop_class_name)]

    if crop_predicts.empty:
        raise HTTPException(status_code=400, detail=f"{crop_class_name} not found in photo")

    # if there are several detections, choose the one with more confidence
    if len(crop_predicts) > 1:
        crop_predicts = crop_predicts.sort_values(by=['confidence'], ascending=False)

    crop_bbox = crop_predicts[['xmin', 'ymin', 'xmax','ymax']].iloc[0].values
    # crop
    img_crop = image.crop(crop_bbox)
    return(img_crop)


######################### MAIN Func #################################


@app.post(
    "/img_object_detection_to_json",
    response_model=DetectionResponse,
    summary="Detecção de objetos retornando JSON",
    description="""
    Realiza detecção de objetos em uma imagem usando YOLOv8 e retorna os resultados em formato JSON.
    
    ## Parâmetros
    
    - **file**: Arquivo de imagem (suporta formatos: JPEG, PNG, WEBP, etc.)
    
    ## Resposta
    
    Retorna um JSON contendo:
    - `detect_objects`: Lista de objetos detectados com nome e confiança
    - `detect_objects_names`: String com nomes dos objetos separados por vírgula
    
    ## Exemplo de Uso
    
    ```bash
    curl -X POST "http://localhost:8001/img_object_detection_to_json" \\
         -H "accept: application/json" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@test_image.jpg"
    ```
    """,
    responses={
        200: {
            "description": "Detecção realizada com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "detect_objects": [
                            {"name": "person", "confidence": 0.95},
                            {"name": "car", "confidence": 0.87},
                            {"name": "dog", "confidence": 0.72}
                        ],
                        "detect_objects_names": "person, car, dog"
                    }
                }
            }
        },
        400: {
            "description": "Erro ao processar a imagem",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid image format"
                    }
                }
            }
        },
        422: {
            "description": "Erro de validação - arquivo não fornecido",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "file"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        }
    },
    tags=["Detecção"]
)
async def img_object_detection_to_json(
    file: UploadFile = File(
        ...,
        description="Arquivo de imagem para detecção de objetos",
        example="test_image.jpg"
    )
):
    """
    Detecta objetos em uma imagem e retorna os resultados em formato JSON.

    Args:
        file: Arquivo de imagem enviado via multipart/form-data

    Returns:
        DetectionResponse: JSON com objetos detectados e suas confianças
    """
    try:
        # Step 1: Initialize the result dictionary with None values
        result={'detect_objects': None}

        # Step 2: Convert the image file to an image object
        file_bytes = await file.read()
        input_image = get_image_from_bytes(file_bytes)

        # Step 3: Predict from model
        predict = detect_sample_model(input_image)

        # Step 4: Select detect obj return info
        # here you can choose what data to send to the result
        detect_res = predict[['name', 'confidence']]
        objects = detect_res['name'].values

        result['detect_objects_names'] = ', '.join(objects) if len(objects) > 0 else ''
        result['detect_objects'] = json.loads(detect_res.to_json(orient='records'))

        # Step 5: Logs and return
        logger.info("results: {}", result)
        return result
    except Exception as e:
        logger.error("Error processing image: {}", str(e))
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

@app.post(
    "/img_object_detection_to_img",
    summary="Detecção de objetos retornando imagem anotada",
    description="""
    Realiza detecção de objetos em uma imagem usando YOLOv8 e retorna a imagem original 
    com bounding boxes e labels desenhados.
    
    ## Parâmetros
    
    - **file**: Arquivo de imagem (suporta formatos: JPEG, PNG, WEBP, etc.)
    
    ## Resposta
    
    Retorna a imagem processada em formato JPEG com:
    - Bounding boxes desenhados ao redor dos objetos detectados
    - Labels com nome da classe e porcentagem de confiança
    
    ## Exemplo de Uso
    
    ```bash
    curl -X POST "http://localhost:8001/img_object_detection_to_img" \\
         -H "accept: image/jpeg" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@test_image.jpg" \\
         --output result.jpg
    ```
    
    Ou usando Python:
    ```python
    import requests
    
    with open('test_image.jpg', 'rb') as f:
        response = requests.post(
            'http://localhost:8001/img_object_detection_to_img',
            files={'file': f}
        )
    
    with open('result.jpg', 'wb') as f:
        f.write(response.content)
    ```
    """,
    responses={
        200: {
            "description": "Imagem processada com sucesso",
            "content": {
                "image/jpeg": {
                    "example": "Imagem JPEG com bounding boxes desenhados"
                }
            }
        },
        400: {
            "description": "Erro ao processar a imagem",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid image format"
                    }
                }
            }
        },
        422: {
            "description": "Erro de validação - arquivo não fornecido",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "file"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        }
    },
    tags=["Detecção"]
)
async def img_object_detection_to_img(
    file: UploadFile = File(
        ...,
        description="Arquivo de imagem para detecção de objetos",
        example="test_image.jpg"
    )
):
    """
    Detecta objetos em uma imagem e retorna a imagem anotada com bounding boxes.

    Args:
        file: Arquivo de imagem enviado via multipart/form-data

    Returns:
        StreamingResponse: Imagem JPEG com bounding boxes e labels desenhados
    """
    try:
        # get image from bytes
        file_bytes = await file.read()
        input_image = get_image_from_bytes(file_bytes)

        # model predict
        predict = detect_sample_model(input_image)

        # add bbox on image
        final_image = add_bboxs_on_img(image = input_image, predict = predict)

        # return image in bytes format
        return StreamingResponse(content=get_bytes_from_image(final_image), media_type="image/jpeg")
    except Exception as e:
        logger.error("Error processing image: {}", str(e))
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")


######################### Neuromarketing Endpoints #################################


@app.post(
    "/img_text_extraction",
    response_model=OCRResponse,
    summary="Extração de texto (OCR)",
    description="""
    Extrai texto de uma imagem usando OCR (Optical Character Recognition).
    
    ## Parâmetros
    
    - **file**: Arquivo de imagem (JPEG, PNG, WEBP, etc.)
    - **method** (opcional): Método de OCR - "easyocr" ou "tesseract" (padrão: "easyocr")
    
    ## Resposta
    
    Retorna texto extraído com coordenadas de cada segmento detectado.
    
    ## Exemplo de Uso
    
    ```bash
    curl -X POST "http://localhost:8001/img_text_extraction" \\
         -H "accept: application/json" \\
         -F "file=@test_image.jpg" \\
         -F "method=easyocr"
    ```
    """,
    responses={
        200: {
            "description": "Texto extraído com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "full_text": "Frete Grátis Compre Agora",
                        "segments": [
                            {
                                "text": "Frete Grátis",
                                "confidence": 0.95,
                                "bbox": {"xmin": 100, "ymin": 50, "xmax": 300, "ymax": 80}
                            }
                        ],
                        "total_segments": 1,
                        "method_used": "easyocr"
                    }
                }
            }
        }
    },
    tags=["Neuromarketing"]
)
async def img_text_extraction(
    file: UploadFile = File(..., description="Arquivo de imagem para extração de texto", example="test_image.jpg"),
    method: str = Query("easyocr", description="Método de OCR: 'easyocr' ou 'tesseract'", example="easyocr")
):
    """Extrai texto de uma imagem usando OCR"""
    try:
        file_bytes = await file.read()
        input_image = get_image_from_bytes(file_bytes)
        
        result = ocr_service.extract_text(input_image, method=method)
        
        return result
    except Exception as e:
        logger.error("Error extracting text: {}", str(e))
        raise HTTPException(status_code=400, detail=f"Error extracting text: {str(e)}")


@app.post(
    "/img_color_analysis",
    response_model=ColorAnalysisResponse,
    summary="Análise de cores",
    description="""
    Analisa cores dominantes e impacto emocional de uma imagem.
    
    ## Parâmetros
    
    - **file**: Arquivo de imagem
    - **n_colors** (opcional): Número de cores dominantes a extrair (padrão: 5)
    
    ## Resposta
    
    Retorna cores dominantes com porcentagem, tags emocionais e análise de contraste.
    
    ## Exemplo de Uso
    
    ```bash
    curl -X POST "http://localhost:8001/img_color_analysis" \\
         -H "accept: application/json" \\
         -F "file=@test_image.jpg" \\
         -F "n_colors=5"
    ```
    """,
    tags=["Neuromarketing"]
)
async def img_color_analysis(
    file: UploadFile = File(..., description="Arquivo de imagem para análise de cores", example="test_image.jpg"),
    n_colors: int = Query(5, description="Número de cores dominantes a extrair", ge=1, le=10, example=5)
):
    """Analisa cores dominantes e impacto emocional"""
    try:
        file_bytes = await file.read()
        input_image = get_image_from_bytes(file_bytes)
        
        result = color_service.analyze_image_colors(input_image, n_colors=n_colors)
        
        return result
    except Exception as e:
        logger.error("Error analyzing colors: {}", str(e))
        raise HTTPException(status_code=400, detail=f"Error analyzing colors: {str(e)}")


@app.post(
    "/img_caption",
    response_model=CaptionResponse,
    summary="Geração de descrição",
    description="""
    Gera descrição automática da imagem usando modelos de captioning.
    
    ## Parâmetros
    
    - **file**: Arquivo de imagem
    - **max_length** (opcional): Comprimento máximo da descrição em palavras (padrão: 50)
    
    ## Resposta
    
    Retorna descrição textual da imagem.
    
    ## Exemplo de Uso
    
    ```bash
    curl -X POST "http://localhost:8001/img_caption" \\
         -H "accept: application/json" \\
         -F "file=@test_image.jpg"
    ```
    """,
    tags=["Neuromarketing"]
)
async def img_caption(
    file: UploadFile = File(..., description="Arquivo de imagem para geração de descrição", example="test_image.jpg"),
    max_length: int = Query(50, description="Comprimento máximo da descrição em palavras", ge=10, le=100, example=50)
):
    """Gera descrição automática da imagem"""
    try:
        file_bytes = await file.read()
        input_image = get_image_from_bytes(file_bytes)
        
        result = caption_service.generate_caption(input_image, max_length=max_length)
        
        return result
    except Exception as e:
        logger.error("Error generating caption: {}", str(e))
        raise HTTPException(status_code=400, detail=f"Error generating caption: {str(e)}")


@app.post(
    "/img_emotion_detection",
    response_model=EmotionResponse,
    summary="Detecção de emoções",
    description="""
    Detecta emoções em faces presentes na imagem.
    
    ## Parâmetros
    
    - **file**: Arquivo de imagem
    
    ## Resposta
    
    Retorna emoções detectadas em cada face e emoção geral da cena.
    
    ## Exemplo de Uso
    
    ```bash
    curl -X POST "http://localhost:8001/img_emotion_detection" \\
         -H "accept: application/json" \\
         -F "file=@test_image.jpg"
    ```
    """,
    tags=["Neuromarketing"]
)
async def img_emotion_detection(
    file: UploadFile = File(..., description="Arquivo de imagem para detecção de emoções", example="test_image.jpg")
):
    """Detecta emoções em faces"""
    try:
        file_bytes = await file.read()
        input_image = get_image_from_bytes(file_bytes)
        
        result = emotion_service.detect_emotions(input_image)
        
        return result
    except Exception as e:
        logger.error("Error detecting emotions: {}", str(e))
        raise HTTPException(status_code=400, detail=f"Error detecting emotions: {str(e)}")


@app.post(
    "/img_attention_analysis",
    response_model=SaliencyResponse,
    summary="Análise de atenção visual",
    description="""
    Analisa mapa de saliência e pontos de atenção visual na imagem.
    
    ## Parâmetros
    
    - **file**: Arquivo de imagem
    - **n_points** (opcional): Número de pontos de atenção a retornar (padrão: 5)
    
    ## Resposta
    
    Retorna mapa de atenção, centro de foco e alinhamento com regra dos terços.
    
    ## Exemplo de Uso
    
    ```bash
    curl -X POST "http://localhost:8001/img_attention_analysis" \\
         -H "accept: application/json" \\
         -F "file=@test_image.jpg"
    ```
    """,
    tags=["Neuromarketing"]
)
async def img_attention_analysis(
    file: UploadFile = File(..., description="Arquivo de imagem para análise de atenção", example="test_image.jpg"),
    n_points: int = Query(5, description="Número de pontos de atenção a retornar", ge=1, le=20, example=5)
):
    """Analisa atenção visual e saliência"""
    try:
        file_bytes = await file.read()
        input_image = get_image_from_bytes(file_bytes)
        
        attention_dist = saliency_service.analyze_attention_distribution(input_image)
        attention_points = saliency_service.find_attention_points(input_image, n_points=n_points)
        
        attention_dist["attention_points"] = attention_points
        
        return attention_dist
    except Exception as e:
        logger.error("Error analyzing attention: {}", str(e))
        raise HTTPException(status_code=400, detail=f"Error analyzing attention: {str(e)}")


@app.post(
    "/img_cta_detection",
    response_model=CTAResponse,
    summary="Detecção de CTAs",
    description="""
    Detecta elementos Call-to-Action (CTAs) na imagem baseado em texto e posição.
    
    ## Parâmetros
    
    - **file**: Arquivo de imagem
    
    ## Resposta
    
    Retorna CTAs detectados com análise de efetividade.
    
    ## Exemplo de Uso
    
    ```bash
    curl -X POST "http://localhost:8001/img_cta_detection" \\
         -H "accept: application/json" \\
         -F "file=@test_image.jpg"
    ```
    """,
    tags=["Neuromarketing"]
)
async def img_cta_detection(
    file: UploadFile = File(..., description="Arquivo de imagem para detecção de CTAs", example="test_image.jpg")
):
    """Detecta elementos Call-to-Action"""
    try:
        file_bytes = await file.read()
        input_image = get_image_from_bytes(file_bytes)
        
        # Extrai texto primeiro
        ocr_result = ocr_service.extract_text(input_image)
        text_segments = ocr_result.get("segments", [])
        
        # Detecta CTAs
        cta_elements = cta_service.detect_cta_elements(input_image, text_segments)
        
        # Analisa cores para calcular efetividade
        color_result = color_service.analyze_image_colors(input_image)
        effectiveness = cta_service.analyze_cta_effectiveness(cta_elements, color_result)
        
        return {
            "cta_present": len(cta_elements) > 0,
            "cta_count": len(cta_elements),
            "cta_elements": cta_elements,
            **effectiveness
        }
    except Exception as e:
        logger.error("Error detecting CTAs: {}", str(e))
        raise HTTPException(status_code=400, detail=f"Error detecting CTAs: {str(e)}")


@app.post(
    "/img_neuromarketing_report",
    response_model=NeuromarketingReportResponse,
    summary="Relatório completo de neuromarketing",
    description="""
    Gera relatório completo de análise neuromarketing combinando todas as análises disponíveis.
    
    ## Parâmetros
    
    - **file**: Arquivo de imagem
    
    ## Resposta
    
    Retorna relatório completo com:
    - Objetos detectados
    - Texto extraído (OCR)
    - Análise de cores
    - Descrição gerada
    - Análise emocional
    - Análise de atenção
    - Detecção de CTAs
    - Resumo executivo
    
    ## Exemplo de Uso
    
    ```bash
    curl -X POST "http://localhost:8001/img_neuromarketing_report" \\
         -H "accept: application/json" \\
         -F "file=@test_image.jpg"
    ```
    """,
    tags=["Neuromarketing"]
)
async def img_neuromarketing_report(
    file: UploadFile = File(..., description="Arquivo de imagem para análise completa", example="test_image.jpg")
):
    """Gera relatório completo de neuromarketing"""
    try:
        file_bytes = await file.read()
        input_image = get_image_from_bytes(file_bytes)
        
        # Executa todas as análises
        # 1. Detecção de objetos
        predict = detect_sample_model(input_image)
        detect_res = predict[['name', 'confidence']]
        objects = [
            DetectionObject(name=row['name'], confidence=float(row['confidence']))
            for _, row in detect_res.iterrows()
        ]
        
        # 2. OCR
        ocr_result = ocr_service.extract_text(input_image)
        
        # 3. Análise de cores
        color_result = color_service.analyze_image_colors(input_image)
        
        # 4. Caption
        caption_result = caption_service.generate_caption(input_image)
        
        # 5. Emoções
        emotion_result = emotion_service.detect_emotions(input_image)
        emotional_impact = emotion_service.analyze_emotional_impact(input_image, emotion_result)
        
        # 6. Atenção
        attention_dist = saliency_service.analyze_attention_distribution(input_image)
        attention_points = saliency_service.find_attention_points(input_image, n_points=5)
        attention_dist["attention_points"] = attention_points
        attention_dist.setdefault("primary_focus_zone", "unknown")
        
        # 7. CTAs
        text_segments = ocr_result.get("segments", [])
        cta_elements = cta_service.detect_cta_elements(input_image, text_segments)
        cta_effectiveness = cta_service.analyze_cta_effectiveness(cta_elements, color_result)
        cta_result = {
            "cta_present": len(cta_elements) > 0,
            "cta_count": len(cta_elements),
            "cta_elements": cta_elements,
            "effectiveness_score": cta_effectiveness.get("effectiveness_score", 0.0),
            "recommendations": cta_effectiveness.get("recommendations", []),
        }
        
        # 8. Resumo executivo
        summary = {
            "total_objects": len(objects),
            "text_present": len(text_segments) > 0,
            "faces_detected": emotion_result.get("faces_detected", 0),
            "scene_emotion": emotion_result.get("scene_emotion", "neutral"),
            "emotional_impact": emotional_impact.get("emotional_impact", "neutral-low"),
            "attention_score": attention_dist.get("attention_score", 0.0),
            "cta_present": cta_result.get("cta_present", False),
            "cta_effectiveness": cta_result.get("effectiveness_score", 0.0),
            "color_palette": color_result.get("emotion_palette", "neutral"),
            "recommendations": []
        }
        
        # Adiciona recomendações
        if summary["attention_score"] < 0.5:
            summary["recommendations"].append("Considere aumentar elementos que atraiam atenção visual")
        
        if not summary["cta_present"]:
            summary["recommendations"].append("Adicione um Call-to-Action claro e visível")
        
        if summary["faces_detected"] == 0:
            summary["recommendations"].append("Considere adicionar faces humanas para maior conexão emocional")
        
        if summary["emotional_impact"] == "negative":
            summary["recommendations"].append("Ajuste elementos visuais para transmitir emoções mais positivas")
        
        return {
            "objects": objects,
            "text": ocr_result,
            "colors": color_result,
            "caption": caption_result,
            "emotions": emotion_result,
            "attention": attention_dist,
            "cta": cta_result,
            "summary": summary
        }
    except Exception as e:
        logger.error("Error generating neuromarketing report: {}", str(e))
        raise HTTPException(status_code=400, detail=f"Error generating report: {str(e)}")

