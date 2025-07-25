import pynetbox

# NetBox API setup
NETBOX_URL = "http://your-netbox-url"
NETBOX_TOKEN = "your-api-token"
nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)

# User input
rack_id = input("Enter rack ID (e.g., a01): ").strip()
nic1_name = input("Enter NIC1 name (server → switch A, e.g., enp216s0f0): ").strip()

# Automatically generate NIC2
if nic1_name.endswith("0"):
    nic2_name = nic1_name[:-1] + "1"
else:
    print("[ERROR] NIC1 must end with '0' to auto-generate NIC2")
    exit(1)

# Name generation
server_prefix = rack_id  # e.g., a01
switch_suffix = rack_id[1:]  # e.g., 01
switch_a_name = f"rsa{switch_suffix}a.company.com"
switch_b_name = f"rsa{switch_suffix}b.company.com"

# Fetch switch devices
switch_a = nb.dcim.devices.get(name=switch_a_name)
switch_b = nb.dcim.devices.get(name=switch_b_name)

if not switch_a or not switch_b:
    print(f"[ERROR] Could not find one or both switches: {switch_a_name}, {switch_b_name}")
    exit(1)

# Loop over 40 servers
for i in range(1, 41):
    server_name = f"{server_prefix}p{i}.company.com"
    port_name = f"Et{i}"

    server = nb.dcim.devices.get(name=server_name)
    if not server:
        print(f"[WARN] Server not found: {server_name}")
        continue

    # Get specific interfaces by name
    nic1 = nb.dcim.interfaces.get(device_id=server.id, name=nic1_name)
    nic2 = nb.dcim.interfaces.get(device_id=server.id, name=nic2_name)

    intf_a = nb.dcim.interfaces.get(device_id=switch_a.id, name=port_name)
    intf_b = nb.dcim.interfaces.get(device_id=switch_b.id, name=port_name)

    # Server NIC1 → Switch A
    if not nic1 or not intf_a:
        print(f"[SKIP] A-side missing: {server_name}.{nic1_name} or {switch_a_name}.{port_name}")
    elif nic1.connected_endpoint or intf_a.connected_endpoint:
        print(f"[SKIP] Already connected: {server_name}.{nic1_name} or {switch_a_name}.{port_name}")
    else:
        try:
            nb.dcim.cables.create({
                "termination_a_type": "dcim.interface",
                "termination_a_id": nic1.id,
                "termination_b_type": "dcim.interface",
                "termination_b_id": intf_a.id,
                "status": "connected"
            })
            print(f"[OK] {server_name}.{nic1_name} → {switch_a_name}.{port_name}")
        except Exception as e:
            print(f"[ERROR] Failed A-side cable: {e}")

    # Server NIC2 → Switch B
    if not nic2 or not intf_b:
        print(f"[SKIP] B-side missing: {server_name}.{nic2_name} or {switch_b_name}.{port_name}")
    elif nic2.connected_endpoint or intf_b.connected_endpoint:
        print(f"[SKIP] Already connected: {server_name}.{nic2_name} or {switch_b_name}.{port_name}")
    else:
        try:
            nb.dcim.cables.create({
                "termination_a_type": "dcim.interface",
                "termination_a_id": nic2.id,
                "termination_b_type": "dcim.interface",
                "termination_b_id": intf_b.id,
                "status": "connected"
            })
            print(f"[OK] {server_name}.{nic2_name} → {switch_b_name}.{port_name}")
        except Exception as e:
            print(f"[ERROR] Failed B-side cable: {e}")
