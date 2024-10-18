

from pyzabbix import ZabbixAPI,ZabbixAPIException
import pynetbox
import atexit
import urllib3


from externaljober.my_env import zbx_api_url, zbx_api_token,netbox_url,netbox_api_token



urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ZabbixAPIInstance:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.zapi = None
        return cls._instance

    def get_instance(self):
        if not self.zapi:
            self.zapi = ZabbixAPI(zbx_api_url)
            self.zapi.session.verify = False
            self.zapi.login(api_token=zbx_api_token)
            #atexit.register(self.logout)
        return self.zapi

    def logout(self):
        if self.zapi:
            try:
                self.zapi.user.logout()
            except ZabbixAPIException as e:
                print(f"Error during logout: {e}")

zabbix_api_instance = ZabbixAPIInstance()


class NetboxAPIInstance:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.nb = None
        return cls._instance

    def get_instance(self):
        if not self.nb:
            self.url = netbox_url
            self.token = netbox_api_token
            self.nb = pynetbox.api(url=self.url, token=self.token)
            self.nb.http_session.verify = False
            atexit.register(self.logout)
        return self.nb

    def logout(self):
        if self.nb:
            try:
                self.nb.http_session.close()
            except Exception as e:
                print(f"Error during logout: {e}")


netbox_api_instance = NetboxAPIInstance()



