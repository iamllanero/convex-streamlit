import streamlit as st
import pandas as pd
import glob

def main():
    st.set_page_config(page_title="Round Forecasts",
                       layout="wide")
    st.title("Round Forecasts")
    st.markdown("""
**Note: These forecasts are based on the current round's submitted incentives 
as determined by the smart contract events and an adjusted extrapolation based 
on the last round's incentives. This forecast should be used with caution as
it almost certainly will not be accurate!**
""")

    forecast_files = glob.glob('data/forecast*.csv')
    forecasts = [f.split('/')[-1].split('.')[0] for f in forecast_files]
    
    forecast = st.selectbox('Select a forecast', sorted(forecasts, reverse=True))

    df = pd.read_csv(f"data/{forecast}.csv")

    st.header("Forecast Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Forecast", 
            f"${df['forecast'].sum():,.0f}", 
            f"{df['forecast'].sum() - df['usd_last'].sum():+,.0f}"
        )

    with col2:
        st.metric(
            "Current Incentives", 
            f"${df['usd'].sum():,.0f}",
            f"{df['usd'].sum() - df['usd_last'].sum():+,.0f}"
        )

    with col3:
        st.metric(
            "No. of Gauges", 
            f"{df['usd'].count():,.0f}", 
            f"{df['usd'].count() - df['usd_last'].count():+,.0f}"
        )

    with col4:
        current_round_score = df.groupby('choice').first()['score_current'].sum()
        current_round_per = df['usd'].sum() / current_round_score
        last_round_score = df.groupby('choice').first()['score_last'].sum()
        last_round_per = df['usd_last'].sum() / last_round_score
        st.metric(
            "Per vlCVX",
            f"${current_round_per:,.4f}",
            f"{current_round_per - last_round_per:,.4f}",
        )

    st.header("Forecast Details")
    st.dataframe(
        df[['choice', 'symbol', 'amount', 'usd', 'per', 'amount_last', 'usd_last', 'per_last', 'forecast']],
        height=(df.shape[0] + 1) * 35 + 2,
        hide_index=True,
        use_container_width=True,
        column_config={
            'choice': st.column_config.TextColumn(
                'Gauge'),
            'symbol': st.column_config.TextColumn(
                'Token'),
            'amount': st.column_config.NumberColumn(
                'Amount',
                format="%.0f"),
            'usd': st.column_config.NumberColumn(
                'USD',
                format="$ %.2f"),
            'per': st.column_config.NumberColumn(
                'Per vlCVX',
                format="$ %.4f"),
            'amount_last': st.column_config.NumberColumn(
                'Amount Last',
                format="%.0f"),
            'usd_last': st.column_config.NumberColumn(
                'USD Last',
                format="$ %.2f"),
            'per_last': st.column_config.NumberColumn(
                'Per vlCVX Last',
                format="$ %.4f"),
            'forecast': st.column_config.NumberColumn(
                'Forecast USD',
                format="$ %.2f"),
        }
    )


if __name__ == "__main__":
    main()