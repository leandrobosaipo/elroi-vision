####################################### IMPORT #################################
import json
import pandas as pd
from PIL import Image
from loguru import logger
import sys

from fastapi import FastAPI, File, status, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException

from io import BytesIO

from app import get_image_from_bytes
from app import detect_sample_model
from app import add_bboxs_on_img
from app import get_bytes_from_image
from schemas import DetectionResponse, HealthCheckResponse
from config import settings

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
    
    ## Modelos
    
    O serviço utiliza modelos YOLOv8 pré-treinados para detecção de objetos em tempo real.
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

