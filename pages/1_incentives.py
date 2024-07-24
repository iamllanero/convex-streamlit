import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import os

# Constants
TOKEN_IDS = {
    "BTC": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
    "ETH": "0x0000000000000000000000000000000000000000",
    "CRV": "0xd533a949740bb3306d119cc777fa900ba034cd52",
    "CVX": "0x4e3fbd56cd56c3e72c1403e103b45db9da5b9d2b",
}

CACHE_FILE = "output/cache/dl_prices.csv"


def load_cache():
    if os.path.exists(CACHE_FILE):
        df = pd.read_csv(CACHE_FILE)
        df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
        return df
    else:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        df = pd.DataFrame(
            {
                "timestamp": pd.Series(dtype="float64"),
                "chain": pd.Series(dtype="str"),
                "token_id": pd.Series(dtype="str"),
                "symbol": pd.Series(dtype="str"),
                "price": pd.Series(dtype="float64"),
            }
        )
        df.to_csv(CACHE_FILE, index=False)
        return df


def get_price(token_symbol, date, cache_df):
    token_id = TOKEN_IDS[token_symbol]
    timestamp = date.timestamp()

    cached_price = cache_df[
        (cache_df["timestamp"] == timestamp) & (cache_df["token_id"] == token_id)
    ]
    if not cached_price.empty:
        return cached_price["price"].values[0]

    url = f"https://coins.llama.fi/prices/historical/{int(timestamp)}/ethereum:{token_id}?searchWidth=4h"
    response = requests.get(url)
    if response.status_code == 200:
        price = response.json()["coins"][f"ethereum:{token_id}"]["price"]
        new_row = pd.DataFrame(
            {
                "timestamp": [timestamp],
                "chain": ["ethereum"],
                "token_id": [token_id],
                "symbol": [token_symbol],
                "price": [price],
            }
        )
        cache_df = pd.concat([cache_df, new_row], ignore_index=True)
        cache_df.to_csv(CACHE_FILE, index=False)
        return price
    else:
        print(f"Error: {response.status_code}")
        print(f"URL: {url}")
        return None


def convert_to(date, usd_amount, token_symbol, cache_df):
    date = pd.to_datetime(date)
    price = get_price(token_symbol, date, cache_df)
    return usd_amount / price if price else None


def process_data(prices_df):
    print("Loading cache")
    cache_df = load_cache()

    # Preprocess the data
    print("Preprocessing data")
    prices_df["date"] = pd.to_datetime(prices_df["date"])
    prices_df["usd_value"] = pd.to_numeric(prices_df["usd_value"], errors="coerce")
    prices_df["score"] = pd.to_numeric(prices_df["score"], errors="coerce")
    prices_df["round"] = pd.to_numeric(prices_df["round"], errors="coerce")

    # Aggregate data by round
    print("Calculating rounds dataframe")
    rounds_df = (
        prices_df.groupby("round")
        .agg({"date": "first", "usd_value": "sum", "score": "sum"})
        .reset_index()
    )

    # Calculate metrics
    rounds_df["Incentives ($M)"] = rounds_df["usd_value"] / 1000000
    rounds_df["Score (M)"] = rounds_df["score"] / 1000000
    rounds_df["Per ($)"] = rounds_df["usd_value"] / rounds_df["score"]

    # Augment rounds_df with other denominations
    for token_symbol in ["BTC", "ETH", "CRV", "CVX"]:
        rounds_df[token_symbol] = rounds_df.apply(
            lambda x: convert_to(x["date"], x["usd_value"], token_symbol, cache_df),
            axis=1,
        )

    rounds_df["ETH (K)"] = rounds_df["ETH"] / 1000
    rounds_df["CRV (M)"] = rounds_df["CRV"] / 1000000
    rounds_df["CVX (100K)"] = rounds_df["CVX"] / 100000

    # Ensure all numeric columns are float64
    for col in rounds_df.columns:
        if rounds_df[col].dtype.name != "datetime64[ns]":
            rounds_df[col] = pd.to_numeric(rounds_df[col], errors="coerce")

    return rounds_df


def main():
    st.set_page_config(page_title="Incentives", layout="wide")
    st.title("Incentives")

    try:
        # Load and process data
        prices_df = pd.read_csv("output/consolidate/prices.csv")
        rounds_df = process_data(prices_df)

        # Debugging: Display the processed data
        # st.subheader("Debug: Processed Data")
        # st.write(rounds_df.dtypes)
        # st.write(rounds_df)

        # Set up slider
        max_value = int(rounds_df["round"].max())
        min_value = int(rounds_df["round"].min())
        show_rounds = st.slider(
            "Rounds to Display",
            min_value=min_value,
            max_value=max_value,
            value=[max(min_value, max_value - 12), max_value],
            step=1,
            label_visibility="collapsed",
        )

        # Select and display data
        selected_df = rounds_df[
            rounds_df["round"].between(show_rounds[0], show_rounds[1])
        ].sort_values("round")

        # Display charts
        for column in ["Incentives ($M)", "ETH (K)", "CRV (M)", "CVX (100K)"]:
            st.subheader(f"{column} Chart")
            chart_data = selected_df[["round", column]]
            # st.write(chart_data)  # Debug: Show data being used for the chart
            st.bar_chart(data=chart_data, x="round", y=column, height=250)

        st.subheader("Incentives per vlCVX")
        per_data = selected_df[["round", "Per ($)"]]
        # st.write(per_data)  # Debug: Show data being used for the chart
        st.bar_chart(data=per_data, x="round", y="Per ($)", height=300)

        st.subheader("Score (M)")
        score_data = selected_df[["round", "Score (M)"]]
        # st.write(score_data)  # Debug: Show data being used for the chart
        st.bar_chart(data=score_data, x="round", y="Score (M)", height=250)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Debug information:")
        st.write(
            f"rounds_df shape: {rounds_df.shape if 'rounds_df' in locals() else 'Not available'}"
        )
        st.write(
            f"rounds_df dtypes: {rounds_df.dtypes if 'rounds_df' in locals() else 'Not available'}"
        )
        st.write(f"rounds_df info:")
        st.write(rounds_df.info() if "rounds_df" in locals() else "Not available")


if __name__ == "__main__":
    main()
