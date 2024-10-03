



import os
import sys

#sys.path.append('/opt/zabbix_custom/zabbix_MAP/')
#sys.path.append('/app/')
#current_dir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(current_dir, '..', '..'))

from keep_api_connect import netbox_api_instance



class GetNBData():
    """
    class for getting different information about hosts from zabbix api
    """

    def __init__(self):
            self.nb = netbox_api_instance.get_instance()

    def get_all_MAP_groups(self):
        map_groups = []
        try:
            all_groups = self.nb.tenancy.contact_roles.all()
            for gr in all_groups:
                if "MAP" in str(gr.name) and str(gr.name) != "MAP_Group_MOCIKT_Hidden":
                    map_groups.append(str(gr))
                    return [True,map_groups]
        except Exception as err:
            print(err)
            return [False,err]



