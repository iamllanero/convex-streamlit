from datetime import datetime, timedelta
from utils import list_to_csv
import coingecko as cg
import json

def parse_currency_str(s:str):
    """
    Accepts a currency string in the form of <symbol><amount><k or m> and
    returns a float value. For example, the following are all valid:

    $0.99
    $156.33k
    $25m
    """

    f = 0.0
    s = s[1:] if s.startswith('$') else s
    if s.lower().endswith('k'):
        f = float(s[:-1]) * 1000
    elif s.lower().endswith('m'):
        f = float(s[:-1]) * 1000000

    return f

def calc_prices():
    today = datetime.now()
    round = 1
    round_start = datetime.strptime('2021-09-16', '%Y-%m-%d')
    round_end = round_start + timedelta(days=5)

    rounds = [[
        'round',
        'start',
        'end',
        'total_bribes',
        'btc',
        'eth',
        'crv',
        'cvx',
    ]]

    while round_end < today:
        btc_price = cg.get_historical_price('btc', round_end)
        eth_price = cg.get_historical_price('eth', round_end)
        crv_price = cg.get_historical_price('crv', round_end)
        cvx_price = cg.get_historical_price('cvx', round_end)

        with open(f'data/round-{round}.json', 'r') as f:
            bribes = json.load(f)
        
        total_bribes = parse_currency_str(bribes['total'])

        rounds.append([
            round,
            round_start,
            round_end,
            total_bribes,
            btc_price,
            eth_price,
            crv_price,
            cvx_price,
        ])

        round += 1
        round_start += timedelta(days=14)
        round_end = round_start + timedelta(days=5)

    list_to_csv(rounds, 'data/rounds-prices.csv')


def calc_bribes():
    today = datetime.now()
    round = 1
    round_start = datetime.strptime('2021-09-16', '%Y-%m-%d')
    round_end = round_start + timedelta(days=5)

    rounds = [[
        'round',
        'start',
        'end',
        'btc',
        'eth',
        'crv',
        'cvx',
    ]]

    while round_end < today:
    
        pass

        round += 1
        round_start += timedelta(days=14)
        round_end = round_start + timedelta(days=5)

    

if __name__ == '__main__':
    calc_prices()
    calc_bribes()
