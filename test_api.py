#!/usr/bin/env python3
"""
Exemplo de uso da API PIX Duckfy
Este arquivo demonstra como usar a API para criar pagamentos PIX
"""

import requests
import json
from datetime import datetime, timedelta

# URL base da API (ajuste conforme necessário)
API_BASE_URL = "http://localhost:5000"

def test_health():
    """Testa se a API está funcionando"""
    print("🔍 Testando health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False

def create_simple_pix():
    """Cria um PIX simples com dados mínimos"""
    print("\n💰 Criando PIX simples...")
    
    data = {
        "amount": 25.90,
        "client": {
            "name": "João da Silva",
            "email": "joao.silva@example.com",
            "phone": "(11) 99999-9999",
            "document": "123.456.789-00"
        }
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/pix/create", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 201 and 'data' in result:
            pix_data = result['data']
            print(f"\n✅ PIX criado com sucesso!")
            print(f"Transaction ID: {pix_data.get('transactionId')}")
            print(f"Status: {pix_data.get('status')}")
            if 'pix' in pix_data:
                print(f"Código PIX: {pix_data['pix'].get('code')[:50]}...")
                if 'image' in pix_data['pix']:
                    print(f"QR Code: {pix_data['pix']['image']}")
        
        return response.status_code == 201
        
    except Exception as e:
        print(f"❌ Erro ao criar PIX: {e}")
        return False

def create_complete_pix():
    """Cria um PIX com todos os campos possíveis"""
    print("\n🛍️ Criando PIX completo com produtos...")
    
    tomorrow = datetime.now() + timedelta(days=1)
    
    data = {
        "amount": 155.75,
        "shippingFee": 15.00,
        "extraFee": 5.00,
        "discount": 10.25,
        "client": {
            "name": "Maria Santos",
            "email": "maria.santos@example.com",
            "phone": "(11) 98765-4321",
            "document": "987.654.321-00"
        },
        "products": [
            {
                "id": "prod_001",
                "name": "Camiseta Premium",
                "quantity": 2,
                "price": 50.00
            },
            {
                "id": "prod_002",
                "name": "Calça Jeans",
                "quantity": 1,
                "price": 89.90
            }
        ],
        "dueDate": tomorrow.strftime("%Y-%m-%d"),
        "metadata": {
            "orderId": "ORDER-2025-001",
            "source": "website",
            "campaign": "summer_sale",
            "customer_type": "premium"
        },
        "callbackUrl": "https://meusite.com/webhook/pix/callback"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/pix/create", json=data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 201 and 'data' in result:
            pix_data = result['data']
            print(f"\n✅ PIX completo criado com sucesso!")
            print(f"Transaction ID: {pix_data.get('transactionId')}")
            print(f"Status: {pix_data.get('status')}")
            if 'order' in pix_data:
                print(f"Order ID: {pix_data['order'].get('id')}")
        
        return response.status_code == 201
        
    except Exception as e:
        print(f"❌ Erro ao criar PIX completo: {e}")
        return False

def test_invalid_data():
    """Testa validação com dados inválidos"""
    print("\n❌ Testando dados inválidos...")
    
    invalid_data = {
        "amount": -10,  # Valor negativo
        "client": {
            "name": "Teste",
            # email ausente
            "document": "123.456.789-00"
        }
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/pix/create", json=invalid_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 400:
            print("✅ Validação funcionando corretamente - dados inválidos rejeitados")
        
        return response.status_code == 400
        
    except Exception as e:
        print(f"❌ Erro no teste de validação: {e}")
        return False

def get_example():
    """Busca o exemplo de uso da API"""
    print("\n📖 Buscando exemplo de uso...")
    try:
        response = requests.get(f"{API_BASE_URL}/pix/example")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Exemplo: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao buscar exemplo: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes da API PIX Duckfy")
    print("=" * 50)
    
    # Contador de testes
    tests_passed = 0
    total_tests = 5
    
    # Executar testes
    if test_health():
        tests_passed += 1
    
    if create_simple_pix():
        tests_passed += 1
    
    if create_complete_pix():
        tests_passed += 1
    
    if test_invalid_data():
        tests_passed += 1
    
    if get_example():
        tests_passed += 1
    
    # Resultado final
    print("\n" + "=" * 50)
    print(f"📊 Resultado dos testes: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 Todos os testes passaram! API funcionando perfeitamente.")
    elif tests_passed > 0:
        print(f"⚠️ {total_tests - tests_passed} teste(s) falharam. Verifique os erros acima.")
    else:
        print("❌ Todos os testes falharam. Verifique se a API está rodando.")
    
    print("\n💡 Para iniciar a API, execute: python app.py")
    print(f"🌐 URL da API: {API_BASE_URL}")

if __name__ == "__main__":
    main()
