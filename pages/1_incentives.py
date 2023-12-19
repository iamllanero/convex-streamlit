import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import os

TOKEN_IDS = {
    'BTC': '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',
    'ETH': '0x0000000000000000000000000000000000000000',
    'CRV': '0xd533a949740bb3306d119cc777fa900ba034cd52',
    'CVX': '0x4e3fbd56cd56c3e72c1403e103b45db9da5b9d2b',
}

# Prep the cache file
CACHE_DF = None
CACHE_FILE = "output/cache/dl_prices.csv"
if os.path.exists(CACHE_FILE):
    CACHE_DF = pd.read_csv(CACHE_FILE)
else:
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    CACHE_DF = pd.DataFrame(columns=['timestamp', 'chain', 'token_id', 'symbol', 'price'])
    CACHE_DF.to_csv(CACHE_FILE, index=False)

def get_price(token_symbol, date):

    token_id = TOKEN_IDS[token_symbol]
    timestamp = int(date.timestamp())

    # Check the cache
    if CACHE_DF[(CACHE_DF['timestamp'] == timestamp) & (CACHE_DF['token_id'] == token_id)].shape[0] > 0:
        return CACHE_DF[(CACHE_DF['timestamp'] == timestamp) & (CACHE_DF['token_id'] == token_id)]['price'].values[0]

    # Get the token price from the API
    url = f"https://coins.llama.fi/prices/historical/{timestamp}/ethereum:{token_id}?searchWidth=4h"
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        price = response.json()['coins'][f'ethereum:{token_id}']['price']
        # Add the result to the cache
        CACHE_DF.loc[len(CACHE_DF)] = [timestamp, 'ethereum', token_id, token_symbol, price]
        CACHE_DF.to_csv(CACHE_FILE, index=False)
        return price
    else:
        print(f"Error: {response.status_code}")
        print(f"URL: {url}")
        return None


def convert_to(date, usd_amount, token_symbol):
    date = datetime.strptime(date, '%Y-%m-%d')
    price = get_price(token_symbol, date)
    return usd_amount / price


def main():
    st.set_page_config(page_title="Incentives",
                       layout="wide")

    st.title("Incentives")

    prices_df = pd.read_csv('output/consolidate/prices.csv')

    # Create a dataframe with the total incentives per round
    # rounds_df = prices_df.groupby('round')[['usd_amount', 'score']].sum().reset_index()
    rounds_df = prices_df.groupby('round').agg({
        'date': 'first',
        'score': 'sum',
        'usd_value': 'sum'
    }).reset_index()
    rounds_df['Incentives ($M)'] = rounds_df['usd_value'] / 1000000
    rounds_df['Score (M)'] = rounds_df['score'] / 1000000
    rounds_df['Per ($)'] = rounds_df['usd_value'] / rounds_df['score']

    # Augment rounds_df with other denominations
    for token_symbol in ['BTC', 'ETH', 'CRV', 'CVX']:
        rounds_df[token_symbol] = rounds_df.apply(lambda x: convert_to(x['date'], x['usd_value'], token_symbol), axis=1)

    rounds_df['ETH (K)'] = rounds_df['ETH'] / 1000
    rounds_df['CRV (M)'] = rounds_df['CRV'] / 1000000
    rounds_df['CVX (100K)'] = rounds_df['CVX'] / 100000

    max_value = rounds_df['round'].max()
    min_value = rounds_df['round'].min()
    show_rounds = st.slider(
        'Rounds to Display',
        min_value = min_value,
        max_value = max_value,
        value=[max_value-12,max_value],
        label_visibility="collapsed",
    )

    st.bar_chart(data=rounds_df.iloc[show_rounds[0]-1:show_rounds[1]], 
                 x='round', 
                 y=['Incentives ($M)'], 
                 height=250)
    st.bar_chart(data=rounds_df.iloc[show_rounds[0]-1:show_rounds[1]], 
                 x='round', 
                 y=['ETH (K)'], 
                 height=250)
    st.bar_chart(data=rounds_df.iloc[show_rounds[0]-1:show_rounds[1]], 
                 x='round', 
                 y=['CRV (M)'], 
                 height=250)
    st.bar_chart(data=rounds_df.iloc[show_rounds[0]-1:show_rounds[1]], 
                 x='round', 
                 y=['CVX (100K)'], 
                 height=250)
    
    st.text("Incentives per vlCVX")

    st.bar_chart(data=rounds_df.iloc[show_rounds[0]-1:show_rounds[1]], 
                 x='round', 
                 y=['Per ($)'], 
                 height=300)

    st.text("Score (M)")
    st.bar_chart(data=rounds_df.iloc[show_rounds[0]-1:show_rounds[1]], 
                 x='round', 
                 y=['Score (M)'], 
                 height=250)

    # st.text("NOTE: This is currently incorrect.")

    # st.bar_chart(data=rounds_df.iloc[show_rounds[0]-1:show_rounds[1]], 
    #              x='round', 
    #              y=['Score (M)'], 
    #              height=300)

if __name__ == "__main__":
    main()