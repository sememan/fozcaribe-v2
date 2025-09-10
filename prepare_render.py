#!/usr/bin/env python3
"""
FozCaribe v2.0 - Render Deploy Preparation Script
Script para preparar o projeto para deploy no Render
"""

import os
import json
import sys
import subprocess

def check_files():
    """Verificar se todos os ficheiros necessários existem"""
    required_files = [
        'main.py',
        'requirements.txt', 
        'build.sh',
        'Procfile',
        'README.md',
        '.gitignore'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Ficheiros em falta: {', '.join(missing_files)}")
        return False
    
    print("✅ Todos os ficheiros necessários estão presentes")
    return True

def check_git_status():
    """Verificar status do Git"""
    try:
        # Verificar se é um repositório Git
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Este não é um repositório Git")
            print("💡 Execute: git init && git add . && git commit -m 'Initial commit'")
            return False
        
        # Verificar se há alterações não commitadas
        if result.stdout.strip():
            print("⚠️  Há alterações não commitadas:")
            print(result.stdout)
            print("💡 Execute: git add . && git commit -m 'Deploy preparation'")
            return False
        
        print("✅ Repositório Git está limpo")
        return True
        
    except FileNotFoundError:
        print("❌ Git não está instalado")
        return False

def check_credentials():
    """Verificar credenciais Google"""
    if not os.path.exists('credentials.json'):
        print("⚠️  credentials.json não encontrado")
        print("📝 Adicione suas credenciais do Google Cloud Platform")
        return False
    
    try:
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
        
        required_keys = ['type', 'project_id', 'private_key', 'client_email']
        missing_keys = [key for key in required_keys if key not in creds]
        
        if missing_keys:
            print(f"❌ Chaves em falta no credentials.json: {', '.join(missing_keys)}")
            return False
        
        print("✅ Credenciais Google válidas")
        return True
        
    except json.JSONDecodeError:
        print("❌ credentials.json não é um JSON válido")
        return False

def check_requirements():
    """Verificar requirements.txt"""
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        essential_packages = ['fastapi', 'uvicorn', 'jinja2', 'gspread']
        missing_packages = []
        
        for package in essential_packages:
            if package not in content:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"⚠️  Pacotes essenciais podem estar em falta: {', '.join(missing_packages)}")
            return False
        
        print("✅ requirements.txt parece estar correto")
        return True
        
    except FileNotFoundError:
        print("❌ requirements.txt não encontrado")
        return False

def generate_env_vars():
    """Gerar lista de variáveis de ambiente para Render"""
    env_vars = {
        'PYTHON_VERSION': '3.9.16',
        'GOOGLE_SHEETS_NAME': 'FozCaribe App',
        'APP_NAME': 'FozCaribe',
        'APP_VERSION': '2.0.0',
        'TIMEZONE': 'Europe/Lisbon',
        'LOG_LEVEL': 'INFO',
        'FOLDER_ID_MAIN': '1769MEGbRjrUFu_HbplMDY0fh-9meEVuA'
    }
    
    print("\n📝 Variáveis de ambiente para configurar no Render:")
    print("=" * 50)
    for key, value in env_vars.items():
        print(f"{key}={value}")
    
    return env_vars

def main():
    """Função principal"""
    print("🚀 FozCaribe v2.0 - Preparação para Render Deploy")
    print("=" * 55)
    
    checks = [
        ("Ficheiros do projeto", check_files),
        ("Status do Git", check_git_status),
        ("Credenciais Google", check_credentials),
        ("Requirements.txt", check_requirements)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n🔍 Verificando: {check_name}")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 55)
    
    if all_passed:
        print("🎉 Projeto pronto para deploy no Render!")
        print("\n📋 Próximos passos:")
        print("1. Fazer push para GitHub (se ainda não fez)")
        print("2. Ir para render.com e criar Web Service")
        print("3. Conectar repositório GitHub")
        print("4. Configurar variáveis de ambiente (lista abaixo)")
        print("5. Fazer deploy!")
        
        generate_env_vars()
        
        # Oferecer para abrir o guia
        print(f"\n📖 Guia completo disponível em: DEPLOY_RENDER.md")
        
    else:
        print("❌ Alguns problemas precisam ser resolvidos antes do deploy")
        print("💡 Corrija os problemas acima e execute novamente")
        sys.exit(1)

if __name__ == "__main__":
    main()
