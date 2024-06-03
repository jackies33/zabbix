

import requests


class telega_bot():

    """
    Class for telegram bot , send messages
    """

    from my_env import tg_token, chat_id
    def __init__(self, message=None):
        self.message = message


    def tg_sender(self,*args):

                try:
                    url = f"https://api.telegram.org/bot{self.tg_token}/sendMessage?chat_id={self.chat_id}&text={self.message}"
                    requests.get(url).json()
                except ValueError:
                    print("Error send message")
                return print("tg_sender is ok")


if __name__ == '__main__':
        message = 'test'
        tgbot = telega_bot()
        tgbot.tg_sender(message)


