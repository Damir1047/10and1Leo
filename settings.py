from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv('ALOR_USERNAME')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
EXCHANGE = 'SPBX'
URL_OAUTH = 'https://oauth.alor.ru'

shares_path = './shares/shares.csv'
