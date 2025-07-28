import yaml
import pynetbox

# --- NetBox connection ---
netbox_url = input("NetBox URL (e.g., http://netbox.local): ").strip()
netbox_token = input("NetBox API Token: ").strip()
yaml_file = input("YAML file path (e.g., a01_netbox_devices.yaml): ").strip()

nb = pynetbox.api(netbox_url, token=netbox_token)

# --- Load server list from YAML ---
with open(yaml_file, 'r') as f:
    data = yaml.safe_load(f)

servers = data.get("servers", [])
if not servers:
    print("❌ No 'servers' list found in YAML.")
    exit(1)

# --- Process each server ---
for server in servers:
    device_name = server.get("name")
    if not device_name:
        continue

    device = nb.dcim.devices.get(name=device_name)
    if not device:
        print(f"❌ Device not found in NetBox: {device_name}")
        continue

    bond_iface = nb.dcim.interfaces.get(device_id=device.id, name="bond0")
    if not bond_iface:
        print(f"❌ 'bond0' interface not found on {device_name}")
        continue

    ip_list = nb.ipam.ip_addresses.filter(device=device.id, interface_id=bond_iface.id)
    ip = next((ip for ip in ip_list if ip.family.label == "IPv4"), None)

    if not ip:
        print(f"❌ No IPv4 address found on bond0 of {device_name}")
        continue

    updated = device.update({"primary_ip4": ip.id})
    if updated:
        print(f"✅ {device_name}: Primary IPv4 set to {ip.address}")
    else:
        print(f"❌ Failed to set primary IP for {device_name}")
