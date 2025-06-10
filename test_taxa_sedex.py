#!/usr/bin/env python3
import requests
import json

def test_taxa_sedex_endpoint():
    """Testar o endpoint específico da Taxa Sedex"""
    
    url = "https://api-pix-duckyfy.onrender.com/pix/create/taxa-sedex"
    
    data = {
        "client": {
            "name": "João Teste Taxa Sedex",
            "email": "joao.sedex@email.com",
            "phone": "(11) 99999-7777",
            "document": "44746461856"
        },
        "utm_source": "FB",
        "utm_campaign": "Taxa Sedex Black Friday|555123456",
        "utm_medium": "Interesse Correios|777888999",
        "utm_content": "Anuncio Sedex Promocional|333444555",
        "utm_term": "feed"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("🧪 Testando endpoint Taxa Sedex...")
    print(f"📤 URL: {url}")
    print(f"📤 Dados: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        print(f"📥 Status Code: {response.status_code}")
        print(f"📥 Response:")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if response.status_code == 201 and result.get('status') == 'success':
                print("✅ Teste da Taxa Sedex passou!")
                print(f"💰 Produto: {result['product']['name']} - R$ {result['product']['price']}")
                print(f"🔗 Código PIX: {result['data']['pix']['code'][:50]}...")
                
                if 'tracking' in result:
                    print(f"📊 UTM capturado: {result['tracking']['campaign']}")
                
                return True
            else:
                print("❌ Teste falhou!")
                return False
        else:
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        return False

if __name__ == "__main__":
    test_taxa_sedex_endpoint()
