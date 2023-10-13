import csv
import json

from settings import EXCHANGE
from ticker_class import Ticker


async def connect_to_tickers_candles(websocket, name_ticker_dict, tf, start_timestamp):
    # подключаемся к бумагам
    for ticker in name_ticker_dict.values():
        payload = {
            "token": Ticker.acces_token,
            "opcode": "BarsGetAndSubscribe",
            "code": ticker.name,
            "tf": tf,
            "from": start_timestamp,
            "delayed": 'false',
            "exchange": EXCHANGE,
            "format": "Simple",
            "guid": ticker.guid,
        }
        await websocket.send(json.dumps(payload))    


def get_lst_shares(file_path):
    """принимает csv файл и возвращяет список имен акций"""
    # акции, к которым будем подключаться
    tickers = []
    with open(file_path) as f:
        reader = csv.reader(f)
        i = 0
        for row in reader:
            name = row[0].replace('.', ' ')
            if name not in Ticker.prohibited_tickers:
                tickers.append(name)
    return tickers


def find_nearest_round_number_up(num):
    #new round number finder by Damir
    if num < 11:
        return int(num) + 1
    if num < 50:
        return (int(num / 5) + 1) * 5
    if num < 100:
        return (int(num / 10) + 1) * 10
    if num < 500:
        return (int(num / 50) + 1) * 50
    if num < 1000:
        return (int(num / 100) + 1) * 100
    if num < 5000:
        return (int(num / 500) + 1) * 500
    if num < 10000:
        return (int(num / 1000) + 1) * 1000
    if num < 100000:
        return (int(num / 10000) + 1) * 10000
    if num < 1000000:
        return (int(num / 100000) + 1) * 100000
    # Old finder
    # res = int(num) + 1
    # # print(res)
    # while res % 10:
    #     res += 1
    # return res
