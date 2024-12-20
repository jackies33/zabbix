


import requests
import sys

sys.path.append('/opt/zabbix_custom/')

from remote_system.core.my_env_kr01 import chat_id,tg_token

class tg_bot():

    """
    Class for telegram bot , send messages
    """

    def __init__(self, message=None):
        self.message = message


    def tg_sender(self,*args):

                try:
                    url = f"https://api.telegram.org/bot{tg_token}/sendMessage?chat_id={chat_id}&text={self.message}"
                    requests.get(url).json()
                except ValueError:
                    print("Error send message")
                return print("tg_sender is ok")


if __name__ == '__main__':
        message = 'test'
        tgbot = tg_bot()
        tgbot.tg_sender(message)


