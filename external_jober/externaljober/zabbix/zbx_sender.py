

import subprocess
import time
import os


#from externaljober.my_env import TEMP_FILE_PATH
#TEMP_FILE_PATH = os.getenv('TEMP_FILE_PATH', '/app/tmp/data_for_sender')
TEMP_FILE_PATH = '/app/externaljober/zabbix/data_for_sender'

"""

def send_to_zabbix_bulk(zabbix_server, data):
    '''#Send bulk data to Zabbix'''
    try:
        if os.path.exists(TEMP_FILE_PATH):
            os.remove(TEMP_FILE_PATH)
        time.sleep(3)
        with open(TEMP_FILE_PATH, 'w') as temp_file:
            temp_file.write("\n".join(data) + '\n')
            print(f"Data written to temp file {TEMP_FILE_PATH}")
        command = f'sudo zabbix_sender -z {zabbix_server} -i {TEMP_FILE_PATH}'
        print(f"Executing command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"Successfully sent bulk data to Zabbix: {result.stdout}")
    except Exception as e:
        print(f"Exception occurred: {e}")


"""



def send_to_zabbix_bulk(zabbix_server, data):
    """Send bulk data to Zabbix using stdin instead of a temp file"""
    try:
        #print(data)
        command = f'zabbix_sender -z {zabbix_server} -i -'
        print(f"Executing command: {command}")
        result = subprocess.run(command, input="\n".join(data) + '\n', shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Successfully sent bulk data to Zabbix: {result.stdout}")
        else:
            print(f"Error occurred: {result.stderr}")
    except Exception as e:
        print(f"Exception occurred: {e}")


#if __name__ == "__main__":
#    # Пример вызова функции с тестовыми данными
#    send_to_zabbix_bulk('10.50.164.38', ['data1', 'data2', 'data3'])




