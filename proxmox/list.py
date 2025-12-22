from proxmox.client import get_proxmox

def list_all_instances():
    proxmox = get_proxmox()
    instances = []

    nodes = proxmox.nodes.get()

    for node in nodes:
        node_name = node["node"]

  
        for vm in proxmox.nodes(node_name).qemu.get():
            instances.append({
                "type": "vm",
                "id": vm["vmid"],
                "name": vm.get("name", f"vm-{vm['vmid']}"),
                "status": vm["status"],
                "node": node_name
            })

  
        for ct in proxmox.nodes(node_name).lxc.get():
            instances.append({
                "type": "lxc",
                "id": ct["vmid"],
                "name": ct.get("name", f"ct-{ct['vmid']}"),
                "status": ct["status"],
                "node": node_name
            })

    return instances
