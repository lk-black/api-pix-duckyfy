# API PIX Duckfy

Uma API simples para integração com a gateway de pagamentos Duckfy, permitindo criar pagamentos PIX de forma fácil e eficaz.

## 🚀 Instalação e Execução

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente
As chaves já estão configuradas no arquivo `.env`:
- `PUBLIC_KEY`: Sua chave pública da Duckfy
- `SECRET_KEY`: Sua chave secreta da Duckfy

### 3. Executar a API
```bash
python app.py
```

A API estará disponível em: `http://localhost:5000`

## 📚 Endpoints

### GET /health
Verifica se a API está funcionando.

**Resposta:**
```json
{
  "status": "OK",
  "message": "API PIX Duckfy funcionando",
  "timestamp": "2025-06-10T10:30:00"
}
```

### POST /pix/create
Cria um novo pagamento PIX.

**Body obrigatório:**
```json
{
  "amount": 100.50,
  "client": {
    "name": "João da Silva",
    "email": "joao@example.com",
    "phone": "(11) 99999-9999",
    "document": "123.456.789-00"
  }
}
```

**Body completo (com campos opcionais):**
```json
{
  "amount": 100.50,
  "client": {
    "name": "João da Silva",
    "email": "joao@example.com",
    "phone": "(11) 99999-9999",
    "document": "123.456.789-00"
  },
  "products": [
    {
      "id": "produto1",
      "name": "Produto Exemplo",
      "quantity": 1,
      "price": 100.50
    }
  ],
  "shippingFee": 0,
  "extraFee": 0,
  "discount": 0,
  "dueDate": "2025-06-11",
  "metadata": {
    "orderId": "12345",
    "source": "website"
  },
  "callbackUrl": "https://example.com/callback"
}
```

**Resposta de sucesso (201):**
```json
{
  "status": "success",
  "message": "PIX criado com sucesso",
  "data": {
    "transactionId": "clwuwmn4i0007emp9lgn66u1h",
    "status": "OK",
    "order": {
      "id": "cm92389asdaskdjkasjdka",
      "url": "https://api-de-pagamentos.com/order/cm92389asdaskdjkasjdka"
    },
    "pix": {
      "code": "00020101021126530014BR.GOV.BCB.PIX...",
      "base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQ...",
      "image": "https://api.gateway.com/pix/qr/..."
    }
  }
}
```

**Resposta de erro (400):**
```json
{
  "status": "error",
  "message": "Campos obrigatórios ausentes: amount, client"
}
```

### POST /pix/create/taxa-sedex
Endpoint dedicado para o produto Taxa Sedex (R$ 28,97).

**Body simplificado (dados do cliente + UTM):**
```json
{
  "client": {
    "name": "Maria Silva",
    "email": "maria@email.com",
    "phone": "(11) 99999-8888",
    "document": "44746461856"
  },
  "utm_source": "FB",
  "utm_campaign": "Taxa Sedex Promo|123456789",
  "utm_medium": "Interesse Correios|987654321",
  "utm_content": "Anuncio Sedex Barato|456789123",
  "utm_term": "feed"
}
```

**Características:**
- ✅ **Valor fixo**: R$ 28,97
- ✅ **Produto automático**: Taxa Sedex (código: Z29J23C)
- ✅ **UTM tracking**: Captura parâmetros do Facebook Ads
- ✅ **Simplificado**: Só precisa dos dados do cliente

**Resposta de sucesso (201):**
```json
{
  "status": "success",
  "message": "PIX Taxa Sedex criado com sucesso",
  "product": {
    "name": "Taxa Sedex",
    "code": "Z29J23C",
    "price": 28.97
  },
  "data": {
    "transactionId": "abc123xyz",
    "status": "PENDING",
    "pix": {
      "code": "00020101021126530014BR.GOV.BCB.PIX...",
      "image": "https://api.gateway.com/pix/qr/..."
    }
  },
  "tracking": {
    "utm_captured": true,
    "campaign": "Taxa Sedex Promo|123456789",
    "source": "FB"
  }
}
```

### GET /pix/example
Retorna um exemplo completo de como usar a API.

### GET /pix/example/utm
Retorna exemplos específicos para tracking UTM do Facebook Ads.

### GET /pix/example/taxa-sedex
Retorna exemplo específico do endpoint Taxa Sedex com integração JavaScript.

## 🔧 Campos

### Obrigatórios
- `amount` (number): Valor da transação em reais
- `client` (object): Dados do cliente
  - `name` (string): Nome do cliente
  - `email` (string): E-mail do cliente
  - `document` (string): CPF/CNPJ do cliente

### Opcionais
- `identifier` (string): Identificador único da transação (gerado automaticamente se não fornecido)
- `shippingFee` (number): Valor do frete
- `extraFee` (number): Outras taxas
- `discount` (number): Desconto
- `products` (array): Lista de produtos
- `dueDate` (string): Data de vencimento (YYYY-MM-DD, padrão: amanhã)
- `metadata` (object): Metadados da transação
- `callbackUrl` (string): URL para notificação de status

## 🧪 Testando a API

### Usando curl:
```bash
# Verificar se a API está funcionando
curl http://localhost:5000/health

# Criar um PIX
curl -X POST http://localhost:5000/pix/create \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50.00,
    "client": {
      "name": "Maria Silva",
      "email": "maria@example.com",
      "phone": "(11) 98765-4321",
      "document": "123.456.789-00"
    }
  }'

# Ver exemplo de uso
curl http://localhost:5000/pix/example

# Testar endpoint Taxa Sedex
curl -X POST https://api-pix-duckyfy.onrender.com/pix/create/taxa-sedex \
  -H "Content-Type: application/json" \
  -d '{
    "client": {
      "name": "Teste Taxa Sedex",
      "email": "teste@email.com",
      "phone": "(11) 99999-9999",
      "document": "44746461856"
    },
    "utm_source": "FB",
    "utm_campaign": "Teste Sedex|123",
    "utm_medium": "Audiencia|456",
    "utm_content": "Anuncio|789",
    "utm_term": "feed"
  }'

# Ver exemplo Taxa Sedex
curl https://api-pix-duckyfy.onrender.com/pix/example/taxa-sedex

# Ver exemplos UTM
curl https://api-pix-duckyfy.onrender.com/pix/example/utm
```

### Usando Python:
```python
import requests

# Criar PIX
response = requests.post('http://localhost:5000/pix/create', json={
    "amount": 75.50,
    "client": {
        "name": "Carlos Santos",
        "email": "carlos@example.com",
        "phone": "(11) 99999-8888",
        "document": "987.654.321-00"
    },
    "metadata": {
        "orderId": "ORDER-123",
        "source": "mobile_app"
    }
})

print(response.json())
```

## 🔐 Segurança

- As chaves de API são carregadas do arquivo `.env`
- Todas as requisições para a Duckfy incluem autenticação nos headers
- Validação completa dos dados de entrada
- Tratamento de erros detalhado

## 📝 Estrutura do Projeto

```
api-pix-duckfy/
├── app.py              # API principal
├── config.py           # Configurações por ambiente
├── requirements.txt    # Dependências Python
├── Dockerfile          # Imagem Docker
├── docker-compose.yml  # Orquestração Docker
├── deploy.sh          # Script de deploy automatizado
├── setup-production.sh # Setup manual para produção
├── render.yaml        # Configurações para Render
├── .env               # Chaves da Duckfy (não versionado)
├── .env.example       # Exemplo de configuração
├── .gitignore         # Arquivos ignorados pelo Git
├── .dockerignore      # Arquivos ignorados pelo Docker
├── README.md          # Esta documentação
├── DEPLOY_RENDER.md   # Guia de deploy na Render
├── UTM_TRACKING.md   # Guia de tracking Facebook Ads
├── API_DOCS.md       # Documentação simplificada
└── test_api.py        # Testes da API
└── test_taxa_sedex.py # Teste endpoint Taxa Sedex
```

## 🐳 Deploy com Docker (Recomendado)

### 1. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas chaves reais da Duckfy
```

### 2. Deploy automático
```bash
./deploy.sh
```

### 3. Deploy manual
```bash
# Construir e executar
docker-compose up -d

# Verificar logs
docker-compose logs -f api-pix

# Verificar status
docker-compose ps

# Parar serviços
docker-compose down
```

### 4. Características do deploy Docker
- **Gunicorn**: 4 workers para alta performance
- **Logs estruturados**: Adequados para produção
- **Health checks**: Monitoramento automático
- **Auto-restart**: Reinicia em caso de falha
- **Segurança**: Executa com usuário não-root
- **Otimizado**: Imagem slim para menor tamanho

## 🌐 Deploy na Nuvem

### Render (Recomendado - Gratuito)
Para deploy gratuito na Render, siga o guia completo:
**📖 [DEPLOY_RENDER.md](DEPLOY_RENDER.md)**

Características:
- ✅ Gratuito (750h/mês)
- ✅ SSL automático
- ✅ Deploy automático do GitHub
- ✅ Logs em tempo real

### Outras Plataformas
- **Heroku**: Similar ao Render, com plano gratuito limitado
- **Railway**: Alternativa moderna ao Heroku
- **DigitalOcean App Platform**: Para uso profissional
- **AWS/GCP/Azure**: Para enterprise

## 🚀 Deploy Manual (Produção)

1. Configure as variáveis de ambiente em seu servidor
2. Use um servidor WSGI como Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
3. Configure um proxy reverso (nginx) se necessário

## 📞 Suporte

Se encontrar algum problema ou tiver dúvidas, verifique:
1. Se as chaves da Duckfy estão corretas no `.env`
2. Se todas as dependências estão instaladas
3. Se os dados enviados estão no formato correto

## 🎯 Próximas Melhorias

- [ ] Adicionar logs estruturados
- [ ] Implementar cache para consultas
- [ ] Adicionar testes automatizados
- [ ] Implementar webhook para receber notificações
- [ ] Adicionar monitoramento e métricas
# api-pix-duckyfy
