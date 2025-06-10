# 📊 Tracking UTM para Facebook Ads

Este guia mostra como configurar tracking UTM simplificado na sua API PIX para campanhas do Facebook Ads.

## 🎯 Parâmetros UTM Configurados

A API captura automaticamente os seguintes parâmetros UTM:

- **utm_source**: FB (Facebook)
- **utm_campaign**: {{campaign.name}}|{{campaign.id}}
- **utm_medium**: {{adset.name}}|{{adset.id}}
- **utm_content**: {{ad.name}}|{{ad.id}}
- **utm_term**: {{placement}}

## 🔗 Configuração no Facebook Ads

### URL de Destino
Configure esta URL no seu anúncio como página de destino:

```
https://seusite.com/checkout?utm_source=FB&utm_campaign={{campaign.name}}|{{campaign.id}}&utm_medium={{adset.name}}|{{adset.id}}&utm_content={{ad.name}}|{{ad.id}}&utm_term={{placement}}
```

### Exemplo Real
```
https://seusite.com/checkout?utm_source=FB&utm_campaign=Black%20Friday%202024|123456789&utm_medium=Audiencia%20Lookalike|987654321&utm_content=Video%20VSL%2030s|456789123&utm_term=feed
```

## 💻 Implementação Frontend

### 1. JavaScript - Capturar UTM da URL
```javascript
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
```

### 2. Enviar PIX com Tracking
```javascript
async function createPixWithTracking(clientData, amount) {
    const utmParams = getUtmFromUrl();
    
    const pixData = {
        amount: amount,
        client: clientData,
        ...utmParams,  // Adiciona automaticamente os UTMs
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
```

### 3. Exemplo Completo de Checkout
```javascript
document.getElementById('checkout-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const clientData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        document: document.getElementById('document').value
    };
    
    try {
        const result = await createPixWithTracking(clientData, 197.90);
        
        if (result.status === 'success') {
            // Mostrar QR Code
            showPixQrCode(result.data.pix);
            
            // Log tracking capturado
            if (result.tracking) {
                console.log('UTM capturado:', result.tracking);
            }
            
            // Enviar evento para Facebook Pixel (se configurado)
            if (typeof fbq !== 'undefined') {
                fbq('track', 'Purchase', {
                    value: 197.90,
                    currency: 'BRL'
                });
            }
        }
    } catch (error) {
        alert('Erro: ' + error.message);
    }
});
```

## 📡 API Request Example

### Request
```json
POST https://api-pix-duckyfy.onrender.com/pix/create

{
    "amount": 197.90,
    "client": {
        "name": "João Silva",
        "email": "joao@email.com",
        "phone": "(11) 99999-9999",
        "document": "44746461856"
    },
    "utm_source": "FB",
    "utm_campaign": "Black Friday 2024|123456789",
    "utm_medium": "Audiencia Lookalike|987654321", 
    "utm_content": "Video VSL 30s|456789123",
    "utm_term": "feed"
}
```

### Response
```json
{
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
        "utm_captured": true,
        "parameters": ["utm_source", "utm_campaign", "utm_medium", "utm_content", "utm_term"],
        "campaign": "Black Friday 2024|123456789",
        "source": "FB"
    }
}
```

## 📊 Dados Salvos nos Metadados

Os parâmetros UTM são salvos automaticamente nos metadados do PIX na Duckfy:

```json
{
    "metadata": {
        "tracking": {
            "utm_source": "FB",
            "utm_campaign": "Black Friday 2024|123456789",
            "utm_medium": "Audiencia Lookalike|987654321",
            "utm_content": "Video VSL 30s|456789123",
            "utm_term": "feed",
            "conversion_timestamp": "2025-06-10T20:45:00.123456",
            "tracking_source": "facebook_ads"
        }
    }
}
```

## 🔍 Como Analisar os Dados

### 1. Separar Campanha e ID
```javascript
// utm_campaign = "Black Friday 2024|123456789"
const [campaignName, campaignId] = utmCampaign.split('|');
console.log('Nome:', campaignName);  // "Black Friday 2024"
console.log('ID:', campaignId);      // "123456789"
```

### 2. Métricas Importantes
- **Custo por Conversão**: Gasto / Número de PIX pagos
- **ROI por Campanha**: (Receita - Gasto) / Gasto * 100
- **Taxa de Conversão**: PIX pagos / Cliques
- **Ticket Médio**: Receita total / Número de PIX

### 3. Exemplo de Dashboard
```javascript
// Agrupar conversões por campanha
const conversoesPorCampanha = pixPagos.reduce((acc, pix) => {
    const campaign = pix.metadata.tracking.utm_campaign;
    if (!acc[campaign]) acc[campaign] = [];
    acc[campaign].push(pix);
    return acc;
}, {});

// Calcular métricas
Object.entries(conversoesPorCampanha).forEach(([campaign, pixs]) => {
    const receita = pixs.reduce((sum, pix) => sum + pix.amount, 0);
    const conversoes = pixs.length;
    console.log(`${campaign}: ${conversoes} conversões, R$ ${receita}`);
});
```

## 🎯 Próximos Passos

1. **Configurar URLs** com UTM nos seus anúncios
2. **Implementar captura** no frontend
3. **Testar** com campanhas pequenas
4. **Criar dashboard** para análise
5. **Otimizar** baseado nos dados

## 📞 Testar a API

### Ver exemplos:
```bash
curl https://api-pix-duckyfy.onrender.com/pix/example/utm
```

### Testar com UTM:
```bash
curl -X POST https://api-pix-duckyfy.onrender.com/pix/create \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50.00,
    "client": {
      "name": "Teste UTM",
      "email": "teste@email.com",
      "document": "44746461856"
    },
    "utm_source": "FB",
    "utm_campaign": "Teste|123",
    "utm_medium": "Audiencia|456",
    "utm_content": "Anuncio|789",
    "utm_term": "feed"
  }'
```

---

**🚀 Sua API está pronta para tracking completo do Facebook Ads!**
