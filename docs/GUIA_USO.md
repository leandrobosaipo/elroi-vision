# Guia Completo de Uso - ElRoi Vision API

## 📚 Índice

1. [Introdução](#introdução)
2. [Instalação e Configuração](#instalação-e-configuração)
3. [Como Iniciar o Servidor](#como-iniciar-o-servidor)
4. [Como Usar a API](#como-usar-a-api)
5. [Endpoints Disponíveis](#endpoints-disponíveis)
6. [Exemplos Práticos](#exemplos-práticos)
7. [Troubleshooting](#troubleshooting)

---

## Introdução

A **ElRoi Vision API** é uma ferramenta que analisa imagens usando inteligência artificial. Ela pode:

- Detectar objetos em imagens (pessoas, carros, animais, etc.)
- Extrair texto de imagens
- Analisar cores e impacto emocional
- Detectar emoções em faces
- Gerar descrições automáticas de imagens
- Fazer análises completas de neuromarketing

**Não é necessário conhecimento técnico avançado** para usar esta API. Este guia vai te ensinar tudo passo a passo.

---

## Instalação e Configuração

### Pré-requisitos

Antes de começar, você precisa ter instalado:

- **Python 3.10 ou superior** ([Download aqui](https://www.python.org/downloads/))
- **Git** ([Download aqui](https://git-scm.com/downloads))

### Passo 1: Baixar o Projeto

Abra o terminal (ou Prompt de Comando no Windows) e execute:

```bash
git clone https://github.com/leandrobosaipo/elroi-vision.git
cd elroi-vision
```

### Passo 2: Instalar as Dependências

Execute o comando abaixo para instalar todas as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

**⏱️ Tempo estimado:** 5-10 minutos (depende da velocidade da sua internet)

**💡 Dica:** Se você tiver problemas de permissão, use:
- Windows: `pip install -r requirements.txt`
- Mac/Linux: `pip3 install -r requirements.txt` ou `sudo pip install -r requirements.txt`

### Passo 3: Verificar se Está Tudo OK

Execute este comando para verificar se a instalação funcionou:

```bash
python -c "from main import app; print('✅ Tudo instalado corretamente!')"
```

Se aparecer a mensagem de sucesso, você está pronto para continuar!

---

## Como Iniciar o Servidor

### Opção 1: Modo Desenvolvimento (Recomendado para Testes)

Execute este comando no terminal:

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

**O que significa:**
- `--host 0.0.0.0` = Permite acesso de qualquer lugar na sua rede
- `--port 8001` = A API estará disponível na porta 8001
- `--reload` = Recarrega automaticamente quando você faz mudanças no código

**Você verá uma mensagem assim:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**✅ Sucesso!** A API está rodando. Mantenha este terminal aberto.

### Opção 2: Modo Produção (Para Uso Contínuo)

Se você quer deixar o servidor rodando sem o modo de desenvolvimento:

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

**O que significa:**
- `--workers 4` = Usa 4 processos para atender múltiplas requisições ao mesmo tempo

### Como Parar o Servidor

Pressione `CTRL + C` no terminal onde o servidor está rodando.

---

## Como Usar a API

### Acessando a Documentação Interativa

A forma mais fácil de usar a API é através da interface web:

1. Abra seu navegador (Chrome, Firefox, Safari, etc.)
2. Acesse: `http://localhost:8001/docs`
3. Você verá uma página com todos os endpoints disponíveis

**Esta interface permite:**
- Ver todos os endpoints disponíveis
- Testar cada endpoint diretamente no navegador
- Ver exemplos de requisições e respostas
- Entender o que cada endpoint faz

### Testando se a API Está Funcionando

Antes de usar os endpoints complexos, teste o healthcheck:

1. No navegador, acesse: `http://localhost:8001/healthcheck`
2. Você deve ver: `{"healthcheck": "Everything OK!"}`

Se aparecer essa mensagem, a API está funcionando perfeitamente!

---

## Endpoints Disponíveis

### 1. Healthcheck - Verificar Status do Servidor

**O que faz:** Verifica se o servidor está funcionando.

**Como usar:**
- **Navegador:** Acesse `http://localhost:8001/healthcheck`
- **cURL:**
  ```bash
  curl http://localhost:8001/healthcheck
  ```

**Resposta esperada:**
```json
{
  "healthcheck": "Everything OK!"
}
```

---

### 2. Detecção de Objetos (Retorna JSON)

**O que faz:** Analisa uma imagem e retorna uma lista de objetos detectados (pessoas, carros, animais, etc.) em formato JSON.

**Como usar:**

**Opção A - Interface Web (Mais Fácil):**
1. Acesse `http://localhost:8001/docs`
2. Clique em `POST /img_object_detection_to_json`
3. Clique em "Try it out"
4. Clique em "Choose File" e selecione uma imagem
5. Clique em "Execute"
6. Veja o resultado abaixo

**Opção B - cURL (Terminal):**
```bash
curl -X POST "http://localhost:8001/img_object_detection_to_json" \
     -F "file=@caminho/para/sua/imagem.jpg"
```

**Opção C - Python:**
```python
import requests

# Abre a imagem
with open('sua_imagem.jpg', 'rb') as f:
    # Envia para a API
    response = requests.post(
        'http://localhost:8001/img_object_detection_to_json',
        files={'file': f}
    )

# Mostra o resultado
resultado = response.json()
print(f"Objetos detectados: {resultado['detect_objects_names']}")
for obj in resultado['detect_objects']:
    print(f"- {obj['name']}: {obj['confidence']*100:.1f}% de confiança")
```

**Resposta esperada:**
```json
{
  "detect_objects": [
    {"name": "person", "confidence": 0.95},
    {"name": "car", "confidence": 0.87},
    {"name": "dog", "confidence": 0.72}
  ],
  "detect_objects_names": "person, car, dog"
}
```

**Explicação:**
- `detect_objects`: Lista de objetos encontrados
- `name`: Nome do objeto (person = pessoa, car = carro, etc.)
- `confidence`: Nível de confiança (0.0 a 1.0, onde 1.0 = 100% de certeza)

---

### 3. Detecção de Objetos (Retorna Imagem Anotada)

**O que faz:** Analisa uma imagem e retorna a mesma imagem com caixas desenhadas ao redor dos objetos detectados.

**Como usar:**

**Opção A - Interface Web:**
1. Acesse `http://localhost:8001/docs`
2. Clique em `POST /img_object_detection_to_img`
3. Clique em "Try it out"
4. Selecione uma imagem
5. Clique em "Execute"
6. A imagem anotada será exibida

**Opção B - cURL:**
```bash
curl -X POST "http://localhost:8001/img_object_detection_to_img" \
     -F "file=@sua_imagem.jpg" \
     --output imagem_com_caixas.jpg
```

**Opção C - Python:**
```python
import requests

with open('sua_imagem.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/img_object_detection_to_img',
        files={'file': f}
    )

# Salva a imagem anotada
with open('resultado.jpg', 'wb') as f:
    f.write(response.content)

print("Imagem salva como 'resultado.jpg'")
```

**Resposta:** Uma imagem JPEG com caixas coloridas ao redor dos objetos detectados.

---

### 4. Extração de Texto (OCR)

**O que faz:** Extrai todo o texto que aparece em uma imagem.

**Como usar:**

**Interface Web:**
1. Acesse `http://localhost:8001/docs`
2. Clique em `POST /img_text_extraction`
3. Selecione uma imagem com texto
4. (Opcional) Escolha o método: `easyocr` ou `tesseract`
5. Execute

**cURL:**
```bash
curl -X POST "http://localhost:8001/img_text_extraction?method=easyocr" \
     -F "file=@imagem_com_texto.jpg"
```

**Python:**
```python
import requests

with open('imagem_com_texto.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/img_text_extraction?method=easyocr',
        files={'file': f}
    )

resultado = response.json()
print(f"Texto completo: {resultado['full_text']}")
print(f"Total de segmentos: {resultado['total_segments']}")
```

**Resposta esperada:**
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

---

### 5. Análise de Cores

**O que faz:** Identifica as cores dominantes na imagem e analisa o impacto emocional delas.

**Como usar:**

**Interface Web:**
1. Acesse `http://localhost:8001/docs`
2. Clique em `POST /img_color_analysis`
3. Selecione uma imagem
4. (Opcional) Defina quantas cores analisar (padrão: 5, máximo: 10)
5. Execute

**cURL:**
```bash
curl -X POST "http://localhost:8001/img_color_analysis?n_colors=5" \
     -F "file=@sua_imagem.jpg"
```

**Python:**
```python
import requests

with open('sua_imagem.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/img_color_analysis?n_colors=5',
        files={'file': f}
    )

resultado = response.json()
print(f"Paleta emocional: {resultado['emotion_palette']}")
for cor in resultado['dominant_colors']:
    print(f"- {cor['hex']}: {cor['percentage']:.1f}% ({cor['emotion_tag']})")
```

**Resposta esperada:**
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

**Explicação:**
- `emotion_palette`: Paleta emocional geral (warm-energetic = quente-energética, cool-calm = fria-calma, etc.)
- `emotion_tag`: Tag emocional de cada cor

---

### 6. Geração de Descrição Automática

**O que faz:** Gera uma descrição textual automática do que aparece na imagem.

**Como usar:**

**Interface Web:**
1. Acesse `http://localhost:8001/docs`
2. Clique em `POST /img_caption`
3. Selecione uma imagem
4. (Opcional) Defina o tamanho máximo da descrição em palavras (padrão: 50)
5. Execute

**cURL:**
```bash
curl -X POST "http://localhost:8001/img_caption?max_length=50" \
     -F "file=@sua_imagem.jpg"
```

**Python:**
```python
import requests

with open('sua_imagem.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/img_caption?max_length=50',
        files={'file': f}
    )

resultado = response.json()
print(f"Descrição: {resultado['caption']}")
print(f"Confiança: {resultado['confidence']*100:.1f}%")
```

**Resposta esperada:**
```json
{
  "caption": "A woman smiling while holding a cosmetic product",
  "method": "blip",
  "confidence": 0.85,
  "length": 8
}
```

---

### 7. Detecção de Emoções

**O que faz:** Detecta emoções em faces humanas presentes na imagem (felicidade, tristeza, raiva, etc.).

**Como usar:**

**Interface Web:**
1. Acesse `http://localhost:8001/docs`
2. Clique em `POST /img_emotion_detection`
3. Selecione uma imagem com pessoas
4. Execute

**cURL:**
```bash
curl -X POST "http://localhost:8001/img_emotion_detection" \
     -F "file=@imagem_com_pessoas.jpg"
```

**Python:**
```python
import requests

with open('imagem_com_pessoas.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/img_emotion_detection',
        files={'file': f}
    )

resultado = response.json()
print(f"Faces detectadas: {resultado['faces_detected']}")
print(f"Emoção geral da cena: {resultado['scene_emotion']}")
for emotion in resultado['emotions']:
    print(f"Face {emotion['face_id']}: {emotion['dominant_emotion']} ({emotion['dominant_confidence']*100:.1f}%)")
```

**Resposta esperada:**
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

**Emoções possíveis:** happy (feliz), sad (triste), angry (raiva), fear (medo), surprise (surpresa), neutral (neutro), disgust (nojo)

---

### 8. Análise de Atenção Visual

**O que faz:** Analisa para onde o olhar das pessoas é direcionado na imagem e identifica os pontos de maior atenção.

**Como usar:**

**Interface Web:**
1. Acesse `http://localhost:8001/docs`
2. Clique em `POST /img_attention_analysis`
3. Selecione uma imagem
4. (Opcional) Defina quantos pontos de atenção retornar (padrão: 5, máximo: 20)
5. Execute

**cURL:**
```bash
curl -X POST "http://localhost:8001/img_attention_analysis?n_points=5" \
     -F "file=@sua_imagem.jpg"
```

**Python:**
```python
import requests

with open('sua_imagem.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/img_attention_analysis?n_points=5',
        files={'file': f}
    )

resultado = response.json()
print(f"Score de atenção: {resultado['attention_score']*100:.1f}%")
print(f"Alinhamento com regra dos terços: {resultado['rule_of_thirds_alignment']}")
```

**Resposta esperada:**
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

---

### 9. Detecção de CTAs (Call-to-Action)

**O que faz:** Identifica elementos de chamada para ação na imagem (botões, textos como "Compre Agora", "Clique Aqui", etc.).

**Como usar:**

**Interface Web:**
1. Acesse `http://localhost:8001/docs`
2. Clique em `POST /img_cta_detection`
3. Selecione uma imagem (idealmente com textos de ação)
4. Execute

**cURL:**
```bash
curl -X POST "http://localhost:8001/img_cta_detection" \
     -F "file=@imagem_com_cta.jpg"
```

**Python:**
```python
import requests

with open('imagem_com_cta.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/img_cta_detection',
        files={'file': f}
    )

resultado = response.json()
print(f"CTAs presentes: {resultado['cta_present']}")
print(f"Quantidade: {resultado['cta_count']}")
print(f"Score de efetividade: {resultado['effectiveness_score']*100:.1f}%")
for cta in resultado['cta_elements']:
    print(f"- {cta['text']} (confiança: {cta['confidence']*100:.1f}%)")
```

**Resposta esperada:**
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

---

### 10. Relatório Completo de Neuromarketing

**O que faz:** Combina todas as análises anteriores em um único relatório completo.

**Como usar:**

**Interface Web:**
1. Acesse `http://localhost:8001/docs`
2. Clique em `POST /img_neuromarketing_report`
3. Selecione uma imagem
4. Execute

**cURL:**
```bash
curl -X POST "http://localhost:8001/img_neuromarketing_report" \
     -F "file=@sua_imagem.jpg"
```

**Python:**
```python
import requests
import json

with open('sua_imagem.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/img_neuromarketing_report',
        files={'file': f}
    )

resultado = response.json()

# Salva o resultado completo em um arquivo JSON
with open('relatorio_completo.json', 'w', encoding='utf-8') as f:
    json.dump(resultado, f, indent=2, ensure_ascii=False)

# Mostra o resumo
summary = resultado['summary']
print(f"Total de objetos: {summary['total_objects']}")
print(f"Emoção da cena: {summary['scene_emotion']}")
print(f"Score de atenção: {summary['attention_score']*100:.1f}%")
print(f"Paleta de cores: {summary['color_palette']}")
print("\nRecomendações:")
for rec in summary['recommendations']:
    print(f"- {rec}")
```

**Resposta:** Um JSON completo com todas as análises combinadas.

---

### 11. Análise Completa de Neuromarketing (20 Dimensões)

**O que faz:** Realiza uma análise extremamente detalhada com 20 dimensões diferentes de neuromarketing, tudo em português.

**Como usar:**

**Interface Web:**
1. Acesse `http://localhost:8001/docs`
2. Clique em `POST /analisar_imagem_neuromarketing`
3. Selecione uma imagem
4. Execute

**cURL:**
```bash
curl -X POST "http://localhost:8001/analisar_imagem_neuromarketing" \
     -F "file=@sua_imagem.jpg" \
     -o resultado_completo.json
```

**Python:**
```python
import requests
import json

with open('sua_imagem.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/analisar_imagem_neuromarketing',
        files={'file': f}
    )

resultado = response.json()

# Salva o resultado
with open('analise_completa.json', 'w', encoding='utf-8') as f:
    json.dump(resultado, f, indent=2, ensure_ascii=False)

# Mostra informações principais
print(f"Pessoas detectadas: {resultado['numero_de_pessoas']}")
print(f"Emoção dominante: {resultado['expressao_emocional']['emocao_dominante']}")
print(f"Paleta emocional: {resultado['cores_dominantes']['emotion_palette']}")
print(f"Tipo de plano: {resultado['tipo_de_plano']['plano']}")
```

**Dimensões analisadas:**
1. Expressão facial e emoções
2. Direção do olhar
3. Paleta de cores e impacto emocional
4. Contraste visual
5. Profundidade de campo
6. Sensação de movimento
7. Simetria visual
8. Tipo de plano (close-up, médio, aberto)
9. Iluminação e temperatura de cor
10. Símbolos sociais
11. Proximidade social
12. Ponto focal de atenção
13. Linguagem corporal
14. Coerência narrativa
15. Gatilhos de escassez
16. Textos e tipografia
17. Humor e incongruência
18. Textura sensorial
19. Ambiente (natural vs artificial)
20. Resumo executivo

---

## Exemplos Práticos

### Exemplo 1: Analisar uma Foto de Produto

```python
import requests
import json

# 1. Abre a imagem do produto
with open('produto.jpg', 'rb') as f:
    # 2. Envia para análise completa
    response = requests.post(
        'http://localhost:8001/analisar_imagem_neuromarketing',
        files={'file': f}
    )

# 3. Processa o resultado
resultado = response.json()

# 4. Mostra insights importantes
print("=== ANÁLISE DE PRODUTO ===\n")
print(f"Objetos detectados: {len(resultado['objetos'])}")
print(f"Emoção transmitida: {resultado['expressao_emocional']['emocao_dominante']}")
print(f"Paleta de cores: {resultado['cores_dominantes']['emotion_palette']}")
print(f"CTAs presentes: {resultado['gatilho_escassez_visual']['ctas_detectados']}")

# 5. Salva relatório completo
with open('relatorio_produto.json', 'w', encoding='utf-8') as f:
    json.dump(resultado, f, indent=2, ensure_ascii=False)
```

### Exemplo 2: Verificar se uma Imagem tem Texto

```python
import requests

with open('imagem.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/img_text_extraction',
        files={'file': f}
    )

resultado = response.json()

if resultado['full_text']:
    print(f"Texto encontrado: {resultado['full_text']}")
else:
    print("Nenhum texto encontrado na imagem")
```

### Exemplo 3: Comparar Cores de Duas Imagens

```python
import requests

def analisar_cores(arquivo_imagem):
    with open(arquivo_imagem, 'rb') as f:
        response = requests.post(
            'http://localhost:8001/img_color_analysis',
            files={'file': f}
        )
    return response.json()

# Analisa duas imagens
cores1 = analisar_cores('imagem1.jpg')
cores2 = analisar_cores('imagem2.jpg')

print(f"Imagem 1 - Paleta: {cores1['emotion_palette']}")
print(f"Imagem 2 - Paleta: {cores2['emotion_palette']}")

if cores1['emotion_palette'] == cores2['emotion_palette']:
    print("As duas imagens têm paletas emocionais similares!")
```

### Exemplo 4: Detectar Objetos e Salvar Imagem Anotada

```python
import requests

# 1. Detecta objetos e recebe JSON
with open('foto.jpg', 'rb') as f:
    response_json = requests.post(
        'http://localhost:8001/img_object_detection_to_json',
        files={'file': f}
    )
    objetos = response_json.json()

# 2. Mostra objetos detectados
print("Objetos encontrados:")
for obj in objetos['detect_objects']:
    print(f"- {obj['name']}: {obj['confidence']*100:.1f}%")

# 3. Gera imagem anotada
with open('foto.jpg', 'rb') as f:
    response_img = requests.post(
        'http://localhost:8001/img_object_detection_to_img',
        files={'file': f}
    )

# 4. Salva imagem com caixas
with open('foto_com_caixas.jpg', 'wb') as f:
    f.write(response_img.content)

print("\nImagem anotada salva como 'foto_com_caixas.jpg'")
```

---

## Troubleshooting

### Problema: "Address already in use"

**Causa:** A porta 8001 já está sendo usada por outro programa.

**Solução:**
1. Use outra porta:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8002 --reload
   ```
2. Ou encontre e pare o processo que está usando a porta:
   ```bash
   # Mac/Linux
   lsof -ti:8001 | xargs kill -9
   
   # Windows
   netstat -ano | findstr :8001
   # Depois use o PID para matar o processo
   ```

### Problema: "ModuleNotFoundError"

**Causa:** Alguma biblioteca não foi instalada.

**Solução:**
```bash
pip install -r requirements.txt --upgrade
```

### Problema: A API não responde

**Soluções:**
1. Verifique se o servidor está rodando (veja o terminal)
2. Teste o healthcheck: `http://localhost:8001/healthcheck`
3. Verifique se está usando a porta correta
4. Reinicie o servidor (CTRL+C e depois inicie novamente)

### Problema: Erro ao processar imagem

**Causas possíveis:**
- Formato de imagem não suportado (use JPEG, PNG, WEBP)
- Imagem muito grande (tente redimensionar)
- Arquivo corrompido

**Solução:**
- Use imagens em formato JPEG ou PNG
- Tente com uma imagem menor
- Verifique se o arquivo não está corrompido

### Problema: Resultados estranhos ou imprecisos

**Explicação:**
- A IA pode ter dificuldades com imagens muito escuras, borradas ou de baixa qualidade
- Alguns objetos podem não ser detectados se estiverem parcialmente ocultos
- A precisão depende da qualidade da imagem

**Soluções:**
- Use imagens de boa qualidade (resolução mínima recomendada: 640x640 pixels)
- Garanta boa iluminação na imagem
- Evite imagens muito borradas ou pixeladas

---

## Dicas Finais

1. **Use a Interface Web:** A forma mais fácil é usar `http://localhost:8001/docs` - não precisa escrever código!

2. **Comece Simples:** Teste primeiro o healthcheck, depois detecção de objetos, e só então os endpoints mais complexos.

3. **Salve os Resultados:** Sempre salve os resultados em arquivos JSON para análise posterior.

4. **Leia as Respostas:** As respostas da API contêm informações valiosas - explore os campos retornados.

5. **Experimente Diferentes Imagens:** Teste com vários tipos de imagens para entender melhor o que cada endpoint faz.

---

## Próximos Passos

Agora que você sabe usar a API, pode:

- Integrar em seus próprios projetos
- Criar scripts automatizados para análise em lote
- Desenvolver aplicações web que usam a API
- Explorar os endpoints avançados de neuromarketing

**Boa sorte e divirta-se usando a ElRoi Vision API! 🚀**

---

## Suporte

Se tiver dúvidas ou problemas:
- Consulte a documentação Swagger em `/docs`
- Verifique os logs do servidor
- Abra uma issue no repositório do projeto
```

Salve este conteúdo em `docs/GUIA_USO.md`. O guia inclui:

- Instruções passo a passo para iniciantes
- Explicações de cada endpoint
- Exemplos práticos em Python, cURL e interface web
- Troubleshooting
- Dicas e próximos passos

O documento está formatado em markdown e pronto para uso.