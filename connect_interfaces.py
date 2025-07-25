import pynetbox

NETBOX_URL = "http://your-netbox-url"
NETBOX_TOKEN = "your-api-token"

nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)

# 사용자 입력: 랙 이름 (예: a01)
rack_id = input("Enter rack name (ex: a01): ").strip()

# 이름 생성
server_base = rack_id  # a01
switch_base = rack_id[1:]  # 01
switch_a_name = f"rsa{switch_base}a.company.com"
switch_b_name = f"rsa{switch_base}b.company.com"

# 스위치 조회
switch_a = nb.dcim.devices.get(name=switch_a_name)
switch_b = nb.dcim.devices.get(name=switch_b_name)

if not switch_a or not switch_b:
    print(f"[ERROR] Switches not found: {switch_a_name}, {switch_b_name}")
    exit(1)

for i in range(1, 41):
    server_name = f"{server_base}p{i}.company.com"
    port_name = f"Et{i}"

    server = nb.dcim.devices.get(name=server_name)
    if not server:
        print(f"[WARN] Server not found: {server_name}")
        continue

    interfaces = list(nb.dcim.interfaces.filter(device_id=server.id))
    data_interfaces = [
        intf for intf in interfaces
        if not intf.mgmt_only and intf.name != "bond0"
    ]

    if len(data_interfaces) < 2:
        print(f"[WARN] Not enough data interfaces on {server_name}")
        continue

    data_interfaces.sort(key=lambda x: x.name)
    nic1 = data_interfaces[0]
    nic2 = data_interfaces[1]

    intf_a = nb.dcim.interfaces.get(device_id=switch_a.id, name=port_name)
    intf_b = nb.dcim.interfaces.get(device_id=switch_b.id, name=port_name)

    if not intf_a or not intf_b:
        print(f"[WARN] Switch port {port_name} not found on switch A or B")
        continue

    try:
        nb.dcim.cables.create({
            "termination_a_type": "dcim.interface",
            "termination_a_id": nic1.id,
            "termination_b_type": "dcim.interface",
            "termination_b_id": intf_a.id,
            "status": "connected"
        })
        print(f"[OK] {server_name}.{nic1.name} <-> {switch_a_name}.{port_name}")
    except Exception as e:
        print(f"[ERROR] {server_name}.{nic1.name} connection failed: {e}")

    try:
        nb.dcim.cables.create({
            "termination_a_type": "dcim.interface",
            "termination_a_id": nic2.id,
            "termination_b_type": "dcim.interface",
            "termination_b_id": intf_b.id,
            "status": "connected"
        })
        print(f"[OK] {server_name}.{nic2.name} <-> {switch_b_name}.{port_name}")
    except Exception as e:
        print(f"[ERROR] {server_name}.{nic2.name} connection failed: {e}")
