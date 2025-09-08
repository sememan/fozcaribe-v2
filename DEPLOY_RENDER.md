# 🚀 Guia de Deploy no Render - FozCaribe v2.0

Este guia mostra como fazer deploy da aplicação FozCaribe no Render.com

## 📋 Pré-requisitos

- ✅ Conta GitHub com o repositório FozCaribe
- ✅ Conta Google Cloud Platform configurada
- ✅ Ficheiro `credentials.json` do Google
- ✅ Google Sheets criada ("FozCaribe App")
- ✅ Pastas Google Drive configuradas

## 🎯 Passo a Passo

### 1. Preparar o Repositório

```bash
# Garantir que todos os ficheiros estão commitados
git add .
git commit -m "Prepare for Render deploy"
git push origin main
```

### 2. Criar Conta no Render

1. Ir para [render.com](https://render.com)
2. Clicar "Get Started" 
3. Conectar com GitHub
4. Autorizar acesso aos repositórios

### 3. Criar Web Service

1. **Dashboard > New > Web Service**
2. **Connect Repository**: Selecionar `fozcaribe.v2`
3. **Configurações**:
   ```
   Name: fozcaribe-app
   Region: Frankfurt (mais próximo de Portugal)
   Branch: main
   Root Directory: (deixar vazio)
   Runtime: Python 3
   Build Command: ./build.sh
   Start Command: uvicorn main:app --host=0.0.0.0 --port=$PORT
   ```

### 4. Configurar Variáveis de Ambiente

No dashboard do service, ir para **Environment** e adicionar:

#### Variáveis Básicas
```
PYTHON_VERSION=3.9.16
GOOGLE_SHEETS_NAME=FozCaribe App
APP_NAME=FozCaribe
APP_VERSION=2.0.0
TIMEZONE=Europe/Lisbon
LOG_LEVEL=INFO
```

#### Google Drive - IDs das Pastas
```
FOLDER_ID_MAIN=1769MEGbRjrUFu_HbplMDY0fh-9meEVuA
FOLDER_ID_BACHATA_INT=1U2RM0P-_88KN8Eibs7WJkbf4hozKAqPZ
FOLDER_ID_BACHATA_FUND=1Fb7drcC1HwvLQGqCWvd9bkV0NTv0nzw4
FOLDER_ID_SALSA=1OuBDGBqvUKxvNWM2vdJxPG_DlwZ2zcWo
FOLDER_ID_SUNSET=1gd64oEz09oFCh4VhqC09yfLSGAg4iJbB
FOLDER_ID_AULAS=1kP8rVjVNBUaWYOcvEeCdI04q8NgB7Uy3
```

### 5. Adicionar Credenciais Google

#### Método 1: Environment Variable (Recomendado)
1. Abrir o ficheiro `credentials.json`
2. Copiar todo o conteúdo JSON
3. No Render Dashboard:
   - **Environment > Add Environment Variable**
   - **Key**: `GOOGLE_CREDENTIALS_JSON`
   - **Value**: (colar o JSON completo)

#### Método 2: Secret File
1. Upload do `credentials.json` como secret file
2. Modificar código para ler do caminho secreto

### 6. Deploy Automático

1. Clicar **"Create Web Service"**
2. Render irá:
   - Clonar o repositório
   - Executar `./build.sh`
   - Instalar dependências 
   - Iniciar aplicação
3. Deploy demora ~2-5 minutos

### 7. Verificar Deploy

#### URL da Aplicação
Após sucesso: `https://fozcaribe-app.onrender.com`

#### Health Check
- Homepage: `https://fozcaribe-app.onrender.com/`
- Gallery: `https://fozcaribe-app.onrender.com/gallery`
- API Status: Verificar logs no dashboard

### 8. Configurar Domínio Personalizado (Opcional)

1. **Settings > Custom Domains**
2. Adicionar: `app.fozcaribe.com`
3. Configurar DNS:
   ```
   Type: CNAME
   Name: app
   Value: fozcaribe-app.onrender.com
   ```

## 🔧 Resolução de Problemas

### Build Falha
```bash
# Verificar logs no Render Dashboard
# Problemas comuns:
- requirements.txt inválido
- Python version incompatível  
- build.sh sem permissões
```

### Credenciais Google Não Funcionam
```bash
# Verificar no dashboard:
1. Environment variables configuradas
2. JSON válido no GOOGLE_CREDENTIALS_JSON
3. APIs ativadas no Google Cloud
4. Planilhas partilhadas com service account
```

### Aplicação Não Inicia
```bash
# Verificar:
1. Start command correto: uvicorn main:app --host=0.0.0.0 --port=$PORT
2. main.py na raiz do projeto
3. PORT environment variable disponível
4. Logs de erro no dashboard
```

### Imagens Não Carregam
```bash
# Verificar:
1. IDs das pastas Google Drive corretos
2. Pastas partilhadas com service account
3. Proxy endpoint /drive-image/ funcional
```

## 💰 Custos

### Free Tier
- ✅ 750 horas/mês grátis
- ✅ Suficiente para desenvolvimento/teste
- ⚠️ Aplicação "dorme" após inatividade

### Starter Plan ($7/mês)
- ✅ Sempre ativo (sem sleep)
- ✅ Melhor performance
- ✅ SSL gratuito
- ✅ Ideal para produção

## 🔄 Updates Automáticos

Cada push para `main` trigger novo deploy:

```bash
# Fazer alterações
git add .
git commit -m "Update feature"
git push origin main
# Render deploy automaticamente
```

## 📊 Monitorização

### Dashboard Render
- Logs em tempo real
- Métricas de performance  
- Status da aplicação
- Usage statistics

### Alerts
Configurar alerts para:
- Deploy failures
- Application downtime
- High resource usage

---

## 🎉 Deploy Completo!

Após seguir este guia, terá:
- ✅ Aplicação FozCaribe live em produção
- ✅ Deploy automático via Git
- ✅ SSL/HTTPS gratuito
- ✅ Logs e monitorização
- ✅ Escalabilidade automática

**URL Final**: `https://fozcaribe-app.onrender.com`

Para suporte: [render.com/docs](https://render.com/docs)
