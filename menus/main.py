from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu():
    keyboard = [
        [InlineKeyboardButton("🖥️ Proxmox", callback_data="proxmox")],
        [InlineKeyboardButton("📄 Auditoria", callback_data="audit:menu")],
        [InlineKeyboardButton("🚪 Sair", callback_data="exit")],
    ]

    return InlineKeyboardMarkup(keyboard)
