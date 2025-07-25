import pynetbox

NETBOX_URL = "http://localhost:8001"
NETBOX_TOKEN = "your-netbox-token"
nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)

server_name = "a01p1.company.com"
server_iface_name = "enp216s0f0"
switch_name = "rsa01a.company.com"
switch_port_name = "Et1"

# Get devices
server = nb.dcim.devices.get(name=server_name)
switch = nb.dcim.devices.get(name=switch_name)

# Get interfaces
nic = nb.dcim.interfaces.get(device_id=server.id, name=server_iface_name)
port = nb.dcim.interfaces.get(device_id=switch.id, name=switch_port_name)

# Confirm validity
if not nic or not port or not nic.id or not port.id:
    raise ValueError("Invalid interface(s)")

# Delete existing cables if any
for intf in [nic, port]:
    if intf.connected_endpoint and intf.cable:
        nb.dcim.cables.delete([intf.cable.id])
        print(f"Deleted existing cable on {intf.device.name}.{intf.name}")

# Create cable
cable_data = {
    "termination_a_type": "dcim.interface",
    "termination_a_id": nic.id,
    "termination_b_type": "dcim.interface",
    "termination_b_id": port.id,
    "status": "connected"
}

try:
    cable = nb.dcim.cables.create(cable_data)
    print(f"[OK] Cable created: ID {cable.id}")
except Exception as e:
    print("[ERROR] Cable creation failed")
    if hasattr(e, 'response'):
        print(e.response.status_code)
        try:
            print(e.response.json())
        except:
            print(e)
    else:
        print(e)
