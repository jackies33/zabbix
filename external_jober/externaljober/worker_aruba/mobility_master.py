
import requests


from externaljober.my_env import MOBILITY_MASTER_BASE_URL,MOBILITY_MASTER_USERNAME, MOBILITY_MASTER_PASSWORD




class MOB_MASTER():

    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.login_response = self.session.post(
            f"{MOBILITY_MASTER_BASE_URL}/v1/api/login",
            data={"username":MOBILITY_MASTER_USERNAME, "password": MOBILITY_MASTER_PASSWORD}
        )
        if self.login_response.status_code == 200:
            print("Success auth")

    def get_ssid_count_users(self):
        try:
            uid_aruba = self.session.cookies.get("SESSION")
            # Выполнение команды
            command_url = f"{MOBILITY_MASTER_BASE_URL}/v1/configuration/showcommand?json=1&command=show+global-user-table+list&UIDARUBA={uid_aruba}"
            response = self.session.get(command_url)
            ssid_users_count = {}
            if response.status_code == 200:
                global_list_users = response.json()
                if global_list_users:
                    global_list_users = global_list_users["Global Users"]
                    for dict_user in global_list_users:
                        users_ssid = dict_user['Essid']
                        if users_ssid in ssid_users_count:
                            ssid_users_count[users_ssid] += 1
                        else:
                            ssid_users_count[users_ssid] = 1

            else:
                print("ERROR:", response.text)
            #keys_for_poping = []
            #for key in ssid_users_count:
            #    if "_" in key:
            #        keys_for_poping.append(key)
            #for key in keys_for_poping:
            #    ssid_users_count.pop(key)
            return [True,ssid_users_count]
        except Exception as err:
            return [False,err]





