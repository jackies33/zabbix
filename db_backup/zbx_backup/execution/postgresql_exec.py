

import subprocess
from datetime import datetime
import time
import os
import requests
import sys

sys.path.append("/opt/db_backup/")

from zbx_backup.my_env import list_dbs,tg_token, chat_id, db_ip, db_port


def tg_bot(message):
    try:
        url = f"https://api.telegram.org/bot{tg_token}/sendMessage?chat_id={chat_id}&text={message}"
        requests.get(url).json()
    except ValueError:
        print("Error send message")
    return print("tg_sender is ok")



def delete_old_backups(backup_dir):
    try:
        # Получаем список файлов в директории
        files = [
            os.path.join(backup_dir, f) for f in os.listdir(backup_dir)
            if os.path.isfile(os.path.join(backup_dir, f))
        ]
        files.sort(key=os.path.getmtime, reverse=True)
        if len(files) > 3:
            for old_file in files[3:]:
                try:
                    os.remove(old_file)
                    print(f"Deleted old backup: {old_file}")
                except OSError as e:
                    print(f"Error deleting file {old_file}: {e}")
    except Exception as e:
        print(f"Error during backup cleanup: {e}")


def db_execution():
    try:
        list_backups_exec = []
        subprocess.run("sudo mount 10.50.100.75:/opt/nfs/noc.tech.mosreg.ru /mnt/sharedfolder_client", shell=True)
        time.sleep(2)
        now = datetime.now()
        dt_string = now.strftime("Date_%Y-%m-%d_Time_%H-%M-%S")
        for db_inst in list_dbs:
            db_name = db_inst['db_name']
            db_user = db_inst['db_user']
            db_pass = db_inst['db_pass']
            result_dict = {"db_name": db_name}
            # Проверка и создание директории для бэкапа
            backup_dir = f"/mnt/sharedfolder_client/Full/{db_name}"
            if not os.path.exists(backup_dir):
                try:
                    os.makedirs(backup_dir)
                    print(f"Created backup directory: {backup_dir}")
                except OSError as e:
                    print(f"Error creating directory {backup_dir}: {e}")
                    result_dict.update({"result": False})
                    list_backups_exec.append(result_dict)
                    continue
            pg_dump_command = f"sudo PGPASSWORD={db_pass} pg_dump -U {db_user} -h {db_ip} -p {db_port} {db_name} > " \
                              f"{backup_dir}/pgsql_backup_from_{dt_string}.sql"

            try:
                result = subprocess.run(pg_dump_command, shell=True, check=True)
                print("Backup completed successfully.")
            except subprocess.CalledProcessError as e:
                print("Error during backup:", e.stderr.decode())
            backup_file_path = f"{backup_dir}/pgsql_backup_from_{dt_string}.sql"
            if os.path.exists(backup_file_path):
                print(f"Backup file created: {backup_file_path}")
                result_dict.update({"result": True})
            else:
                print("Backup file not found.")
                result_dict.update({"result": False})
            delete_old_backups(backup_dir)
            list_backups_exec.append(result_dict)

        return [True,list_backups_exec]
    except Exception as e:
        print(e)
        return [False,e]

def execution_core():

    db_executing_result = db_execution()
    if db_executing_result[0] == False:
        print(db_executing_result[1])
        tg_massage = f"The backup for zabbix and grafana DB's was FAILED!"
        if tg_massage:
            tg_sending = tg_bot(tg_massage)
            print(tg_sending)
    elif db_executing_result[0] == True:
        for db in db_executing_result[1]:
            db_name = db['db_name']
            backup_result = db['result']
            tg_massage = None
            if backup_result == True:
                tg_massage = f"The backup for db:{db_name} was completed successfully"
            elif backup_result == False:
                tg_massage = f"The backup for db:{db_name} was FAILED!"
            if tg_massage:
                tg_sending = tg_bot(tg_massage)
                print(tg_sending)




if __name__ == '__main__':
    executing = execution_core()

