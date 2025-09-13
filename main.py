from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import os
import bleach
import re
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import io


# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="FozCaribe - Modern Web App", version="2.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Security: Input sanitization functions
def sanitize_text_input(text: str, max_length: int = 200) -> str:
    """Sanitize text input to prevent XSS and limit length"""
    if not text:
        return ""
    
    # Remove HTML tags and limit length
    sanitized = bleach.clean(text.strip(), tags=[], strip=True)
    return sanitized[:max_length]

def sanitize_phone(phone: str) -> str:
    """Sanitize phone number - only digits, spaces, +, -, ()"""
    if not phone:
        return ""
    
    # Allow only phone-related characters
    return re.sub(r'[^0-9\+\-\(\)\s]', '', phone.strip())[:20]

def sanitize_email(email: str) -> str:
    """Basic email sanitization"""
    if not email:
        return ""
    
    email = email.strip().lower()
    # Basic email validation
    if '@' in email and '.' in email.split('@')[1]:
        return email[:100]
    return ""

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Error handlers
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    elif exc.status_code == 500:
        return templates.TemplateResponse("500.html", {"request": request}, status_code=500)
    else:
        return await http_exception_handler(request, exc)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return templates.TemplateResponse("500.html", {"request": request}, status_code=400)

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    print(f"❌ Unhandled exception: {exc}")
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)

# Create directories if they don't exist
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)



# IDs das pastas do Google Drive para a galeria
FOLDER_ID = '1769MEGbRjrUFu_HbplMDY0fh-9meEVuA'

def get_drive_files(folder_id=None):
    """Busca arquivos de uma pasta específica do Google Drive"""
    try:
        # Tentar usar o drive_service se disponível
        if 'drive_service' in globals() and drive_service:
            folder_id = folder_id or FOLDER_ID
            query = f"'{folder_id}' in parents and (mimeType contains 'image/' or mimeType contains 'video/')"
            
            results = drive_service.files().list(
                q=query,
                fields="nextPageToken, files(id, name, mimeType, webViewLink, webContentLink)"
            ).execute()
            
            items = results.get('files', [])
            
            media_files = []
            for item in items:
                file_id = item['id']
                is_video = 'video' in item['mimeType']
                
                if is_video:
                    # Para vídeos, usar embed URL do Google Drive
                    download_url = f"https://drive.google.com/file/d/{file_id}/preview"
                    thumbnail_url = f"https://drive.google.com/thumbnail?id={file_id}&sz=w400"
                else:
                    # Para imagens, usar nosso proxy local
                    download_url = f"/drive-image/{file_id}"
                    thumbnail_url = f"/drive-image/{file_id}"
                
                media_files.append({
                    'id': item['id'],
                    'name': item['name'],
                    'mimeType': item['mimeType'],
                    'webViewLink': item['webViewLink'],
                    'downloadLink': download_url,
                    'thumbnail_url': thumbnail_url,
                    'isVideo': is_video,
                    'isImage': 'image' in item['mimeType']
                })
            
            print(f"✅ Encontrados {len(media_files)} arquivos na pasta {folder_id}")
            if media_files:
                example = media_files[0]
                print(f"🔗 URL de exemplo ({example['mimeType']}): {example['downloadLink']}")
            return media_files
        else:
            print("⚠️  Google Drive não disponível - usando galeria local")
            return []
    except Exception as e:
        print(f"Erro ao buscar arquivos do Drive: {e}")
        return []


# Autenticazione con Google Sheets
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

try:
    credentials = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(credentials)
    drive_service = build("drive", "v3", credentials=credentials)
    
    # Tentar abrir as planilhas (criar se não existirem)
    spreadsheet = client.open("FozCaribe App")

    # Verificar e criar planilhas necessárias
    try:
        registration_sheet = spreadsheet.worksheet("Registrations")
    except gspread.WorksheetNotFound:
        registration_sheet = spreadsheet.add_worksheet("Registrations", rows=1000, cols=10)
        # Add headers matching your Google Sheets structure
        registration_sheet.append_row(['Timestamp', 'Nome', 'Tel', 'Cidade', 'Nascimento', 'Inscrição', 'Nota'])

    try:
        preregistration_sheet = spreadsheet.worksheet("Preregistrations")
    except gspread.WorksheetNotFound:
        preregistration_sheet = spreadsheet.add_worksheet("Preregistrations", rows=1000, cols=10)
        # Adicionar cabeçalhos
        preregistration_sheet.append_row(['Timestamp', 'Nome', 'Telefone', 'Cidade', 'Nivel', 'Tipo_Inscricao', 'Estilo_Danca', 'Nota'])
    
    try:
        users_sheet = spreadsheet.worksheet("Users")
    except gspread.WorksheetNotFound:
        users_sheet = spreadsheet.add_worksheet("Users", rows=1000, cols=10)
        # Adicionar cabeçalhos
        users_sheet.append_row(['Nome', 'Email', 'Telefone', 'Timestamp'])
    
    print("✅ Google Sheets conectado com sucesso!")
    print(f"📊 Planilhas disponíveis: Registrations, Preregistrations, Users")
    GOOGLE_SHEETS_ENABLED = True
except Exception as e:
    print(f"⚠️  Google Sheets não conectado: {e}")
    print("📝 A aplicação funcionará sem Google Sheets")
    registration_sheet = None
    preregistration_sheet = None
    users_sheet = None
    GOOGLE_SHEETS_ENABLED = False

@app.get("/preregister", response_class=HTMLResponse)
async def preregister_page(request: Request):
    return templates.TemplateResponse("preregister.html", {"request": request})

@app.post("/preregister")
@limiter.limit("5/minute")
async def preregister(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(None),
    city: str = Form(...),
    level: str = Form(...),  # Mensalidade e Nível
    inscription_type: str = Form(...),
    dance_style: str = Form(...),  # Novo campo
    message: str = Form(None)  # Default empty if not provided
):
    # Security: Sanitize all inputs
    nome = sanitize_text_input(name, 100)
    tel = sanitize_phone(phone)
    email_clean = sanitize_email(email) if email else ""
    cidade = sanitize_text_input(city, 100)
    nivel = sanitize_text_input(level, 50)
    registration_type = sanitize_text_input(inscription_type, 50)
    estilo_danca = sanitize_text_input(dance_style, 50)
    nota = sanitize_text_input(message, 500) if message else ""
    
    # Validate required fields
    if not nome or not tel or not cidade:
        raise HTTPException(status_code=400, detail="Campos obrigatórios em falta")
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # Adicionar linha ao Google Sheets
        if GOOGLE_SHEETS_ENABLED and preregistration_sheet:
            preregistration_sheet.append_row([timestamp, nome, tel, cidade, nivel, registration_type, estilo_danca, nota or ""])
            print(f"✅ Dados salvos no Google Sheets: {nome} - {timestamp}")
        else:
            print(f"📝 Google Sheets não disponível. Dados: {nome}, {tel}, {cidade}")
        
        # Redirect to success page with complete registration data
        registration_id = f"PRE{timestamp.replace('-', '').replace(':', '').replace(' ', '')}"
        return templates.TemplateResponse("preregister_success.html", {
            "request": request,
            "registration": {
                "id": registration_id,
                "name": nome,
                "phone": tel,
                "email": email_clean,
                "city": cidade,
                "level": nivel,
                "inscription_type": registration_type,
                "dance_style": estilo_danca,
                "message": nota,
                "timestamp": timestamp
            }
        })
    except Exception as e:
        print(f"Erro no preregister: {e}")
        return templates.TemplateResponse("preregister.html", {
            "request": request,
            "error": "Falha na pré-inscrição. Por favor, tente novamente."
        })


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Página de registo completo"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
@limiter.limit("3/minute")
async def register(
    request: Request,
    nome: str = Form(...),
    telefone: str = Form(...),
    cidade: str = Form(...),
    month: str = Form(...),      # Month from select
    day: str = Form(...),        # Day from select
    inscricao: str = Form(...),  # Registration type
    nota: str = Form(None),      # Optional note
    aceito_termos: str = Form(None)  # Terms acceptance checkbox
):
    """Submissão do formulário de registo completo"""
    
    # Security: Sanitize all inputs
    nome_clean = sanitize_text_input(nome, 100)
    telefone_clean = sanitize_phone(telefone)
    cidade_clean = sanitize_text_input(cidade, 100)
    inscricao_clean = sanitize_text_input(inscricao, 100)
    nota_clean = sanitize_text_input(nota, 500) if nota else ""
    
    # Validate terms acceptance
    if not aceito_termos:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Deve aceitar os termos e condições para completar o registo."
        })
    
    # Format birth date like in Flask app
    month_str = str(int(str(month)))
    day_str = str(int(str(day)))
    if len(month_str) == 1:
        month_str = f"0{month_str}"
    if len(day_str) == 1:
        day_str = f"0{day_str}"
    nascimento = f"{month_str}/{day_str}"
    
    # Validate required fields
    if not nome_clean or not telefone_clean or not cidade_clean:
        raise HTTPException(status_code=400, detail="Campos obrigatórios em falta ou inválidos")
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # Save to Google Sheets with correct column structure
        if GOOGLE_SHEETS_ENABLED and registration_sheet:
            registration_sheet.append_row([
                timestamp,      # A: Timestamp
                nome_clean,     # B: Nome
                telefone_clean, # C: Tel
                cidade_clean,   # D: Cidade
                nascimento,     # E: Nascimento (formatted MM/DD)
                inscricao_clean,  # F: Inscrição
                nota_clean        # G: Nota
            ])
            print(f"✅ Registo completo salvo no Google Sheets: {nome_clean} - {timestamp}")
        else:
            print(f"📝 Google Sheets não disponível. Registo: {nome_clean}, {telefone_clean}, {cidade_clean}")
        
        # Redirect to success page
        return templates.TemplateResponse("register_success.html", {
            "request": request,
            "registration": {"name": nome_clean, "timestamp": timestamp}
        })
    except Exception as e:
        print(f"Erro no registo: {e}")
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Falha no registo. Por favor, tente novamente."
        })
    except Exception as e:
        print(f"Erro no registo: {e}")
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Falha no registo. Por favor, tente novamente."
        })


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
@limiter.limit("10/minute")
async def login_submit(request: Request):
    """Submissão do formulário de login"""
    try:
        # Obter dados JSON do corpo da requisição
        data = await request.json()
        
        email = sanitize_email(data.get('email', ''))
        password = data.get('password', '')[:100]  # Limit password length
        remember = data.get('remember', False)
        
        # Validações básicas
        if not email or not password:
            return JSONResponse(
                content={"success": False, "message": "Email e palavra-passe são obrigatórios"},
                status_code=400
            )
        
        # Verificar credenciais no Google Sheets
        if GOOGLE_SHEETS_ENABLED and users_sheet:
            try:
                all_users = users_sheet.get_all_values()
                
                # Assumindo que a primeira linha são os cabeçalhos
                if len(all_users) > 1:
                    for row in all_users[1:]:  # Skip header
                        if len(row) >= 3 and row[1].strip().lower() == email.lower():
                            stored_password = row[2].strip()
                            user_name = row[0].strip()
                            
                            # Verificação simples de senha (em produção, usar hash)
                            if stored_password == password:
                                return JSONResponse(content={
                                    "success": True, 
                                    "message": "Login efetuado com sucesso",
                                    "redirect": "/",
                                    "user": user_name
                                })
                
                return JSONResponse(
                    content={"success": False, "message": "Credenciais inválidas"},
                    status_code=401
                )
                
            except Exception as e:
                print(f"Erro ao verificar credenciais: {e}")
                return JSONResponse(
                    content={"success": False, "message": "Erro na verificação de credenciais"},
                    status_code=500
                )
        else:
            # Se Google Sheets não estiver disponível, simulação para desenvolvimento
            if email == "admin@fozcaribe.com" and password == "admin123":
                return JSONResponse(content={
                    "success": True, 
                    "message": "Login efetuado com sucesso",
                    "redirect": "/",
                    "user": "Administrador"
                })
            else:
                return JSONResponse(
                    content={"success": False, "message": "Credenciais inválidas"},
                    status_code=401
                )
        
    except Exception as e:
        print(f"Erro no login: {e}")
        return JSONResponse(
            content={"success": False, "message": "Erro interno do servidor"},
            status_code=500
        )

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/gallery", response_class=HTMLResponse)
async def gallery(request: Request):
    """Galeria principal com imagens do Google Drive"""
    media_files = get_drive_files()
    
    print(f"🔍 Debug: Encontrados {len(media_files)} arquivos do Google Drive")
    
    # Converter para formato compatível com template existente
    images = []
    for media in media_files:
        images.append({
            "filename": media['name'],
            "url": media['downloadLink'],
            "id": media['id'],
            "mimeType": media['mimeType'],
            "isVideo": media['isVideo'],
            "isImage": media['isImage']
        })
    
    print(f"🔍 Debug: Convertidos {len(images)} imagens para o template")
    
    return templates.TemplateResponse("gallery.html", {
        "request": request,
        "images": images
    })

@app.get("/drive-image/{file_id}")
async def serve_drive_image(file_id: str):
    """Proxy para servir imagens do Google Drive com autenticação"""
    try:
        if not GOOGLE_SHEETS_ENABLED or not drive_service:
            return HTMLResponse("Google Drive não disponível", status_code=503)
        
        # Obter informações do arquivo primeiro
        file_metadata = drive_service.files().get(fileId=file_id).execute()
        mime_type = file_metadata.get('mimeType', 'application/octet-stream')
        file_name = file_metadata.get('name', 'unknown')
        
        print(f"🔍 Tentando servir arquivo: {file_name} ({mime_type})")
        
        # Baixar o arquivo do Google Drive
        file_content = drive_service.files().get_media(fileId=file_id).execute()
        
        print(f"✅ Arquivo {file_name} servido com sucesso")
        
        # Retornar como streaming response
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type=mime_type,
            headers={
                "Cache-Control": "max-age=3600",  # Cache por 1 hora
                "Content-Disposition": f"inline; filename={file_name}"
            }
        )
    except Exception as e:
        print(f"❌ Erro ao servir arquivo {file_id}: {e}")
        
        # Se falhar, tentar retornar um placeholder ou redirecionar para webViewLink
        try:
            file_metadata = drive_service.files().get(fileId=file_id).execute()
            web_view_link = file_metadata.get('webViewLink')
            file_name = file_metadata.get('name', 'unknown')
            
            print(f"🔄 Redirecionando para webViewLink: {file_name}")
            return RedirectResponse(url=web_view_link)
        except:
            return HTMLResponse("Arquivo não encontrado ou sem permissão", status_code=404)






if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
