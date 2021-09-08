# Author: Yogesh K for finxter.com
# python script: trading with Bollinger bands for Binance


import os
from binance.client import Client
import pprint
import pandas as pd     # needs pip install
import numpy as np
import matplotlib.pyplot as plt   # needs pip install

def get_data_frame():
    # valid intervals - 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
    # request historical candle (or klines) data using timestamp from above, interval either every min, hr, day or month
    # starttime = '30 minutes ago UTC' for last 30 mins time
    # e.g. client.get_historical_klines(symbol='ETHUSDTUSDT', '1m', starttime)
    # starttime = '1 Dec, 2017', '1 Jan, 2018'  for last month of 2017
    # e.g. client.get_historical_klines(symbol='BTCUSDT', '1h', "1 Dec, 2017", "1 Jan, 2018")
    starttime = '1 day ago UTC'  # to start for 1 day ago
    interval = '5m'
    bars = client.get_historical_klines(symbol, interval, starttime)
    pprint.pprint(bars)
    
    for line in bars:        # Keep only first 5 columns, "date" "open" "high" "low" "close"
        del line[5:]

    df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close']) #  2 dimensional tabular data
    return df

def plot_graph(df):
    df=df.astype(float)
    df[['close', 'sma','upper', 'lower']].plot()
    plt.xlabel('Date',fontsize=18)
    plt.ylabel('Close price',fontsize=18)
    x_axis = df.index
    plt.fill_between(x_axis, df['lower'], df['upper'], color='grey',alpha=0.30)

    plt.scatter(df.index,df['buy'], color='purple',label='Buy',  marker='^', alpha = 1) # purple = buy
    plt.scatter(df.index,df['sell'], color='red',label='Sell',  marker='v', alpha = 1)  # red = sell


    plt.show()


def buy_or_sell(df):

    buy_list  = pd.to_numeric(df['buy'], downcast='float')
    sell_list = pd.to_numeric(df['sell'], downcast='float')

    for i in range(len(buy_list)):
         # get current price of the symbol
        current_price = client.get_symbol_ticker(symbol =symbol)
        if float(current_price['price']) >= sell_list[i]:  # sell order
            print("sell sell sell...")
            sell_order = client.order_market_sell(symbol=symbol, quantity=0.01)
            print(sell_order)
        elif float(current_price['price']) <= buy_list[i]:  # buy order
            print("buy buy buy...")
            buy_order = client.order_market_buy(symbol=symbol, quantity=0.001)
            print(buy_order)
        else:
            print("...do nothing...")




def bollinger_trade_logic():
    symbol_df = get_data_frame()
    period = 20
    # small time Moving average. calculate 20 moving average using Pandas over close price
    symbol_df['sma'] = symbol_df['close'].rolling(period).mean()
    # Get standard deviation
    symbol_df['std'] = symbol_df['close'].rolling(period).std()

    # Calculate Upper Bollinger band
    symbol_df['upper'] = symbol_df['sma']  + (2 * symbol_df['std'])
    # Calculate Lower Bollinger band
    symbol_df['lower'] = symbol_df['sma']  - (2 * symbol_df['std'])

    # To print in human readable date and time (from timestamp)
    symbol_df.set_index('date', inplace=True)
    symbol_df.index = pd.to_datetime(symbol_df.index, unit='ms') # index set to first column = date_and_time
 
    # prepare buy and sell signals. The lists prepared are still panda dataframes with float nos
    close_list = pd.to_numeric(symbol_df['close'], downcast='float')
    upper_list = pd.to_numeric(symbol_df['upper'], downcast='float')
    lower_list = pd.to_numeric(symbol_df['lower'], downcast='float')

    symbol_df['buy'] = np.where(close_list < lower_list,   symbol_df['close'], np.NaN )
    symbol_df['sell'] = np.where(close_list > upper_list,   symbol_df['close'], np.NaN )

    with open('output.txt', 'w') as f:
        f.write(
                symbol_df.to_string()
               )
    
#    plot_graph(symbol_df)

    buy_or_sell(symbol_df)

    




def main():
    bollinger_trade_logic()


if __name__ == "__main__":

    api_key = os.environ.get('BINANCE_TESTNET_KEY')     # passkey (saved in bashrc for linux)
    api_secret = os.environ.get('BINANCE_TESTNET_PASSWORD')  # secret (saved in bashrc for linux)

    client = Client(api_key, api_secret, testnet=True)
    print("Using Binance TestNet Server")

    pprint.pprint(client.get_account())

    symbol = 'BTCUSDT'   # Change symbol here e.g. BTCUSDT, BNBBTC, ETHUSDT, NEOBTC
    main()
