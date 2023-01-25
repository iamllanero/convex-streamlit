import streamlit as st
import pandas as pd
# import altair as alt
from millify import millify

st.set_page_config(
    page_title='Convex Bribes', 
    page_icon=':moneybag:', 
    layout='wide', 
    initial_sidebar_state='auto', 
    menu_items=None
    )

st.title('Convex Bribe Rounds')

df = pd.read_csv('data/rounds-prices.csv')
# round,start,end,btc,eth,crv,cvx
df = df.astype({
    'round': 'int',
    'start': 'datetime64[ns]',
    'end': 'datetime64[ns]',
    'total_bribes': 'float64',
    'btc': 'float64',
    'eth': 'float64',
    'crv': 'float64',
    'cvx': 'float64',
})

df['bribes_btc'] = df['total_bribes'] / df['btc']
df['bribes_eth'] = df['total_bribes'] / df['eth']
df['bribes_crv'] = df['total_bribes'] / df['crv']
df['bribes_cvx'] = df['total_bribes'] / df['cvx']

df['cvxcrv'] = df['cvx'] / df['crv']

df['btc_chg'] = df['btc'].pct_change()
df['eth_chg'] = df['eth'].pct_change()
df['crv_chg'] = df['crv'].pct_change()
df['cvx_chg'] = df['cvx'].pct_change()

max_value = int(df['round'].max())
min_value = int(df['round'].min())
curr_round_bribe = float(df[df['round'] == max_value]['total_bribes'])
prev_round_bribe = float(df[df['round'] == (max_value - 1)]['total_bribes'])

metric1, metric2 = st.columns(2)
metric1.metric('Latest Round', max_value)
metric2.metric(
    'Latest Bribe', 
    f'${millify(curr_round_bribe, precision=2)}',
    f'${millify(curr_round_bribe - prev_round_bribe)}',
    )

show_rounds = st.slider(
    'Rounds to Display',
    min_value = min_value,
    max_value = max_value,
    value=[max_value-12,max_value],
)
print(f'{show_rounds=}')

st.header('Total Bribes')
denomination = st.selectbox(
    'Show denominated as',
    (
        'USD',
        'BTC',
        'ETH',
        'CRV',
        'CVX',
    )
)

y = {
    'USD': 'total_bribes',
    'BTC': 'bribes_btc',
    'ETH': 'bribes_eth',
    'CRV': 'bribes_crv',
    'CVX': 'bribes_cvx',
}[denomination]

st.bar_chart(
    data=df.iloc[show_rounds[0]-1:show_rounds[1]],
    x='round',
    y=y,
)

st.header('CVX/CRV Ratio')

print(df['cvxcrv'])
st.bar_chart(
    data=df.iloc[show_rounds[0]-1:show_rounds[1]],
    x='round',
    y='cvxcrv',
)

st.header('Token Price Changes')

# token1, token2, token3, token4 = st.columns(4)
# token1.checkbox('BTC', value=True)
# token2.checkbox('ETH', value=True)
# token3.checkbox('CRV', value=True)
# token4.checkbox('CVX', value=True)

with st.expander("Show/Hide Tokens"):
    show_btc = st.checkbox('BTC', value=True)
    show_eth = st.checkbox('ETH', value=True)
    show_crv = st.checkbox('CRV', value=True)
    show_cvx = st.checkbox('CVX', value=True)

show_tokens = []
if show_btc:
    show_tokens.append('btc_chg')
if show_eth:
    show_tokens.append('eth_chg')
if show_crv:
    show_tokens.append('crv_chg')
if show_cvx:
    show_tokens.append('cvx_chg')

st.line_chart(
    data=df.iloc[show_rounds[0]-1:show_rounds[1]],
    x='round',
    y=show_tokens,
)


# st.line_chart(
#     data=df,
#     x='end',
#     y=['apr_open', 'apr_close'],
#     )

# st.line_chart(
#     data=df,
#     x='end_date',
#     y=['cvxcrv_open', 'cvxcrv_close'],
#     )

# a = alt.Chart(df).mark_area(opacity=0.5).encode(
#     x='end_date', y='apr_close')

# b = alt.Chart(df).mark_area(opacity=0.6).encode(
#     x='end_date', y='cvxcrv_close')

# c = alt.layer(a, b)

# st.altair_chart(c, use_container_width=True)

st.header('Raw Data')
st.write(df)

