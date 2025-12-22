from ssh.executor import run_command



def get_vm_ip_via_agent(proxmox, node, vmid):
    """
    IP de VM via QEMU Guest Agent (automático)
    """
    try:
        data = proxmox.nodes(node).qemu(vmid).agent.get(
            "network-get-interfaces"
        )

        for iface in data.get("result", []):
            for addr in iface.get("ip-addresses", []):
                if (
                    addr.get("ip-address-type") == "ipv4"
                    and not addr.get("ip-address").startswith("127")
                ):
                    return addr.get("ip-address")
    except Exception as e:
        print("Erro Guest Agent VM:", e)

    return "Indisponível"


def get_lxc_ip_via_api(proxmox, node, vmid):
    try:
        # Consulta as interfaces do container via API
        interfaces = proxmox.nodes(node).lxc(vmid).interfaces.get()
        for iface in interfaces:
            # Filtra o IP da interface que não seja loopback
            if iface.get("name") != "lo":
                ip = iface.get("inet") # Retorna algo como "192.168.1.50/24"
                if ip:
                    return ip.split('/')[0]
    except Exception as e:
        print(f"Erro API LXC: {e}")
    return "Indisponível"
