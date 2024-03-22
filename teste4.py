import requests
import time
from binance.client import Client

# Variáveis de controle

API_KEY = 'vNYI9mxeTvePkiq06ZxHkG3yoX4jyZBxXG3TYfFJ2jdoLx1d6hDPcF24kSx7iudP'
SECRET_KEY = 'IxN9t7UNwEp12fwzCpKkq5oYr04QbPbGKQRHGr2H2DOv3DuPLa0Jse7Hy0LW4cn0'
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT']  #, 'ADAUSDT', 'DOGEUSDT'
VAR_PERCENT_COMPRA_CAMADA_1 = -3.5
VER_PERCENT_COMPRA_CAMADA_2 = -4.5
VAR_PERCENT_VENDA_CAMADA_1 = 2.0
VAR_PERCENT_VENDA_CAMADA_2 = 4.0
CAMADA_1 = 1
CAMADA_2 = 2
SPLIT = int(input("Quantas divisões você deseja para sua carteira? 1 a 4 partes: "))

if SPLIT <= 0 or SPLIT > 4:
    print("Número de divisões inválido. Escolha um número entre 1 e 4.")
    exit()


estado_camada = {symbol: 1 for symbol in SYMBOLS}

# Funções
def get_balance(symbol):
    client = Client(api_key=API_KEY, api_secret=SECRET_KEY)
    
    try:
        balances = client.get_account()['balances']
    except Exception as e:
        return 0.0

    for balance in balances:
        if balance['asset'] == symbol:
            return float(balance['free'])

    return 0.0

def get_binance_price(symbol):
    base_url = 'https://api.binance.com/api/v3/ticker/price'
    params = {'symbol': symbol}
    response = requests.get(base_url, params=params)
    data = response.json()
    price = float(data['price'])

    stats = get_price_change_4h(symbol)
    price_change_percent_4h = stats

    return price, price_change_percent_4h

def get_price_change_4h(symbol):
    base_url = 'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': symbol,
        'interval': '4h',
        'limit': 1
    }
    response = requests.get(base_url, params=params)
    data = response.json()

    open_price = float(data[0][1])
    close_price = float(data[0][4])

    price_change_percent_4h = ((close_price - open_price) / open_price) * 100
    return price_change_percent_4h


def execute_buy_order(symbol, buy_amount, var_perecent_venda):
    client = Client(api_key=API_KEY, api_secret=SECRET_KEY)
    usdt_balance = get_balance("USDT")
    sell_price_limit = buy_price * var_perecent_venda

    if usdt_balance < buy_amount:
        print(f"Saldo insuficiente para comprar {buy_amount} {symbol}. Saldo disponível: {usdt_balance}")
        return

    order = client.create_order(
        symbol=symbol,
        side='BUY',
        type='MARKET',
        quoteOrderQty=buy_amount,
    )
    print(f'Ordem de compra executada para {symbol}. Detalhes: {order}')

    order = client.create_order(
        symbol=symbol,
        side='SELL',
        type='LIMIT_MAKER',
        quoteOrderQty=buy_amount,
        price=(sell_price_limit)
    )
    print(f'Ordem de venda executada para {symbol}. Detalhes: {order}')

def compare_prices():
    usdt_balance = get_balance("USDT")
    initial_buy_amount = usdt_balance / SPLIT

    while True:
        print(f'*'*30)

        for symbol in SYMBOLS:
            price, price_change_percent_4h = get_binance_price(symbol)
            print(f'{symbol}')

            camada_atual = estado_camada[symbol]

            if camada_atual == CAMADA_1:
                if price_change_percent_4h <= VAR_PERCENT_COMPRA_CAMADA_1:
                    execute_buy_order(symbol, initial_buy_amount, VAR_PERCENT_VENDA_CAMADA_1)
                    estado_camada[symbol] = 2
                else:
                    print(f'O valor está dentro da margem de variação. Mantenha.')
                    print(f'Variação das últimas 4 horas: {price_change_percent_4h}%')
            elif camada_atual == CAMADA_2:
                if price_change_percent_4h <= VAR_PERCENT_COMPRA_CAMADA_2:
                    execute_buy_order(symbol, initial_buy_amount, VAR_PERCENT_VENDA_CAMADA_2)
                    estado_camada[symbol] = 2
                else:
                    print(f'O valor está dentro da margem de variação. Mantenha.')
                    print(f'Variação das últimas 4 horas: {price_change_percent_4h}%')
            else:
                print("Erro: Camada inválida.")
                exit()

            print(f'*'*10)
        time.sleep(60)  

if __name__ == '__main__':
    compare_prices()
