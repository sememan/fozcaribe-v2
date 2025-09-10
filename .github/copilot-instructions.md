# FozCaribe v2.0 - AI Coding Agent Instructions

## Project Architecture

**FastAPI + Google Cloud Integration**: Modern dance school web app with Portuguese localization, built as a single-file monolith (`main.py`) with external Google Services for data persistence and media storage.

### Core Components
- **Backend**: FastAPI app with Jinja2 templates, serving both API endpoints and rendered HTML
- **Data Layer**: Google Sheets as database (Preregistrations, Registrations, Users worksheets)
- **Media Storage**: Google Drive with authenticated proxy serving (`/drive-image/{file_id}`)
- **Frontend**: Tailwind CSS + vanilla JS, no build process required

### Key Integration Pattern
```python
# Google Services initialization with graceful fallback
try:
    credentials = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(credentials)
    drive_service = build("drive", "v3", credentials=credentials)
    GOOGLE_SHEETS_ENABLED = True
except Exception:
    GOOGLE_SHEETS_ENABLED = False  # App continues without external services
```

## Critical Development Workflows

### Local Development
```bash
# ALWAYS use the virtual environment Python binary
/Users/emanuele/PycharmProjects/fozcaribe.v2/venv/bin/python -m uvicorn main:app --reload --port 8000
```

### Google Sheets Auto-Creation Pattern
Worksheets are created on-demand if missing:
```python
try:
    sheet = spreadsheet.worksheet("SheetName")
except gspread.WorksheetNotFound:
    sheet = spreadsheet.add_worksheet("SheetName", rows=1000, cols=10)
    sheet.append_row(['Header1', 'Header2', ...])  # Always add headers
```

### Template Inheritance Strategy
- `base.html`: Shared navigation, Tailwind config, brand colors
- Page templates: Either extend base (`{% extends "base.html" %}`) or standalone with full styling
- Portuguese language throughout (`lang="pt"`)

## Project-Specific Conventions

### Form Processing Patterns
**Different forms = different endpoints + worksheets**:
- `/preregister` → "Preregistrations" sheet (quick signup)
- `/register` → "Registrations" sheet (detailed form with experience, goals)
- `/inscricao` template exists but endpoint was removed (avoid confusion)

### Google Drive Folder Structure
Multiple hardcoded folder IDs for different galleries:
```python
FOLDER_ID = '1769MEGbRjrUFu_HbplMDY0fh-9meEVuA'  # Main gallery
FOLDER_ID_bachata_fund = "1Fb7drcC1HwvLQGqCWvd9bkV0NTv0nzw4"  # Course content
FOLDER_ID_salsa = "1OuBDGBqvUKxvNWM2vdJxPG_DlwZ2zcWo"
# etc.
```

### Error Handling Philosophy
- External service failures don't break the app (graceful degradation)
- Always provide Portuguese error messages in templates
- Use console logging for debugging: `print(f"✅ Success: {details}")` or `print(f"❌ Error: {error}")`

## Cross-Component Communication

### Media Serving Architecture
Google Drive files are proxied through FastAPI to handle authentication:
```python
@app.get("/drive-image/{file_id}")
async def serve_drive_image(file_id: str):
    # Downloads from Google Drive, streams to client with proper headers
```

### Template Data Flow
Controllers pass minimal context to templates:
```python
return templates.TemplateResponse("template.html", {
    "request": request,
    "registration": {"name": nome, "timestamp": timestamp}
})
```

### Deployment Configuration
- **Render.com ready**: `build.sh`, `Procfile`, `render.yaml` all configured
- **Environment variables**: Store Google credentials as `GOOGLE_CREDENTIALS_JSON`
- **Static files**: Served directly by FastAPI, no CDN required

## Key Files for Understanding
- `main.py`: Single-file application (595 lines) - start here
- `templates/base.html`: Navigation + Tailwind configuration
- `templates/index.html`: Homepage with 5-column statistics grid
- `requirements.txt`: All dependencies (google-api-python-client, gspread, fastapi)
- `DEPLOY_RENDER.md`: Complete deployment instructions

## Portuguese Context
- All user-facing text in Portuguese (Portugal variant)
- Form field names use Portuguese: `nome`, `telefone`, `cidade`
- Business logic reflects Portuguese dance school operations
- Timestamps use Portuguese format: `%Y-%m-%d %H:%M:%S`
