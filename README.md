# Cambio_Bot# 💱 CambioBot

Assistente virtual para conversão de moedas em tempo real, desenvolvido com **Rasa Framework** e integrado à **ExchangeRate-API**.

## 📋 Sobre o Projeto

O CambioBot foi desenvolvido para uma fintech de soluções financeiras cujos usuários perdem tempo pesquisando taxas de câmbio manualmente. O bot permite conversões instantâneas diretamente no chat, com suporte a linguagem natural em português.

**Exemplos de uso:**
- *"Converta 100 dólares para reais"*
- *"Quanto dá 50 euros em reais?"*
- *"500 libras em dólares"*
- *"Quais moedas você suporta?"*

---

## 🏗️ Estrutura do Projeto

```
cambiobot/
├── actions/
│   ├── __init__.py
│   └── actions.py          # Custom actions + integração com API
├── data/
│   ├── nlu.yml             # Exemplos de treinamento NLU
│   ├── stories.yml         # Histórias de diálogo
│   └── rules.yml           # Regras determinísticas
├── config.yml              # Pipeline NLU e políticas de diálogo
├── domain.yml              # Intents, entities, slots, actions, respostas
├── endpoints.yml           # Configuração do Action Server
├── credentials.yml         # Canais de comunicação
├── requirements.txt        # Dependências Python
└── README.md
```

---

## ⚙️ Configuração

### 1. Pré-requisitos

- Python 3.8 ou superior
- pip

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Obter a API Key (ExchangeRate-API)

1. Acesse [https://www.exchangerate-api.com/](https://www.exchangerate-api.com/)
2. Crie uma conta gratuita (sem cartão de crédito)
3. Copie sua API Key no painel

### 4. Inserir a API Key no projeto

Abra o arquivo `actions/actions.py` e substitua na linha:

```python
API_KEY = "SUA_API_KEY_AQUI"
```

### 5. Validar a API Key com curl

```bash
curl https://v6.exchangerate-api.com/v6/SUA_API_KEY_AQUI/latest/USD
```

A resposta deve conter `"result": "success"` e um objeto `conversion_rates`.

---

## 🚀 Execução

### Terminal 1 — Treinar e iniciar o Rasa

```bash
# Treinar o modelo
rasa train

# Iniciar o servidor Rasa
rasa run --enable-api --endpoints endpoints.yml --credentials credentials.yml
```

### Terminal 2 — Iniciar o Action Server

```bash
rasa run actions
```

### Testar no terminal (modo interativo)

```bash
rasa shell
```

---

## 🗣️ Capacidades do Bot

| Capacidade | Descrição |
|---|---|
| Identificar intenção | Detecta pedidos de conversão em linguagem natural |
| Tratar dados faltantes | Solicita moeda ou valor caso não informados |
| Consultar API externa | Taxa de câmbio em tempo real via ExchangeRate-API |
| Listar moedas | Exibe todas as moedas suportadas |
| Normalização | Converte "reais" → BRL, "dólares" → USD automaticamente |

---

## 🪙 Moedas Suportadas

| Código | Nome |
|---|---|
| USD | Dólar Americano |
| BRL | Real Brasileiro |
| EUR | Euro |
| GBP | Libra Esterlina |
| JPY | Iene Japonês |
| ARS | Peso Argentino |
| CHF | Franco Suíço |
| CAD | Dólar Canadense |
| AUD | Dólar Australiano |
| CNY | Yuan Chinês |
| MXN | Peso Mexicano |
| INR | Rúpia Indiana |
| KRW | Won Sul-Coreano |
| ZAR | Rand Sul-Africano |
| SEK | Coroa Sueca |

---

## 🧪 Testando via API REST

```bash
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender": "usuario1", "message": "Converta 100 dólares para reais"}'
```

---

## 🔧 Componentes Técnicos

### Intents (intenções)
- `converter_moeda` — pedido de conversão
- `listar_moedas` — listar moedas disponíveis
- `cumprimentar` / `despedir` — saudações
- `bot_desafio` — perguntas sobre o bot

### Entities (entidades)
- `moeda_origem` — moeda de partida (ex: dólar, EUR)
- `moeda_destino` — moeda de destino (ex: real, BRL)
- `valor` — quantia numérica (ex: 100, 50.5)

### Slots
Armazenam os valores extraídos para uso na custom action.

### Custom Actions
- `action_converter_moeda` — consulta API e calcula conversão
- `action_listar_moedas` — lista moedas disponíveis

---

## 📚 Tecnologias

- [Rasa Framework](https://rasa.com/) — NLU e gerenciamento de diálogo
- [ExchangeRate-API](https://www.exchangerate-api.com/) — cotações em tempo real
- Python 3.8+

---

*Projeto desenvolvido para a disciplina de ChatBot.*