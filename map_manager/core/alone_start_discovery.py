






import sys
import os

sys.stderr = open(os.devnull, 'w')

#sys.path.append('/opt/zabbix_custom/zabbix_MAP/')
#sys.path.append('/app/')
#current_dir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(current_dir, '..', '..'))

from discovery import START_DISCOVERY

if __name__ == "__main__":
    #essense_value = 'MAP for p-pe devices TEST'
    essenses_values = ['MAP_Group_Core']
    #essenses_values = my_maps_groups
    for ess in essenses_values:
        starting = START_DISCOVERY(**{"essence": "MAP_Group", "essence_value": ess})
        result = starting.start_proccess_discovery_main()
        print(f"\n\n{result[0]}")
        for res in result[1]:
            print(res)


sys.stderr = sys.__stderr__


