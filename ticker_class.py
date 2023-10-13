import csv
import json
import uuid
from datetime import datetime, timedelta
import pickle
import requests

from settings import REFRESH_TOKEN, URL_OAUTH


def get_acces_token():
        payload = {'token': REFRESH_TOKEN}
        res = requests.post(
            url=f'{URL_OAUTH}/refresh',
            params=payload
        )
        return res.json()['AccessToken']


class Ticker:
    uri = "wss://api.alor.ru/ws"
    max_prices_path = './shares/max_prices.csv'
    start_timestamp = datetime(2023, 9, 30).timestamp()
    now = datetime.now()
    stop_timestamp = (datetime(now.year, now.month, 1, hour=3, minute=0, second=0) + timedelta(hours=2)).timestamp()
    acces_token = get_acces_token()

    close_min_percent = 0.5

    guid_name_dict = {}
    # акции, которые недоступны через api алора 'MXIM', 'BBWI', 'FOX', 'COTY', 'CCJ', 'VSCO', 'GXO', 'CNI','LFST', 
    prohibited_tickers = ['MXIM', 'BBWI','VSCO', 'GXO','KSU', 'QTS', 'PFPT', 'SYKE', 'LII', 'SWI', 'CCJ', 'CHCO', 'PSMT', 'QADA', 'GATX', 'SXI', 'CNI', 'ATR', 'MUSA', 'LNN', 'UNF', 'WRB', 'COHR', 'RXN', 'UFS', 'WWD', 'SAFM', 'MDLA', 'STMP', 'CLDR', 'CREE', 'JCOM', 'CSOD', 'XEC', 'COG', 'MLHR', 'RAVN', 'GRA', 'SIGI', 'UMBF', 'MGLN', 'OSIS', 'CW', 'RBC', 'NWLI', 'KWR', 'WSO', 'FCNCA','THG', 'XLRN', 'ECHO', 'SJW', 'BRKS', 'MKL', 'ACA', 'ACBF1P1', 'AFYA', 'AGX', 'AKRO', 'ASMB', 'ASTE', 'ATHM', 'Atomenpr01', 'ATRR01', 'ATSG', 'AZZ', 'B', 'B4B@DE', 'B4B3@DE', 'BANF', 'BANR', 'BEI@DE', 'BEL0226', 'BEL0230', 'BEL0231', 'BEL0627', 'BKKT', 'BMW3@DE', 'BOOM', 'BP', 'BRK A', 'CAC', 'CART', 'CATY', 'CBZ', 'CHMF0924', 'CNA', 'CPSI', 'CSIQ', 'CSTL', 'CTS', 'CUE', 'CVI', 'DIRP01', 'DIRP02', 'DIRP03', 'DMNN01', 'DOYU', 'DTE', 'EBIX', 'EFSC', 'EGBN', 'EGPT0329', 'EGPT0431', 'EHC', 'ELFV', 'ENRC01', 'EQNR', 'FBK', 'FBNC', 'FIE@DE', 'FIX', 'FSS', 'GAZP0325', 'GAZP0326', 'GAZP0327', 'GAZP0837', 'GAZP1124', 'GAZP1128', 'GBF@DE', 'GLGR02', 'GLPR0923', 'GOLF', 'GTY', 'HAYN', 'HCI', 'HELE', 'HEN@DE', 'HLAG@DE', 'HLIO', 'HMN', 'HMST', 'HSII', 'HTLF', 'HY', 'IBOC', 'IIIV', 'ISBNK0424', 'IVX@DE', 'JYNT', 'KAMN', 'KBR', 'KCEL', 'KFRC', 'KROS', 'KVYO', 'LAAC', 'LEN B', 'LKFN', 'LMAT', 'LTC', 'LUK1126', 'LX', 'LZB', 'MATW', 'MBG@DE', 'MFC', 'MLI', 'MODN', 'MOR@DE', 'MRTN', 'MT', 'MTS18soc', 'NAT', 'NBTB', 'NGM', 'NPO', 'NSA', 'OMA0128', 'OMA0148', 'OMI', 'ORG1P1', 'OTTR', 'OXM', 'PAHC', 'PARAA', 'PBR', 'PDD', 'PEBO', 'PETS', 'PHAT', 'PLOW', 'PNM', 'POWL', 'PSM@DE', 'QD', 'QSR', 'QTRX', 'REPL', 'REXR', 'RLMD', 'RMAX', 'RMR', 'RU000A0JXTY7', 'RU000A1008J4', 'RU000A100FE5', 'RU000A100N12', 'RU000A100P85', 'RUS0628', 'RUSHA', 'RZD0324', 'RZD0527', 'SANM', 'SASR', 'SBSI', 'SCHL', 'SCVL', 'SEAS', 'SEB', 'SEGE2P1R', 'SEGE2P3R', 'SFBS', 'SGENperp', 'SGH', 'SIB0924', 'SLF', 'SMP', 'SNDR', 'SNEX', 'SRCE', 'SSTI', 'STBA', 'STC', 'STM1P2', 'STOK', 'SUI', 'SVEC1P1', 'SZU@DE', 'TCBK', 'TD', 'TDEU01', 'TDEU03', 'TEVA', 'TFIN', 'TFM01', 'TKA@DE', 'TKKclA1', 'TKKclA2', 'TKKclA3', 'TKKclB', 'TLX@DE', 'TPB', 'TPL', 'TRMK', 'TRP', 'TRS', 'TRY0130', 'TRY0141', 'TRY0225', 'TRY0228', 'TRY0234', 'TRY0327', 'TRY0330', 'TRY0336', 'TRY1028', 'TTEC', 'TTEL0225', 'TTGT', 'UEIC', 'UFCS', 'UN01@DE', 'UTDI@DE', 'UVV', 'VAKI0324', 'VAR1@DE', 'VIAV', 'VIB3@DE', 'VKCO', 'VOD', 'VOW@DE', 'VSH', 'WD', 'WTM', 'XMTR', 'XS0191754729', 'XS0885736925', 'XS1577953174', 'XS1693971043', 'YMAB']

    def __init__(self, name, highest_price=-1, round_price=-1):
        self.name = name.upper()
        self.highest_price = highest_price
        if self.highest_price == -1:
            self.got_highest_price = False
        else:
            self.got_highest_price = True
        self.round_price = round_price
        
        self.close_to_round_price = False
        self.reached_round_price = False
        self.broke_the_round_price = False

        guid = uuid.uuid4().hex
        self.guid = guid[:8] + '-' + guid[8:12] + '-' + guid[12:16] + '-' + guid[16:20] + '-' + guid[20:]
        Ticker.guid_name_dict[self.guid] = name

    def __repr__(self):
        return f'<{self.name} - {self.highest_price}>'

    '''
    работа с csv файлами
    '''
    def get_rows_from_csv(path, skip_firts=False):
        '''получить все строки из csv файла'''
        rows = []
        with open(path) as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(row)
        if skip_firts:
            return rows[1:]
        return rows
