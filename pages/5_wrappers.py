from datetime import datetime
from web3 import Web3
import altair as alt
import csv
import os
import pandas as pd
import requests
import streamlit as st


WRAPPER_FILE = 'output/wrappers/wrappers.csv'

WRAPPERS = [
    {
        'name': 'PRISMA',
        'base': '0xdA47862a83dac0c112BA89c6abC2159b95afd71C',
        'wrapper': '0x34635280737b5BFe6c7DC2FC3065D60d66e78185',
        'pool': '0x3b21C2868B6028CfB38Ff86127eF22E68d16d53B',
    },
    {
        'name': 'FXS',
        'base': '0x3432B6A60D23Ca0dFCa7761B7ab56459D9C964D0',
        'wrapper': '0xFEEf77d3f69374f66429C91d732A244f074bdf74',
        'pool': '0x6a9014FB802dCC5efE3b97Fd40aAa632585636D0',
    },
    {
        'name': 'CRV',
        'base': '0xD533a949740bb3306d119CC777fa900bA034cd52',
        'wrapper': '0x62B9c7356A2Dc64a1969e19C23e4f579F9810Aa7',
        'pool': '0x971add32Ea87f10bD192671630be3BE8A11b8623',
    },
    {
        'name': 'FPIS',
        'base': '0xc2544A32872A91F4A553b404C6950e89De901fdb',
        'wrapper': '0xa2847348b58CEd0cA58d23c7e9106A49f1427Df6',
        'pool': '0xfBB481A443382416357fA81F16dB5A725DC6ceC8',
    },
    {
        'name': 'FXN',
        'base': '0x365AccFCa291e7D3914637ABf1F7635dB165Bb09',
        'wrapper': '0x183395DbD0B5e93323a7286D1973150697FFFCB3',
        'pool': '0x1062FD8eD633c1f080754c19317cb3912810B5e5',
    },
]

WEB3_HTTP_PROVIDER = os.environ.get('WEB3_HTTP_PROVIDER')
w3 = Web3(Web3.HTTPProvider(WEB3_HTTP_PROVIDER))


def get_pool_balances(address):

    with open('data/abis/curve_other_factory.json') as f:
        abi = f.read()
    contract = w3.eth.contract(address=address, abi=abi)
    balance0 = contract.functions.balances(0).call() / 1e18
    balance1 = contract.functions.balances(1).call() / 1e18

    return balance0, balance1


def get_price(address):
    url = f"https://coins.llama.fi/prices/current/ethereum:{address}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    return data['coins'][f'ethereum:{address}']['price']


def update_data():

    timestamp = int(datetime.now().timestamp())

    for wrapper in WRAPPERS:
        base_balance, wrapper_balance = get_pool_balances(wrapper['pool'])
        base_balance_pct = base_balance / (base_balance + wrapper_balance)
        base_price = get_price(wrapper['base'])
        wrapper_price = get_price(wrapper['wrapper'])
        peg = wrapper_price / base_price
        with open(WRAPPER_FILE, 'a') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                wrapper['name'],
                base_balance,
                wrapper_balance,
                base_balance_pct,
                base_price,
                wrapper_price,
                peg,
            ])


def check_data():

    # If file doesn't exist, create it
    if not os.path.exists(WRAPPER_FILE):
        os.makedirs(os.path.dirname(WRAPPER_FILE), exist_ok=True)
        with open(WRAPPER_FILE, 'w') as f:
            writer = csv.writer(f)
            writer.writerow([
                            'timestamp',
                            'name',
                            'base_balance',
                            'wrapper_balance',
                            'base_balance_pct',
                            'base_price',
                            'wrapper_price',
                            'peg',
                            ])

    # Else, read it in
    else:
        df = pd.read_csv(WRAPPER_FILE)

        # Get the highest timestamp
        highest_timestamp = df['timestamp'].max()

        # Get the current UNIX timestamp
        timestamp = int(datetime.now().timestamp())

        # If timestamp more than 12 seconds (avg eth block time), update data
        if timestamp - highest_timestamp > 12:
            print(f"Updating data...({timestamp - highest_timestamp} elapsed)")
            update_data()


def main():
    st.set_page_config(page_title="Round Forecasts",
                       layout="wide")

    st.title("Convex Wrappers")
    st.markdown("""
**Note: This page is a quick and dirty implementation for now. It pulls the 
data "just in time" on each page refresh.**
""")

    df = pd.read_csv(WRAPPER_FILE)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df

    # Create a Streamlit line chart for each 'name' group
    st.title("Peg Values Over Time")
    chart = alt.Chart(df).mark_line().encode(
        x='timestamp:T',
        y=alt.Y('peg:Q', scale=alt.Scale(domain=[0.5, 1.0])),
        color='name:N'
    ).properties(
        width=800,
        height=400
    )

    st.altair_chart(chart)

    check_data()



if __name__ == "__main__":
    main()
