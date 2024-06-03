

from keep_api_connect import netbox_api_instance



class NetboxGet():

    def __init__(self):
        self.nb = netbox_api_instance.get_instance()


    def get_phys_address(self,**kwargs):
        site_id = kwargs['site']['id']
        site = self.nb.dcim.sites.get(id=site_id)
        my_address = str(site.physical_address)
        return my_address


