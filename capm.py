import datetime
import pandas as pd
import streamlit as st
import yfinance as yf
import pandas_datareader.data as web
import capm_functions

# setting page layout
st.set_page_config(page_title="CAPM",
                   page_icon="chart_with_upwards_trend",
                   layout='wide')
# set title
st.title("Capital Asset pricing model")

# input
# columns layout
try:
    col1, col2 = st.columns([1, 1])

    with col1:
        stocks_list = st.multiselect("Choose 4 stocks", ('TSLA', 'AAPL', 'NFLX', 'MSFT', 'MGM', 'AMZN', 'NVDA', 'GOOGL'),['TSLA', 'AAPL','AMZN', 'GOOGL'])
    with col2:
        years = st.number_input("Number of year", 1, 10)

    # Downloading data for sp500

    end = datetime.date.today()
    start = datetime.date(datetime.date.today().year-years, datetime.date.today().month, datetime.date.today().day)
    sp500 = web.DataReader(['sp500'], 'fred', start, end)

    # new dataframe
    stock_df = pd.DataFrame()

    for stock in stocks_list:
        data = yf.download(stock, period=f'{years}y')
        stock_df[f'{stock}'] = data['Close']

    stock_df.reset_index(inplace=True)
    sp500.reset_index(inplace=True)

    sp500.rename(columns={'DATE': 'Date'}, inplace=True)

    stock_df = pd.merge(stock_df, sp500, on='Date', how='inner')

    col3, col4 = st.columns([1, 1])

    with col3:
        st.markdown("### Dataframe Head")
        st.dataframe(stock_df.head(), use_container_width=True)

    with col4:
        st.markdown("### Dataframe Tail")
        st.dataframe(stock_df.tail(), use_container_width=True)

    # plots

    col5, col6 = st.columns([1, 1])

    with col5:
        st.markdown("### Prices over time")
        st.plotly_chart(capm_functions.interactive_fig(stock_df))
    with col6:
        st.markdown("### Normalize price")
        norm_df = capm_functions.normalize_stock(stock_df)
        st.plotly_chart(capm_functions.interactive_fig(norm_df))

    stocks_daily_return = capm_functions.daily_return(stock_df)
    print(stocks_daily_return)

    beta = {}
    alpha = {}

    for i in stocks_daily_return.columns:
        if i != 'Date' and i != 'sp500':
            b,a = capm_functions.calculate_beta(stocks_daily_return, i)
            beta[i] = b
            alpha[i] = a
    print(alpha,beta)

    beta_df = pd.DataFrame(columns=['Stock', 'Beta value'])
    beta_df['Stock'] = beta.keys()
    beta_df['Beta value'] = [str(round(i,2)) for i in beta.values()]


    col7, col8 = st.columns([1,1])
    with col7:
        st.markdown("### Calculated beta values")
        st.dataframe(beta_df, use_container_width=True)

    rf = 0
    rm = stocks_daily_return['sp500'].mean() * 252

    return_df = pd.DataFrame()
    return_values = []

    for stock, value in beta.items():
        return_values.append(str(round(rf+(value*(rm-rf)),2)))
    return_df['Stock'] = stocks_list

    return_df['Return_values'] = return_values

    with col8:
        st.markdown("### Calculated return using capm")
        st.dataframe(return_df, use_container_width=True)

except:
    st.write('Please select valid input')
