from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from proxmox.list import list_all_instances


def instances_menu():
    instances = list_all_instances()
    rows = []

    for inst in instances:
        label = "🖥️" if inst["type"] == "vm" else "📦"
        rows.append(
            [
                InlineKeyboardButton(
                    f"{label} {inst['name']} ({inst['status']})",
                    callback_data=f"instance:{inst['type']}:{inst['node']}:{inst['id']}"
                )
            ]
        )

    # 🚪 Botão Sair na lista de VMs/LXCs
    rows.append(
        [
            InlineKeyboardButton(
                "🚪 Sair",
                callback_data="exit"
            )
        ]
    )

    return InlineKeyboardMarkup(rows)
