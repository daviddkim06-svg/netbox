import pynetbox

# NetBox API setup
NETBOX_URL = "http://your-netbox-url"
NETBOX_TOKEN = "your-netbox-token"
nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)

# Function to delete existing cable
def delete_existing_cable(interface):
    if interface and interface.connected_endpoint and interface.cable:
        try:
            cable_id = interface.cable.id
            nb.dcim.cables.delete([cable_id])
            print(f"[INFO] Deleted existing cable on {interface.device.name}.{interface.name} (cable ID {cable_id})")
        except Exception as e:
            print(f"[ERROR] Failed to delete cable on {interface.name}: {e}")

# Get user input
rack_id = input("Enter rack ID (e.g., a01): ").strip()
nic1_name = input("Enter NIC1 name (e.g., enp216s0f0): ").strip()

# Auto-generate NIC2
if nic1_name.endswith("0"):
    nic2_name = nic1_name[:-1] + "1"
else:
    print("[ERROR] NIC1 must end with '0' to auto-derive NIC2")
    exit(1)

# Build device names
server_prefix = rack_id
switch_suffix = rack_id[1:]
switch_a_name = f"rsa{switch_suffix}a.company.com"
switch_b_name = f"rsa{switch_suffix}b.company.com"

# Fetch switch devices
switch_a = nb.dcim.devices.get(name=switch_a_name)
switch_b = nb.dcim.devices.get(name=switch_b_name)

if not switch_a or not switch_b:
    print(f"[ERROR] Switch not found: {switch_a_name}, {switch_b_name}")
    exit(1)

# Loop through servers
for i in range(1, 41):
    server_name = f"{server_prefix}p{i}.company.com"
    port_name = f"Et{i}"

    server = nb.dcim.devices.get(name=server_name)
    if not server:
        print(f"[WARN] Server not found: {server_name}")
        continue

    nic1 = nb.dcim.interfaces.get(device_id=server.id, name=nic1_name)
    nic2 = nb.dcim.interfaces.get(device_id=server.id, name=nic2_name)
    intf_a = nb.dcim.interfaces.get(device_id=switch_a.id, name=port_name)
    intf_b = nb.dcim.interfaces.get(device_id=switch_b.id, name=port_name)

    # A-side: Server NIC1 → Switch A
    if not nic1 or not intf_a:
        print(f"[SKIP] Missing A-side interface: {server_name}.{nic1_name} or {switch_a_name}.{port_name}")
    else:
        delete_existing_cable(nic1)
        delete_existing_cable(intf_a)
        try:
            cable = nb.dcim.cables.create({
                "termination_a_type": "dcim.interface",
                "termination_a_id": nic1.id,
                "termination_b_type": "dcim.interface",
                "termination_b_id": intf_a.id,
                "status": "connected"
            })
            if cable and hasattr(cable, 'id'):
                print(f"[OK] {server_name}.{nic1.name} → {switch_a_name}.{port_name} (Cable ID {cable.id})")
            else:
                print(f"[ERROR] A-side: No cable returned for {server_name}.{nic1.name}")
        except Exception as e:
            if hasattr(e, 'response'):
                print(f"[ERROR] A-side ({server_name}.{nic1.name}): {e.response.json()}")
            else:
                print(f"[ERROR] A-side unexpected: {e}")

    # B-side: Server NIC2 → Switch B
    if not nic2 or not intf_b:
        print(f"[SKIP] Missing B-side interface: {server_name}.{nic2_name} or {switch_b_name}.{port_name}")
    else:
        delete_existing_cable(nic2)
        delete_existing_cable(intf_b)
        try:
            cable = nb.dcim.cables.create({
                "termination_a_type": "dcim.interface",
                "termination_a_id": nic2.id,
                "termination_b_type": "dcim.interface",
                "termination_b_id": intf_b.id,
                "status": "connected"
            })
            if cable and hasattr(cable, 'id'):
                print(f"[OK] {server_name}.{nic2.name} → {switch_b_name}.{port_name} (Cable ID {cable.id})")
            else:
                print(f"[ERROR] B-side: No cable returned for {server_name}.{nic2.name}")
        except Exception as e:
            if hasattr(e, 'response'):
                print(f"[ERROR] B-side ({server_name}.{nic2.name}): {e.response.json()}")
            else:
                print(f"[ERROR] B-side unexpected: {e}")
