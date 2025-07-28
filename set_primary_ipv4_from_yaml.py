import yaml
import pynetbox

# Connect to NetBox
netbox_url = input("NetBox URL: ").strip()
netbox_token = input("NetBox API Token: ").strip()
yaml_file = input("YAML file with servers: ").strip()

nb = pynetbox.api(netbox_url, token=netbox_token)

# Load servers from YAML
with open(yaml_file, "r") as f:
    data = yaml.safe_load(f)

servers = data.get("servers", [])
if not servers:
    print("❌ No 'servers' found in YAML.")
    exit(1)

# Process each server
for server in servers:
    name = server.get("name")
    if not name:
        continue

    device = nb.dcim.devices.get(name=name)
    if not device:
        print(f"❌ Device not found: {name}")
        continue

    bond_iface = nb.dcim.interfaces.get(device_id=device.id, name="bond0")
    if not bond_iface:
        print(f"❌ bond0 not found on {name}")
        continue

    # Fetch all IPs for the device
    ip_list = nb.ipam.ip_addresses.filter(device_id=device.id)
    ip_found = None

    for ip in ip_list:
        if (
            ip.assigned_object_type == "dcim.interface"
            and ip.assigned_object_id == bond_iface.id
            and ip.family.label == "IPv4"
        ):
            ip_found = ip
            break

    if not ip_found:
        print(f"❌ No IPv4 assigned to bond0 on {name}")
        continue

    updated = device.update({"primary_ip4": ip_found.id})
    if updated:
        print(f"✅ {name}: primary_ip4 set to {ip_found.address}")
    else:
        print(f"❌ Failed to update primary IP for {name}")
