import pynetbox

# Setup
NETBOX_URL = "http://your-netbox-url"
NETBOX_TOKEN = "your-netbox-token"
nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)

# Define target devices and interfaces
server_name = "a01p1.company.com"
server_iface_name = "enp216s0f0"
switch_name = "rsa01a.company.com"
switch_port_name = "Et1"

# Fetch devices
server = nb.dcim.devices.get(name=server_name)
switch = nb.dcim.devices.get(name=switch_name)

# Fetch interfaces
nic = nb.dcim.interfaces.get(device_id=server.id, name=server_iface_name)
port = nb.dcim.interfaces.get(device_id=switch.id, name=switch_port_name)

# Debug info
print("\n=== Interface Info ===")
print(f"Server NIC: {nic.name if nic else 'NOT FOUND'} (ID: {nic.id if nic else 'N/A'})")
print(f"Switch Port: {port.name if port else 'NOT FOUND'} (ID: {port.id if port else 'N/A'})")

if not nic or not port or not nic.id or not port.id:
    print("[ERROR] One or both interfaces are missing or invalid.")
    exit(1)

# Optional: delete existing cable
def delete_existing_cable(interface):
    if interface and interface.connected_endpoint and interface.cable:
        try:
            nb.dcim.cables.delete([interface.cable.id])
            print(f"[INFO] Deleted cable on {interface.device.name}.{interface.name}")
        except Exception as e:
            print(f"[ERROR] Could not delete cable on {interface.name}: {e}")

delete_existing_cable(nic)
delete_existing_cable(port)

# Try cable creation
print("\n=== Cable Create Attempt ===")
print(f"A: {server.name}.{nic.name} (ID: {nic.id})")
print(f"B: {switch.name}.{port.name} (ID: {port.id})")

try:
    cable = nb.dcim.cables.create({
        "termination_a_type": "dcim.interface",
        "termination_a_id": nic.id,
        "termination_b_type": "dcim.interface",
        "termination_b_id": port.id,
        "status": "connected"
    })
    if cable and hasattr(cable, 'id'):
        print(f"[OK] Cable created with ID: {cable.id}")
    else:
        print(f"[FAIL] Cable object not returned.")
except Exception as e:
    print("[ERROR] Exception during cable creation.")
    if hasattr(e, 'response'):
        try:
            print(f"→ HTTP {e.response.status_code}: {e.response.json()}")
        except:
            print(f"→ Exception has response but no JSON: {e}")
    else:
        print(f"→ Unexpected exception: {e}")
