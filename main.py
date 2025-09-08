from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
import os
import json
from datetime import datetime
import aiofiles
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import io


app = FastAPI(title="FozCaribe - Modern Web App", version="2.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Create directories if they don't exist
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("static/images", exist_ok=True)
os.makedirs("static/gallery", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("data", exist_ok=True)



# IDs das pastas do Google Drive para a galeria
FOLDER_ID = '1769MEGbRjrUFu_HbplMDY0fh-9meEVuA'

def get_drive_files(folder_id=None):
    """Busca arquivos de uma pasta específica do Google Drive"""
    if not GOOGLE_SHEETS_ENABLED or not drive_service:
        return []
    
    try:
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
    
    # Apre i fogli "Registrations" e "Attendance"
    preregistration_sheet = client.open("FozCaribe App").worksheet("Preregistrations")
    inscricao_sheet = client.open("FozCaribe App").worksheet("Inscricoes")
    users_sheet = client.open("FozCaribe App").worksheet("Users")
    
    print("✅ Google Sheets conectado com sucesso!")
    GOOGLE_SHEETS_ENABLED = True
except Exception as e:
    print(f"⚠️  Google Sheets não conectado: {e}")
    print("📝 A aplicação funcionará sem Google Sheets")
    preregistration_sheet = None
    inscricao_sheet = None
    users_sheet = None
    GOOGLE_SHEETS_ENABLED = False

@app.get("/preregister", response_class=HTMLResponse)
async def preregister_page(request: Request):
    return templates.TemplateResponse("preregister.html", {"request": request})

@app.post("/preregister")
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
    # Converter para os nomes usados no Google Sheets
    nome = name
    tel = phone
    cidade = city
    nivel = level
    tipo_inscricao = inscription_type
    estilo_danca = dance_style
    nota = message
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # Adicionar linha ao Google Sheets
        if GOOGLE_SHEETS_ENABLED and preregistration_sheet:
            preregistration_sheet.append_row([timestamp, nome, tel, cidade, nivel, tipo_inscricao, estilo_danca, nota or ""])
            print(f"✅ Dados salvos no Google Sheets: {nome} - {timestamp}")
        else:
            print(f"📝 Google Sheets não disponível. Dados: {nome}, {tel}, {cidade}")
        
        # Redirect to success page with name
        return templates.TemplateResponse("preregister_success.html", {
            "request": request,
            "registration": {"name": nome, "timestamp": timestamp}
        })
    except Exception as e:
        print(f"Erro no preregister: {e}")
        return templates.TemplateResponse("preregister.html", {
            "request": request,
            "error": "Falha na pré-inscrição. Por favor, tente novamente."
        })


@app.get("/inscricao", response_class=HTMLResponse)
async def inscricao_page(request: Request):
    """Página de inscrição completa"""
    return templates.TemplateResponse("inscricao.html", {"request": request})

@app.post("/inscricao")
async def inscricao_submit(request: Request):
    """Submissão do formulário de inscrição"""
    try:
        # Obter dados JSON do corpo da requisição
        data = await request.json()
        
        # Extrair informações do formulário
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        nome = data.get('nome', '')
        email = data.get('email', '')
        telefone = data.get('telefone', '')
        data_nascimento = data.get('data_nascimento', '')
        morada = data.get('morada', '')
        cidade = data.get('cidade', '')
        codigo_postal = data.get('codigo_postal', '')
        modalidade = data.get('modalidade', '')
        experiencia = data.get('experiencia', '')
        tipo_pagamento = data.get('tipo_pagamento', '')
        contacto_emergencia_nome = data.get('contacto_emergencia_nome', '')
        contacto_emergencia_telefone = data.get('contacto_emergencia_telefone', '')
        observacoes = data.get('observacoes', '')
        aceitar_termos = data.get('aceitar_termos', False)
        
        # Validações básicas
        if not all([nome, email, telefone, data_nascimento, cidade, modalidade, tipo_pagamento]):
            return JSONResponse(
                content={"success": False, "message": "Campos obrigatórios em falta"},
                status_code=400
            )
        
        if not aceitar_termos:
            return JSONResponse(
                content={"success": False, "message": "Deve aceitar os termos e condições"},
                status_code=400
            )
        
        # Salvar no Google Sheets
        if GOOGLE_SHEETS_ENABLED and inscricao_sheet:
            inscricao_sheet.append_row([
                timestamp, nome, email, telefone, data_nascimento, morada, 
                cidade, codigo_postal, modalidade, experiencia, tipo_pagamento,
                contacto_emergencia_nome, contacto_emergencia_telefone, observacoes
            ])
            print(f"✅ Inscrição salva no Google Sheets: {nome} - {timestamp}")
        else:
            print(f"📝 Google Sheets não disponível. Inscrição: {nome}, {email}")
        
        return JSONResponse(content={"success": True, "message": "Inscrição submetida com sucesso"})
        
    except Exception as e:
        print(f"Erro na inscrição: {e}")
        return JSONResponse(
            content={"success": False, "message": "Erro interno do servidor"},
            status_code=500
        )

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_submit(request: Request):
    """Submissão do formulário de login"""
    try:
        # Obter dados JSON do corpo da requisição
        data = await request.json()
        
        email = data.get('email', '')
        password = data.get('password', '')
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
                                    "redirect": "/dashboard",
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
                    "redirect": "/dashboard",
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

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard básico após login"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


def get_gallery_images():
    gallery_dir = "static/gallery"
    if os.path.exists(gallery_dir):
        images = []
        for filename in os.listdir(gallery_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                images.append({
                    "filename": filename,
                    "url": f"/static/gallery/{filename}"
                })
        return images
    return []

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

@app.get("/galeria", response_class=HTMLResponse)
async def galeria(request: Request):
    """Alias para galeria em português"""
    media_files = get_drive_files()
    
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
    
    return templates.TemplateResponse("gallery.html", {
        "request": request,
        "images": images
    })

@app.get("/galeria/conteudo-login", response_class=HTMLResponse)
async def galeria_conteudo_login(request: Request):
    """Página de login para conteúdo exclusivo"""
    return templates.TemplateResponse("galery_conteudo_login.html", {
        "request": request
    })

@app.post("/galeria/conteudo-login")
async def galeria_conteudo_login_post(
    request: Request,
    username: str = Form(...),
    pin: str = Form(...)
):
    """Verificação de login para conteúdo exclusivo"""
    try:
        if GOOGLE_SHEETS_ENABLED and preregistration_sheet:
            # Buscar usuários registrados (pode adaptar conforme sua necessidade)
            all_users = preregistration_sheet.get_all_values()[1:]  # Skip headers
            users_dict = {row[1].strip(): str(len(row[1])) for row in all_users}  # Nome → PIN simples
            
            # Verificação simples - pode melhorar conforme necessário
            if username.strip() in users_dict:
                return RedirectResponse(url=f"/galeria/conteudo/{username}/salsa", status_code=302)
        
        return templates.TemplateResponse("galery_conteudo_login.html", {
            "request": request,
            "error": "Nome ou PIN inválido"
        })
    except Exception as e:
        print(f"Erro no login: {e}")
        return templates.TemplateResponse("galery_conteudo_login.html", {
            "request": request,
            "error": "Erro no sistema de login"
        })

@app.get("/galeria/conteudo/{username}/bachata-fundamentos", response_class=HTMLResponse)
async def galeria_conteudo_bachata_fund(request: Request, username: str):
    """Galeria Bachata Fundamentos"""
    media_files = get_conteudo_bachata_fund()
    return templates.TemplateResponse("galery_conteudo_bachata_fund.html", {
        "request": request,
        "username": username,
        "media_files": media_files
    })

@app.get("/galeria/conteudo/{username}/bachata-intermedio", response_class=HTMLResponse)
async def galeria_conteudo_bachata_int(request: Request, username: str):
    """Galeria Bachata Intermédio"""
    media_files = get_conteudo_bachata_int()
    return templates.TemplateResponse("galery_conteudo_bachata_int.html", {
        "request": request,
        "username": username,
        "media_files": media_files
    })

@app.get("/galeria/conteudo/{username}/salsa", response_class=HTMLResponse)
async def galeria_conteudo_salsa(request: Request, username: str):
    """Galeria Salsa"""
    media_files = get_conteudo_salsa()
    return templates.TemplateResponse("galery_conteudo_salsa.html", {
        "request": request,
        "username": username,
        "media_files": media_files
    })

@app.get("/galeria/sunset", response_class=HTMLResponse)
async def galeria_sunset(request: Request):
    """Galeria Sunset (pública)"""
    media_files = get_sunset()
    return templates.TemplateResponse("galery_sunset.html", {
        "request": request,
        "media_files": media_files
    })

@app.get("/galeria/aulas", response_class=HTMLResponse)
async def galeria_aulas(request: Request):
    """Galeria de Aulas (pública)"""
    media_files = get_aulas()
    return templates.TemplateResponse("galery_aulas.html", {
        "request": request,
        "media_files": media_files
    })

# Funções para buscar arquivos das diferentes pastas do Google Drive
FOLDER_ID_bachata_int = "1U2RM0P-_88KN8Eibs7WJkbf4hozKAqPZ"
FOLDER_ID_bachata_fund = "1Fb7drcC1HwvLQGqCWvd9bkV0NTv0nzw4"
FOLDER_ID_salsa = "1OuBDGBqvUKxvNWM2vdJxPG_DlwZ2zcWo"
FOLDER_ID_sunset = "1gd64oEz09oFCh4VhqC09yfLSGAg4iJbB"
FOLDER_ID_aulas = "1kP8rVjVNBUaWYOcvEeCdI04q8NgB7Uy3"

def get_conteudo_bachata_fund():
    """Busca arquivos da pasta Bachata Fundamentos"""
    return get_drive_files(FOLDER_ID_bachata_fund)

def get_conteudo_bachata_int():
    """Busca arquivos da pasta Bachata Intermédio"""
    return get_drive_files(FOLDER_ID_bachata_int)

def get_conteudo_salsa():
    """Busca arquivos da pasta Salsa"""
    return get_drive_files(FOLDER_ID_salsa)

def get_sunset():
    """Busca arquivos da pasta Sunset"""
    return get_drive_files(FOLDER_ID_sunset)

def get_aulas():
    """Busca arquivos da pasta Aulas"""
    return get_drive_files(FOLDER_ID_aulas)

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
