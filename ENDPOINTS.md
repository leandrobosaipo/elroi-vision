# Resumo dos Endpoints - ElRoi Vision API

## 📡 Lista Completa de Endpoints

### 1. GET `/`
- **Descrição**: Redireciona para `/docs` (documentação Swagger)
- **Método**: GET
- **Parâmetros**: Nenhum
- **Resposta**: Redirect para `/docs`
- **Incluído no Schema**: Não

### 2. GET `/healthcheck`
- **Descrição**: Verifica o status do serviço
- **Método**: GET
- **Parâmetros**: Nenhum
- **Resposta**: 
  ```json
  {
    "healthcheck": "Everything OK!"
  }
  ```
- **Status Code**: 200 OK
- **Tags**: Monitoramento
- **Uso**: Healthcheck para load balancers e monitoramento

### 3. POST `/img_object_detection_to_json`
- **Descrição**: Detecta objetos em uma imagem e retorna resultados em JSON
- **Método**: POST
- **Parâmetros**:
  - `file` (multipart/form-data, obrigatório): Arquivo de imagem
- **Resposta**:
  ```json
  {
    "detect_objects": [
      {
        "name": "person",
        "confidence": 0.95
      },
      {
        "name": "car",
        "confidence": 0.87
      }
    ],
    "detect_objects_names": "person, car"
  }
  ```
- **Status Codes**:
  - 200: Sucesso
  - 400: Erro ao processar imagem
  - 422: Erro de validação (arquivo não fornecido)
- **Tags**: Detecção
- **Content-Type**: `multipart/form-data`
- **Response Type**: `application/json`

### 4. POST `/img_object_detection_to_img`
- **Descrição**: Detecta objetos em uma imagem e retorna imagem anotada
- **Método**: POST
- **Parâmetros**:
  - `file` (multipart/form-data, obrigatório): Arquivo de imagem
- **Resposta**: Imagem JPEG com bounding boxes e labels
- **Status Codes**:
  - 200: Sucesso
  - 400: Erro ao processar imagem
  - 422: Erro de validação (arquivo não fornecido)
- **Tags**: Detecção
- **Content-Type**: `multipart/form-data`
- **Response Type**: `image/jpeg`

## 🔍 Endpoints de Documentação

### GET `/docs`
- **Descrição**: Interface Swagger UI interativa
- **Método**: GET
- **Acesso**: Navegador web
- **Funcionalidades**: Testar endpoints, ver schemas, exemplos

### GET `/redoc`
- **Descrição**: Documentação ReDoc alternativa
- **Método**: GET
- **Acesso**: Navegador web

### GET `/openapi.json`
- **Descrição**: Especificação OpenAPI em JSON
- **Método**: GET
- **Resposta**: JSON com especificação completa da API
- **Uso**: Gerar clientes, importar em ferramentas

## 📊 Resumo de Parâmetros

### Parâmetros de Query
Nenhum endpoint usa parâmetros de query no momento.

### Parâmetros de Path
Nenhum endpoint usa parâmetros de path no momento.

### Parâmetros de Body
- **`file`** (UploadFile): Usado em ambos os endpoints POST
  - Tipo: `multipart/form-data`
  - Obrigatório: Sim
  - Formatos aceitos: JPEG, PNG, WEBP, e outros formatos suportados pelo PIL

## 🔄 Variações e Configurações

### Configurações via Variáveis de Ambiente

Os endpoints de detecção são afetados pelas seguintes variáveis:

- **`CONFIDENCE_THRESHOLD`**: Controla o limiar mínimo de confiança (padrão: 0.5)
- **`IMAGE_SIZE`**: Tamanho da imagem para processamento (padrão: 640)
- **`AUGMENT`**: Habilita augmentação de dados (padrão: false)
- **`MODEL_PATH`**: Caminho do modelo YOLO usado

### Possíveis Variações Futuras

Endpoints que poderiam ser adicionados:

1. **GET `/status`**: Status detalhado do serviço (modelo carregado, memória, etc.)
2. **GET `/queue/status`**: Status de fila de processamento (se implementar processamento assíncrono)
3. **POST `/img_object_detection_batch`**: Processamento em lote de múltiplas imagens
4. **GET `/models`**: Lista modelos disponíveis
5. **POST `/img_object_detection_to_json?confidence=0.7`**: Parâmetro de confiança customizado

## 📝 Notas sobre Endpoints

### Endpoints de Status e Fila

**Status atual**: 
- ✅ Existe endpoint `/healthcheck` para verificação básica de saúde
- ❌ Não existe endpoint `/status` detalhado
- ❌ Não existe endpoint de fila (processamento é síncrono)

**Recomendações**:
- O endpoint `/healthcheck` é suficiente para monitoramento básico
- Para monitoramento avançado, considere adicionar `/status` com informações do sistema
- Para processamento assíncrono, considere implementar fila com Celery/Redis

### Processamento

- **Tipo**: Síncrono (cada requisição é processada imediatamente)
- **Timeout**: Depende da configuração do servidor (recomendado: 120s+)
- **Concorrência**: Controlada pelo número de workers (uvicorn/gunicorn)

## 🧪 Exemplos de Uso

### Exemplo 1: Healthcheck
```bash
curl http://localhost:8001/healthcheck
```

### Exemplo 2: Detecção para JSON
```bash
curl -X POST "http://localhost:8001/img_object_detection_to_json" \
     -F "file=@test_image.jpg"
```

### Exemplo 3: Detecção para Imagem
```bash
curl -X POST "http://localhost:8001/img_object_detection_to_img" \
     -F "file=@test_image.jpg" \
     --output result.jpg
```

### Exemplo 4: Python
```python
import requests

# Healthcheck
response = requests.get('http://localhost:8001/healthcheck')
print(response.json())

# Detecção
with open('test_image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/img_object_detection_to_json',
        files={'file': f}
    )
    print(response.json())
```

## 🔗 Links Úteis

- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`
- OpenAPI JSON: `http://localhost:8001/openapi.json`

