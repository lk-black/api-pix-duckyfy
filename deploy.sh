#!/bin/bash

# Script de deploy para API PIX Duckfy
echo "🚀 Iniciando deploy da API PIX Duckfy..."

# Verificar se o Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Inicie o Docker primeiro."
    exit 1
fi

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo "❌ Arquivo .env não encontrado. Copie .env.example para .env e configure suas chaves."
    exit 1
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Rebuild da imagem
echo "🔨 Construindo nova imagem..."
docker-compose build --no-cache

# Iniciar os serviços
echo "🚀 Iniciando serviços..."
docker-compose up -d

# Verificar status
echo "⏳ Aguardando serviços iniciarem..."
sleep 10

# Teste de saúde
echo "🔍 Verificando saúde da API..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ API está funcionando!"
    echo "🌐 API disponível em: http://localhost:5000"
    echo "📖 Documentação: http://localhost:5000/pix/example"
else
    echo "❌ API não está respondendo. Verificando logs..."
    docker-compose logs api-pix
fi

echo "📊 Para ver logs: docker-compose logs -f api-pix"
echo "🛑 Para parar: docker-compose down"
