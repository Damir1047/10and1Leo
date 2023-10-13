import csv
import json
import asyncio
import websockets
import chime
from datetime import datetime, timedelta

from ticker_class import Ticker
from functions import connect_to_tickers_candles, find_nearest_round_number_up


async def start():
    async with websockets.connect(Ticker.uri) as websocket:
        start_timestamp = (datetime.now() - timedelta(minutes=1)).timestamp()
        await connect_to_tickers_candles(websocket, name_ticker_dict, tf=60, start_timestamp=start_timestamp)
        async for message in websocket:
            data = (json.loads(message))
            # print(data)
            if 'data' in data:
                name = Ticker.guid_name_dict[data['guid']]

                ticker = name_ticker_dict[name]
                data = data['data']
                candle_time = data['time']
                date = datetime.fromtimestamp(candle_time)
                # print(f'{date} *** {name} *** o: {data["open"]}; c: {data["close"]}; h: {data["high"]}; l: {data["low"]}; v: {data["volume"]}')
                # следить за close или за hight?
                h = data["high"]
                c = data["close"]

                # подход к круглой цене
                perc_to_round = (ticker.round_price - c) / ticker.round_price * 100
                #print (c)
                if not ticker.close_to_round_price and c < ticker.round_price and perc_to_round <= Ticker.close_min_percent:
                    print(f'{date} --- {ticker.name}: curr_price: {c} round_price: {ticker.round_price} (до круглой цены осталось {round(perc_to_round, 2)})')
                    chime.theme('mario')
                    chime.success(sync=True)
                    ticker.close_to_round_price = True
                
                # круглая цена
                if not ticker.reached_round_price and c == ticker.round_price:
                    print(f'{date} --- {ticker.name}: curr_price: {c} round_price: {ticker.round_price} (дошли до круглой цены)')
                    ticker.reached_round_price = True
                
                # пробой круглой цены
                if not ticker.broke_the_round_price and c > ticker.round_price:
                    if not ticker.close_to_round_price:
                        # обновить максимальную цену так как она неправильная
                        nearest_round_number = find_nearest_round_number_up(c)
                        # print(f'***** {ticker.name} curr: {c}; обновили максимальную цену с {ticker.round_price} до {nearest_round_number}')
                        ticker.round_price = nearest_round_number
                    else:
                        print(f'{date} --- {ticker.name}: curr_price: {c} round_price: {ticker.round_price} (ПРОБИЛИ КРУГЛУЮ ЦЕНУ!!)')
                        chime.theme('mario')
                        chime.warning(sync=True)
                        ticker.broke_the_round_price = True
            else:
                name = Ticker.guid_name_dict[data['requestGuid']]
                ticker = name_ticker_dict[name]
                if data['httpCode'] != 200:
                    print(f'Не смог подключиться к {ticker.name}')


# словарь соответствия
name_ticker_dict = {}

with open(Ticker.max_prices_path) as f:
    reader = csv.reader(f)
    for row in reader:
        name = row[0]
        highest_price = float(row[1])
        round_price = float(row[2])
        print(float(row[2]))
        print(row[0])
        ticker = Ticker(name, highest_price, round_price)
        name_ticker_dict[name] = ticker

asyncio.get_event_loop().run_until_complete(start())
