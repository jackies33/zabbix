

import subprocess
import logging
import time
import os


from my_env import TEMP_FILE_PATH


def send_to_zabbix_bulk(zabbix_server, data):
    """Send bulk data to Zabbix"""
    try:
        if os.path.exists(TEMP_FILE_PATH):
            os.remove(TEMP_FILE_PATH)
        time.sleep(5)
        with open(TEMP_FILE_PATH, 'w') as temp_file:
            temp_file.write("\n".join(data) + '\n')
            logging.debug(f"Data written to temp file {TEMP_FILE_PATH}")
        command = f'sudo zabbix_sender -z {zabbix_server} -i {TEMP_FILE_PATH}'
        logging.debug(f"Executing command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        logging.debug(f"Successfully sent bulk data to Zabbix: {result.stdout}")
    except Exception as e:
        logging.error(f"Exception occurred: {e}")




