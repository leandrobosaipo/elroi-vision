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

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente (veja seção abaixo)

4. Inicie o servidor:
```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

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

### Erro CORS
- Verifique a configuração de `CORS_ORIGINS`
- Para desenvolvimento local, use `*`
- Para produção, liste domínios específicos separados por vírgula

### Porta já em uso
- Altere a porta nas variáveis de ambiente
- Ou pare o processo que está usando a porta

## 📄 Licença

MIT License

## 👥 Contato

Para dúvidas ou suporte, abra uma issue no repositório.
