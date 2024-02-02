

from flask import Flask, request, make_response
import json
from handler_core import Handler_WebHook



''' 
for daemon setup script
create  - >> "mcedit etc/systemd/system/web_root.service"
copy in web_root.service ->> 
_______________________________

[Unit]
Description=Listen and classifier web hooks from netbox App

[Service]
ExecStart=/usr/bin/python3 /opt/noc/custom/etl/web_root.py
StandardOutput=file:/var/log/web_root/output.log
StandardError=file:/var/log/web_root/error.log
Restart=always

[Install]
WantedBy=multi-user.target
_________________________________

<<----copy in web_root.service

run next commands -->>>
_____________________________
sudo systemctl daemon-reload
sudo systemctl enable web_root.service
sudo systemctl start web_root.service

______________________________

<<--- run next commands

'''


app = Flask(__name__)
@app.route('/netbox_webhook', methods=['POST'])

#create listener web hooks from netbox

def webhook():
            data = request.get_json()
            json_dump = json.dumps(data)
            print(json_dump)
            hanlder = Handler_WebHook(data)
            hanlder.core_handler()



            response = {
                'fulfillmentText': 'success'
            }
            return make_response(json.dumps(response))



if __name__ == '__main__':
    app.run(host='10.50.50.178', port=3501)

