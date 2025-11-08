# Guia de Deploy - EasyPanel

Este documento fornece instruções detalhadas para fazer deploy da aplicação ElRoi Vision no EasyPanel.

## 📋 Checklist Pré-Deploy

- [ ] Repositório Git configurado e código commitado
- [ ] Modelo YOLO disponível (pode estar no repositório ou em storage)
- [ ] Variáveis de ambiente definidas
- [ ] Domínio configurado (opcional)

## 🚀 Passo a Passo Detalhado

### 1. Preparar o Repositório

Certifique-se de que todos os arquivos necessários estão commitados:

```bash
git add .
git commit -m "Preparar para deploy"
git push origin main
```

### 2. Criar Aplicação no EasyPanel

1. Acesse o painel do EasyPanel
2. Clique em **"New App"** ou **"Create App"**
3. Selecione **"Git Repository"**
4. Conecte seu repositório:
   - GitHub: Autorize e selecione o repositório
   - GitLab: Autorize e selecione o repositório
   - Outros: Configure conforme necessário

### 3. Configurar Build

Na seção **"Build Settings"**:

- **Build Method**: Dockerfile
- **Dockerfile Path**: `/Dockerfile` (ou deixe vazio se estiver na raiz)
- **Build Context**: `/` (raiz do projeto)
- **Build Command**: Deixe vazio (o Dockerfile já define o build)

### 4. Configurar Variáveis de Ambiente

Na seção **"Environment Variables"**, adicione:

| Variável | Valor | Descrição |
|----------|-------|-----------|
| `MODEL_PATH` | `/app/models/sample_model/yolov8n.pt` | Caminho do modelo YOLO |
| `CONFIDENCE_THRESHOLD` | `0.5` | Limiar de confiança |
| `IMAGE_SIZE` | `640` | Tamanho da imagem |
| `AUGMENT` | `false` | Augmentação de dados |
| `HOST` | `0.0.0.0` | Host do servidor |
| `PORT` | `8001` | Porta do servidor |
| `CORS_ORIGINS` | `*` | Origens CORS (ou lista separada por vírgula) |
| `LOG_LEVEL` | `INFO` | Nível de log |
| `LOG_FILE` | `log.log` | Arquivo de log |
| `LOG_ROTATION` | `1 MB` | Rotação de log |
| `ENVIRONMENT` | `production` | Ambiente |

**Importante**: Para produção, configure `CORS_ORIGINS` com domínios específicos:
```
CORS_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com
```

### 5. Configurar Storage/Volumes (Opcional)

Se o modelo YOLO não estiver no repositório Git:

1. Vá em **"Storage"** ou **"Volumes"**
2. Crie um volume:
   - **Name**: `models`
   - **Mount Path**: `/app/models`
   - **Size**: Conforme necessário (modelos YOLO são ~6-50MB)
3. Após o deploy, faça upload do modelo para o volume

### 6. Configurar Porta

Na seção **"Ports"** ou **"Networking"**:

- **Port**: `8001`
- **Protocol**: `HTTP`
- **Public**: `Yes` (se quiser acesso externo)

### 7. Configurar Healthcheck

Na seção **"Healthcheck"**:

- **Path**: `/healthcheck`
- **Interval**: `30s`
- **Timeout**: `10s`
- **Retries**: `3`

### 8. Configurar Comando de Start (Opcional)

Se preferir usar Gunicorn para produção:

Na seção **"Start Command"**, use:

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001 --timeout 120
```

Ou com uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

**Nota**: O número de workers depende da memória disponível. Cada worker carrega o modelo YOLO na memória.

### 9. Configurar Recursos

Na seção **"Resources"**:

- **CPU**: Mínimo 1 core (recomendado 2+)
- **Memory**: Mínimo 2GB (recomendado 4GB+)
- **Storage**: Conforme necessário para modelos e logs

### 10. Deploy

1. Revise todas as configurações
2. Clique em **"Deploy"** ou **"Save & Deploy"**
3. Aguarde o build completar (pode levar alguns minutos)
4. Verifique os logs durante o build

### 11. Verificação Pós-Deploy

Após o deploy completar:

1. **Healthcheck**:
   ```bash
   curl https://seu-dominio.com/healthcheck
   ```
   Deve retornar: `{"healthcheck": "Everything OK!"}`

2. **Swagger Docs**:
   Acesse: `https://seu-dominio.com/docs`
   Deve abrir a interface Swagger

3. **Teste de Detecção**:
   Use a interface Swagger ou faça uma requisição:
   ```bash
   curl -X POST "https://seu-dominio.com/img_object_detection_to_json" \
        -F "file=@test_image.jpg"
   ```

## 🔧 Troubleshooting

### Build Falha

- Verifique os logs do build
- Confirme que o Dockerfile está correto
- Verifique se todas as dependências estão no `requirements.txt`

### Erro ao Carregar Modelo

- Verifique se `MODEL_PATH` está correto
- Confirme que o modelo existe no caminho especificado
- Se usando volume, verifique se o volume está montado corretamente

### Erro 502 Bad Gateway

- Verifique se a porta está configurada corretamente
- Confirme que o healthcheck está funcionando
- Verifique os logs da aplicação

### Erro de Memória

- Aumente a memória alocada
- Reduza o número de workers
- Verifique se há vazamentos de memória nos logs

### CORS Errors

- Verifique a configuração de `CORS_ORIGINS`
- Confirme que os domínios estão corretos
- Para desenvolvimento, pode usar `*` temporariamente

## 📊 Monitoramento

### Logs

Acesse os logs no EasyPanel:
- **Logs**: Seção de logs da aplicação
- **Log File**: Verifique `log.log` se configurado

### Métricas

Monitore:
- Uso de CPU e memória
- Tempo de resposta dos endpoints
- Taxa de erro
- Número de requisições

## 🔄 Atualizações

Para atualizar a aplicação:

1. Faça as alterações no código
2. Commit e push para o repositório
3. No EasyPanel, clique em **"Redeploy"** ou **"Deploy"**
4. Aguarde o novo build

## 📝 Notas Adicionais

- O modelo YOLO é carregado na memória ao iniciar a aplicação
- Cada worker carrega uma instância do modelo
- Para alta disponibilidade, considere usar múltiplas instâncias
- Configure backup regular dos modelos e logs

## 🆘 Suporte

Em caso de problemas:
1. Verifique os logs da aplicação
2. Verifique os logs do build
3. Consulte a documentação do EasyPanel
4. Abra uma issue no repositório

