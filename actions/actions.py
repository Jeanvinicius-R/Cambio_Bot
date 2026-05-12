from typing import Any, Text, Dict, List, Optional
import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


MAPA_MOEDAS = {
    # Real brasileiro
    "real": "BRL", "reais": "BRL", "real brasileiro": "BRL",
    "reais brasileiros": "BRL", "brl": "BRL",

    # Dólar americano
    "dólar": "USD", "dolar": "USD", "dólares": "USD", "dolares": "USD",
    "dólar americano": "USD", "dólares americanos": "USD",
    "dollar": "USD", "dollars": "USD", "usd": "USD",

    # Euro
    "euro": "EUR", "euros": "EUR", "eur": "EUR",

    # Libra esterlina
    "libra": "GBP", "libras": "GBP", "libra esterlina": "GBP",
    "libras esterlinas": "GBP", "gbp": "GBP",

    # Iene japonês
    "iene": "JPY", "ienes": "JPY", "yen": "JPY", "yenes": "JPY", "jpy": "JPY",

    # Peso argentino
    "peso": "ARS", "pesos": "ARS", "peso argentino": "ARS",
    "pesos argentinos": "ARS", "ars": "ARS",

    # Franco suíço
    "franco suíço": "CHF", "francos suíços": "CHF",
    "franco": "CHF", "chf": "CHF",

    # Dólar canadense
    "dólar canadense": "CAD", "dólares canadenses": "CAD",
    "dolár canadense": "CAD", "cad": "CAD",

    # Dólar australiano
    "dólar australiano": "AUD", "dólares australianos": "AUD", "aud": "AUD",

    # Yuan chinês
    "yuan": "CNY", "yuan chinês": "CNY", "renminbi": "CNY", "cny": "CNY",

    # Outras moedas comuns
    "franco suíco": "CHF",
    "coroa sueca": "SEK", "coroas suecas": "SEK", "sek": "SEK",
    "coroa norueguesa": "NOK", "coroas norueguesas": "NOK", "nok": "NOK",
    "rand sul-africano": "ZAR", "rand": "ZAR", "zar": "ZAR",
    "rúpia indiana": "INR", "rúpias indianas": "INR", "inr": "INR",
    "rublo": "RUB", "rublos": "RUB", "rub": "RUB",
    "won": "KRW", "won sul-coreano": "KRW", "krw": "KRW",
    "dírham": "AED", "dirham": "AED", "dirhams": "AED", "aed": "AED",
    "peso mexicano": "MXN", "pesos mexicanos": "MXN", "mxn": "MXN",
}

# Moedas exibidas na listagem
MOEDAS_SUPORTADAS = {
    "USD": "Dólar Americano",
    "BRL": "Real Brasileiro",
    "EUR": "Euro",
    "GBP": "Libra Esterlina",
    "JPY": "Iene Japonês",
    "ARS": "Peso Argentino",
    "CHF": "Franco Suíço",
    "CAD": "Dólar Canadense",
    "AUD": "Dólar Australiano",
    "CNY": "Yuan Chinês",
    "MXN": "Peso Mexicano",
    "INR": "Rúpia Indiana",
    "KRW": "Won Sul-Coreano",
    "ZAR": "Rand Sul-Africano",
    "SEK": "Coroa Sueca",
}


def normalizar_moeda(nome: Optional[str]) -> Optional[str]:
    """Converte nome em linguagem natural para código ISO 4217.
    
    Exemplos:
        "reais"  → "BRL"
        "dólar"  → "USD"
        "EUR"    → "EUR"  (já é código, apenas normaliza maiúsculas)
    """
    if not nome:
        return None
    # Tenta o mapeamento customizado primeiro (case-insensitive)
    chave = nome.strip().lower()
    if chave in MAPA_MOEDAS:
        return MAPA_MOEDAS[chave]
    # Se já for um código ISO de 3 letras, aceita diretamente
    if len(nome) == 3 and nome.upper().isalpha():
        return nome.upper()
    return None


# ─── ACTION: CONVERTER MOEDA ──────────────────────────────────────────────────

class ActionConverterMoeda(Action):
    """Consulta a ExchangeRate-API e retorna o valor convertido."""

    def name(self) -> Text:
        return "action_converter_moeda"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # 1. Recuperar slots preenchidos pelo NLU
        moeda_origem_raw = tracker.get_slot("moeda_origem")
        moeda_destino_raw = tracker.get_slot("moeda_destino")
        valor = tracker.get_slot("valor")

        # 2. Normalizar nomes para códigos ISO
        moeda_origem = normalizar_moeda(moeda_origem_raw)
        moeda_destino = normalizar_moeda(moeda_destino_raw)

        # 3. Verificar dados faltantes e solicitar ao usuário
        if not moeda_origem:
            dispatcher.utter_message(response="utter_pedir_moeda_origem")
            return []

        if not moeda_destino:
            dispatcher.utter_message(response="utter_pedir_moeda_destino")
            return []

        if not valor:
            dispatcher.utter_message(response="utter_pedir_valor")
            return []

        # 4. Consultar a ExchangeRate-API
        try:
            url = API_URL + moeda_origem
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            dados = response.json()

            if dados.get("result") != "success":
                dispatcher.utter_message(
                    text=f"⚠️ Não consegui obter a cotação para **{moeda_origem}**. "
                         f"Verifique se o código da moeda é válido."
                )
                return []

            taxas = dados.get("conversion_rates", {})

            if moeda_destino not in taxas:
                dispatcher.utter_message(
                    text=f"⚠️ Moeda **{moeda_destino}** não encontrada. "
                         f"Digite *\"quais moedas você suporta?\"* para ver a lista."
                )
                return []

            # 5. Calcular conversão
            taxa = taxas[moeda_destino]
            resultado = float(valor) * taxa

            # 6. Formatar e enviar resposta
            nome_origem = MOEDAS_SUPORTADAS.get(moeda_origem, moeda_origem)
            nome_destino = MOEDAS_SUPORTADAS.get(moeda_destino, moeda_destino)

            dispatcher.utter_message(
                text=(
                    f"💱 **Conversão realizada!**\n\n"
                    f"💵 {valor:,.2f} {moeda_origem} ({nome_origem})\n"
                    f"➡️  **{resultado:,.2f} {moeda_destino}** ({nome_destino})\n\n"
                    f"📊 Taxa atual: 1 {moeda_origem} = {taxa:.4f} {moeda_destino}"
                )
            )

        except requests.exceptions.ConnectionError:
            dispatcher.utter_message(
                text="❌ Não consegui me conectar ao serviço de câmbio. "
                     "Verifique sua conexão com a internet e tente novamente."
            )
        except requests.exceptions.Timeout:
            dispatcher.utter_message(
                text="⏱️ O serviço de câmbio demorou para responder. Tente novamente em instantes."
            )
        except requests.exceptions.HTTPError as e:
            if response.status_code == 403:
                dispatcher.utter_message(
                    text="🔑 API Key inválida ou sem permissão. "
                         "Verifique a variável API_KEY no arquivo actions.py."
                )
            else:
                dispatcher.utter_message(
                    text=f"❌ Erro ao consultar a API de câmbio (código {response.status_code}). "
                         f"Tente novamente mais tarde."
                )
        except Exception as e:
            dispatcher.utter_message(
                text="❌ Ocorreu um erro inesperado ao realizar a conversão. Tente novamente."
            )

        # Limpar slots após conversão para próxima pergunta
        return [
            SlotSet("moeda_origem", None),
            SlotSet("moeda_destino", None),
            SlotSet("valor", None),
        ]


# ─── ACTION: LISTAR MOEDAS ────────────────────────────────────────────────────

class ActionListarMoedas(Action):
    """Lista todas as moedas suportadas pelo CambioBot."""

    def name(self) -> Text:
        return "action_listar_moedas"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        linhas = [f"• **{codigo}** — {nome}" for codigo, nome in MOEDAS_SUPORTADAS.items()]
        lista = "\n".join(linhas)

        dispatcher.utter_message(
            text=(
                f"💱 **Moedas suportadas pelo CambioBot:**\n\n"
                f"{lista}\n\n"
                f"_Para converter, diga: \"Converta 100 dólares para reais\"_"
            )
        )

        return []