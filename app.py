import os
import uuid
import requests
import logging
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime, timedelta
from config import config

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging para produção
if os.environ.get('FLASK_ENV') == 'production':
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Configurar app baseado no ambiente
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config.get(config_name, config['default']))

CORS(app)

# Configurações
DUCKFY_BASE_URL = "https://app.duckfyoficial.com/api/v1"
PUBLIC_KEY = os.getenv('PUBLIC_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')

if not PUBLIC_KEY or not SECRET_KEY:
    raise ValueError("Chaves PUBLIC_KEY e SECRET_KEY devem estar definidas no arquivo .env")

class DuckfyAPIError(Exception):
    """Exceção customizada para erros da API Duckfy"""
    def __init__(self, message, status_code=None, error_code=None, details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details

def generate_unique_identifier():
    """Gera um identificador único para a transação"""
    return str(uuid.uuid4())[:10]

def validate_pix_request(data):
    """Valida os dados da requisição PIX"""
    required_fields = ['amount', 'client']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        raise ValueError(f"Campos obrigatórios ausentes: {', '.join(missing_fields)}")
    
    # Validar campo client
    if not isinstance(data['client'], dict):
        raise ValueError("Campo 'client' deve ser um objeto")
    
    required_client_fields = ['name', 'email', 'cpf']
    missing_client_fields = [field for field in required_client_fields if field not in data['client']]
    
    if missing_client_fields:
        raise ValueError(f"Campos obrigatórios do cliente ausentes: {', '.join(missing_client_fields)}")
    
    # Validar valor
    if not isinstance(data['amount'], (int, float)) or data['amount'] <= 0:
        raise ValueError("Campo 'amount' deve ser um número positivo")

def create_pix_payment(pix_data):
    """Faz a requisição para a API Duckfy para criar o pagamento PIX"""
    headers = {
        'x-public-key': PUBLIC_KEY,
        'x-secret-key': SECRET_KEY,
        'Content-Type': 'application/json'
    }
    
    url = f"{DUCKFY_BASE_URL}/gateway/pix/receive"
    
    # Log para debugging
    if app.config.get('DEBUG'):
        print(f"🔗 Fazendo requisição para: {url}")
        print(f"📤 Dados enviados: {pix_data}")
        print(f"🔑 Headers: {headers}")
    else:
        logging.info(f"Creating PIX payment for amount: {pix_data.get('amount')}")
    
    try:
        response = requests.post(url, json=pix_data, headers=headers, timeout=30)
        
        if app.config.get('DEBUG'):
            print(f"📥 Status Code: {response.status_code}")
            print(f"📥 Response Headers: {dict(response.headers)}")
            print(f"📥 Response Text: {response.text}")
        else:
            logging.info(f"Duckfy API response status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            raise DuckfyAPIError(
                message=error_data.get('message', f'Erro da gateway (Status: {response.status_code}). Response: {response.text}'),
                status_code=response.status_code,
                error_code=error_data.get('errorCode'),
                details=error_data.get('details')
            )
    
    except requests.RequestException as e:
        logging.error(f"Connection error with Duckfy API: {str(e)}")
        raise DuckfyAPIError(f"Erro de conexão com a gateway: {str(e)}")

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return jsonify({
        'status': 'OK',
        'message': 'API PIX Duckfy funcionando',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/pix/create', methods=['POST'])
def create_pix():
    """
    Endpoint para criar um pagamento PIX
    
    Body esperado:
    {
        "amount": 100.50,
        "client": {
            "name": "João da Silva",
            "email": "joao@example.com",
            "phone": "(11) 99999-9999",
            "cpf": "123.456.789-00"
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
        "metadata": {},
        "callbackUrl": "https://example.com/callback"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Dados JSON não fornecidos',
                'status': 'error'
            }), 400
        
        # Validar dados
        validate_pix_request(data)
        
        # Processar parâmetros UTM do Facebook Ads
        utm_tracking = process_utm_parameters(data)
        
        # Preparar dados para a Duckfy
        pix_data = {
            'identifier': data.get('identifier', generate_unique_identifier()),
            'amount': data['amount'],
            'client': data['client']
        }
        
        # Campos opcionais
        optional_fields = ['shippingFee', 'extraFee', 'discount', 'products', 'splits', 'dueDate', 'callbackUrl']
        for field in optional_fields:
            if field in data:
                pix_data[field] = data[field]
        
        # Combinar metadata existente com tracking UTM
        existing_metadata = data.get('metadata', {})
        if isinstance(existing_metadata, str):
            try:
                existing_metadata = json.loads(existing_metadata)
            except:
                existing_metadata = {'original_metadata': existing_metadata}
        
        # Criar metadata final com tracking
        final_metadata = {
            **existing_metadata,
            'tracking': utm_tracking
        }
        
        pix_data['metadata'] = final_metadata
        
        # Se não foi fornecida uma data de vencimento, usar 1 dia a partir de hoje
        if 'dueDate' not in pix_data:
            tomorrow = datetime.now() + timedelta(days=1)
            pix_data['dueDate'] = tomorrow.strftime('%Y-%m-%d')
        
        # Fazer requisição para a Duckfy
        result = create_pix_payment(pix_data)
        
        # Preparar resposta com informações de tracking
        response_data = {
            'status': 'success',
            'message': 'PIX criado com sucesso',
            'data': result
        }
        
        # Adicionar informações de tracking se capturado
        if utm_tracking:
            response_data['tracking'] = {
                'utm_captured': True,
                'parameters': list(utm_tracking.keys()),
                'campaign': utm_tracking.get('utm_campaign', 'unknown'),
                'source': utm_tracking.get('utm_source', 'unknown')
            }
        
        return jsonify(response_data), 201
    
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    
    except DuckfyAPIError as e:
        return jsonify({
            'status': 'error',
            'message': e.message,
            'errorCode': e.error_code,
            'details': e.details
        }), e.status_code or 500
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro interno do servidor: {str(e)}'
        }), 500

@app.route('/pix/create/taxa-sedex', methods=['POST'])
def create_pix_taxa_sedex():
    """
    Endpoint específico para o produto Taxa Sedex
    
    Body esperado (simplificado):
    {
        "client": {
            "name": "João da Silva",
            "email": "joao@example.com",
            "phone": "(11) 99999-9999",
            "cpf": "123.456.789-00"
        },
        "utm_source": "FB",
        "utm_campaign": "Campanha Black Friday|123456789",
        "utm_medium": "Audiencia Lookalike|987654321",
        "utm_content": "Video VSL 30s|456789123",
        "utm_term": "feed"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Dados JSON não fornecidos',
                'status': 'error'
            }), 400
        
        # Validar apenas dados do cliente
        if 'client' not in data or not isinstance(data['client'], dict):
            return jsonify({
                'status': 'error',
                'message': 'Campo "client" é obrigatório e deve ser um objeto'
            }), 400
        
        required_client_fields = ['name', 'email', 'cpf']
        missing_client_fields = [field for field in required_client_fields if field not in data['client']]
        
        if missing_client_fields:
            return jsonify({
                'status': 'error',
                'message': f"Campos obrigatórios do cliente ausentes: {', '.join(missing_client_fields)}"
            }), 400
        
        # Processar parâmetros UTM
        utm_tracking = process_utm_parameters(data)
        
        # Dados fixos do produto Taxa Sedex
        produto_taxa_sedex = {
            "id": "Z29J23C",
            "name": "Taxa Sedex",
            "quantity": 1,
            "price": 28.97
        }
        
        # Preparar dados completos para a Duckfy
        pix_data = {
            'identifier': f"SEDEX_{generate_unique_identifier()}",
            'amount': 28.97,
            'client': data['client'],
            'products': [produto_taxa_sedex],
            'metadata': {
                'product_type': 'taxa_sedex',
                'product_code': 'Z29J23C',
                'auto_generated': True,
                'api_endpoint': '/pix/create/taxa-sedex',
                'tracking': utm_tracking
            }
        }
        
        # Adicionar data de vencimento (1 dia)
        tomorrow = datetime.now() + timedelta(days=1)
        pix_data['dueDate'] = tomorrow.strftime('%Y-%m-%d')
        
        # Log específico para Taxa Sedex
        if utm_tracking:
            logging.info(f"Taxa Sedex PIX created with UTM: {utm_tracking.get('utm_campaign', 'unknown')}")
        
        # Fazer requisição para a Duckfy
        result = create_pix_payment(pix_data)
        
        # Preparar resposta específica
        response_data = {
            'status': 'success',
            'message': 'PIX Taxa Sedex criado com sucesso',
            'product': {
                'name': 'Taxa Sedex',
                'code': 'Z29J23C',
                'price': 28.97
            },
            'data': result
        }
        
        # Adicionar informações de tracking se capturado
        if utm_tracking:
            response_data['tracking'] = {
                'utm_captured': True,
                'parameters': list(utm_tracking.keys()),
                'campaign': utm_tracking.get('utm_campaign', 'unknown'),
                'source': utm_tracking.get('utm_source', 'unknown')
            }
        
        return jsonify(response_data), 201
    
    except DuckfyAPIError as e:
        return jsonify({
            'status': 'error',
            'message': e.message,
            'errorCode': e.error_code,
            'details': e.details
        }), e.status_code or 500
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro interno do servidor: {str(e)}'
        }), 500

@app.route('/pix/example', methods=['GET'])
def pix_example():
    """Endpoint que retorna um exemplo de como usar a API"""
    example = {
        "example_request": {
            "url": "/pix/create",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": {
                "amount": 100.50,
                "client": {
                    "name": "João da Silva",
                    "email": "joao@example.com",
                    "phone": "(11) 99999-9999",
                    "cpf": "123.456.789-00"
                },
                "products": [
                    {
                        "id": "produto1",
                        "name": "Produto Exemplo",
                        "quantity": 1,
                        "price": 100.50
                    }
                ],
                "metadata": {
                    "orderId": "12345",
                    "source": "website"
                }
            }
        },
        "expected_response": {
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
    }
    
    return jsonify(example)

@app.route('/pix/example/utm', methods=['GET'])
def pix_utm_example():
    """Endpoint que retorna exemplos específicos para tracking UTM do Facebook Ads"""
    example = {
        "facebook_ads_url_example": {
            "description": "Configure esta URL no seu Facebook Ads como página de destino",
            "url": "https://seusite.com/checkout?utm_source=FB&utm_campaign={{campaign.name}}|{{campaign.id}}&utm_medium={{adset.name}}|{{adset.id}}&utm_content={{ad.name}}|{{ad.id}}&utm_term={{placement}}"
        },
        "api_request_example": {
            "url": "/pix/create",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": {
                "amount": 197.90,
                "client": {
                    "name": "João da Silva",
                    "email": "joao@example.com",
                    "phone": "(11) 99999-9999",
                    "cpf": "44746461856"
                },
                "products": [
                    {
                        "id": "curso_001",
                        "name": "Curso Online",
                        "quantity": 1,
                        "price": 197.90
                    }
                ],
                # Parâmetros UTM capturados da URL
                "utm_source": "FB",
                "utm_campaign": "Black Friday 2024|123456789",
                "utm_medium": "Audiencia Lookalike|987654321",
                "utm_content": "Video VSL 30s|456789123",
                "utm_term": "feed",
                "metadata": {
                    "orderId": "ORDER-12345",
                    "source": "facebook_ads"
                }
            }
        },
        "expected_response": {
            "status": "success",
            "message": "PIX criado com sucesso",
            "data": {
                "transactionId": "abc123xyz",
                "status": "PENDING",
                "pix": {
                    "code": "00020101021126530014BR.GOV.BCB.PIX...",
                    "image": "https://api.gateway.com/pix/qr/..."
                }
            },
            "tracking": {
                "utm_captured": True,
                "parameters": ["utm_source", "utm_campaign", "utm_medium", "utm_content", "utm_term"],
                "campaign": "Black Friday 2024|123456789",
                "source": "FB"
            }
        },
        "javascript_integration": {
            "description": "Exemplo de como capturar UTM da URL e enviar para a API",
            "code": """
// Função para capturar parâmetros UTM da URL
function getUtmFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return {
        utm_source: urlParams.get('utm_source'),
        utm_campaign: urlParams.get('utm_campaign'),
        utm_medium: urlParams.get('utm_medium'),
        utm_content: urlParams.get('utm_content'),
        utm_term: urlParams.get('utm_term')
    };
}

// Enviar PIX com tracking
async function createPixWithTracking(clientData, productData, amount) {
    const utmParams = getUtmFromUrl();
    
    const pixData = {
        amount: amount,
        client: clientData,
        products: productData,
        ...utmParams,  // Adiciona todos os parâmetros UTM
        metadata: {
            page_url: window.location.href,
            timestamp: new Date().toISOString()
        }
    };
    
    const response = await fetch('https://api-pix-duckyfy.onrender.com/pix/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pixData)
    });
    
    return response.json();
}
            """
        },
        "utm_parameters_explained": {
            "utm_source": "FB (Facebook)",
            "utm_campaign": "{{campaign.name}}|{{campaign.id}} - Nome e ID da campanha",
            "utm_medium": "{{adset.name}}|{{adset.id}} - Nome e ID do conjunto de anúncios",
            "utm_content": "{{ad.name}}|{{ad.id}} - Nome e ID do anúncio",
            "utm_term": "{{placement}} - Posicionamento do anúncio (feed, stories, etc)"
        },
        "benefits": [
            "Rastrear ROI por campanha específica",
            "Identificar anúncios que mais convertem",
            "Otimizar conjuntos de anúncios",
            "Medir performance por posicionamento",
            "Calcular ROAS real por criativo"
        ]
    }
    
    return jsonify(example)

@app.route('/pix/example/taxa-sedex', methods=['GET'])
def pix_taxa_sedex_example():
    """Endpoint que retorna exemplo específico para o produto Taxa Sedex"""
    example = {
        "produto": {
            "nome": "Taxa Sedex",
            "codigo": "Z29J23C",
            "preco": 28.97,
            "descricao": "Endpoint simplificado que preenche automaticamente os dados do produto"
        },
        "endpoint": "/pix/create/taxa-sedex",
        "method": "POST",
        "facebook_ads_url": {
            "description": "Configure esta URL no seu Facebook Ads",
            "url": "https://seusite.com/checkout-sedex?utm_source=FB&utm_campaign={{campaign.name}}|{{campaign.id}}&utm_medium={{adset.name}}|{{adset.id}}&utm_content={{ad.name}}|{{ad.id}}&utm_term={{placement}}"
        },
        "request_example": {
            "headers": {
                "Content-Type": "application/json"
            },
            "body": {
                "client": {
                    "name": "Maria Silva",
                    "email": "maria@email.com", 
                    "phone": "(11) 99999-8888",
                    "cpf": "12345678901"
                },
                "utm_source": "FB",
                "utm_campaign": "Taxa Sedex Promo|123456789",
                "utm_medium": "Interesse Correios|987654321",
                "utm_content": "Anuncio Sedex Barato|456789123",
                "utm_term": "feed"
            }
        },
        "response_example": {
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
                "utm_captured": True,
                "campaign": "Taxa Sedex Promo|123456789",
                "source": "FB"
            }
        },
        "javascript_integration": {
            "description": "Exemplo de integração no frontend",
            "code": """
// Capturar UTM da URL
function getUtmFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return {
        utm_source: params.get('utm_source'),
        utm_campaign: params.get('utm_campaign'),
        utm_medium: params.get('utm_medium'),
        utm_content: params.get('utm_content'),
        utm_term: params.get('utm_term')
    };
}

// Criar PIX Taxa Sedex
async function criarPixTaxaSedex(clientData) {
    const utmParams = getUtmFromUrl();
    
    const requestData = {
        client: clientData,
        ...utmParams
    };
    
    const response = await fetch('https://api-pix-duckyfy.onrender.com/pix/create/taxa-sedex', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
    });
    
    return response.json();
}

// Exemplo de uso no checkout
document.getElementById('checkout-sedex').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const clientData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        cpf: document.getElementById('document').value
    };
    
    try {
        const result = await criarPixTaxaSedex(clientData);
        
        if (result.status === 'success') {
            // Mostrar QR Code
            document.getElementById('qr-code').innerHTML = `
                <img src="${result.data.pix.image}" alt="QR Code PIX Taxa Sedex" />
                <p>Valor: R$ 28,97 - Taxa Sedex</p>
                <p>Código: ${result.data.pix.code}</p>
            `;
            
            // Enviar conversão para Facebook Pixel
            if (typeof fbq !== 'undefined') {
                fbq('track', 'Purchase', {
                    value: 28.97,
                    currency: 'BRL',
                    content_ids: ['Z29J23C'],
                    content_name: 'Taxa Sedex'
                });
            }
        }
    } catch (error) {
        alert('Erro: ' + error.message);
    }
});
            """
        },
        "vantagens": [
            "Endpoint dedicado e otimizado para Taxa Sedex",
            "Dados do produto preenchidos automaticamente",
            "Tracking UTM completo para campanhas",
            "Integração simplificada no frontend",
            "Controle de conversões específicas do produto"
        ]
    }
    
    return jsonify(example)

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint não encontrado',
        'available_endpoints': [
            'GET /health - Verificar status da API',
            'POST /pix/create - Criar pagamento PIX (com suporte a UTM)',
            'POST /pix/create/taxa-sedex - Criar PIX Taxa Sedex (R$ 28,97)',
            'GET /pix/example - Ver exemplo básico de uso',
            'GET /pix/example/utm - Ver exemplos com tracking UTM',
            'GET /pix/example/taxa-sedex - Ver exemplo Taxa Sedex'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Erro interno do servidor'
    }), 500

def process_utm_parameters(data):
    """Processa parâmetros UTM específicos do Facebook Ads"""
    utm_data = {}
    
    # Parâmetros UTM específicos que vamos capturar
    utm_params = ['utm_source', 'utm_campaign', 'utm_medium', 'utm_content', 'utm_term']
    
    for param in utm_params:
        if param in data and data[param]:
            utm_data[param] = str(data[param])[:200]  # Limitar tamanho
    
    # Adicionar timestamp de conversão se há dados UTM
    if utm_data:
        utm_data['conversion_timestamp'] = datetime.now().isoformat()
        utm_data['tracking_source'] = 'facebook_ads'
    
    return utm_data

if __name__ == '__main__':
    print("🚀 Iniciando API PIX Duckfy...")
    print(f"📋 Chaves configuradas: PUBLIC_KEY={PUBLIC_KEY[:10]}...")
    print("📖 Acesse /pix/example para ver como usar a API")
    app.run(debug=True, host='0.0.0.0', port=5000)