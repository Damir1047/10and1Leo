import asyncio
import websockets
import json
import csv
import time
from datetime import datetime, timedelta

from ticker_class import Ticker, get_acces_token

from settings import EXCHANGE, shares_path
from functions import get_lst_shares, connect_to_tickers_candles, find_nearest_round_number_up


def progress_data(message):
    data = (json.loads(message))
    # print('----------', data)
    if 'data' in data:
        name = Ticker.guid_name_dict[data['guid']]
        ticker = name_ticker_dict[name]
        data = data['data']
        candle_time = data['time']
        
        print(candle_time, Ticker.stop_timestamp) 
        
        if data['high'] > ticker.highest_price:
            ticker.highest_price = data['high']
        if not ticker.got_highest_price and Ticker.stop_timestamp == candle_time:
            print(ticker.name)
            ticker.got_highest_price = True
            del remaining_shares_dict[ticker.name]
    else:
        name = Ticker.guid_name_dict[data['requestGuid']]
        ticker = name_ticker_dict[name]
        if data['httpCode'] != 200:
            print('-', ticker.name)


def write_highest_price_to_file(file_for_write, tickers):
    rows = []
    for ticker in name_ticker_dict.values():
        rows.append([ticker.name, ticker.highest_price, find_nearest_round_number_up(ticker.highest_price)])
    with open(file_for_write, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)


async def start():
    async with websockets.connect(Ticker.uri) as websocket:
        await connect_to_tickers_candles(websocket, name_ticker_dict, 'M', Ticker.start_timestamp)
        
        # отладочная информация
        t1 = time.time()

        async for message in websocket:
            progress_data(message)
            print(f'осталось: {len(remaining_shares_dict)}')
            if len(remaining_shares_dict) < 250:
                print(list(remaining_shares_dict.keys()))
            if not len(remaining_shares_dict):
                # запись в файл
                write_highest_price_to_file(Ticker.max_prices_path, name_ticker_dict)
                t2 = time.time()
                print(t2 - t1)
                break


# словарь соответствия
name_ticker_dict = {}

# словарь для акций, к которым пока не получается подключиться
remaining_shares_dict = {}

names = get_lst_shares(shares_path)
# names = get_lst_shares(liquid_shares)

for name in names:
    ticker = Ticker(name)
    name_ticker_dict[name] = ticker
    remaining_shares_dict[name] = ticker

asyncio.get_event_loop().run_until_complete(start())
