from datetime import datetime, timedelta
from utils import list_to_csv
import coingecko as cg
import json
import pandas as pd
import tomllib

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
    else:
        f = float(s[:-1])

    return f

def calc_prices():
    today = datetime.now() + timedelta(hours=6)
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
        print(f"Calculating {round_end} compared to {today} -")

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
    with open('bribe-map.toml', 'rb') as bf:
        bribe_map = tomllib.load(bf)
    today = datetime.now() + timedelta(hours=6)
    round = 1
    round_start = datetime.strptime('2021-09-16', '%Y-%m-%d')
    round_end = round_start + timedelta(days=5)

    all_df = None
    while round_end < today:
    
        fn = f'data/round-{round}.json'
        # print(f'Opening {fn}')
        with open(fn) as f:
            s = json.load(f)

        round_df = pd.json_normalize(s)
        bribes = {'round': round}
        for i in round_df.columns:
            if i.startswith('bribes.') and i.endswith('.amount'):
                protocol = i[7:i.rfind('.')]
                protocol = protocol.replace('crvFRAX', 'FRAXBP')

                if protocol in bribe_map['mapping']:
                    # Remap
                    #print(f'Remapping {protocol}')
                    protocol = bribe_map['mapping'][protocol]
                bribes[protocol] = parse_currency_str(round_df[i][0])
        bribes_df = pd.DataFrame([bribes])

        if all_df is None:
            all_df = bribes_df
        else:
            all_df = pd.concat([all_df, bribes_df], ignore_index=True)

        round += 1
        round_start += timedelta(days=14)
        round_end = round_start + timedelta(days=5)

    all_df.to_csv('data/rounds-bribes.csv', index=False)  

if __name__ == '__main__':
    calc_prices()
    calc_bribes()
