# FozCaribe v2.0 - Aplicação Web Moderna

🌴 Uma aplicação web moderna para a escola de dança FozCaribe, construída com FastAPI e design responsivo, com integração Google Sheets e Google Drive.

## 🚀 Funcionalidades

- ✅ **Homepage moderna** com estatísticas reais dos alunos
- ✅ **Sistema de pré-inscrição** integrado com Google Sheets
- ✅ **Sistema de inscrição completa** com formulário detalhado
- ✅ **Sistema de login** e autenticação de utilizadores
- ✅ **Galeria de imagens e vídeos** integrada com Google Drive
- ✅ **Dashboard administrativo** com estatísticas e gestão
- ✅ **Design responsivo** otimizado para mobile e desktop
- ✅ **Interface em português** adaptada ao público português
- ✅ **Conteúdo exclusivo** para alunos registados
- ✅ **Proxy de imagens** para Google Drive

## 🛠 Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework Python moderno e rápido
- **Python 3.8+** - Linguagem principal
- **Google Sheets API** - Armazenamento de dados
- **Google Drive API** - Gestão de galeria
- **Uvicorn** - Servidor ASGI
- **gspread** - Integração com Google Sheets

### Frontend
- **Jinja2** - Template engine
- **Tailwind CSS** - Framework CSS moderno
- **Font Awesome** - Ícones
- **JavaScript vanilla** - Interatividade
- **Inter Font** - Tipografia moderna

### Integração
- **google-api-python-client** - APIs do Google
- **python-multipart** - Upload de ficheiros

## ⚡ Instalação Rápida

### 1. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/fozcaribe.v2.git
cd fozcaribe.v2
```

### 2. Criar ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar credenciais do Google

#### 4.1. Google Cloud Console
1. Aceder ao [Google Cloud Console](https://console.cloud.google.com/)
2. Criar um novo projeto ou selecionar existente
3. Ativar as APIs:
   - Google Sheets API
   - Google Drive API

#### 4.2. Credenciais de Serviço
1. Ir para "APIs & Services" > "Credentials"
2. Clicar "Create Credentials" > "Service Account"
3. Preencher os detalhes da conta de serviço
4. Descarregar o ficheiro JSON das credenciais
5. Renomear para `credentials.json` e colocar na raiz do projeto

### 5. Configurar Google Sheets
Criar uma planilha Google Sheets com o nome **"FozCaribe App"** e as seguintes abas:

#### Aba "Preregistrations"
Colunas: Timestamp | Nome | Telefone | Cidade | Nivel | Tipo_Inscricao | Estilo_Danca | Nota

#### Aba "Inscricoes" 
Colunas: Timestamp | Nome | Email | Telefone | Data_Nascimento | Morada | Cidade | Codigo_Postal | Modalidade | Experiencia | Tipo_Pagamento | Contacto_Emergencia_Nome | Contacto_Emergencia_Telefone | Observacoes

#### Aba "Users"
Colunas: Nome | Email | Password

**Importante**: Partilhar a planilha com o email da conta de serviço (encontrado no credentials.json)

### 6. Configurar Google Drive (Opcional)
1. Criar pastas no Google Drive para a galeria
2. Partilhar as pastas com a conta de serviço
3. Copiar os IDs das pastas e atualizar no `main.py`:
   - `FOLDER_ID` - Galeria principal
   - `FOLDER_ID_bachata_fund` - Bachata Fundamentos
   - `FOLDER_ID_bachata_int` - Bachata Intermédio
   - `FOLDER_ID_salsa` - Salsa
   - `FOLDER_ID_sunset` - Sunset
   - `FOLDER_ID_aulas` - Aulas

### 7. Executar a aplicação
```bash
python main.py
```

A aplicação estará disponível em: **http://localhost:8000**

## 📁 Estrutura do Projeto

```
fozcaribe.v2/
├── main.py                 # Aplicação principal FastAPI
├── requirements.txt        # Dependências Python
├── credentials.json        # Credenciais Google (não incluído no Git)
├── README.md              # Este ficheiro
├── .gitignore             # Ficheiros a ignorar no Git
├── templates/             # Templates HTML
│   ├── base.html          # Template base com navegação
│   ├── index.html         # Homepage com estatísticas
│   ├── preregister.html   # Formulário de pré-inscrição
│   ├── inscricao.html     # Formulário de inscrição completa
│   ├── login.html         # Sistema de login
│   ├── dashboard.html     # Dashboard administrativo
│   └── gallery.html       # Galeria principal
├── static/               # Ficheiros estáticos
│   ├── css/              # Estilos CSS personalizados
│   ├── js/               # JavaScript
│   └── images/           # Imagens do site
└── venv/                 # Ambiente virtual (não incluído no Git)
```

## 🎯 Páginas e Rotas

| Rota | Método | Descrição |
|------|--------|-----------|
| `/` | GET | Homepage com estatísticas e apresentação |
| `/preregister` | GET/POST | Formulário de pré-inscrição rápida |
| `/inscricao` | GET/POST | Formulário de inscrição completa |
| `/login` | GET/POST | Sistema de autenticação |
| `/dashboard` | GET | Painel administrativo (requer login) |
| `/gallery` | GET | Galeria pública de imagens e vídeos |
| `/galeria/conteudo-login` | GET/POST | Acesso a conteúdo exclusivo |
| `/galeria/conteudo/{user}/bachata-fundamentos` | GET | Conteúdo Bachata Fundamentos |
| `/galeria/conteudo/{user}/bachata-intermedio` | GET | Conteúdo Bachata Intermédio |
| `/galeria/conteudo/{user}/salsa` | GET | Conteúdo Salsa |
| `/galeria/sunset` | GET | Galeria Sunset (pública) |
| `/galeria/aulas` | GET | Galeria de Aulas (pública) |
| `/drive-image/{file_id}` | GET | Proxy para imagens do Google Drive |

## 🔐 Funcionalidades de Segurança

### Google Cloud Platform
- ✅ Credenciais de conta de serviço
- ✅ APIs restritas às necessárias
- ✅ Permissões mínimas necessárias

### Gestão de Dados
- ✅ Validação de formulários
- ✅ Sanitização de inputs
- ✅ Integração segura com Google Sheets

### Proxy de Imagens
- ✅ Acesso autenticado ao Google Drive
- ✅ Cache de imagens
- ✅ Fallback para links diretos

## 🚀 Deploy em Produção

### 🌟 Opção 1: Render (Recomendado)

#### Preparação do Projeto
```bash
# 1. Garantir que todos os ficheiros estão no repositório
git add .
git commit -m "Deploy to Render"
git push origin main
```

#### Deploy Automático via GitHub
1. **Criar conta no Render**: [https://render.com](https://render.com)
2. **Conectar GitHub**: Link your GitHub account
3. **Create New Web Service**:
   - Repository: Selecionar `fozcaribe.v2`
   - Branch: `main`
   - Root Directory: `.` (raiz)
   - Environment: `Python 3`
   - Build Command: `./build.sh`
   - Start Command: `uvicorn main:app --host=0.0.0.0 --port=$PORT`

#### Configurar Variáveis de Ambiente no Render
No dashboard do Render, adicionar:
```
PYTHON_VERSION=3.9.16
GOOGLE_SHEETS_NAME=FozCaribe App
APP_NAME=FozCaribe
APP_VERSION=2.0.0
TIMEZONE=Europe/Lisbon
```

#### Adicionar Credenciais Google
1. **Via Render Dashboard**:
   - Environment > Add Environment Variable
   - Key: `GOOGLE_CREDENTIALS_JSON`
   - Value: (conteúdo completo do credentials.json)

2. **Ou via ficheiro secreto**:
   - Upload `credentials.json` como ficheiro secreto
   - Referenciar no código

#### URL da Aplicação
Após deploy: `https://fozcaribe-app.onrender.com`

### Opção 2: Railway/Heroku
```bash
# Criar Procfile (já existe)
echo "web: uvicorn main:app --host=0.0.0.0 --port=\$PORT" > Procfile

# Deploy
git add .
git commit -m "Deploy to production"
git push origin main
```

### Opção 2: DigitalOcean/AWS/VPS
```bash
# Instalar gunicorn para produção
pip install gunicorn

# Executar com gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Opção 3: Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🎨 Personalização

### Cores da Marca
```css
:root {
  --brand-50: #f0f9ff;
  --brand-100: #e0f2fe;
  --brand-500: #0ea5e9;
  --brand-600: #0284c7;
  --brand-700: #0369a1;
}
```

### Adicionar Novas Páginas
1. Criar template HTML em `templates/`
2. Adicionar rota no `main.py`
3. Atualizar navegação no `base.html`

### Integrar Nova API
1. Instalar dependências: `pip install nome-biblioteca`
2. Atualizar `requirements.txt`: `pip freeze > requirements.txt`
3. Configurar credenciais
4. Implementar endpoints

## 🤝 Contribuição

1. **Fork** o projeto
2. **Criar branch** para feature (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** das alterações (`git commit -m 'Adicionar nova funcionalidade'`)
4. **Push** para branch (`git push origin feature/nova-funcionalidade`)
5. **Abrir Pull Request**

### Diretrizes de Contribuição
- Usar português nos comentários e documentação
- Seguir padrões de código Python (PEP 8)
- Testar todas as funcionalidades antes do commit
- Atualizar documentação quando necessário

## 📱 Suporte a Dispositivos

### Desktop
- Chrome (último)
- Firefox (último)
- Safari (último)
- Edge (último)

### Mobile
- iOS Safari
- Chrome Mobile
- Samsung Internet
- Firefox Mobile

### Tablets
- iPad (Safari)
- Android tablets
- Surface tablets

## 🔧 Resolução de Problemas

### Google Sheets não conecta
```bash
# Verificar se o ficheiro credentials.json existe
ls -la credentials.json

# Verificar se as APIs estão ativadas no Google Cloud
# Verificar se a planilha foi partilhada com a conta de serviço
```

### Imagens não carregam
```bash
# Verificar permissões das pastas do Google Drive
# Verificar IDs das pastas no main.py
# Verificar se o proxy /drive-image/ está a funcionar
```

### Erro de dependências
```bash
# Reinstalar dependências
pip install -r requirements.txt --force-reinstall

# Ou criar novo ambiente virtual
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📞 Suporte e Contacto

- **Email**: suporte@fozcaribe.com
- **Website**: [fozcaribe.com](https://fozcaribe.com)
- **GitHub Issues**: Para bugs e sugestões
- **WhatsApp**: +351 XXX XXX XXX

## 📈 Estatísticas do Projeto

- ✅ **71 alunos** registados em 2024/25
- ✅ **4 turmas** ativas
- ✅ **2 cidades** (Foz do Arelho, Caldas da Rainha)
- ✅ **100%** paixão pela dança caribenha

## 📄 Licença

Este projeto está sob licença MIT. Ver ficheiro `LICENSE` para mais detalhes.

---

**Desenvolvido com ❤️ para a comunidade FozCaribe**

*Dança Caribenha • Paixão • Comunidade • Modernidade*
