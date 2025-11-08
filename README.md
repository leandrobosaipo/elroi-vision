# ElRoi Vision - Object Detection API

API de detecção de objetos usando YOLOv8 e FastAPI. Esta API permite detectar objetos em imagens e retornar os resultados em formato JSON ou como imagem anotada com bounding boxes.

## 📋 Índice

- [Funcionalidades](#funcionalidades)
- [Endpoints](#endpoints)
- [Instalação e Configuração](#instalação-e-configuração)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Uso da API](#uso-da-api)
- [Deploy no EasyPanel](#deploy-no-easypanel)
- [Documentação Swagger](#documentação-swagger)
- [Testes](#testes)

## 🚀 Funcionalidades

- **Detecção de Objetos**: Detecta objetos em imagens usando modelos YOLOv8 pré-treinados
- **Resposta em JSON**: Retorna objetos detectados com nome e confiança
- **Resposta em Imagem**: Retorna imagem anotada com bounding boxes e labels
- **OCR**: Extração de texto de imagens usando EasyOCR ou Tesseract
- **Análise de Cores**: Identifica cores dominantes e impacto emocional
- **Geração de Descrição**: Gera descrições automáticas de imagens usando BLIP
- **Análise Emocional**: Detecta emoções em faces usando DeepFace
- **Análise de Atenção**: Mapa de saliência e pontos de foco visual
- **Detecção de CTAs**: Identifica elementos Call-to-Action
- **Relatório Neuromarketing**: Análise completa combinando todas as funcionalidades
- **Healthcheck**: Endpoint para verificar status do serviço
- **Documentação Swagger**: Documentação interativa automática

## 📡 Endpoints

### 1. `GET /healthcheck`

Verifica o status do serviço.

**Resposta:**
```json
{
  "healthcheck": "Everything OK!"
}
```

**Exemplo:**
```bash
curl http://localhost:8001/healthcheck
```

### 2. `POST /img_object_detection_to_json`

Detecta objetos em uma imagem e retorna os resultados em formato JSON.

**Parâmetros:**
- `file` (multipart/form-data): Arquivo de imagem (JPEG, PNG, WEBP, etc.)

**Resposta:**
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

**Exemplo com curl:**
```bash
curl -X POST "http://localhost:8001/img_object_detection_to_json" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@test_image.jpg"
```

**Exemplo com Python:**
```python
import requests

with open('test_image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/img_object_detection_to_json',
        files={'file': f}
    )

data = response.json()     
print(data)
```

### 3. `POST /img_object_detection_to_img`

Detecta objetos em uma imagem e retorna a imagem anotada com bounding boxes.

**Parâmetros:**
- `file` (multipart/form-data): Arquivo de imagem (JPEG, PNG, WEBP, etc.)

**Resposta:**
- Imagem JPEG com bounding boxes e labels desenhados

**Exemplo com curl:**
```bash
curl -X POST "http://localhost:8001/img_object_detection_to_img" \
     -H "accept: image/jpeg" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@test_image.jpg" \
     --output result.jpg
```

**Exemplo com Python:**
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

### 4. `POST /img_text_extraction`

Extrai texto de uma imagem usando OCR (Optical Character Recognition).

**Parâmetros:**
- `file` (multipart/form-data): Arquivo de imagem
- `method` (query, opcional): Método de OCR - "easyocr" ou "tesseract" (padrão: "easyocr")

**Resposta:**
```json
{
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
```

**Exemplo:**
```bash
curl -X POST "http://localhost:8001/img_text_extraction?method=easyocr" \
     -F "file=@test_image.jpg"
```

### 5. `POST /img_color_analysis`

Analisa cores dominantes e impacto emocional de uma imagem.

**Parâmetros:**
- `file` (multipart/form-data): Arquivo de imagem
- `n_colors` (query, opcional): Número de cores dominantes (padrão: 5, máximo: 10)

**Resposta:**
```json
{
  "dominant_colors": [
    {
      "rgb": [255, 100, 50],
      "hex": "#FF6432",
      "percentage": 35.5,
      "emotion_tag": "warm-energetic"
    }
  ],
  "average_contrast": 4.8,
  "emotion_palette": "warm-energetic",
  "color_count": 5
}
```

**Exemplo:**
```bash
curl -X POST "http://localhost:8001/img_color_analysis?n_colors=5" \
     -F "file=@test_image.jpg"
```

### 6. `POST /img_caption`

Gera descrição automática da imagem usando modelos de captioning.

**Parâmetros:**
- `file` (multipart/form-data): Arquivo de imagem
- `max_length` (query, opcional): Comprimento máximo da descrição em palavras (padrão: 50)

**Resposta:**
```json
{
  "caption": "A woman smiling while holding a cosmetic product",
  "method": "blip",
  "confidence": 0.85,
  "length": 8
}
```

**Exemplo:**
```bash
curl -X POST "http://localhost:8001/img_caption?max_length=50" \
     -F "file=@test_image.jpg"
```

### 7. `POST /img_emotion_detection`

Detecta emoções em faces presentes na imagem.

**Parâmetros:**
- `file` (multipart/form-data): Arquivo de imagem

**Resposta:**
```json
{
  "faces_detected": 1,
  "emotions": [
    {
      "face_id": 1,
      "dominant_emotion": "happy",
      "dominant_confidence": 0.92,
      "bbox": {}
    }
  ],
  "scene_emotion": "happy",
  "average_confidence": 0.88,
  "method": "deepface"
}
```

**Exemplo:**
```bash
curl -X POST "http://localhost:8001/img_emotion_detection" \
     -F "file=@test_image.jpg"
```

### 8. `POST /img_attention_analysis`

Analisa mapa de saliência e pontos de atenção visual na imagem.

**Parâmetros:**
- `file` (multipart/form-data): Arquivo de imagem
- `n_points` (query, opcional): Número de pontos de atenção (padrão: 5, máximo: 20)

**Resposta:**
```json
{
  "attention_score": 0.72,
  "focus_center": {
    "x": 320,
    "y": 240,
    "normalized_x": 0.5,
    "normalized_y": 0.5
  },
  "rule_of_thirds_alignment": "aligned",
  "primary_focus_zone": "aligned-0.33-0.33",
  "attention_points": [...]
}
```

**Exemplo:**
```bash
curl -X POST "http://localhost:8001/img_attention_analysis?n_points=5" \
     -F "file=@test_image.jpg"
```

### 9. `POST /img_cta_detection`

Detecta elementos Call-to-Action (CTAs) na imagem baseado em texto e posição.

**Parâmetros:**
- `file` (multipart/form-data): Arquivo de imagem

**Resposta:**
```json
{
  "cta_present": true,
  "cta_count": 1,
  "cta_elements": [
    {
      "text": "Compre Agora",
      "keywords": ["compre", "agora"],
      "bbox": {},
      "is_strategic_position": true,
      "relative_size": 2.5,
      "confidence": 0.95
    }
  ],
  "effectiveness_score": 0.75,
  "recommendations": ["CTAs bem posicionados"]
}
```

**Exemplo:**
```bash
curl -X POST "http://localhost:8001/img_cta_detection" \
     -F "file=@test_image.jpg"
```

### 10. `POST /img_neuromarketing_report`

Gera relatório completo de análise neuromarketing combinando todas as análises disponíveis.

**Parâmetros:**
- `file` (multipart/form-data): Arquivo de imagem

**Resposta:**
```json
{
  "objects": [...],
  "text": {...},
  "colors": {...},
  "caption": {...},
  "emotions": {...},
  "attention": {...},
  "cta": {...},
  "summary": {
    "total_objects": 3,
    "text_present": true,
    "faces_detected": 1,
    "scene_emotion": "happy",
    "emotional_impact": "positive-high",
    "attention_score": 0.72,
    "cta_present": true,
    "cta_effectiveness": 0.75,
    "color_palette": "warm-energetic",
    "recommendations": [...]
  }
}
```

**Exemplo:**
```bash
curl -X POST "http://localhost:8001/img_neuromarketing_report" \
     -F "file=@test_image.jpg"
```

#### `/analisar_imagem_neuromarketing` - Análise Completa de Neuromarketing

Endpoint principal para análise completa de neuromarketing com todos os 20 parâmetros em português:

```bash
curl -X POST "http://localhost:8001/analisar_imagem_neuromarketing" \
     -F "file=@test_image.jpg"
```

Retorna análise completa incluindo:
- Expressão facial e emoções
- Direção do olhar
- Paleta de cores e impacto emocional
- Contraste visual
- Profundidade de campo
- Sensação de movimento
- Simetria visual
- Tipo de plano (close-up, médio, aberto)
- Iluminação e temperatura de cor
- Símbolos sociais
- Proximidade social
- Ponto focal de atenção
- Linguagem corporal
- Coerência narrativa
- Gatilhos de escassez
- Textos e tipografia
- Humor e incongruência
- Textura sensorial
- Ambiente (natural vs artificial)

## 🛠 Instalação e Configuração

### Pré-requisitos

- Python 3.10 ou superior
- pip

### Instalação Local

1. Clone o repositório:
```bash
git clone https://github.com/leandrobosaipo/elroi-vision.git
cd elroi-vision
```

2. **IMPORTANTE**: Instale as dependências antes de iniciar o servidor:
```bash
pip install -r requirements.txt
```

**Nota sobre dependências opcionais**: Alguns serviços de neuromarketing requerem bibliotecas adicionais que podem ser instaladas separadamente:

- **OCR**: `easyocr` ou `pytesseract` (requer Tesseract instalado no sistema)
- **Caption**: `transformers` e `torch` (para BLIP)
- **Emoções**: `deepface` (requer TensorFlow)
- **Atenção**: `opencv-python-headless` e `scipy`
- **Gaze/Pose**: `mediapipe` (para análise de olhar e linguagem corporal)
- **Textura**: `scikit-image` (para análise de textura avançada)
- **Cena**: `torchvision` (para classificação de ambiente)

Se algum serviço não estiver disponível, o endpoint retornará uma mensagem informativa. Os serviços básicos (detecção de objetos e análise de cores) funcionam sem dependências adicionais.

3. Configure as variáveis de ambiente (veja seção abaixo)

4. Inicie o servidor:
```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

**Troubleshooting**: Se encontrar o erro `ModuleNotFoundError: No module named 'ultralytics'`, execute novamente `pip install -r requirements.txt` para garantir que todas as dependências estão instaladas.

### Instalação com Docker

1. Construa e inicie o container:
```bash
docker-compose up
```

O servidor estará disponível em `http://localhost:8001`

## ⚙️ Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Configurações do Modelo YOLO
MODEL_PATH=./models/sample_model/yolov8n.pt

# Configurações de Detecção
CONFIDENCE_THRESHOLD=0.5
IMAGE_SIZE=640
AUGMENT=false

# Configurações do Servidor
HOST=0.0.0.0
PORT=8001
RELOAD=false

# CORS - Use * para permitir todas as origens ou liste separado por vírgula
# Exemplo: http://localhost:3000,https://example.com
CORS_ORIGINS=*

# Logging
LOG_LEVEL=INFO
LOG_FILE=log.log
LOG_ROTATION=1 MB

# Ambiente (development, staging, production)
ENVIRONMENT=production
```

### Descrição das Variáveis

- **MODEL_PATH**: Caminho para o arquivo do modelo YOLO (.pt)
- **CONFIDENCE_THRESHOLD**: Limiar de confiança para detecções (0.0 a 1.0)
- **IMAGE_SIZE**: Tamanho da imagem para processamento (padrão: 640)
- **AUGMENT**: Habilita aumento de dados (true/false)
- **HOST**: Endereço IP do servidor
- **PORT**: Porta do servidor
- **RELOAD**: Habilita reload automático em desenvolvimento (true/false)
- **CORS_ORIGINS**: Origens permitidas para CORS (* para todas)
- **LOG_LEVEL**: Nível de log (DEBUG, INFO, WARNING, ERROR)
- **LOG_FILE**: Arquivo de log
- **LOG_ROTATION**: Tamanho máximo do arquivo de log antes de rotacionar
- **ENVIRONMENT**: Ambiente de execução

## 📚 Documentação Swagger

A documentação interativa da API está disponível em:

- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`
- **OpenAPI JSON**: `http://localhost:8001/openapi.json`

A documentação inclui:
- Descrição detalhada de cada endpoint
- Exemplos de requisições e respostas
- Schemas de validação
- Códigos de erro possíveis
- Interface interativa para testar os endpoints

## 🚢 Deploy no EasyPanel

### Pré-requisitos

- Conta no EasyPanel
- Repositório Git configurado
- Modelo YOLO disponível

### Passo a Passo

1. **Criar Nova Aplicação**
   - Acesse o painel do EasyPanel
   - Clique em "New App"
   - Selecione "Git Repository"
   - Conecte seu repositório GitHub/GitLab

2. **Configurar Build**
   - **Build Command**: Deixe vazio (usará Dockerfile)
   - **Dockerfile**: O projeto já inclui um Dockerfile
   - **Build Context**: `/`

3. **Configurar Variáveis de Ambiente**
   
   No EasyPanel, vá em "Environment Variables" e adicione:

   ```
   MODEL_PATH=/app/models/sample_model/yolov8n.pt
   CONFIDENCE_THRESHOLD=0.5
   IMAGE_SIZE=640
   AUGMENT=false
   HOST=0.0.0.0
   PORT=8001
   CORS_ORIGINS=*
   LOG_LEVEL=INFO
   ENVIRONMENT=production
   ```

4. **Configurar Storage/Volumes**
   
   Se o modelo não estiver no repositório, configure um volume:
   - **Volume Path**: `/app/models`
   - **Mount Path**: `/app/models`
   - Faça upload do modelo YOLO para este volume

5. **Configurar Porta**
   - **Port**: `8001`
   - **Protocol**: `HTTP`

6. **Configurar Healthcheck**
   - **Healthcheck Path**: `/healthcheck`
   - **Healthcheck Interval**: `30s`
   - **Healthcheck Timeout**: `10s`

7. **Deploy**
   - Clique em "Deploy"
   - Aguarde o build e deploy completarem
   - Acesse a URL fornecida pelo EasyPanel

### Comandos de Deploy Alternativos

Se preferir usar comandos customizados:

**Start Command:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

**Ou com Gunicorn:**
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

### Verificação Pós-Deploy

1. Acesse `https://seu-dominio.com/healthcheck` - deve retornar `{"healthcheck": "Everything OK!"}`
2. Acesse `https://seu-dominio.com/docs` - deve abrir a documentação Swagger
3. Teste um endpoint de detecção com uma imagem

## 🧪 Testes

Execute os testes com:

```bash
pytest -v --disable-warnings
```

Para executar com cobertura:

```bash
pytest -v --cov=. --cov-report=html
```

## 📁 Estrutura do Projeto

```
elroi-vision/
├── app.py                 # Funções de processamento YOLO
├── main.py                # Endpoints FastAPI
├── schemas.py             # Schemas Pydantic para validação
├── config.py              # Configurações e variáveis de ambiente
├── requirements.txt       # Dependências Python
├── Dockerfile             # Configuração Docker
├── docker-compose.yaml    # Configuração Docker Compose
├── models/                # Modelos YOLO
│   └── sample_model/
│       └── yolov8n.pt
└── tests/                 # Testes automatizados
    ├── test_app.py
    └── test_main.py
```

## 📝 Notas Importantes

- O modelo YOLO precisa estar presente no caminho especificado em `MODEL_PATH`
- Para produção, configure `CORS_ORIGINS` com domínios específicos ao invés de `*`
- O processamento de imagens pode consumir bastante memória - ajuste os workers conforme necessário
- Logs são salvos em `log.log` por padrão

## 🔧 Troubleshooting

### Erro ao carregar modelo
- Verifique se o arquivo do modelo existe no caminho especificado
- Confirme que `MODEL_PATH` está correto nas variáveis de ambiente
- **PyTorch 2.6+**: Se encontrar erro "Weights only load failed", o código já está configurado para lidar com isso automaticamente usando um monkey patch que permite carregar modelos YOLO confiáveis

### Erro CORS
- Verifique a configuração de `CORS_ORIGINS`
- Para desenvolvimento local, use `*`
- Para produção, liste domínios específicos separados por vírgula

### Porta já em uso
- Altere a porta nas variáveis de ambiente
- Ou pare o processo que está usando a porta

### ModuleNotFoundError
- Execute `pip install -r requirements.txt` para instalar todas as dependências
- Verifique se está usando Python 3.10 ou superior
- Certifique-se de que está no ambiente virtual correto (se estiver usando um)

## 📄 Licença

MIT License

## 👥 Contato

Para dúvidas ou suporte, abra uma issue no repositório.
