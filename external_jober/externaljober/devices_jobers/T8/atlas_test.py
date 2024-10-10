

from puresnmp import get

result = get("10.100.137.85", 'n0cdwdm', '1.3.6.1.4.1.39433.1.4')
print(f"SNMP result: {result}")

