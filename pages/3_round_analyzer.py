import streamlit as st
import pandas as pd
from helper import adjusted_amount

def main():

    st.set_page_config(layout="wide")
    st.title("Round Analyzer")

    prices_df = pd.read_csv('output/consolidate/prices.csv')

    round_col, gauge_col, token_col = st.columns(3)

    with round_col:
        selected_round = st.selectbox('Select a round', sorted(prices_df['round'].unique(), reverse=True))

    with gauge_col:
        gauge_filter = st.text_input('Gauge Filter')
        if gauge_filter != '':
            prices_df = prices_df[prices_df['choice'].str.contains(gauge_filter)]

    with token_col:
        token_filter = st.multiselect('Tokens', 
                                      sorted(prices_df['token_symbol'].unique()),
                                      help='Select tokens to show, or leave blank to show all')
        if len(token_filter) > 0:
            prices_df = prices_df[prices_df['token_symbol'].isin(token_filter)]

    round_df = prices_df[prices_df['round'] == selected_round].copy()
    round_df['adj_amount'] = round_df.apply(lambda x: adjusted_amount(x['amount'], x['token_symbol']), axis=1) 
    round_df['per_vlcvx'] = round_df['usd_amount'] / round_df['score']

    grouped_df = round_df.groupby('choice').agg({
        'usd_amount': 'sum',
        'adj_amount': list,
        'token_symbol': list,
        'per_vlcvx': 'sum',
        'score': 'first',
    }).reset_index()
    grouped_df['tokens'] = grouped_df.apply(lambda x: '\n'.join([f"{a:,.0f} {s}\n" for a, s in zip(x['adj_amount'], x['token_symbol'])]), axis=1)

    # grouped_df
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total USD", 
            f"${round_df['usd_amount'].sum():,.0f}", 
        )
    
    with col2:
        st.metric(
            "Per vlCVX", 
            f"${round_df['usd_amount'].sum()/grouped_df['score'].sum():,.4f}", 
        )
    
    with col3:
        st.metric(
            "Total Gauges", 
            f"{grouped_df['score'].count():,.0f}", 
        )   
    
    with col4:
        st.metric(
            "Total Incentives", 
            f"{round_df['score'].count():,.0f}", 
        )   

    st.dataframe(
        # round_df[['choice', 'adj_amount', 'token_symbol', 'usd_amount', 'per_vlcvx']], 
        grouped_df[['choice', 'usd_amount', 'per_vlcvx', 'tokens']], 
        height=(grouped_df.shape[0] + 1) * 35 + 2,
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