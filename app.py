import streamlit as st
import pandas as pd
import altair as alt
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

# print(df['cvxcrv'])
st.bar_chart(
    data=df.iloc[show_rounds[0]-1:show_rounds[1]],
    x='round',
    y='cvxcrv',
)

st.header('Token Price Changes')

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

st.header('Raw Data')
st.write(df)

st.header('Bribe Data')
bribes_df = pd.read_csv('data/rounds-bribes.csv')
bribes_df = bribes_df.iloc[show_rounds[0]-1:show_rounds[1]].copy()
bribes_df = bribes_df.dropna(axis=1, how='all')
bribes = list(bribes_df.columns)
bribes.remove('round')
bribes_df = pd.concat([bribes_df['round'].astype('string'), bribes_df[bribes].astype('float64')], axis=1)
wide_df = bribes_df.melt('round', var_name='briber', value_name='amount')
st.altair_chart(
    alt.Chart(wide_df).mark_area().encode(
        x='round',
        y=alt.Y('amount', stack='normalize'),
        color='briber',
    ),
    use_container_width=True,
)

st.header('Bribe Summary')
summary_df = pd.concat([bribes_df.sum().T, bribes_df.describe().T], axis=1)
summary_df.columns = ['sum', 'count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']
st.write(summary_df)

st.header('Bribe Raw Data')
st.write(bribes_df)

