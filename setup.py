# FozCaribe v2.0 - Setup Script
# Script de configuração rápida para desenvolvimento

import os
import sys
import subprocess
import json

def create_directories():
    """Criar diretorias necessárias"""
    directories = [
        "static/css",
        "static/js", 
        "static/images",
        "templates"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Criado diretório: {directory}")

def check_python_version():
    """Verificar versão do Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")

def install_dependencies():
    """Instalar dependências"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso")
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        sys.exit(1)

def check_credentials():
    """Verificar se credentials.json existe"""
    if os.path.exists("credentials.json"):
        print("✅ Arquivo credentials.json encontrado")
        try:
            with open("credentials.json", 'r') as f:
                json.load(f)
            print("✅ Arquivo credentials.json válido")
        except json.JSONDecodeError:
            print("⚠️  Arquivo credentials.json parece estar corrompido")
    else:
        print("⚠️  Arquivo credentials.json não encontrado")
        print("📝 Por favor, adicione suas credenciais do Google Cloud Platform")

def create_sample_data():
    """Criar configuração de exemplo se necessário"""
    if not os.path.exists("config.json"):
        sample_config = {
            "setup_date": "2025-01-01",
            "version": "2.0.0",
            "status": "configured"
        }
        with open("config.json", 'w') as f:
            json.dump(sample_config, f, indent=2)
        print("✅ Arquivo de configuração de exemplo criado")

def main():
    """Função principal de setup"""
    print("🌴 FozCaribe v2.0 - Setup")
    print("=" * 40)
    
    # Verificações
    check_python_version()
    
    # Criar estrutura
    create_directories()
    
    # Instalar dependências
    if os.path.exists("requirements.txt"):
        install_dependencies()
    else:
        print("⚠️  requirements.txt não encontrado")
    
    # Verificar credenciais
    check_credentials()
    
    # Criar dados de exemplo
    create_sample_data()
    
    print("\n🎉 Setup concluído!")
    print("📝 Próximos passos:")
    print("   1. Configure suas credenciais Google (credentials.json)")
    print("   2. Execute: python main.py")
    print("   3. Acesse: http://localhost:8000")

if __name__ == "__main__":
    main()
