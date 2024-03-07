import requests
import time
from binance.client import Client

# Variáveis de controle

API_KEY = 'vNYI9mxeTvePkiq06ZxHkG3yoX4jyZBxXG3TYfFJ2jdoLx1d6hDPcF24kSx7iudP'
SECRET_KEY = 'IxN9t7UNwEp12fwzCpKkq5oYr04QbPbGKQRHGr2H2DOv3DuPLa0Jse7Hy0LW4cn0'
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']  #, 'ADAUSDT', 'DOGEUSDT'
TOTAL_PORTFOLIO_USDT = 1000.0

INITIAL_CAPITAL_PER_COIN = 200.0
initial_capital = {symbol: INITIAL_CAPITAL_PER_COIN for symbol in SYMBOLS}

modo_investimento = input("Escolha o modo de investimento (conservador/arrojado): ").lower()

VAR_PERCENT_COMPRA = (-4.5) if modo_investimento == 'arrojado' else (-3.5)
VAR_PERCENT_VENDA_MAP = {
    'BTCUSDT': 4.0 if modo_investimento == 'conservador' else 2.0,
    'ETHUSDT': 4.0 if modo_investimento == 'conservador' else 3.0,
    'BNBUSDT': 4.0 if modo_investimento == 'conservador' else 3.0,
    'ADAUSDT': 4.0 if modo_investimento == 'conservador' else 3.0,
    'DOGEUSDT': 4.0 if modo_investimento == 'conservador' else 2.0,
}


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

def distribute_capital(capital, current_portfolio):
    # Distribui o capital proporcionalmente com base no valor inicial
    total_initial_capital = sum(initial_capital.values())
    ratio = capital / total_initial_capital
    return {symbol: ratio * initial_capital[symbol] for symbol in SYMBOLS}

def get_user_input():
    # Retorna o capital atual distribuído proporcionalmente entre as moedas
    distributed_capital = distribute_capital(TOTAL_PORTFOLIO_USDT, initial_capital)
    return {symbol: get_balance(symbol) + distributed_capital[symbol] for symbol in SYMBOLS}

def get_binance_price(symbol):
    base_url = 'https://api.binance.com/api/v3/ticker/price'
    params = {'symbol': symbol}
    response = requests.get(base_url, params=params)
    data = response.json()
    price = float(data['price'])

    stats = get_binance_24hr_stats(symbol)
    price_change_percent_24h = stats['price_change_percent']

    return price, price_change_percent_24h

def get_binance_24hr_stats(symbol):
    base_url = 'https://api.binance.com/api/v3/ticker/24hr'
    params = {'symbol': symbol}
    response = requests.get(base_url, params=params)
    data = response.json()
    value = float(data['priceChangePercent'])
    return {
        'symbol': data['symbol'],
        'price_change_percent': float(data['priceChangePercent']),
    }

def get_last_trade_price(symbol):
    client = Client(api_key=API_KEY, api_secret=SECRET_KEY)
    trades = client.get_my_trades(symbol=symbol, limit=1)

    if trades:
        return float(trades[0]['price'])
    else:
        print(f"Nenhuma negociação encontrada para {symbol}.")
        return 0.0

def get_account_informaions():
    client = Client(api_key=API_KEY, api_secret=SECRET_KEY)
    account_info = client.get_account()

    for balance in account_info['balances']:
        asset = balance['asset']
        free_balance = balance['free']
        locked_balance = balance['locked']
    
        print(f"Moeda: {asset}, Saldo Livre: {free_balance}, Saldo Bloqueado: {locked_balance}")


def execute_buy_order(symbol, available_balance):
    
    client = Client(api_key=API_KEY, api_secret=SECRET_KEY)
    price, _ = get_binance_price(symbol)

    usdt_balance = get_balance("USDT")
    buy_price = price
    sell_price_limit = buy_price * 1.045

    if usdt_balance < quantity:
        print(f"Saldo insuficiente para vender {quantity} {symbol}. Saldo disponível: {usdt_balance}")
        return

    order = client.create_order(
        symbol=symbol,
        side='BUY',
        type='MARKET',
        quoteOrderQty=available_balance,
    )
    print(f'Ordem de compra executada para {symbol}. Detalhes: {order}')

    execute_sell_order(symbol, available_balance, sell_price_limit)

def execute_sell_order(symbol, quantity, sell_price_limit ):
    client = Client(api_key=API_KEY, api_secret=SECRET_KEY)
    price, _ = get_binance_price(symbol)

    if symbol_info:
        print(symbol_info['filters'])
    
    print(f"chamou a ordem de venda: {quantity}")

    order = client.create_order(
        symbol=symbol,
        side='SELL',
        type='TYPE',
        quantity=round(quantity, 8),
        stopPrice=sell_price_limit,
        price=(sell_price_limit-1)
    )

    print(f'Ordem de venda executada para {symbol}. Detalhes: {order}')

def compare_prices():

    while True:
        distributed_capital = distribute_capital(TOTAL_PORTFOLIO_USDT, initial_capital)
        print(f'*'*30)

        for symbol in SYMBOLS:
            price, price_change_percent_24h = get_binance_price(symbol)
            compra = get_last_trade_price(symbol)
            available_balance = get_balance(symbol[:3]) #valor disponível em carteira

            # Calcular a variação percentual
            var_percent_compra = ((price - compra) / compra) * 100 if compra != 0 else 0.0
            var_percent_venda = VAR_PERCENT_VENDA_MAP.get(symbol, 3.0)
            
            print(f'{symbol}')
            print(f'Saldo disponível: {available_balance}')
            print(f'Valor Atual: {price}')

            # Comparar a variação percentual
            if price_change_percent_24h <= VAR_PERCENT_COMPRA:
                buyable_amount = distributed_capital[symbol]  
                execute_buy_order(symbol, buyable_amount)
                print(f'variação nas ultimas 12h é de: {abs(price_change_percent_24h):.2f}%. Compre!')
                print(f'Compra de {buyable_amount}')

            # elif var_percent_compra >= var_percent_venda:
            #     print(f'O valor subiu {var_percent_compra:.2f}% do valor da compra. Venda!')
            #     execute_sell_order(symbol, available_balance)
            else:
                print(f'O valor está dentro da margem de variação. Mantenha.')
                print(f'Variação das últimas 12 horas: {price_change_percent_24h}%')
                print(f'Variação desde a ultima compra: {var_percent_compra}%')

            print(f'*'*10)
        time.sleep(60)  

if __name__ == '__main__':
    #get_account_informaions()
    compare_prices()
