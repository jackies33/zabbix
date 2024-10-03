




import requests
import argparse
import os
import sys

#sys.path.append('/opt/zabbix_custom/zabbix_MAP/')
#sys.path.append('/app/')
#current_dir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(current_dir, '..', '..'))

from my_env import tg_token, chat_id

parser = argparse.ArgumentParser()
parser.add_argument("--db_type")
args = parser.parse_args()
db = args.db_type

class telega_bot():


    """
    Class for telegram bot , send messages
    """

    def tg_sender(self,**kwargs):
        message = kwargs['message']
        try:
            url = f"https://api.telegram.org/bot{tg_token}/sendMessage?chat_id={chat_id}&text={message}"
            requests.get(url).json()
        except ValueError:
            print("Error send message")
        return print("tg_sender is ok")





