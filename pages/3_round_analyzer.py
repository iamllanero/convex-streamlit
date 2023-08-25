import streamlit as st
import pandas as pd
from helper import adjusted_amount

def main():

    st.set_page_config(layout="wide")
    st.title("Round Analyzer")

    prices_df = pd.read_csv('data/prices.csv')

    round_col, gauge_col, token_col = st.columns(3)

    with round_col:
        selected_round = st.selectbox('Select a round', sorted(prices_df['round'].unique(), reverse=True))

    with gauge_col:
        gauge_filter = st.text_input('Gauge Filter')
        if gauge_filter is not '':
            prices_df = prices_df[prices_df['choice'].str.contains(gauge_filter)]

    with token_col:
        token_filter = st.multiselect('Tokens', 
                                      sorted(prices_df['token_symbol'].unique()),
                                      help='Select tokens to show, or leave blank to show all')
        if len(token_filter) > 0:
            prices_df = prices_df[prices_df['token_symbol'].isin(token_filter)]

    round_df = prices_df[prices_df['round'] == selected_round]  
    round_df['adj_amount'] = round_df['amount'].apply(lambda x: adjusted_amount(x, round_df['token_symbol'].iloc[0])) 
    round_df['per_vlcvx'] = round_df['usd_amount'] / round_df['score']

    grouped_df = round_df.groupby('choice').agg({
        'usd_amount': 'sum',
        'adj_amount': list,
        'token_symbol': list,
        'per_vlcvx': 'sum',
    }).reset_index()
    grouped_df['tokens'] = grouped_df.apply(lambda x: '\n'.join([f"{a:,.0f} {s}\n" for a, s in zip(x['adj_amount'], x['token_symbol'])]), axis=1)

    # grouped_df

    st.dataframe(
        # round_df[['choice', 'adj_amount', 'token_symbol', 'usd_amount', 'per_vlcvx']], 
        grouped_df[['choice', 'usd_amount', 'per_vlcvx', 'tokens']], 
        height=500,
        hide_index=True,
        use_container_width=True,
        column_config={
            'choice': st.column_config.TextColumn(
                'Gauge'),
            'token_symbol': st.column_config.TextColumn(
                'Token',
                ),
            'adj_amount': st.column_config.NumberColumn(
                'Amount',
                format="%.0f"),
            'usd_amount': st.column_config.NumberColumn(
                'USD',
                format="$ %.2f"),
            'per_vlcvx': st.column_config.NumberColumn(
                'Per vlCVX',
                format="$ %.4f"),
        }
    )
    

if __name__ == '__main__':
    main()