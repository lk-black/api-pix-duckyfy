#!/bin/bash

# Script de produção sem Docker para API PIX Duckfy
echo "🚀 Preparando API PIX Duckfy para produção..."

# Verificar se Python está disponível
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale Python3 primeiro."
    exit 1
fi

# Verificar se pip está disponível
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Instale pip3 primeiro."
    exit 1
fi

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "❌ Arquivo .env não encontrado. Copie .env.example para .env e configure suas chaves."
    exit 1
fi

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "📋 Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Configurar variáveis de ambiente para produção
export FLASK_ENV=production

# Verificar se Gunicorn está instalado
if ! command -v gunicorn &> /dev/null; then
    echo "❌ Gunicorn não encontrado nas dependências."
    exit 1
fi

echo "✅ Preparação concluída!"
echo ""
echo "🚀 Para iniciar em produção, execute:"
echo "   source venv/bin/activate"
echo "   export FLASK_ENV=production"
echo "   gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 30 --access-logfile - app:app"
echo ""
echo "🔍 Para testar localmente:"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo "🌐 API estará disponível em: http://localhost:5000"
