# Deploy na Render - Guia Passo a Passo

Este guia te ensina como fazer deploy da API PIX Duckfy na plataforma Render de forma simples e gratuita.

## 📋 Pré-requisitos

1. **Conta no GitHub**: Para versionar seu código
2. **Conta na Render**: Gratuita em [render.com](https://render.com)
3. **Chaves da Duckfy**: PUBLIC_KEY e SECRET_KEY

## 🚀 Passo 1: Preparar o Repositório

### 1.1 Inicializar Git (se ainda não fez)
```bash
git init
git add .
git commit -m "Initial commit - API PIX Duckfy"
```

### 1.2 Criar repositório no GitHub
1. Acesse [github.com](https://github.com)
2. Clique em "New repository"
3. Nome: `api-pix-duckfy`
4. Deixe público ou privado (sua escolha)
5. Clique em "Create repository"

### 1.3 Enviar código para o GitHub
```bash
git remote add origin https://github.com/SEU_USUARIO/api-pix-duckfy.git
git branch -M main
git push -u origin main
```

## 🌐 Passo 2: Configurar na Render

### 2.1 Acessar a Render
1. Acesse [render.com](https://render.com)
2. Clique em "Get Started for Free"
3. Faça login com GitHub ou crie uma conta

### 2.2 Conectar com GitHub
1. No dashboard da Render, clique em "New +"
2. Selecione "Web Service"
3. Conecte sua conta do GitHub
4. Selecione o repositório `api-pix-duckfy`

### 2.3 Configurar o Serviço
Preencha os campos:

**Basic Information:**
- **Name**: `api-pix-duckfy` (ou nome de sua preferência)
- **Region**: `Ohio (US East)` (recomendado para menor latência)
- **Branch**: `main`
- **Root Directory**: deixe em branco

**Build and Deploy:**
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 30 app:app`

**Pricing:**
- Selecione **"Free"** (0 USD/mês)

### 2.4 Configurar Variáveis de Ambiente
Na seção "Environment Variables", adicione:

```
FLASK_ENV = production
PUBLIC_KEY = sua_chave_publica_duckfy_aqui
SECRET_KEY = sua_chave_secreta_duckfy_aqui
```

⚠️ **IMPORTANTE**: Use suas chaves reais da Duckfy, não as de exemplo!

### 2.5 Finalizar Deploy
1. Clique em "Create Web Service"
2. A Render começará o build automaticamente
3. Aguarde alguns minutos (primeira vez pode demorar 5-10 min)

## 🔍 Passo 3: Verificar o Deploy

### 3.1 Acompanhar o Build
1. Na página do serviço, vá para a aba "Logs"
2. Acompanhe o processo de build e deploy
3. Procure por mensagens como:
   ```
   ==> Build successful 🎉
   ==> Starting service with 'gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 30 app:app'
   ```

### 3.2 Testar a API
Sua API estará disponível em uma URL como:
```
https://api-pix-duckfy.onrender.com
```

Teste os endpoints:
```bash
# Health check
curl https://SEU_APP.onrender.com/health

# Exemplo de uso
curl https://SEU_APP.onrender.com/pix/example
```

## ⚙️ Passo 4: Configurações Avançadas (Opcional)

### 4.1 Domínio Customizado
1. Na aba "Settings" do seu serviço
2. Seção "Custom Domains"
3. Clique em "Add Custom Domain"
4. Configure seu DNS para apontar para a Render

### 4.2 Auto-Deploy
Por padrão, a Render faz deploy automático quando você faz push para o branch `main`:
```bash
git add .
git commit -m "Atualização da API"
git push origin main
```

### 4.3 Monitoramento
1. Na aba "Metrics" você pode ver:
   - CPU e Memória utilizados
   - Requests por minuto
   - Response time
   - Logs de erro

## 🛠️ Solução de Problemas Comuns

### Build Failure - Dependências
Se o build falhar, verifique:
1. Arquivo `requirements.txt` está correto
2. Todas as dependências são compatíveis com Python 3.11

### Service Unavailable
Se a API não responder:
1. Verifique os logs na aba "Logs"
2. Confirme que as variáveis de ambiente estão corretas
3. Teste localmente primeiro

### Erro de Autenticação Duckfy
Se receber erro de autenticação:
1. Verifique se `PUBLIC_KEY` e `SECRET_KEY` estão corretas
2. Confirme que as chaves são válidas no painel Duckfy
3. Não deixe espaços em branco nas variáveis

### Timeout Errors
Se houver timeouts:
1. Aumente o timeout no start command:
   ```
   gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 60 app:app
   ```

## 💰 Limitações do Plano Gratuito

**Render Free Tier:**
- ✅ 750 horas/mês (suficiente para uso contínuo)
- ✅ 512MB RAM
- ✅ SSL automático
- ✅ Custom domains
- ⚠️ "Sleep" após 15 min de inatividade
- ⚠️ ~30s para "acordar" na primeira requisição

**Para produção intensiva:**
- Considere upgrade para plano pago ($7/mês)
- Sem sleep, mais RAM, melhor performance

## 🔐 Segurança em Produção

### Variáveis de Ambiente
✅ **NUNCA** commit suas chaves no código
✅ Use sempre as variáveis de ambiente da Render
✅ Mantenha backup das suas chaves em local seguro

### Monitoramento
- Configure alertas na Render
- Monitor logs regularmente
- Implemente health checks

## 📱 Testando a API em Produção

### Teste Básico
```bash
curl https://SEU_APP.onrender.com/health
```

### Teste de Criação PIX
```bash
curl -X POST https://SEU_APP.onrender.com/pix/create \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 10.50,
    "client": {
      "name": "Teste Produção",
      "email": "teste@email.com",
      "phone": "(11) 99999-9999",
      "document": "12345678901"
    }
  }'
```

## 🎯 Próximos Passos

1. **Configurar domínio próprio** (ex: api.seusite.com)
2. **Implementar monitoramento** com ferramentas como UptimeRobot
3. **Configurar backup** dos logs importantes
4. **Documentar** sua API para outros desenvolvedores
5. **Implementar cache** Redis se necessário

## 📞 Suporte

**Render:**
- Documentação: [render.com/docs](https://render.com/docs)
- Status: [status.render.com](https://status.render.com)
- Suporte: Através do dashboard

**API Issues:**
- Verifique logs na Render
- Teste localmente primeiro
- Confirme chaves da Duckfy

---

## ✅ Checklist de Deploy

- [ ] Código no GitHub
- [ ] Conta na Render criada
- [ ] Serviço configurado na Render
- [ ] Variáveis de ambiente definidas
- [ ] Build e deploy bem-sucedidos
- [ ] API respondendo em produção
- [ ] Endpoint `/health` funcionando
- [ ] Teste de criação PIX realizado
- [ ] Logs monitorados
- [ ] Documentação da URL de produção

🎉 **Parabéns! Sua API PIX está no ar!**
