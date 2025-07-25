import pynetbox
import yaml

NETBOX_URL = "http://localhost:8001"
NETBOX_TOKEN = "your-token"
nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)

# === YAML 파일 불러오기 ===
with open("interface_pairs.yaml", "r") as f:
    data = yaml.safe_load(f)

interfaces = data.get("interfaces", [])
if len(interfaces) % 2 != 0:
    raise ValueError("Interface list must contain an even number of entries (A-B pairs).")

# === 2개씩 묶어서 케이블 연결
for i in range(0, len(interfaces), 2):
    a = interfaces[i]
    b = interfaces[i+1]

    a_id = a.get("interface_id")
    b_id = b.get("interface_id")

    if not a_id or not b_id:
        print(f"[SKIP] Missing ID in pair: {a.get('device')} / {b.get('device')}")
        continue

    # termination A/B 인터페이스 객체 조회
    iface_a = nb.dcim.interfaces.get(a_id)
    iface_b = nb.dcim.interfaces.get(b_id)

    if not iface_a or not iface_b:
        print(f"[SKIP] Interface not found for IDs: {a_id}, {b_id}")
        continue

    # 기존 케이블 있으면 삭제
    for iface in [iface_a, iface_b]:
        if iface.connected_endpoint and iface.cable:
            nb.dcim.cables.delete([iface.cable.id])
            print(f"[INFO] Deleted existing cable on {iface.device.name}.{iface.name}")

    # 케이블 생성
    try:
        cable = nb.dcim.cables.create({
            "termination_a_type": "dcim.interface",
            "termination_a_id": a_id,
            "termination_b_type": "dcim.interface",
            "termination_b_id": b_id,
            "status": "connected"
        })
        print(f"[OK] Cable created: {iface_a.device.name}.{iface_a.name} ↔ {iface_b.device.name}.{iface_b.name}")
    except Exception as e:
        print(f"[FAIL] Cable create failed for {iface_a.device.name} ↔ {iface_b.device.name}: {e}")
