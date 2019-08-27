from datetime import datetime
from pytz import UTC  # timezone
import time

import numpy as np
import pandas as pd
from pandas import read_excel
import matplotlib.pyplot as plt

import bitfinex

import talib as ta

key = 'API KEY'
secrete = 'API KEY SECRET'

# Create api instance of the v2 API
api_v2 = bitfinex.bitfinex_v2.api_v2(key, secrete)


def DF_TO_EXCEL(df, filename, sheet_name):
    sheet_name = 'Sheet1' if len(sheet_name) == 0 else sheet_name
    writer = pd.ExcelWriter(filename)
    df.to_excel(writer, sheet_name)
    writer.save()


def DF_TO_EXCEL_MUL(dfs, filename):
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    for sheetname, df in dfs.items():  # loop through `dict` of dataframes
        df.to_excel(writer, sheet_name=sheetname)  # send df to writer
        worksheet = writer.sheets[sheetname]  # pull worksheet object
        for idx, col in enumerate(df):  # loop through all columns
            series = df[col]
            max_len = max((
                series.astype(str).map(len).max(),  # len of largest item
                len(str(series.name))  # len of column name/header
            )) + 1  # adding a little extra space
            worksheet.set_column(idx, idx, max_len)  # set column width
    writer.save()


def data_to_pandas(pair_data):
    # Create pandas data frame and clean/format data
    names = ['time', 'open', 'close', 'high', 'low', 'volume']
    df = pd.DataFrame(pair_data, columns=names)
    df.drop_duplicates(inplace=True)
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df.set_index('time', inplace=True)
    df.sort_index(inplace=True)
    return df


def fetch_data(start, stop, symbol, interval, tick_limit, step):
    # Create api instance
    api_v2 = bitfinex.bitfinex_v2.api_v2(key, secrete)
    data = []
    start = start - step
    while start < stop:
        start = start + step
        end = start + step
        res = api_v2.candles(symbol=symbol, interval=interval,
                             limit=tick_limit, start=start,
                             end=end)
        data.extend(res)
        time.sleep(1)
    return data


if __name__ == "__main__":

    # Define query parameters
    pair = 'ethusd'  # Currency pair of interest
    bin_size = '1h'  # This will return minute data
    limit = 5000    # We want the maximum of 1000 data points
    # Set step size
    time_step = limit * 5*60*1000  # x bin_size

    # Define the start date
    t_start = datetime(2019, 1, 1, 0, 0)
    t_start = time.mktime(t_start.timetuple()) * 1000

    # Define the end date
    t_stop = datetime(2019, 8, 27, 0, 0)
    t_stop = time.mktime(t_stop.timetuple()) * 1000

    pair_data = fetch_data(start=t_start, stop=t_stop, symbol=pair,
                           interval=bin_size, tick_limit=limit,
                           step=time_step)

    last_index = pair_data.index('error') if pair_data.index(
        'error') > 0 else len(pair_data)

    df = data_to_pandas(pair_data[:last_index])

    # Calculate ATR

    timeperiod = 14

    high = df.high.values
    low = df.low.values
    close = df.close.values

    atr = ta.ATR(high, low, close, timeperiod=timeperiod)
    atr_sma = ta.SMA(atr, timeperiod)
    atr_sma[0:timeperiod] = 0
    atr[0:timeperiod] = 0
    df['atr'] = atr
    df['atr_sma'] = atr_sma

    df = df.fillna(0)

    # Calculate Zone
    zone_len = 1 if df['close'][:-1].values[0] < 500 else 500  # manage zone
    df['zone'] = df['close'].apply(lambda x: (x-(x % zone_len)))

    path = 'data'
    filename = '{path}/{pair}_{bin_size}-x.xlsx'.format(
        path=path, pair=pair, bin_size=bin_size)
    sheet_name = pair
    DF_TO_EXCEL(df, filename, sheet_name)

    print(filename)
