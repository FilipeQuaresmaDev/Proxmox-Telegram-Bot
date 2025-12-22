def start_instance(proxmox, inst_type, node, vmid):
    if inst_type == "vm":
        return proxmox.nodes(node).qemu(vmid).status.start.post()
    else:
        return proxmox.nodes(node).lxc(vmid).status.start.post()


def stop_instance(proxmox, inst_type, node, vmid):
    if inst_type == "vm":
        return proxmox.nodes(node).qemu(vmid).status.stop.post()
    else:
        return proxmox.nodes(node).lxc(vmid).status.stop.post()


def reboot_instance(proxmox, inst_type, node, vmid):
    if inst_type == "vm":
        return proxmox.nodes(node).qemu(vmid).status.reboot.post()
    else:
        return proxmox.nodes(node).lxc(vmid).status.reboot.post()
