


from datetime import datetime
import requests
import random
import sys

from my_env import url_post_alarms,link_for_perr_alarms


def print_to_stdout(message):
    sys.stdout.write(message + '\n')
    sys.stdout.flush()

def event_manager(**kwargs):
    time = datetime.now()
    current_time = time.strftime("%Y-%m-%d %H:%M:%S.%f")
    peer_ip = kwargs.get("peer_ip","null_peer_ip")
    as_path = kwargs.get('as_path',"null_as_path")
    random_number = random.randint(100000, 999999)
    event_message = {
      "event_name": f"AS Path has been changed in peer {peer_ip}",
      "event_description": f"AS path has been changed in peer {peer_ip}, information recieved from OBMP system",
      "event_id": "239",
      "event_timestamp": f"{current_time}",
      "event_source": "bmp.net.tech.mosreg.ru",
      "event_key": f"{random_number}_bmp_event",
      "event_priority": "1",
      "event_severity": "4",
      "event_alert": "true",
      "link": link_for_perr_alarms,
      "event_interruption": "True",
      "event_timestamp_processing": f"{current_time}",
      "backlog": {
         "last_messages": [
            {
                "as_path": as_path,
                "peer_ip": peer_ip,
            }
         ]
      }
    }
    print_to_stdout(f"{event_message}")
    try:
        response = requests.post(url_post_alarms, json=event_message)

        if response.status_code == 200:
            print_to_stdout("Event posted successfully")
        else:
            print_to_stdout(f"Failed to post event. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print_to_stdout(f"Error sending POST request: {e}")





