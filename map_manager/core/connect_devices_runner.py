


from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import sys
#sys.path.append('/opt/zabbix_custom/zabbix_MAP/')
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, '..', '..'))
from map_manager.core.mappings import MAPPINGS


def run_in_threads(devices, max_threads=30):
    mappings = MAPPINGS()
    results = []
    def worker(dev):
        return mappings.connection_exec(**dev)
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_device = {executor.submit(worker, dev): dev for dev in devices}
        for future in as_completed(future_to_device):
            device = future_to_device[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f"Device {device} generated an exception: {exc}")
                results.append([False, None, (f"Device {device} generated an exception: {exc}")])
    return results


