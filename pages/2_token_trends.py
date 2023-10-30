import streamlit as st
import pandas as pd

def main():
    st.set_page_config(page_title="Token Trends",
                       layout="wide")

    st.title("Token Trends")

    prices_df = pd.read_csv('output/consolidate/prices.csv')

    max_round = prices_df['round'].max()
    min_round = prices_df['round'].min()
    to_round = max_round
    from_round = to_round - 12

    from_round, to_round = st.slider(
        'Rounds to Display',
        min_value = min_round,
        max_value = max_round,
        value=[from_round,to_round],
        label_visibility="collapsed",
    )

    filtered_df = prices_df[(prices_df['round'] >= from_round) & (prices_df['round'] <= to_round)]

    # Group by the token symbols
    tokens_df = filtered_df.groupby(['round', 'token_symbol'])[['usd_amount']].sum().reset_index()
    tokens_df['usd_amount'] = tokens_df['usd_amount'] / 1000
    tokens_df['usd_amount'] = tokens_df['usd_amount'].round(0)

    # Pivot the table to have the tokens as columns
    pivot_df = tokens_df.pivot(index='round', columns='token_symbol', values='usd_amount').reset_index()
    sorted_cols = list(pivot_df.sum().sort_values(ascending=False).index)
    sorted_cols.remove('round')
    sorted_cols.insert(0, 'round')
    pivot_df = pivot_df[sorted_cols]

    tokens_col, other_col = st.columns(2)

    with tokens_col:
        cols = list(pivot_df.columns)
        cols.remove('round')

        token_filter = st.multiselect('Tokens', 
                                        sorted(cols),
                                        help='Select tokens to show, or leave blank to show all')
        if len(token_filter) > 0:
            token_filter.insert(0, 'round')
            pivot_df = pivot_df[token_filter]

    with other_col:
        num_tokens = st.slider('Number of Tokens to Show', 
                               min_value=0, 
                               max_value=tokens_df['token_symbol'].nunique()-1, 
                               value=10)
        # Aggregate the bottom tokens into 'Other'
        first_10_cols = pivot_df[pivot_df.columns[0:num_tokens+1]]
        pivot_df['Other'] = pivot_df[pivot_df.columns[num_tokens+1:]].sum(axis=1)
        pivot_df = pd.concat([first_10_cols, pivot_df['Other']], axis=1)


    st.bar_chart(
        data=pivot_df,
        x='round',
        height=(pivot_df.shape[0] + 1) * 35 + 2,
    )

    st.header("Token Breakdown ($ in thousands)")
    st.dataframe(pivot_df, hide_index=True, use_container_width=True, height=493)


if __name__ == "__main__":
    main()