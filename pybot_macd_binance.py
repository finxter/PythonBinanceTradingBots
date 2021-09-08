# Author: Yogesh K for finxter academy
# MACD - Moving average convergence divergence 
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
    starttime = '1 day ago UTC'
    interval = '1m'
    bars = client.get_historical_klines(symbol, interval, starttime)

    for line in bars:        # Keep only first 5 columns, "date" "open" "high" "low" "close"
        del line[5:]

    df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close']) #  2 dimensional tabular data
    return df

def plot_graph(df):

    df=df.astype(float)
    df[['close', 'MACD','signal']].plot()
    plt.xlabel('Date',fontsize=18)
    plt.ylabel('Close price',fontsize=18)
    x_axis = df.index

    plt.scatter(df.index,df['Buy'], color='purple',label='Buy',  marker='^', alpha = 1) # purple = buy
    plt.scatter(df.index,df['Sell'], color='red',label='Sell',  marker='v', alpha = 1)  # red = sell

    plt.show()



def buy_or_sell(df, buy_sell_list):
    for index, value in enumerate(buy_sell_list):
        current_price = client.get_symbol_ticker(symbol =symbol)
        print(current_price['price']) # Output is in json format, only price needs to be accessed
        if value == 1.0 : # signal to buy (either compare with current price to buy/sell or use limit order with close price)
            if current_price['price'] < df['Buy'][index]:
                print("buy buy buy....")
                buy_order = client.order_market_buy(symbol=symbol, quantity=1)
                print(buy_order)
        
        elif value == -1.0: # signal to sell
            if current_price['price'] > df['Sell'][index]:
                print("sell sell sell....")
                sell_order = client.order_market_sell(symbol=symbol, quantity=1)
                print(sell_order)
        else:
            print("nothing to do...")



def macd_trade_logic():
    symbol_df = get_data_frame()

    # calculate short and long EMA mostly using close values
    shortEMA = symbol_df['close'].ewm(span=12, adjust=False).mean()
    longEMA = symbol_df['close'].ewm(span=26, adjust=False).mean()
    
    # Calculate MACD and signal line
    MACD = shortEMA - longEMA
    signal = MACD.ewm(span=9, adjust=False).mean()

    symbol_df['MACD'] = MACD
    symbol_df['signal'] = signal

    # To print in human readable date and time (from timestamp)
    symbol_df.set_index('date', inplace=True)
    symbol_df.index = pd.to_datetime(symbol_df.index, unit='ms') # index set to first column = date_and_time

    symbol_df['Trigger'] = np.where(symbol_df['MACD'] > symbol_df['signal'], 1, 0)
    symbol_df['Position'] = symbol_df['Trigger'].diff()
    
    # Add buy and sell columns
    symbol_df['Buy'] = np.where(symbol_df['Position'] == 1,symbol_df['close'], np.NaN )
    symbol_df['Sell'] = np.where(symbol_df['Position'] == -1,symbol_df['close'], np.NaN )


    with open('output.txt', 'w') as f:
        f.write(
                symbol_df.to_string()
               )
    

   # plot_graph(symbol_df)

    # get the column=Position as a list of items.
    buy_sell_list = symbol_df['Position'].tolist()

    buy_or_sell(symbol_df, buy_sell_list)




def main():
    macd_trade_logic()





if __name__ == "__main__":

    api_key = os.environ.get('BINANCE_TESTNET_KEY')     # passkey (saved in bashrc for linux)
    api_secret = os.environ.get('BINANCE_TESTNET_PASSWORD')  # secret (saved in bashrc for linux)

    client = Client(api_key, api_secret, testnet=True)
    print("Using Binance TestNet Server")

    pprint.pprint(client.get_account())

    symbol = 'BNBUSDT'   # Change symbol here e.g. BTCUSDT, BNBBTC, ETHUSDT, NEOBTC
    main()
