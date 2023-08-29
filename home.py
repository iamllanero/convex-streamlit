import streamlit as st

page_text = """
This site is intended to provide insights into [Votium]() incentives. If you
are not already familiar with Votium and Convex, please refer to the docs.

_NOTE: The data on this site may be (and probably is) incorrect. Please do not
use it without your own research._

## Votium Incentives

This section shows a bar chart of the total incentives per round. You can 
specify the rounds to show.

Data is sourced from:

- Snapshot API
- Coingecko API
- Ethererum blockchain

## Token Trends

This section shows a stacked bar chart of the incentives per round broken down 
by tokens. You can specify the tokens to show as well as aggregate smaller 
tokens.

## Round Analyzer

This section shows a tablular breakdown of the gauge incentives for a selected 
round.

## Forecasts

This section shows a forecast of various rounds. The forecasts are currently
run sporadically so presented as the round number and latest block number.

## About

This site is created by me, [Llanero](https://x.com/iamllanero), for my own
research and as a fun project. Feel free to reach out to me via Twitter with
any questions, comments, or suggestions.

I'd like to acknowledge Curve, Convex, Votium, and Llama Airforce for this 
incredibly fun ecosystem. I'd also like to acknowledge Streamlit for their
very easy to use framework and open hosting.

"""


def main():
    st.set_page_config(page_title="Convex Votium Incentives",
                       layout="wide")
    st.title("Convex Votium Incentives")

    st.markdown(page_text)


if __name__ == "__main__":
    main()


