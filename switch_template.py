import yaml

def generate_switch_yaml_template(switch_name, device_type, device_role, position):
    interfaces = []

    # Port templates for known switch types
    if device_type == "DCS-7160-48YC6-R":
        # 48 x 10GE ports: Et1 to Et48
        for i in range(1, 49):
            interfaces.append({
                "name": f"Et{i}",
                "type": "10gbase-x-sfpp",
                "mtu": 9000
            })
        # 6 x 100GE ports: Et49/ to Et54/
        for i in range(49, 55):
            interfaces.append({
                "name": f"Et{i}/",
                "type": "100gbase-x-qsfp28",
                "mtu": 9000
            })
    else:
        # Fallback default for unknown models
        interfaces.append({
            "name": "Et1",
            "type": "10gbase-x-sfpp",
            "mtu": 9000
        })

    switch_data = {
        "switches": [
            {
                "name": switch_name,
                "device_type": device_type,
                "device_role": device_role,
                "position": position,
                "interfaces": interfaces
            }
        ]
    }

    output_path = f"{switch_name.replace('.', '_')}_switch.yaml"
    with open(output_path, "w") as f:
        yaml.dump(switch_data, f, sort_keys=False, default_flow_style=False)

    print(f"✅ YAML generated: {output_path}")
    return output_path

# Example usage
if __name__ == "__main__":
    switch_name = input("Switch FQDN (e.g., rsa01a.company.com): ").strip()
    device_type = input("Device type (e.g., DCS-7160-48YC6-R): ").strip()
    device_role = input("Device role (e.g., switch): ").strip()
    position = int(input("Rack position (e.g., 5): "))

    generate_switch_yaml_template(switch_name, device_type, device_role, position)
