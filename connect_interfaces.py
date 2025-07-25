import pynetbox

# NetBox API connection
NETBOX_URL = "http://your-netbox-url"
NETBOX_TOKEN = "your-api-token"
nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)

# Get user input
rack_id = input("Enter rack ID (e.g., a01): ").strip()
nic1_name = input("Enter NIC1 name (server → switch A, e.g., enp216s0f0): ").strip()

# Auto-generate NIC2
if nic1_name.endswith("0"):
    nic2_name = nic1_name[:-1] + "1"
else:
    print("[ERROR] NIC1 must end with '0' to derive NIC2")
    exit(1)

# Construct device names
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

# Loop through 40 servers
for i in range(1, 41):
    server_name = f"{server_prefix}p{i}.company.com"
    port_name = f"Et{i}"

    server = nb.dcim.devices.get(name=server_name)
    if not server:
        print(f"[WARN] Server not found: {server_name}")
        continue

    # Get server interfaces
    nic1 = nb.dcim.interfaces.get(device_id=server.id, name=nic1_name)
    nic2 = nb.dcim.interfaces.get(device_id=server.id, name=nic2_name)

    # Get switch interfaces
    intf_a = nb.dcim.interfaces.get(device_id=switch_a.id, name=port_name)
    intf_b = nb.dcim.interfaces.get(device_id=switch_b.id, name=port_name)

    ### A-SIDE CONNECTION (server.nic1 → switch_a.intf_a)
    if not nic1 or not intf_a:
        print(f"[SKIP] A-side interface missing: {server_name}.{nic1_name} or {switch_a_name}.{port_name}")
    elif nic1.connected_endpoint or intf_a.connected_endpoint:
        print(f"[SKIP] A-side already connected: {server_name}.{nic1_name} or {switch_a_name}.{port_name}")
    else:
        try:
            cable = nb.dcim.cables.create({
                "termination_a_type": "dcim.interface",
                "termination_a_id": nic1.id,
                "termination_b_type": "dcim.interface",
                "termination_b_id": intf_a.id,
                "status": "connected"
            })
            if cable and hasattr(cable, 'id'):
                print(f"[OK] Connected: {server_name}.{nic1.name} → {switch_a_name}.{port_name}")
            else:
                print(f"[ERROR] No cable returned for: {server_name}.{nic1.name} → {switch_a_name}.{port_name}")
        except Exception as e:
            if hasattr(e, 'response'):
                try:
                    print(f"[ERROR] A-side failure ({server_name}.{nic1.name} → {switch_a_name}.{port_name}):")
                    print(f"        {e.response.json()}")
                except:
                    print(f"[ERROR] A-side failure (no JSON): {e}")
            else:
                print(f"[ERROR] Unexpected A-side error: {e}")

    ### B-SIDE CONNECTION (server.nic2 → switch_b.intf_b)
    if not nic2 or not intf_b:
        print(f"[SKIP] B-side interface missing: {server_name}.{nic2_name} or {switch_b_name}.{port_name}")
    elif nic2.connected_endpoint or intf_b.connected_endpoint:
        print(f"[SKIP] B-side already connected: {server_name}.{nic2.name} or {switch_b_name}.{port_name}")
    else:
        try:
            cable = nb.dcim.cables.create({
                "termination_a_type": "dcim.interface",
                "termination_a_id": nic2.id,
                "termination_b_type": "dcim.interface",
                "termination_b_id": intf_b.id,
                "status": "connected"
            })
            if cable and hasattr(cable, 'id'):
                print(f"[OK] Connected: {server_name}.{nic2.name} → {switch_b_name}.{port_name}")
            else:
                print(f"[ERROR] No cable returned for: {server_name}.{nic2.name} → {switch_b_name}.{port_name}")
        except Exception as e:
            if hasattr(e, 'response'):
                try:
                    print(f"[ERROR] B-side failure ({server_name}.{nic2.name} → {switch_b_name}.{port_name}):")
                    print(f"        {e.response.json()}")
                except:
                    print(f"[ERROR] B-side failure (no JSON): {e}")
            else:
                print(f"[ERROR] Unexpected B-side error: {e}")


# Debug test for a01p1
rack_id = "a01"
nic1_name = "enp216s0f0"
nic2_name = "enp216s0f1"

server_name = f"{rack_id}p1.company.com"
switch_a_name = f"rsa01a.company.com"
switch_b_name = f"rsa01b.company.com"

server = nb.dcim.devices.get(name=server_name)
switch_a = nb.dcim.devices.get(name=switch_a_name)
switch_b = nb.dcim.devices.get(name=switch_b_name)

nic1 = nb.dcim.interfaces.get(device_id=server.id, name=nic1_name)
nic2 = nb.dcim.interfaces.get(device_id=server.id, name=nic2_name)
intf_a = nb.dcim.interfaces.get(device_id=switch_a.id, name="Et1")
intf_b = nb.dcim.interfaces.get(device_id=switch_b.id, name="Et1")

print("--- SERVER ---")
print("NIC1:", nic1.name if nic1 else "NOT FOUND")
print("NIC2:", nic2.name if nic2 else "NOT FOUND")

print("--- SWITCH ---")
print("SW-A Et1:", intf_a.name if intf_a else "NOT FOUND")
print("SW-B Et1:", intf_b.name if intf_b else "NOT FOUND")

print("--- CONNECTION STATE ---")
print("NIC1 connected to:", nic1.connected_endpoint if nic1 else "X")
print("NIC2 connected to:", nic2.connected_endpoint if nic2 else "X")
print("SW-A Et1 connected to:", intf_a.connected_endpoint if intf_a else "X")
print("SW-B Et1 connected to:", intf_b.connected_endpoint if intf_b else "X")
