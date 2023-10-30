import streamlit as st
import pandas as pd
from datetime import datetime
# from coingecko import get_historical_price

def convert_to(date, usd_amount, token_symbol):
    date = datetime.strptime(date, '%Y-%m-%d')
    # price = get_historical_price(token_symbol, date)
    price = 1
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
        'usd_amount': 'sum'
    }).reset_index()
    rounds_df['Incentives ($M)'] = rounds_df['usd_amount'] / 1000000
    rounds_df['Score (M)'] = rounds_df['score'] / 1000000
    rounds_df['Per ($)'] = rounds_df['usd_amount'] / rounds_df['score']

    # Augment rounds_df with other denominations
    for token_symbol in ['BTC', 'ETH', 'CRV', 'CVX']:
        rounds_df[token_symbol] = rounds_df.apply(lambda x: convert_to(x['date'], x['usd_amount'], token_symbol), axis=1)

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
    
    # st.header("Incentives per vlCVX")
    # st.text("NOTE: This is currently incorrect.")

    # st.bar_chart(data=rounds_df.iloc[show_rounds[0]-1:show_rounds[1]], 
    #              x='round', 
    #              y=['Per ($)'], 
    #              height=300)

    # st.header("Score (M)")
    # st.text("NOTE: This is currently incorrect.")

    # st.bar_chart(data=rounds_df.iloc[show_rounds[0]-1:show_rounds[1]], 
    #              x='round', 
    #              y=['Score (M)'], 
    #              height=300)

if __name__ == "__main__":
    main()