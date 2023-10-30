import csv
import sys
import pandas as pd
import os
from votium import rounds

PRICE_DATA_DIR = '../votium-py/output/price'
# DATA_DIR = 'data'

CONSOLIDATE_OUTPUT_DIR = 'output/consolidate'
FORECAST_OUTPUT_DIR = 'output/forecast'

for dir in [FORECAST_OUTPUT_DIR, CONSOLIDATE_OUTPUT_DIR]:
    os.makedirs(dir, exist_ok=True)


def consolidate_data():

    consolidated = []
    end_round = rounds.get_last_round()
    for i in range(1, end_round+1):
        file_path = f'{PRICE_DATA_DIR}/round_{i}_price.csv'
        with open(file_path, 'r') as f:
            f.readline()
            reader = csv.reader(f)
            for row in reader:
                (gauge, 
                 amount, 
                 token_symbol, 
                 token_price, 
                 usd_value, 
                 votes, 
                 token_addr,
                 token_name,
                 per_vote) = row
                date = rounds.get_dates_for_round(i)[0]
                consolidated.append([
                    i,
                    str(date)[:10],
                    token_symbol,
                    amount,
                    usd_value,
                    gauge,
                    'block_number',
                    'choice_index',
                    token_name,
                    token_price,
                    token_addr,
                    votes,
                    'proposal',
                    'tx_hash',
                    per_vote,
                ])

    with open(f'{CONSOLIDATE_OUTPUT_DIR}/prices.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow([
            'round',
            'date',
            'token_symbol',
            'amount',
            'usd_amount',
            'choice',
            'block_number',
            'choice_index',
            'token_name',
            'token_price',
            'token_addr',
            'score',
            'proposal',
            'tx_hash',
            'per_vote'
        ])
        writer.writerows(consolidated)


def forecast():
    
    # Quick check on the current round
    current_round = rounds.get_current_round()
    if current_round is None:
        print("No current round found => Last round was ", rounds.get_last_round())
        sys.exit()

    # Get data for current round
    current_round_file = f"{PRICE_DATA_DIR}/round_{current_round}_price.csv"
    current_round_df = pd.read_csv(current_round_file)

    # Get data for last round
    last_round_file = f"{PRICE_DATA_DIR}/round_{current_round-1}_price.csv"
    last_round_df = pd.read_csv(last_round_file)

    # Create the forecast dataframe
    # forecast_df = pd.merge(last_round_df, current_round_df, on=['choice_index', 'token_symbol'], 
    #                        suffixes=('_last', '_current'), how='outer')
    forecast_df = pd.merge(current_round_df, last_round_df, on=['gauge', 'token_symbol'], 
                           suffixes=('_current', '_last'), how='outer')
    
    # Save to a file
    forecast_df.to_csv(f"{FORECAST_OUTPUT_DIR}/tmp-forecast-1.csv", index=False)

    # Compute the forecast
    forecast_df['chng'] = (forecast_df['usd_value_current'] - forecast_df['usd_value_last']) / forecast_df['usd_value_last'] * 100

    avg_change = 1 + forecast_df['chng'].mean() / 100
    print(f"{avg_change=}")
    forecast_df['forecast'] = forecast_df.apply(lambda x: x['usd_value_last'] * avg_change if pd.isnull(x['usd_value_current']) else x['usd_value_current'], axis=1)

    # Clean up duplicates from the outer merge
    # This occurs because the same gauge can be bribed multiple times by the same token in prior rounds
    duplicates = forecast_df.duplicated(subset=['gauge', 'token_symbol', 'amount_current'], keep='first')
    columns_to_set_nan = ['amount_current', 'usd_value_current', 'per_current', 'chng', 'forecast']
    forecast_df.loc[duplicates, columns_to_set_nan] = None

    # Save to a file
    forecast_df.to_csv(f"{FORECAST_OUTPUT_DIR}/tmp-forecast-2.csv", index=False)

    # Get the new gauges
    new_df = forecast_df[pd.isna(forecast_df['amount_last'])]

    # Format the dataframe for printing
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.float_format', '{:,.2f}'.format)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.max_columns', 100)
    pd.set_option('display.width', 1000)

    # forecast_df['choice'] = forecast_df['choice_last'].combine_first(forecast_df['choice_current'])
    forecast_df['amount_last'] = forecast_df['amount_last'].map('{:,.0f}'.format)
    forecast_df['per_vote_last'] = forecast_df['per_vote_last'].map('{:.4f}'.format)
    forecast_df['per_vote_current'] = forecast_df['per_vote_current'].map('{:.4f}'.format)
    forecast_df['amount_current'] = forecast_df['amount_current'].map('{:,.0f}'.format)
    forecast_df['chng'] = forecast_df['chng'].map('{:.1f}'.format)
    forecast_df.rename(columns={
        'token_symbol': 'symbol',
        'usd_value_last': 'usd_last',
        'amount_current': 'amount',
        'usd_value_current': 'usd',
        'per_vote_current': 'per'
    }, inplace=True)
    # max_block_number = int(forecast_df['block_number_current'].max())
    max_block_number = 0
    forecast_file = f"{FORECAST_OUTPUT_DIR}/forecast-{current_round}-{len(forecast_df)}.csv"
    forecast_df.to_csv(forecast_file, index=False)
    print(forecast_df[[
        'gauge',
        # 'choice_index', 
        # 'choice_current', 
        'symbol', 
        'amount', 
        'usd', 
        'per', 
        'chng', 
        'forecast', 
        # 'choice_last', 
        'amount_last', 
        'usd_last', 
        'per_vote_last',
        ]])

    print()
    print(f"Round {current_round-1}")
    print(f"- Total Gauges:    {forecast_df['usd_last'].count():,.0f}")
    # print(f"- Total USD:       ${last_round_usd:,.0f}")
    # print(f"- Total vlCVX:     {last_round_score:,.2f}")
    # print(f"- Per vlCVX:       ${last_round_usd / last_round_score:,.4f}")
    print()
    print(f"Round {current_round} Current")
    print(f"- New Gauges:      {new_df['forecast'].count():,.0f}")
    print(f"- New USD:         ${new_df['forecast'].sum():,.0f}")
    print(f"- Current Gauges:  {forecast_df['usd'].count():,.0f}")
    # print(f"- Current USD:     ${current_round_usd:,.0f}")
    # print(f"- Per vlCVX:       ${current_round_usd / current_round_score:,.4f}")
    print()
    print(f"Round {current_round} Forecast")
    print(f"- Forecast USD:    ${forecast_df['forecast'].sum():,.0f}")
    # print(f"- Per vlCVX:       ${forecast_df['forecast'].sum() / last_round_score:,.4f}")

    # os.remove(f"birbs/data/cache/{current_round}-bribes.csv")
    # os.remove(f"birbs/data/cache/{current_round}-proposal.json")
    # os.remove(f"birbs/data/cache/{current_round}-votes.json")


def main():
    # Create the consolidated file
    consolidate_data()

    # Run the forecast
    forecast()

    pass

if __name__ == '__main__':
    main()