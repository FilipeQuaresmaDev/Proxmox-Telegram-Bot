def get_instance_status(proxmox, inst_type, node, vmid):
    """
    Retorna status avançado de VM ou LXC via Proxmox API
    """

    if inst_type == "vm":
        data = proxmox.nodes(node).qemu(vmid).status.current.get()
    else:
        data = proxmox.nodes(node).lxc(vmid).status.current.get()

    cpu_percent = round(data.get("cpu", 0) * 100, 2)

    mem_used = data.get("mem", 0)
    mem_total = data.get("maxmem", 1)

    maxdisk = data.get("maxdisk", 0)


    if inst_type == "lxc":
        disk_used = data.get("disk", 0)
    else:
        disk_used = None

    net_in = data.get("netin", 0)
    net_out = data.get("netout", 0)

    uptime = data.get("uptime", 0)

    return {
        "cpu": cpu_percent,
        "mem_used": mem_used,
        "mem_total": mem_total,
        "disk_used": disk_used,
        "disk_total": maxdisk,
        "net_in": net_in,
        "net_out": net_out,
        "uptime": uptime,
        "type": inst_type,
    }


def human_bytes(value):
    if value is None:
        return "N/A"

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024:
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{value:.2f} PB"


def human_uptime(seconds):
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")

    return " ".join(parts) if parts else "0m"
